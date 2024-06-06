# YOLOX Tester

## Project Overview

YOLOX Tester is a Dockerized solution for testing YOLOX models, specifically designed to facilitate the deployment and evaluation of these models. 
The setup includes both backend and frontend components, enabling seamless interaction and management.
This project used the https://github.com/Megvii-BaseDetection/YOLOX to obtain the pretrained yolo model which can run in the local system.


## Installation

To get started with YOLOX Tester, you only need to have git and docker in your system and
follow these steps:

1. **Clone the repository:**
    ```bash
    git clone https://github.com/fjmmontiel/yoloX-tester.git
    cd yoloX-tester
    ```

On the docker-compose.yml depending on your arch you should need to change the image for mongoDB, 
if your system is amd64 then you need to use the second line in the mongo section, if your system is
arch64 you can run the command without touching anything!

2. **Build and run the Docker containers:**
    ```bash
    docker-compose up --build
    ```

This command will build the Docker images and start the backend and frontend services.

## Usage

Once the Docker containers are up and running, you can access the application through your web browser at `http://localhost:8501`. The frontend interface allows you to upload images and perform inference using the YOLOX model, also view all predicted images with a summary of classes per image, and finally a tab 
where you can visualize distribution of classes for the overall uploaded dataset, number of objects
per image, average confidence level per class, and a summary of the confidence for all detections.

### Testing the Model

1. Navigate to the web interface.
2. Upload an image file.
3. Click on the "Upload Image" button to see the results.
4. Go to Sample Examinator window and refresh images to see the latest predictions
5. Go to Data Summary to see the dataset summary

## Architecture

The architecture of YOLOX Tester solution is based on a backend built with FastAPI, a frontend built with Streamlit and a noSQL database such as MongoDB to save data related to the predicted images, so the 
backend will extract the necessary information from MongoDB to fulfill user needs.
It is used the local volume of the backend to save the images.


### Components

- **Backend:** Manages model inference, processing and image information retrieval from MongoDB. It is built with Python using FastAPI and includes the YOLOX model in .onnx format, so as an AI framework ONNX is used due to its speed on CPU and integration within the YOLOX ecosystem.

- **Frontend:** Provides a user-friendly interface for uploading images, displaying results and see dataset summary based on the detections. Built with Streamlit and a custom HTML/CSS design page.

## Contributing

We welcome contributions to improve YOLOX Tester! To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a Pull Request.

## License

This project is licensed under the Apache-2.0 License. See the [LICENSE](LICENSE) file for details.
