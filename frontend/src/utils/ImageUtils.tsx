// src/imageUtils.ts
export const resizeImage = (
  file: File,
  maxWidth: number,
  maxHeight: number
): Promise<string> => {
  return new Promise((resolve, reject) => {
    const img = new Image();
    const reader = new FileReader();

    reader.onload = (e) => {
      img.src = e.target?.result as string;
    };

    img.onload = () => {
      const canvas = document.createElement("canvas");
      const ctx = canvas.getContext("2d");

      // Calculate scaling to ensure the image covers the canvas
      const widthScale = maxWidth / img.width;
      const heightScale = maxHeight / img.height;
      const scale = Math.max(widthScale, heightScale);

      const scaledWidth = img.width * scale;
      const scaledHeight = img.height * scale;

      const dx = (maxWidth - scaledWidth) / 2;
      const dy = (maxHeight - scaledHeight) / 2;

      canvas.width = maxWidth;
      canvas.height = maxHeight;

      ctx?.clearRect(0, 0, maxWidth, maxHeight);
      ctx?.drawImage(img, dx, dy, scaledWidth, scaledHeight);

      canvas.toBlob((blob) => {
        if (blob) {
          const newFile = new File([blob], file.name, { type: file.type });
          const reader = new FileReader();
          reader.onloadend = () => {
            resolve(reader.result as string);
          };
          reader.readAsDataURL(newFile);
        } else {
          reject(new Error("Canvas is empty"));
        }
      }, file.type);
    };

    reader.onerror = (error) => reject(error);
    reader.readAsDataURL(file);
  });
};
