import os
import tempfile
import torch
import torch.nn as nn
from torchvision.models import resnet18
from PIL import Image
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

import sys
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(project_root, 'model'))

from dataset import get_transforms

def load_model():
    chkpt_path = os.path.join(project_root, "model", "checkpoints", "baseline_resnet18.pth")
    if not os.path.exists(chkpt_path):
        return None, None
        
    checkpoint = torch.load(chkpt_path, weights_only=False, map_location=torch.device('cpu'))
    classes = checkpoint['classes']
    num_classes = len(classes)
    
    model = resnet18()
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    return model, classes

@api_view(['POST'])
def predict_disease(request):
    if 'image' not in request.FILES:
        return Response({"success": False, "error": "No image uploaded."}, status=status.HTTP_400_BAD_REQUEST)
        
    image_file = request.FILES['image']
    
    if image_file.size > 10 * 1024 * 1024:
        return Response({"success": False, "error": "File size exceeds 10MB limit."}, status=status.HTTP_400_BAD_REQUEST)
        
    valid_extensions = ['.jpg', '.jpeg', '.png']
    ext = os.path.splitext(image_file.name)[1].lower()
    if ext not in valid_extensions:
        return Response({"success": False, "error": "Unsupported file format. Please upload JPG or PNG."}, status=status.HTTP_400_BAD_REQUEST)
        
    model, classes = load_model()
    if model is None:
        return Response({
            "success": False, 
            "error": "Model checkpoint is unavailable. Please run training to generate the checkpoint."
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_img:
        for chunk in image_file.chunks():
            temp_img.write(chunk)
        temp_img_path = temp_img.name
        
    try:
        img = Image.open(temp_img_path).convert('RGB')
        transform = get_transforms(is_train=False)
        img_tensor = transform(img).unsqueeze(0)
        
        with torch.no_grad():
            outputs = model(img_tensor)
            probs = torch.nn.functional.softmax(outputs, dim=1)
            confidence, preds = torch.max(probs, 1)
            
        predicted_class = classes[preds.item()]
        conf_value = round(confidence.item(), 4)
        
        return Response({
            "success": True,
            "predicted_class": predicted_class,
            "confidence": conf_value,
            "model_status": "development_prototype",
            "warning": "This model was trained on a very small development dataset and is not production-ready."
        })
    except Exception as e:
        return Response({"success": False, "error": f"Inference failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        if os.path.exists(temp_img_path):
            os.remove(temp_img_path)


@api_view(['POST'])
def recommend_crop(request):
    try:
        data = request.data
        n = data.get('nitrogen')
        p = data.get('phosphorus')
        k = data.get('potassium')
        ph = data.get('ph')
        temp = data.get('temperature')
        humidity = data.get('humidity')
        rainfall = data.get('rainfall')
        
        # Validation
        fields = {'nitrogen': n, 'phosphorus': p, 'potassium': k, 'ph': ph, 'temperature': temp, 'humidity': humidity, 'rainfall': rainfall}
        for field, val in fields.items():
            if val is None or str(val).strip() == '':
                return Response({'success': False, 'error': f'Missing field: {field}'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                val = float(val)
                if val < 0 and field != 'temperature':
                    return Response({'success': False, 'error': f'{field} cannot be negative.'}, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response({'success': False, 'error': f'{field} must be a valid number.'}, status=status.HTTP_400_BAD_REQUEST)
                
        n, p, k, ph, temp, humidity, rainfall = [float(x) for x in [n, p, k, ph, temp, humidity, rainfall]]
        
        if not (0 <= ph <= 14):
            return Response({'success': False, 'error': 'pH must be between 0 and 14.'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Prototype Rule-based Engine
        recommendations = []
        if 20 <= temp <= 30 and rainfall > 100 and humidity > 60:
            recommendations.append({'crop': 'Rice', 'suitability_score': 85, 'reason': 'High rainfall and humidity are excellent for rice cultivation.'})
        if 15 <= temp <= 25 and 50 <= rainfall <= 100:
            recommendations.append({'crop': 'Wheat', 'suitability_score': 78, 'reason': 'Moderate temperatures and rainfall fit wheat growth cycles.'})
        if 18 <= temp <= 27 and 60 <= rainfall <= 110:
            recommendations.append({'crop': 'Maize', 'suitability_score': 82, 'reason': 'Climate is reasonably compatible with maize requirements.'})
        if 25 <= temp <= 35 and rainfall < 75:
            recommendations.append({'crop': 'Cotton', 'suitability_score': 75, 'reason': 'Higher temperatures and lower rainfall are suitable for cotton.'})
        
        if not recommendations:
            recommendations.append({'crop': 'Millets', 'suitability_score': 65, 'reason': 'Hardy crop suitable for diverse and challenging conditions.'})
            
        # Sort by score
        recommendations.sort(key=lambda x: x['suitability_score'], reverse=True)
        
        return Response({
            'success': True,
            'recommendations': recommendations,
            'model_status': 'development_prototype',
            'warning': 'Recommendations are prototype rule-based estimates and should be verified by an agricultural expert.'
        })
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def recommend_irrigation(request):
    try:
        data = request.data
        crop = data.get('crop', '')
        moisture = data.get('soil_moisture')
        temp = data.get('temperature')
        humidity = data.get('humidity')
        rainfall = data.get('rainfall')
        stage = data.get('growth_stage', '')
        
        # Validation for required weather/irrigation inputs
        if temp is None or rainfall is None:
            return Response({'success': False, 'error': 'Temperature and rainfall are required.'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            temp = float(temp)
            rainfall = float(rainfall)
            if moisture is not None and str(moisture).strip() != '':
                moisture = float(moisture)
                if not (0 <= moisture <= 100):
                    return Response({'success': False, 'error': 'Soil moisture must be a percentage between 0 and 100.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                moisture = None
                
            if humidity is not None and str(humidity).strip() != '':
                humidity = float(humidity)
            else:
                humidity = None
        except ValueError:
            return Response({'success': False, 'error': 'Numeric fields must be valid numbers.'}, status=status.HTTP_400_BAD_REQUEST)

        # Prototype Logic for Irrigation
        priority = 'Monitor soil moisture'
        action = 'Monitor soil moisture and check rainfall conditions before irrigating.'
        reason = 'The available information suggests normal conditions.'
        
        if rainfall > 20:
            priority = 'No irrigation required'
            action = 'Rainfall is sufficient. Hold irrigation.'
            reason = 'Recent or expected rainfall provides adequate water.'
        elif moisture is not None:
            if moisture < 30:
                priority = 'Urgent irrigation recommended'
                action = 'Apply irrigation immediately to prevent wilting.'
                reason = f'Soil moisture is critically low ({moisture}%).'
            elif moisture < 50:
                priority = 'Irrigation recommended'
                action = 'Plan to irrigate soon.'
                reason = 'Soil moisture is dropping below optimal levels.'
        elif temp > 35:
            priority = 'Irrigation recommended'
            action = 'Irrigate to cool crop canopy.'
            reason = 'High temperatures increase evaporation and heat stress risk.'

        # Weather Insights (Rule-based)
        insights = []
        if rainfall > 50:
            insights.append({'type': 'weather', 'severity': 'high', 'message': 'Heavy rain expected. Ensure proper field drainage.'})
        if humidity is not None and humidity > 85 and temp > 25:
            insights.append({'type': 'crop_health', 'severity': 'medium', 'message': 'High temperature and humidity increase fungal disease risk. Consider field inspection.'})
        if temp > 38:
            insights.append({'type': 'weather', 'severity': 'high', 'message': 'Extreme heat stress caution. Avoid spraying chemicals mid-day.'})

        return Response({
            'success': True,
            'irrigation_priority': priority,
            'recommended_action': action,
            'reason': reason,
            'insights': insights,
            'model_status': 'development_prototype',
            'warning': 'This is a prototype advisory and is not a substitute for local agricultural guidance.'
        })
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
