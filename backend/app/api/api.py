import logging
from fastapi import (
    FastAPI,
    UploadFile,
    File
)
from fastapi.responses import StreamingResponse
from core.core_functions import CoreFunctions
from db.db_client import db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

data_model = CoreFunctions(db=db)

app = FastAPI()

@app.get("/health")
async def health():
    logging.info("AI worker up and running!")
    return f"AI worker up and running"

@app.post("/upload-image/")
async def handle_image(file: UploadFile = File(...)):
    logging.info(f"Image upload initiated: {file.filename}")
    contents = await file.read()
    predicted_image_bytes = await data_model.predict_yolox(imag_bytes=contents, filename = file.filename)
    logging.info(f"Image predicted!")
    return StreamingResponse(predicted_image_bytes, media_type="image/png")

@app.get("/list-images")
async def list_images():
    logging.info("Returning all images!")
    images = data_model.list_images()
    return images

@app.get("/get-image/{id}")
async def get_image(id: str):
    logging.info(f"Getting content for image with id: {id}")
    image_bytes = await data_model.get_bytes_from_image_id(id)
    return StreamingResponse(image_bytes, media_type="image/png")

@app.get("/get-histogram-data/{id}")
async def get_histogram_data(id: str):
    logging.info(f"Getting histogram-data for image with id: {id}")
    image_summary = await data_model.image_summary(id)
    return image_summary

@app.get("/get-summary")
async def get_summary():
    logging.info("Getting summary!")
    summary = await data_model.get_summary()
    logging.info("Summary properly fetched")
    return summary

@app.on_event("startup")
async def startup_event():
    logging.info("Loading model!")
    await data_model.load_model()
    logging.info("Model loaded succesfully!")