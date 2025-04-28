import torch
import torchvision.transforms as transforms
from torchvision.models import efficientnet_b0
import os

from google import genai
from google.genai import types
import access_token

# API key as envirnomental varibale
os.environ["GOOGLE_API_KEY"] = access_token.GOOGLE_API_KEY
api_key = os.environ.get("GOOGLE_API_KEY")

IMAGE_SIZE = 256

# Load your trained model
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def input_transform():
    # Define the transformations for the input image
    transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor()
    ])

    return transform

def potato_pred(image):
    class_labels = ['Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy']
    
    model = efficientnet_b0(pretrained=False, num_classes=len(class_labels))  

    # Resolve the model path regardless of where app is run from
    MODEL_PATH = os.path.join(
        os.path.dirname(__file__), "artifacts", "potato_efficientnet_model.pth"
    )

    state_dict = torch.load(MODEL_PATH, map_location=DEVICE)
    model.load_state_dict(state_dict)

    # Move the model to the correct device
    model = model.to(DEVICE)
    model.eval()  # Set the model to evaluation mode

    img_tensor = input_transform()(image).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        outputs = model(img_tensor)
        _, predicted = torch.max(outputs, 1)
        class_name = class_labels[predicted.item()]

    # ✅ Properly initialize and return response
    response = class_name
    return response

def tomato_pred(image):
    class_labels = ['Tomato_Bacterial_spot', 'Tomato_Early_blight', 'Tomato_Late_blight', 
                    'Tomato_Leaf_Mold', 'Tomato_Septoria_leaf_spot', 
                    'Tomato_Spider_mites_Two_spotted_spider_mite', 
                    'Tomato__Target_Spot', 'Tomato__Tomato_YellowLeaf__Curl_Virus', 
                    'Tomato__Tomato_mosaic_virus', 'Tomato_healthy']
    
    model = efficientnet_b0(pretrained=False, num_classes=len(class_labels))  

    # Resolve the model path regardless of where app is run from
    MODEL_PATH = os.path.join(
        os.path.dirname(__file__), "artifacts", "tomato_efficientnet_model.pth"
    )

    state_dict = torch.load(MODEL_PATH, map_location=DEVICE)
    model.load_state_dict(state_dict)

    # Move the model to the correct device
    model = model.to(DEVICE)
    model.eval()  # Set the model to evaluation mode

    img_tensor = input_transform()(image).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        outputs = model(img_tensor)
        _, predicted = torch.max(outputs, 1)
        class_name = class_labels[predicted.item()]

    # ✅ Properly initialize and return response
    response = class_name
    return response

def generate_response(class_pred, user_text, image = None, history=[]):

    prompt = f"You are a helpful AI assistant for farmers."

    image_prediction = None

    prompt += f"\n\nUser said: {user_text}"

    if image and class_pred =='Potato':
        image_prediction = potato_pred(image)
        user_text += f"\n\nModel prediction: {image_prediction}"
    
    elif image and class_pred =='Tomato':
        image_prediction = tomato_pred(image)
        user_text += f"\n\nModel prediction: {image_prediction}"
    # Convert old messages
    conversation = [
        {"role": item["role"], "parts": [{"text": item["parts"]}]}
        for item in history
    ]

    # Add current message
    conversation.append({"role": "user", "parts": [{"text": user_text}]})
    
    sys_instruction=f"""
        You are an expert farming assistant trained to help Indian farmers in simple language.

        You answer questions related to:
        - Crop diseases
        - Soil and fertilizer
        - Government schemes
        - Pest control

        If an image-based prediction, use it to guide your answer.

        Always be clear, friendly, and helpful. Use real-world examples if possible.
        """
    
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(system_instruction=sys_instruction),
            contents=conversation,
        )

        print("✅ Gemini response:", response.text)
        return {
            "text_response": response.text.strip() if hasattr(response, "text") else "No response",
            "image_response": image_prediction or None
        }

    except Exception as e:
        print("❌ Gemini error:", str(e))
        return {
            "text_response": "error",
            "image_response": str(e)
        }