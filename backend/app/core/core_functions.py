from typing import Any
import logging
from util.camel_base_model import CamelBaseModel
import cv2
import numpy as np
from io import BytesIO
from ml.yolox_model import YoloX
from core.data_models import *

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)



class DataModel(CamelBaseModel):
    db: Any   

    ####### I/O from data-files
    async def load_image_from_bytes(self,image_bytes):
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return image
    
    async def return_bytes_from_image(self, image:np) -> BytesIO:
        _, buffer = cv2.imencode('.png', image)
        image_bytes = BytesIO(buffer)
        return image_bytes


    ############# I/O data from MongoDB
    def create_image_object(self, image_data: Any) -> Image:
        image_object = Image.parse_obj(image_data)
        logger.info(f"Image created with timestamp: {datetime.now()}")
        return image_object

    def save_image_to_db(self, image_data: Any):
        image_object = self.create_image_object(image_data)
        self.db["images"].insert_one(image_object.dict())
        logger.info("Image saved to MongoDB!")

    def list_images(self) -> list[dict[str, Any]]:
        try:
            images = list(self.db["images"].find({}, {"_id": 0}))  # Exclude the MongoDB ObjectId from results
            logger.info("Images retrieved from MongoDB!")
            return images
        except Exception as e:
            logger.error(f"Failed to retrieve images: {e}")
            return []
        
    async def get_bytes_original_filename(self,original_filename:str):
        try:
            images = list(self.db["images"].find({"originalFileName": original_filename}, {"_id": 0}))  # Exclude the MongoDB ObjectId from results
            logger.info(f"Here are the images retrieved from MongoDB: {images}")
            filepath = images[0]["filePath"]
            image = cv2.imread(filepath)
            return await self.return_bytes_from_image(image=image)
        except Exception as e:
            logger.error(f"Failed to retrieve images: {e}")
            return []

    # Model loading
    async def load_model(self):
        try:
            YoloX().load_model()
        except Exception as e:
            logger.error(f"Failed to load model!: {e}")



    # Data prediction
    async def predict_yolox(self, imag_bytes, filename):
        logger.info("Loading image to compute prediction!")
        image = await self.load_image_from_bytes(image_bytes=imag_bytes)
        filepath = f"../data-files/{filename}"
        predicted_image, crops_info = YoloX().predict(image, filepath)
        # Generate image_summary dictionary
        image_summary = {}
        for crop in crops_info:
            class_name = crop["class"]
            if class_name in image_summary:
                image_summary[class_name] += 1
            else:
                image_summary[class_name] = 1
        image_data = {"originalFileName": filename, "crops": crops_info, "filePath": filepath, "imageSummary": image_summary}
        predicted_image_bytes = await self.return_bytes_from_image(image=predicted_image)
        self.save_image_to_db(image_data=image_data)
        logger.info("Returning image bytes!")
        return predicted_image_bytes
    
    # Prediction data management functions
    async def image_summary(self, original_filename:str):
        image = list(self.db["images"].find({"originalFileName": original_filename}, {"_id": 0}))[0]
        return Image.parse_obj(image).image_summary
    
    async def get_summary(self):
        images = self.db["images"].find({})
        summary_list = []
        for image in images:
            image_summary = {"id":image["id"],"originalFileName":image["originalFileName"],"crops": image["crops"],"imageSummary":image["imageSummary"]}
            summary_list.append(image_summary)
        return summary_list