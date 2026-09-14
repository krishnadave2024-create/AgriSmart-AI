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

@api_view(['POST'])
def sustainability_score(request):
    try:
        data = request.data
        score = 0
        positive = []
        improvements = []
        
        # Validation and scoring
        # Boolean fields
        def get_bool(key, default=False):
            val = data.get(key, default)
            if isinstance(val, str):
                return val.lower() == 'true'
            return bool(val)
            
        crop_rotation = get_bool('crop_rotation')
        organic_fertilizer = get_bool('organic_fertilizer')
        rainwater_harvesting = get_bool('rainwater_harvesting')
        soil_conservation = get_bool('soil_conservation')
        crop_residue = get_bool('crop_residue_management')
        
        if crop_rotation:
            score += 20
            positive.append('Crop rotation practice is being followed.')
        else:
            improvements.append('Implement crop rotation to improve soil health.')
            
        if organic_fertilizer:
            score += 20
            positive.append('Organic fertilizer usage is reported.')
        else:
            improvements.append('Consider integrating organic fertilizers to reduce chemical reliance.')
            
        if rainwater_harvesting:
            score += 20
            positive.append('Rainwater harvesting is being utilized.')
        else:
            improvements.append('Implement rainwater harvesting to improve water-use efficiency.')
            
        if soil_conservation:
            score += 20
            positive.append('Soil conservation practices are active.')
        else:
            improvements.append('Adopt soil conservation techniques (e.g., minimum tillage, cover crops).')
            
        if crop_residue:
            score += 20
            positive.append('Crop residue is being managed sustainably.')
        else:
            improvements.append('Avoid burning crop residue; compost or incorporate it into the soil.')
            
        # Chemical inputs (Penalty logic)
        chem_fertilizer = data.get('chemical_fertilizer_level', 'medium')
        pesticide = data.get('pesticide_level', 'medium')
        
        if chem_fertilizer == 'high':
            score -= 10
            improvements.append('High chemical fertilizer usage detected. Aim to reduce and optimize application.')
        elif chem_fertilizer == 'low':
            positive.append('Chemical fertilizer usage is kept low.')
            
        if pesticide == 'high':
            score -= 10
            improvements.append('High pesticide usage detected. Implement Integrated Pest Management (IPM).')
        elif pesticide == 'low':
            positive.append('Pesticide usage is minimized.')
            
        # Ensure score bounds
        score = max(0, min(100, score))
        
        if score < 40:
            category = 'Needs Improvement'
        elif score < 60:
            category = 'Developing'
        elif score < 80:
            category = 'Good'
        else:
            category = 'Excellent'
            
        return Response({
            'success': True,
            'score': score,
            'category': category,
            'positive_factors': positive,
            'improvement_suggestions': improvements,
            'model_status': 'development_prototype',
            'warning': 'This is an explainable prototype score and is not an officially certified sustainability assessment.'
        })
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def farmer_assistant(request):
    try:
        data = request.data
        message = data.get('message', '').lower()
        language = data.get('language', 'en')
        
        if language not in ['en', 'hi', 'gu']:
            language = 'en'
            
        # Basic Intent Detection
        intent = 'unknown'
        if any(word in message for word in ['disease', 'sick', 'spot', 'rot', 'blight', 'રોગ', 'बीमारी']):
            intent = 'disease'
        elif any(word in message for word in ['water', 'irrigate', 'rain', 'સિંચાઈ', 'પાણી', 'सिंचाई', 'पानी']):
            intent = 'irrigation'
        elif any(word in message for word in ['crop', 'grow', 'plant', 'પાક', 'વાવવું', 'फसल', 'उगाना']):
            intent = 'crop'
        elif any(word in message for word in ['sustainable', 'soil', 'organic', 'જમીન', 'જૈવિક', 'मिट्टी', 'जैविक']):
            intent = 'sustainability'
            
        responses = {
            'disease': {
                'en': 'For crop diseases, please upload a clear image of the affected leaf in the Disease Detection tab.',
                'hi': 'फसल की बीमारियों के लिए, कृपया रोग पहचान टैब में प्रभावित पत्ते की एक स्पष्ट तस्वीर अपलोड करें।',
                'gu': 'પાકના રોગો માટે, કૃપા કરીને રોગ ઓળખ ટેબમાં અસરગ્રસ્ત પાંદડાનો સ્પષ્ટ ફોટો અપલોડ કરો.'
            },
            'irrigation': {
                'en': 'Irrigation decisions should be based on soil moisture, rainfall, and the crop growth stage. Check the Irrigation tab for detailed insights.',
                'hi': 'सिंचाई का निर्णय मिट्टी की नमी, बारिश और फसल के विकास के चरण पर आधारित होना चाहिए। विस्तृत जानकारी के लिए सिंचाई टैब देखें।',
                'gu': 'સિંચાઈનો નિર્ણય જમીનની ભેજ, વરસાદ અને પાકના વિકાસના તબક્કા પર આધારિત હોવો જોઈએ. વિગતવાર માહિતી માટે સિંચાઈ ટેબ જુઓ.'
            },
            'crop': {
                'en': 'Crop recommendations depend on soil nutrients (NPK), pH, and climate. Use the Crop Recommendation tab to find suitable crops.',
                'hi': 'फसल की सिफारिशें मिट्टी के पोषक तत्वों (NPK), pH और जलवायु पर निर्भर करती हैं। उपयुक्त फसलों को खोजने के लिए फसल सिफारिश टैब का उपयोग करें।',
                'gu': 'પાકની ભલામણો જમીનના પોષક તત્વો (NPK), pH અને આબોહવા પર આધાર રાખે છે. યોગ્ય પાકો શોધવા માટે પાક ભલામણ ટેબનો ઉપયોગ કરો.'
            },
            'sustainability': {
                'en': 'Sustainable farming includes crop rotation, organic fertilizers, and water conservation. Check your Sustainability Score to learn more.',
                'hi': 'सतत खेती में फसल चक्र, जैविक उर्वरक और जल संरक्षण शामिल हैं। अधिक जानने के लिए अपना स्थिरता स्कोर देखें।',
                'gu': 'ટકાઉ ખેતીમાં પાક પરિભ્રમણ, જૈવિક ખાતરો અને જળ સંરક્ષણનો સમાવેશ થાય છે. વધુ જાણવા માટે તમારો ટકાઉપણું સ્કોર જુઓ.'
            },
            'unknown': {
                'en': 'I am a prototype assistant. Please ask about crop diseases, irrigation, crop recommendations, or sustainability.',
                'hi': 'मैं एक प्रोटोटाइप सहायक हूँ। कृपया फसल रोगों, सिंचाई, फसल सिफारिशों या स्थिरता के बारे में पूछें।',
                'gu': 'હું એક પ્રોટોટાઇપ સહાયક છું. કૃપા કરીને પાકના રોગો, સિંચાઈ, પાકની ભલામણો અથવા ટકાઉપણું વિશે પૂછો.'
            }
        }
        
        reply = responses[intent][language]
        
        return Response({
            'success': True,
            'language': language,
            'intent': intent,
            'response': reply,
            'model_status': 'development_prototype',
            'warning': 'This is general prototype guidance. Consult a local agricultural expert for critical decisions.'
        })
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def fieldguard_assess(request):
    try:
        data = request.data
        score = 100
        factors = []
        
        # Validations for required / numerical fields
        def parse_float(val, name, min_val=None, max_val=None):
            if val is None or str(val).strip() == '':
                return None
            try:
                f_val = float(val)
                if min_val is not None and f_val < min_val:
                    raise ValueError(f"{name} must be >= {min_val}")
                if max_val is not None and f_val > max_val:
                    raise ValueError(f"{name} must be <= {max_val}")
                return f_val
            except ValueError as e:
                raise ValueError(f"Invalid value for {name}: {str(e)}")

        try:
            soil_moisture = parse_float(data.get('soil_moisture'), 'soil_moisture', 0, 100)
            rainfall = parse_float(data.get('rainfall'), 'rainfall', 0)
            temperature = parse_float(data.get('temperature'), 'temperature', -50, 100)
            humidity = parse_float(data.get('humidity'), 'humidity', 0, 100)
            disease_confidence = parse_float(data.get('disease_confidence'), 'disease_confidence', 0, 1)
        except ValueError as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        disease_label = data.get('disease_label', '')
        
        # Scoring Logic
        if temperature is not None and temperature > 35:
            score -= 15
            factors.append({'factor': 'High Temperature', 'impact': 'negative', 'description': 'Temperatures above 35°C can cause severe heat stress and reduce yield.'})
            
        if soil_moisture is not None:
            if soil_moisture < 30:
                score -= 20
                factors.append({'factor': 'Low Soil Moisture', 'impact': 'negative', 'description': 'Soil moisture below 30% indicates critical water stress.'})
            elif soil_moisture > 80:
                score -= 10
                factors.append({'factor': 'Excessive Soil Moisture', 'impact': 'negative', 'description': 'High soil moisture can lead to root rot and fungal diseases.'})
            else:
                factors.append({'factor': 'Optimal Soil Moisture', 'impact': 'positive', 'description': 'Current moisture levels are well within the optimal range.'})
                
        if humidity is not None and humidity > 85:
            score -= 10
            factors.append({'factor': 'High Humidity', 'impact': 'negative', 'description': 'Elevated humidity creates favorable conditions for fungal pathogens.'})
            
        if disease_confidence is not None and disease_confidence > 0.5 and disease_label.lower() != 'healthy':
            score -= 30
            factors.append({'factor': f'Disease Detected ({disease_label})', 'impact': 'negative', 'description': 'A high confidence disease prediction significantly impacts crop health.'})
            
        if rainfall is not None and rainfall > 100:
            score -= 10
            factors.append({'factor': 'Heavy Rainfall', 'impact': 'negative', 'description': 'Excessive rainfall risks waterlogging and nutrient leaching.'})
            
        score = max(0, min(100, score))
        
        if score > 80:
            category = 'Low Risk'
            actions = ['Continue standard monitoring.', 'Maintain current irrigation schedules.']
        elif score > 60:
            category = 'Moderate Risk'
            actions = ['Increase field scouting frequency.', 'Check for early signs of stress or pests.']
        elif score > 40:
            category = 'High Risk'
            actions = ['Consider preventive fungicide/pesticide application if conditions persist.', 'Adjust irrigation immediately.']
        else:
            category = 'Critical Risk'
            actions = ['Urgent intervention required. Consult an agronomist.', 'Implement emergency drainage or irrigation based on specific stressor.']
            
        return Response({
            'success': True,
            'score': score,
            'category': category,
            'factors': factors,
            'preventive_actions': actions,
            'model_status': 'explainable_prototype',
            'warning': 'FieldGuard is an explainable prototype based on manually entered data. It is not a substitute for local agricultural experts.'
        })
        
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- Authentication and Profiles ---

