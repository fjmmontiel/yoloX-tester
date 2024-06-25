// src/ImageDisplay.tsx
import React from "react";

interface ImageDisplayProps {
  imageUrl: string;
}

const ImageDisplay: React.FC<ImageDisplayProps> = ({ imageUrl }) => {
  return (
    <div>
      {imageUrl ? (
        <img
          src={imageUrl}
          alt="Uploaded"
          style={{ maxWidth: "1024", height: "1024" }}
        />
      ) : (
        <p>No image uploaded</p>
      )}
    </div>
  );
};

export default ImageDisplay;
