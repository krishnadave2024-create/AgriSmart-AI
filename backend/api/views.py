import os
import tempfile
import requests
import torch
import torch.nn as nn
from torchvision.models import resnet18
from PIL import Image
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache

import sys
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(project_root, 'model'))

from .models import (
    UserProfile, FarmProfile, DiseaseScan, CropRecommendationRecord, 
    IrrigationAssessment, FieldGuardAssessment, SustainabilityAssessment, ActivityRecord
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import permission_classes

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
        
        KNOWLEDGE_DB = {
            'diseased': {
                'disease_name': 'Unspecified Plant Disease',
                'crop_name': 'Generic Crop / Leaf',
                'symptoms': ['Abnormal spots or lesions on leaves', 'Discoloration (yellowing, browning)', 'Wilting or stunted growth', 'Fungal growth or powdery mildew visible'],
                'causes': ['Fungal, bacterial, or viral pathogens', 'Environmental stress (drought, excessive moisture)', 'Pest infestations'],
                'treatment': ['Isolate affected plants if possible', 'Apply broad-spectrum fungicide or appropriate targeted treatment', 'Prune heavily infected leaves or branches'],
                'prevention': ['Ensure proper spacing for air circulation', 'Avoid overhead watering to keep foliage dry', 'Implement crop rotation and use disease-resistant varieties'],
                'severity': 'Moderate to High',
                'expert_consult': 'Consult an agronomist if symptoms spread rapidly to other plants or do not respond to basic treatments.'
            },
            'healthy': {
                'disease_name': 'Healthy Plant',
                'crop_name': 'Generic Crop / Leaf',
                'symptoms': ['Vibrant green color', 'Firm and upright structure', 'No visible spots, lesions, or pests'],
                'causes': ['Optimal growing conditions', 'Good soil health', 'Proper irrigation and nutrient management'],
                'treatment': ['None required. Continue current care regimen.'],
                'prevention': ['Maintain regular monitoring', 'Ensure balanced fertilization', 'Keep field weed-free'],
                'severity': 'None',
                'expert_consult': 'No immediate consultation needed. Keep up the good work!'
            }
        }
        
        knowledge = KNOWLEDGE_DB.get(predicted_class, KNOWLEDGE_DB['diseased'])
        
        scan_record = None
        if request.user.is_authenticated:
            scan_record = DiseaseScan.objects.create(
                user=request.user,
                image=image_file,
                predicted_class=predicted_class,
                confidence=conf_value,
                model_version="baseline_resnet18",
                is_development=True
            )
            ActivityRecord.objects.create(
                user=request.user,
                activity_type='disease_scan',
                title='Disease Scan Completed',
                description=f'Scanned crop. Result: {predicted_class}'
            )
        
        response_data = {
            "success": True,
            "predicted_class": predicted_class,
            "confidence": conf_value,
            "knowledge": knowledge,
            "model_status": "development_prototype",
            "is_development": True,
            "model_version": "baseline_resnet18",
            "warning": "This model was trained on a very small development dataset and is not production-ready. Official SIH dataset not yet available."
        }
        
        if scan_record and scan_record.image:
            response_data['image_url'] = request.build_absolute_uri(scan_record.image.url)
            
        return Response(response_data)
    except Exception as e:
        return Response({"success": False, "error": f"Inference failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        if os.path.exists(temp_img_path):
            os.remove(temp_img_path)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def disease_history(request):
    scans = DiseaseScan.objects.filter(user=request.user).order_by('-created_at')
    history = []
    for scan in scans:
        history.append({
            'id': scan.id,
            'predicted_class': scan.predicted_class,
            'confidence': scan.confidence,
            'image_url': request.build_absolute_uri(scan.image.url) if scan.image else None,
            'model_version': scan.model_version,
            'is_development': scan.is_development,
            'created_at': scan.created_at
        })
    return Response({'success': True, 'history': history})

CROP_KNOWLEDGE_BASE = {
    'Rice': {
        'name': 'Rice',
        'scientific_name': 'Oryza sativa',
        'soil_type': 'Clayey, Loamy',
        'ph_range': (5.5, 7.0),
        'temp_range': (20, 35),
        'rainfall_range': (100, 250),
        'water_req': 'High',
        'season': 'Kharif',
        'duration': '120-150 days',
        'nutrient_req': 'High Nitrogen, Medium Phosphorus, Low Potassium',
        'deficiency_risks': 'Nitrogen deficiency causes yellowing of older leaves.',
        'excess_risks': 'Excess Nitrogen makes plants susceptible to lodging and pests.',
        'advantages': 'High yield in waterlogged areas.',
        'limitations': 'Extremely water-intensive.',
        'sustainability': 'High methane emissions. Consider Alternate Wetting and Drying (AWD).',
        'image_url': 'https://images.unsplash.com/photo-1595015243869-70335e390c58?auto=format&fit=crop&w=400&q=80',
        'reference': 'FAO Crop Water Information'
    },
    'Wheat': {
        'name': 'Wheat',
        'scientific_name': 'Triticum aestivum',
        'soil_type': 'Loamy, Clay Loam',
        'ph_range': (6.0, 7.5),
        'temp_range': (15, 25),
        'rainfall_range': (50, 100),
        'water_req': 'Moderate',
        'season': 'Rabi',
        'duration': '110-130 days',
        'nutrient_req': 'High Nitrogen, Moderate P & K',
        'deficiency_risks': 'Potassium deficiency leads to poor grain filling.',
        'excess_risks': 'N/A',
        'advantages': 'Staple food crop, highly mechanized.',
        'limitations': 'Sensitive to terminal heat stress.',
        'sustainability': 'Requires balanced NPK for long-term soil health.',
        'image_url': 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?auto=format&fit=crop&w=400&q=80',
        'reference': 'FAO Crop Water Information'
    },
    'Maize': {
        'name': 'Maize',
        'scientific_name': 'Zea mays',
        'soil_type': 'Well-drained Loam',
        'ph_range': (5.8, 7.0),
        'temp_range': (18, 27),
        'rainfall_range': (60, 110),
        'water_req': 'Moderate',
        'season': 'Kharif / Zaid',
        'duration': '90-120 days',
        'nutrient_req': 'High N and K',
        'deficiency_risks': 'Phosphorus deficiency causes purple leaves.',
        'excess_risks': 'Sensitive to waterlogging.',
        'advantages': 'High yield potential, versatile uses.',
        'limitations': 'Highly sensitive to drought during tasseling.',
        'sustainability': 'Heavy feeder; requires crop rotation.',
        'image_url': 'https://images.unsplash.com/photo-1599818815197-29367d3448a3?auto=format&fit=crop&w=400&q=80',
        'reference': 'FAO Crop Water Information'
    },
    'Cotton': {
        'name': 'Cotton',
        'scientific_name': 'Gossypium',
        'soil_type': 'Black soil, Clayey',
        'ph_range': (5.8, 8.0),
        'temp_range': (25, 35),
        'rainfall_range': (40, 75),
        'water_req': 'Moderate to Low',
        'season': 'Kharif',
        'duration': '150-180 days',
        'nutrient_req': 'High N and K',
        'deficiency_risks': 'Magnesium deficiency causes red leaves.',
        'excess_risks': 'Excess Nitrogen promotes vegetative growth over bolls.',
        'advantages': 'High cash value.',
        'limitations': 'Highly susceptible to pests (bollworm).',
        'sustainability': 'Pesticide intensive. IPM strongly recommended.',
        'image_url': 'https://images.unsplash.com/photo-1596766465492-b43064fc600c?auto=format&fit=crop&w=400&q=80',
        'reference': 'FAO Crop Water Information'
    },
    'Millets': {
        'name': 'Millets',
        'scientific_name': 'Pennisetum glaucum / Sorghum bicolor',
        'soil_type': 'Sandy, Loamy (Tolerant to poor soils)',
        'ph_range': (5.5, 7.5),
        'temp_range': (25, 35),
        'rainfall_range': (30, 60),
        'water_req': 'Low',
        'season': 'Kharif',
        'duration': '70-100 days',
        'nutrient_req': 'Low',
        'deficiency_risks': 'Very hardy, minimal deficiency risks.',
        'excess_risks': 'Cannot tolerate waterlogging.',
        'advantages': 'Highly drought resistant and climate-resilient.',
        'limitations': 'Lower yield compared to major cereals.',
        'sustainability': 'Excellent for water conservation and soil restoration.',
        'image_url': 'https://images.unsplash.com/photo-1621245059632-4e4444569cb1?auto=format&fit=crop&w=400&q=80',
        'reference': 'FAO Crop Water Information'
    }
}

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
        weather_source = data.get('weather_source', 'manual')
        
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
            
        recommendations = []
        
        for crop, details in CROP_KNOWLEDGE_BASE.items():
            score = 100
            matching = []
            non_matching = []
            
            # Temp logic
            t_min, t_max = details['temp_range']
            if t_min <= temp <= t_max:
                matching.append(f'Temperature ({temp}°C) is optimal ({t_min}-{t_max}°C).')
            else:
                score -= 20
                non_matching.append(f'Temperature ({temp}°C) is outside optimal range ({t_min}-{t_max}°C).')
                
            # Rainfall logic
            r_min, r_max = details['rainfall_range']
            if r_min <= rainfall <= r_max:
                matching.append(f'Rainfall ({rainfall}mm) is optimal ({r_min}-{r_max}mm).')
            else:
                score -= 15
                non_matching.append(f'Rainfall ({rainfall}mm) is outside optimal range ({r_min}-{r_max}mm).')
                
            # pH logic
            ph_min, ph_max = details['ph_range']
            if ph_min <= ph <= ph_max:
                matching.append(f'pH ({ph}) is optimal ({ph_min}-{ph_max}).')
            else:
                score -= 15
                non_matching.append(f'pH ({ph}) is outside optimal range ({ph_min}-{ph_max}).')
                
            if score > 0:
                recommendations.append({
                    'crop': crop,
                    'suitability_score': max(0, score),
                    'matching_conditions': matching,
                    'non_matching_conditions': non_matching,
                    'details': details
                })
        
        recommendations.sort(key=lambda x: x['suitability_score'], reverse=True)
        top_rec = recommendations[0]['crop'] if recommendations else None
        explanation = "Based on your inputs, this crop's growing conditions match well." if top_rec else "No suitable crop found."
        
        # Soil deficiency guidance (General simple rules for demo purposes)
        deficiencies = []
        if n < 20: deficiencies.append("Potential nitrogen deficiency detected. Consider adding nitrogen-rich fertilizers.")
        if p < 10: deficiencies.append("Potential phosphorus deficiency detected. Consider bone meal or superphosphate.")
        if k < 10: deficiencies.append("Potential potassium deficiency detected. Consider potash application.")
        if ph < 5.5: deficiencies.append("Soil is highly acidic. Agricultural lime may be required.")
        elif ph > 8.0: deficiencies.append("Soil is highly alkaline. Elemental sulfur or gypsum may be needed.")

        if request.user.is_authenticated:
            # Try to associate with FarmProfile
            farm_profile = None
            if hasattr(request.user, 'farm'):
                farm_profile = request.user.farm

            rec = CropRecommendationRecord.objects.create(
                user=request.user,
                farm_profile=farm_profile,
                nitrogen=n, phosphorus=p, potassium=k, ph=ph,
                temperature=temp, humidity=humidity, rainfall=rainfall,
                weather_source=weather_source,
                recommendation_method='rule-based',
                top_recommendation=top_rec,
                explanation=explanation
            )
            ActivityRecord.objects.create(
                user=request.user,
                activity_type='crop_recommendation',
                title='Crop Recommendation Generated',
                description=f'Top recommendation: {top_rec} (Score: {recommendations[0]["suitability_score"] if recommendations else 0})'
            )
        
        return Response({
            'success': True,
            'recommendations': recommendations,
            'deficiencies': deficiencies,
            'model_status': 'development_prototype',
            'warning': 'Recommendations are rule-based estimates based on generalized crop parameters. Please verify with a local agronomist.'
        })
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def crop_history(request):
    recs = CropRecommendationRecord.objects.filter(user=request.user).order_by('-created_at')
    history = []
    for r in recs:
        history.append({
            'id': r.id,
            'top_recommendation': r.top_recommendation,
            'nitrogen': r.nitrogen,
            'phosphorus': r.phosphorus,
            'potassium': r.potassium,
            'ph': r.ph,
            'temperature': r.temperature,
            'humidity': r.humidity,
            'rainfall': r.rainfall,
            'weather_source': r.weather_source,
            'recommendation_method': r.recommendation_method,
            'created_at': r.created_at
        })
    return Response({'success': True, 'history': history})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_weather(request):
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    city = request.GET.get('city')
    
    api_key = os.environ.get('OPENWEATHER_API_KEY')
    if not api_key:
        return Response({'success': False, 'error': 'Weather service is not configured on the backend.'}, status=503)
        
    try:
        cache_key = f"weather_current_{lat}_{lon}_{city}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        if lat and lon:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        elif city:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        else:
            return Response({'success': False, 'error': 'Location could not be found.'}, status=status.HTTP_400_BAD_REQUEST)
            
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            resp_data = {
                'success': True,
                'location': data.get('name', 'Unknown'),
                'temperature': data['main']['temp'],
                'temp_min': data['main'].get('temp_min'),
                'temp_max': data['main'].get('temp_max'),
                'pressure': data['main'].get('pressure'),
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'rainfall': data.get('rain', {}).get('1h', 0),
                'wind_speed': data['wind']['speed'],
                'wind_deg': data['wind'].get('deg'),
                'clouds': data.get('clouds', {}).get('all'),
                'condition': data['weather'][0]['main'],
                'description': data['weather'][0]['description'],
                'sunrise': data.get('sys', {}).get('sunrise'),
                'sunset': data.get('sys', {}).get('sunset'),
                'timestamp': data['dt'],
                'source': 'OpenWeather API',
                'units': 'metric',
                'cached': False
            }
            cache.set(cache_key, {**resp_data, 'cached': True}, timeout=900)
            return Response(resp_data)
        elif res.status_code == 401:
            return Response({'success': False, 'error': 'The weather service rejected the configured API key.'}, status=401)
        elif res.status_code == 404:
            return Response({'success': False, 'error': 'Location could not be found.'}, status=404)
        elif res.status_code == 429:
            return Response({'success': False, 'error': 'Weather service rate limit exceeded.'}, status=429)
        else:
            return Response({'success': False, 'error': f"Weather service error (code {res.status_code})."}, status=res.status_code)
    except requests.exceptions.Timeout:
        return Response({'success': False, 'error': 'Weather service timeout.'}, status=504)
    except requests.exceptions.RequestException:
        return Response({'success': False, 'error': 'Weather data is temporarily unavailable.'}, status=502)
    except Exception as e:
        return Response({'success': False, 'error': 'An unexpected error occurred with the weather service.'}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def weather_forecast(request):
    lat = request.GET.get('lat')
    lon = request.GET.get('lon')
    city = request.GET.get('city')
    
    api_key = os.environ.get('OPENWEATHER_API_KEY')
    if not api_key:
        return Response({'success': False, 'error': 'Weather service is not configured on the backend.'}, status=503)
        
    try:
        cache_key = f"weather_forecast_{lat}_{lon}_{city}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        if lat and lon:
            url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        elif city:
            url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
        else:
            return Response({'success': False, 'error': 'Location could not be found.'}, status=status.HTTP_400_BAD_REQUEST)
            
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            forecast_list = []
            for item in data.get('list', []):
                forecast_list.append({
                    'timestamp': item['dt'],
                    'temperature': item['main']['temp'],
                    'humidity': item['main']['humidity'],
                    'condition': item['weather'][0]['main'],
                    'rain_prob': item.get('pop', 0),
                    'rainfall': item.get('rain', {}).get('3h', 0),
                    'wind_speed': item['wind']['speed']
                })
            resp_data = {
                'success': True,
                'location': data.get('city', {}).get('name', 'Unknown'),
                'forecast': forecast_list,
                'source': 'OpenWeather API',
                'cached': False
            }
            cache.set(cache_key, {**resp_data, 'cached': True}, timeout=900)
            return Response(resp_data)
        elif res.status_code == 401:
            return Response({'success': False, 'error': 'The weather service rejected the configured API key.'}, status=401)
        elif res.status_code == 404:
            return Response({'success': False, 'error': 'Location could not be found.'}, status=404)
        elif res.status_code == 429:
            return Response({'success': False, 'error': 'Weather service rate limit exceeded.'}, status=429)
        else:
            return Response({'success': False, 'error': f"Weather service error (code {res.status_code})."}, status=res.status_code)
    except requests.exceptions.Timeout:
        return Response({'success': False, 'error': 'Weather service timeout.'}, status=504)
    except requests.exceptions.RequestException:
        return Response({'success': False, 'error': 'Weather data is temporarily unavailable.'}, status=502)
    except Exception as e:
        return Response({'success': False, 'error': 'An unexpected error occurred with the weather service.'}, status=500)

CROP_IRRIGATION_KB = {
    'wheat': {
        'water_req': 'Medium',
        'sensitive_stages': ['crown root initiation', 'flowering', 'milk stage'],
        'method': 'Sprinkler or surface irrigation'
    },
    'rice': {
        'water_req': 'High',
        'sensitive_stages': ['panicle initiation', 'flowering'],
        'method': 'Flood irrigation'
    },
    'cotton': {
        'water_req': 'Medium',
        'sensitive_stages': ['flowering', 'boll formation'],
        'method': 'Drip or furrow irrigation'
    },
    'maize': {
        'water_req': 'Medium-High',
        'sensitive_stages': ['tasseling', 'silking'],
        'method': 'Drip or furrow irrigation'
    },
    'millets': {
        'water_req': 'Low',
        'sensitive_stages': ['flowering', 'grain filling'],
        'method': 'Surface irrigation'
    }
}

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recommend_irrigation(request):
    try:
        data = request.data
        crop = data.get('crop', '').strip().lower()
        moisture = data.get('soil_moisture')
        temp = data.get('temperature')
        humidity = data.get('humidity')
        rainfall = data.get('rainfall')
        stage = data.get('growth_stage', '').strip().lower()
        area = data.get('field_area')
        method = data.get('irrigation_method', '')
        weather_source = data.get('weather_source', 'manual')
        
        # Validation for required inputs
        if temp is None or rainfall is None:
            return Response({'success': False, 'error': 'Temperature and rainfall are required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not crop:
            return Response({'success': False, 'error': 'Crop name is required.'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            temp = float(temp)
            rainfall = float(rainfall)
            
            if area is not None and str(area).strip() != '':
                area = float(area)
            else:
                area = None
                
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

        crop_info = CROP_IRRIGATION_KB.get(crop, None)
        
        # Rule-based Logic
        priority = 'Monitor soil moisture'
        action = 'Monitor conditions before irrigating.'
        reason = 'Normal weather and crop conditions detected.'
        
        if rainfall > 20:
            priority = 'No irrigation required'
            action = 'Hold irrigation.'
            reason = f'Recent or expected rainfall ({rainfall}mm) is sufficient.'
        elif moisture is not None:
            if moisture < 30:
                priority = 'Urgent irrigation recommended'
                action = 'Apply irrigation immediately.'
                reason = f'Soil moisture is critically low ({moisture}%).'
            elif moisture < 50:
                priority = 'Irrigation recommended'
                action = 'Plan to irrigate soon.'
                reason = f'Soil moisture is dropping ({moisture}%).'
        else:
            if temp > 35:
                priority = 'Irrigation recommended'
                action = 'Irrigate to cool crop canopy.'
                reason = f'High temperatures ({temp}°C) increase evaporation and heat stress risk.'
                
        if crop_info and stage in crop_info['sensitive_stages'] and priority != 'No irrigation required':
            priority = 'Urgent irrigation recommended'
            reason += f' Crop is in a highly water-sensitive stage ({stage}).'
            
        # Insights
        insights = []
        if rainfall > 50:
            insights.append({'type': 'weather', 'severity': 'high', 'message': 'Heavy rain expected. Ensure proper field drainage.'})
        if temp > 38:
            insights.append({'type': 'weather', 'severity': 'high', 'message': 'Extreme heat stress caution. Avoid spraying chemicals mid-day.'})
        if moisture is None:
            insights.append({'type': 'sensor', 'severity': 'low', 'message': 'Sensor reading unavailable - using manual input/weather data.'})
            
        # Create record
        try:
            farm = FarmProfile.objects.get(user=request.user)
        except FarmProfile.DoesNotExist:
            farm = None

        record = IrrigationAssessment.objects.create(
            user=request.user,
            farm_profile=farm,
            crop=crop,
            growth_stage=stage,
            field_area=area,
            irrigation_method=method,
            soil_moisture=moisture,
            temperature=temp,
            humidity=humidity,
            rainfall=rainfall,
            priority=priority,
            reasoning=reason,
            input_sources=weather_source,
            rule_version='v1.0'
        )
        
        ActivityRecord.objects.create(
            user=request.user,
            activity_type='irrigation',
            title='Smart Irrigation Assessment',
            description=f'Priority: {priority} for {crop.capitalize()}'
        )

        return Response({
            'success': True,
            'irrigation_priority': priority,
            'recommended_action': action,
            'reason': reason,
            'insights': insights,
            'crop_info': crop_info if crop_info else {'message': 'Crop-specific quantity unavailable'},
            'model_status': 'development_prototype',
            'warning': 'This is a rule-based advisory and not a substitute for local agricultural guidance.'
        })
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def irrigation_history(request):
    recs = IrrigationAssessment.objects.filter(user=request.user).order_by('-created_at')
    history = []
    for r in recs:
        history.append({
            'id': r.id,
            'crop': r.crop,
            'priority': r.priority,
            'reasoning': r.reasoning,
            'temperature': r.temperature,
            'rainfall': r.rainfall,
            'soil_moisture': r.soil_moisture,
            'input_sources': r.input_sources,
            'created_at': r.created_at
        })
    return Response({'success': True, 'history': history})

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
            
        if request.user.is_authenticated:
            SustainabilityAssessment.objects.create(
                user=request.user,
                score=score,
                category=category
            )
            ActivityRecord.objects.create(
                user=request.user,
                activity_type='sustainability',
                title='Sustainability Score Calculated',
                description=f'Score: {score}/100 ({category})'
            )
            
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
@permission_classes([IsAuthenticated])
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
            
        crop = data.get('crop', '')
        growth_stage = data.get('growth_stage', '')
        weather_source = data.get('weather_source', 'manual')
        disease_scan_id = data.get('disease_scan_id')
        disease_label = data.get('disease_label', '')
        
        disease_scan = None
        if disease_scan_id:
            try:
                disease_scan = DiseaseScan.objects.get(id=disease_scan_id, user=request.user)
                disease_label = disease_scan.predicted_class
                disease_confidence = disease_scan.confidence
            except DiseaseScan.DoesNotExist:
                return Response({'success': False, 'error': 'Invalid disease scan or unauthorized.'}, status=status.HTTP_400_BAD_REQUEST)

        # Require minimum data
        if temperature is None or rainfall is None:
            return Response({'success': False, 'error': 'Insufficient data for a reliable assessment (Temperature and Rainfall required)'}, status=status.HTTP_400_BAD_REQUEST)
            
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
            
        farm_profile = None
        try:
            farm_profile = request.user.farm
        except FarmProfile.DoesNotExist:
            pass

        assessment = FieldGuardAssessment.objects.create(
            user=request.user,
            farm_profile=farm_profile,
            crop=crop,
            growth_stage=growth_stage,
            disease_scan=disease_scan,
            temperature=temperature,
            humidity=humidity,
            rainfall=rainfall,
            soil_moisture=soil_moisture,
            weather_source=weather_source,
            score=score,
            category=category,
            factors=factors,
            preventive_actions=actions,
            rule_version='v1.1'
        )
        
        ActivityRecord.objects.create(
            user=request.user,
            activity_type='fieldguard',
            title='FieldGuard Assessment Completed',
            description=f'Risk Score: {score}/100'
        )
            
        return Response({
            'success': True,
            'score': score,
            'category': category,
            'factors': factors,
            'preventive_actions': actions,
            'rule_version': assessment.rule_version,
            'timestamp': assessment.created_at,
            'data_sources': {
                'weather': weather_source,
                'soil_moisture': 'manual' if soil_moisture is not None else 'unavailable',
                'disease': 'Disease Detection Model' if disease_scan else 'manual'
            },
            'model_status': 'explainable_prototype',
            'warning': 'FieldGuard is an explainable prototype based on rules. It is not a substitute for local agricultural experts.'
        })
        
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fieldguard_history(request):
    assessments = FieldGuardAssessment.objects.filter(user=request.user).order_by('-created_at')
    history = []
    for a in assessments:
        history.append({
            'id': a.id,
            'score': a.score,
            'category': a.category,
            'crop': a.crop,
            'weather_source': a.weather_source,
            'disease': a.disease_scan.predicted_class if a.disease_scan else None,
            'created_at': a.created_at
        })
    return Response({'success': True, 'history': history})

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
            'has_farm_profile': farm is not None and bool(farm.farm_name),
            'farm_name': farm.farm_name if farm else ''
        }
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    user = request.user
    
    # Aggregations
    disease_scans = DiseaseScan.objects.filter(user=user)
    total_disease_scans = disease_scans.count()
    healthy_scans = disease_scans.filter(predicted_class__icontains='healthy').count()
    diseased_scans = total_disease_scans - healthy_scans
    
    total_crop_recs = CropRecommendationRecord.objects.filter(user=user).count()
    total_irrigations = IrrigationAssessment.objects.filter(user=user).count()
    total_fieldguard = FieldGuardAssessment.objects.filter(user=user).count()
    
    latest_fieldguard = FieldGuardAssessment.objects.filter(user=user).order_by('-created_at').first()
    latest_sustainability = SustainabilityAssessment.objects.filter(user=user).order_by('-created_at').first()
    
    recent_activities = ActivityRecord.objects.filter(user=user).order_by('-created_at')[:5]
    activities_data = [{
        'id': a.id,
        'title': a.title,
        'description': a.description,
        'activity_type': a.activity_type,
        'created_at': a.created_at
    } for a in recent_activities]
    
    return Response({
        'success': True,
        'total_disease_scans': total_disease_scans,
        'healthy_scans': healthy_scans,
        'diseased_scans': diseased_scans,
        'total_crop_recommendations': total_crop_recs,
        'total_irrigation_assessments': total_irrigations,
        'total_fieldguard_assessments': total_fieldguard,
        'latest_fieldguard_score': latest_fieldguard.score if latest_fieldguard else None,
        'latest_fieldguard_category': latest_fieldguard.category if latest_fieldguard else None,
        'latest_sustainability_score': latest_sustainability.score if latest_sustainability else None,
        'recent_activities': activities_data
    })
