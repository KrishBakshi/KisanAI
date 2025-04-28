import torch

def load_model():
    model = torch.hub.load('.', 'custom', 
                           path='./my_model_weights/best.pt', 
                           source='local')
    
    return model

def predict_plant(model,image):

    results = model(image, size=256)
    detected_class = results.xyxy[0][:, -1]
    pred_class = model.names[int(detected_class[0])]   

    return pred_class
