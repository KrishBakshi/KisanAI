from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io
from pydantic import BaseModel
import uvicorn
import utils

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
            import json
            parsed_history = json.loads(history)

        print(f"Received text: {text}")
        text_response = f"You said: {text}"

        image = None

        if file:
            print("File received:", file.filename)
            image_bytes = await file.read()
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        return utils.generate_response(text, image=image, history=parsed_history)

    except Exception as e:
        print("ERROR:", str(e))
        return {
            "text_response": "error",
            "image_response": str(e)
        }

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)