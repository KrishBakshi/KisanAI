import httpx
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
from pydantic import BaseModel
import uvicorn
import utils
import json

app = FastAPI()

# Allow requests from your frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["*"] to allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    text: str

@app.post("/predict")
async def predict(
    text: str = Form(...),
    file: UploadFile = File(None),
    history: str = Form(None)
):
    try:
        parsed_history = []
        if history:
            parsed_history = json.loads(history)

        print(f"Received text: {text}")
        text_response = f"You said: {text}"

        image = None

        if file:
            print("File received:", file.filename)
            image_bytes = await file.read()
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

            # Convert the image to bytes for sending to App 2
            image_buffer = io.BytesIO()
            image.save(image_buffer, format="JPEG")
            image_buffer.seek(0)

         # Send the image to App 2
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://127.0.0.1:8001/predict/",  # App 2's URL
                    files={"image": ("image.jpg", image_buffer, "image/jpeg")}
                )

                # Parse the response from App 2
                if response.status_code == 200:
                    class_pred = response.json()
                    pred_class = class_pred.get("prediction")
                else:
                    print("Error from App 2:", response.text)
                    pred_class = None

        return utils.generate_response(pred_class, text, image=image, history=parsed_history)

    except Exception as e:
        print("ERROR:", str(e))
        return {
            "text_response": "error",
            "image_response": str(e)
        }

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)