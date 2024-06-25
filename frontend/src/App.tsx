import React, { useState } from "react";
import "./App.css";

const ImageDisplay: React.FC = () => {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);

  const handleImageChange = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      const reader = new FileReader();

      reader.onloadend = () => {
        setSelectedImage(reader.result as string);
      };

      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="App">
      <div className="header">Image Upload and Display App</div>
      <div className="container">
        <div className="right-panel">
          <input type="file" onChange={handleImageChange} />
        </div>
        <div className="left-panel">
          {selectedImage ? (
            <img src={selectedImage} alt="uploaded" />
          ) : (
            <p>No image uploaded</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default ImageDisplay;