from django.contrib.auth.models import User
from .models import UserProfile, FarmProfile
from .serializers import RegisterSerializer, UserProfileSerializer, FarmProfileSerializer
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True, 'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        return Response({'success': False, 'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response({'success': True, 'profile': serializer.data})
        
    elif request.method == 'PUT':
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'profile': serializer.data})
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def farm_profile(request):
    try:
        farm = request.user.farm
    except FarmProfile.DoesNotExist:
        return Response({'success': False, 'error': 'Farm profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
    if request.method == 'GET':
        serializer = FarmProfileSerializer(farm)
        return Response({'success': True, 'farm': serializer.data})
        
    elif request.method == 'PUT':
        serializer = FarmProfileSerializer(farm, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'farm': serializer.data})
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'success': False, 'error': 'Refresh token is required to logout'}, status=status.HTTP_400_BAD_REQUEST)
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'success': True, 'message': 'Logged out successfully'}, status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        return Response({'success': False, 'error': 'Invalid token or token already blacklisted'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    user = request.user
    profile = getattr(user, 'profile', None)
    farm = getattr(user, 'farm', None)
    
    return Response({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': profile.full_name if profile else '',
            'preferred_language': profile.preferred_language if profile else 'en',
            'has_farm_profile': farm is not None and bool(farm.farm_name)
        }
    })
