import onnxruntime as ort
import numpy as np
import cv2
from util.logger import Logger
from ml.abstract_class_definition import onnx_model
from ml.yolox_utils import COCO_CLASSES, _COLORS

class YoloX(onnx_model):

    def __init__(self):
        self.session = None
        self.load_model()
        self.logger = Logger(self.__class__).get_logger()

    def load_model(self):
        self.session = ort.InferenceSession("./ml/image_models_files/yolox_s.onnx")

    def normalize_input(self, img):
        """
        Normalize the image to have as maximum 1024 x 720, without breaking the aspect ratio of the img.
        For that let's get the ratio to scale the image.
        """
        max_height = 1024
        max_width = 720

        height, width = img.shape[:2]

        scaling_factor = min(max_height / height, max_width / width)

        new_height = int(height * scaling_factor)
        new_width = int(width * scaling_factor)

        resized_img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)

        return resized_img

    def preprocess(self,img, input_size, swap=(2, 0, 1)):
        if len(img.shape) == 3:
            padded_img = np.ones((input_size[0], input_size[1], 3), dtype=np.uint8) * 114
        else:
            padded_img = np.ones(input_size, dtype=np.uint8) * 114

        r = min(input_size[0] / img.shape[0], input_size[1] / img.shape[1])
        resized_img = cv2.resize(
            img,
            (int(img.shape[1] * r), int(img.shape[0] * r)),
            interpolation=cv2.INTER_LINEAR,
        ).astype(np.uint8)
        padded_img[: int(img.shape[0] * r), : int(img.shape[1] * r)] = resized_img

        padded_img = padded_img.transpose(swap)
        padded_img = np.ascontiguousarray(padded_img, dtype=np.float32)
        return padded_img, r
    

    def predict(self,image, filepath):
        input_shape = (640,640)
        resized_image = self.normalize_input(image)
        img, ratio = self.preprocess(resized_image, input_shape)
        
        ort_inputs = {self.session.get_inputs()[0].name: img[None, :, :, :]}
        output = self.session.run(None, ort_inputs)
        predictions = self.demo_postprocess(output[0], input_shape)[0]

        boxes = predictions[:, :4]
        scores = predictions[:, 4:5] * predictions[:, 5:]
        boxes_xyxy = np.ones_like(boxes)
        boxes_xyxy[:, 0] = boxes[:, 0] - boxes[:, 2]/2.
        boxes_xyxy[:, 1] = boxes[:, 1] - boxes[:, 3]/2.
        boxes_xyxy[:, 2] = boxes[:, 0] + boxes[:, 2]/2.
        boxes_xyxy[:, 3] = boxes[:, 1] + boxes[:, 3]/2.
        boxes_xyxy /= ratio
        dets = self.multiclass_nms(boxes_xyxy, scores, nms_thr=0.6, score_thr=0.1, class_agnostic=False)
        if dets is not None:
            final_boxes, final_scores, final_cls_inds = dets[:, :4], dets[:, 4], dets[:, 5]
            crops_info = self.extract_crops_info(final_boxes, final_scores, final_cls_inds,
                            conf=0.45, class_names=COCO_CLASSES)
            annotated_image = self.annotate_image(resized_image, crops_info)
            cv2.imwrite(filepath,annotated_image)
            return annotated_image, crops_info
        else:
            cv2.imwrite(filepath,annotated_image)
            return image, []

    def nms(self,boxes, scores, nms_thr):
        """Single class NMS implemented in Numpy."""
        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]

        areas = (x2 - x1 + 1) * (y2 - y1 + 1)
        order = scores.argsort()[::-1]

        keep = []
        while order.size > 0:
            i = order[0]
            keep.append(i)
            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])

            w = np.maximum(0.0, xx2 - xx1 + 1)
            h = np.maximum(0.0, yy2 - yy1 + 1)
            inter = w * h
            ovr = inter / (areas[i] + areas[order[1:]] - inter)

            inds = np.where(ovr <= nms_thr)[0]
            order = order[inds + 1]

        return keep

    def extract_crops_info(self, boxes, scores, cls_ids, conf=0.5, class_names=COCO_CLASSES):
        crops_info = []
        for i in range(len(boxes)):
            crop_info = {}
            box = boxes[i]
            cls_id = int(cls_ids[i])
            score = scores[i]
            if score < conf:
                continue
            x0 = int(box[0])
            y0 = int(box[1])
            x1 = int(box[2])
            y1 = int(box[3])
            crop_info["bbox"] = {"x_min": x0, "y_min": y0, "x_max": x1, "y_max": y1}
            crop_info["class"] = class_names[cls_id]
            crop_info["confidence"] = round(score * 100, 1)
            crops_info.append(crop_info)

        return crops_info

    def annotate_image(self, img, crops_info):
        for crop in crops_info:
            bbox = crop['bbox']
            class_name = crop['class']
            confidence = crop['confidence']
            x0, y0, x1, y1 = bbox['x_min'], bbox['y_min'], bbox['x_max'], bbox['y_max']

            # Generate color per class
            color = (_COLORS[COCO_CLASSES.index(class_name)] * 255).astype(np.uint8).tolist()

            # Draw bounding box
            cv2.rectangle(img, (x0, y0), (x1, y1), color, 4)

            # Draw label
            label = f"{class_name} {confidence:.2f}"
            t_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(img, (x0, y0 - t_size[1]), (x0 + t_size[0], y0), color, -1)
            cv2.putText(img, label, (x0, y0), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        return img

    def demo_postprocess(self,outputs, img_size, p6=False):
        grids = []
        expanded_strides = []
        strides = [8, 16, 32] if not p6 else [8, 16, 32, 64]

        hsizes = [img_size[0] // stride for stride in strides]
        wsizes = [img_size[1] // stride for stride in strides]

        for hsize, wsize, stride in zip(hsizes, wsizes, strides):
            xv, yv = np.meshgrid(np.arange(wsize), np.arange(hsize))
            grid = np.stack((xv, yv), 2).reshape(1, -1, 2)
            grids.append(grid)
            shape = grid.shape[:2]
            expanded_strides.append(np.full((*shape, 1), stride))

        grids = np.concatenate(grids, 1)
        expanded_strides = np.concatenate(expanded_strides, 1)
        outputs[..., :2] = (outputs[..., :2] + grids) * expanded_strides
        outputs[..., 2:4] = np.exp(outputs[..., 2:4]) * expanded_strides

        return outputs

    def multiclass_nms(self,boxes, scores, nms_thr, score_thr, class_agnostic=True):
        """Multiclass NMS implemented in Numpy"""
        if class_agnostic:
            nms_method = self.multiclass_nms_class_agnostic
        else:
            nms_method = self.multiclass_nms_class_aware
        return nms_method(boxes, scores, nms_thr, score_thr)

    def multiclass_nms_class_aware(self,boxes, scores, nms_thr, score_thr):
        """Multiclass NMS implemented in Numpy. Class-aware version."""
        final_dets = []
        num_classes = scores.shape[1]
        for cls_ind in range(num_classes):
            cls_scores = scores[:, cls_ind]
            valid_score_mask = cls_scores > score_thr
            if valid_score_mask.sum() == 0:
                continue
            else:
                valid_scores = cls_scores[valid_score_mask]
                valid_boxes = boxes[valid_score_mask]
                keep = self.nms(valid_boxes, valid_scores, nms_thr)
                if len(keep) > 0:
                    cls_inds = np.ones((len(keep), 1)) * cls_ind
                    dets = np.concatenate(
                        [valid_boxes[keep], valid_scores[keep, None], cls_inds], 1
                    )
                    final_dets.append(dets)
        if len(final_dets) == 0:
            return None
        return np.concatenate(final_dets, 0)

    def multiclass_nms_class_agnostic(self,boxes, scores, nms_thr, score_thr):
        """Multiclass NMS implemented in Numpy. Class-agnostic version."""
        cls_inds = scores.argmax(1)
        cls_scores = scores[np.arange(len(cls_inds)), cls_inds]

        valid_score_mask = cls_scores > score_thr
        if valid_score_mask.sum() == 0:
            return None
        valid_scores = cls_scores[valid_score_mask]
        valid_boxes = boxes[valid_score_mask]
        valid_cls_inds = cls_inds[valid_score_mask]
        keep = self.nms(valid_boxes, valid_scores, nms_thr)
        if keep:
            dets = np.concatenate(
                [valid_boxes[keep], valid_scores[keep, None], valid_cls_inds[keep, None]], 1
            )
        return dets

