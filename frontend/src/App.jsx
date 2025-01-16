import "./App.css";
import { useState, useRef } from "react";
import { ImageDisplay } from "./components/ImageDisplay";
const API_BASE_URL = "http://localhost:8000";

function App() {
  const [imageBase64, setImageBase64] = useState(null);
  const [predictedImage, setPredictedImagebase64] = useState(null);
  const inputImageRef = useRef(null);

  const handleImageUpload = () => {
    // Here we catch the uploaded image
    console.log("Image uploaded");
    inputImageRef.current.click();
  };

  const handleImage = (e) => {
    // Here we have the handling of the image
    const file = e.target.files[0];
    const reader = new FileReader();
    reader.onloadend = () => {
      setImageBase64(reader.result);
    };
    reader.readAsDataURL(file);
    // Once displayed by the user send the image to the API
    sendImageToAPI(file);
  };

  const sendImageToAPI = async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    
    try {
      const response = await fetch(`${API_BASE_URL}/upload-image/`, {
        method: "POST",
        body: formData,
      });
  
      if (!response.ok) {
        throw new Error('Image upload failed');
      }
  
      const imageBlob = await response.blob();
      const imageUrl = URL.createObjectURL(imageBlob);
      setPredictedImagebase64(imageUrl);
      
      console.log("Image upload successful!");
    } catch (error) {
      console.error(`Image upload failed: ${error}`);
    }
  };

  return (
    <>
      <main>
        <h1>Object Detection App</h1>
        <button onClick={handleImageUpload}>Upload image</button>
        <input
          ref={inputImageRef}
          style={{ display: "none" }}
          type="file"
          accept="image/*"
          onChange={handleImage}
        />
        <ImageDisplay text="Uploaded Image" imageBase64={imageBase64} />
        <ImageDisplay text="Predicted Image" imageBase64={predictedImage} />
      </main>
    </>
  );
}

export default App;
