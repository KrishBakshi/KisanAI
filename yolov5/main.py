from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
import io
import uvicorn
from my_pred import load_model, predict_plant  # Ensure `load_model` is implemented

app = FastAPI()

# Preload the model when the application starts
model = None

@app.on_event("startup")
async def load_model_on_startup():
    global model
    model = load_model()  # Replace with your model loading logic
    print("Model loaded successfully!")

@app.post("/predict/")
async def predict(image: UploadFile = File(...)):
    try:
        # Read the uploaded image
        image_bytes = await image.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Call the prediction function with the preloaded model
        prediction = predict_plant(model, image)

        # Return the prediction result
        return {"prediction": prediction}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8001)