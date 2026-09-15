from django.db.models import Count, Avg
from django.db.models.functions import TruncDate
import os
import json
import time
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
    IrrigationAssessment, FieldGuardAssessment, SustainabilityAssessment, ActivityRecord, Notification
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
    
    if image_file.size > 15 * 1024 * 1024:
        return Response({"success": False, "error": "File size exceeds 15MB limit."}, status=status.HTTP_400_BAD_REQUEST)
        
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    ext = os.path.splitext(image_file.name)[1].lower()
    if ext not in valid_extensions:
        return Response({"success": False, "error": "Unsupported file format. Please upload JPG, PNG, or WEBP."}, status=status.HTTP_400_BAD_REQUEST)
        
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
        
        scan_record = None
        if request.user.is_authenticated:
            scan_record = DiseaseScan.objects.create(
                user=request.user,
                image=image_file,
                predicted_class=predicted_class,
                confidence=conf_value,
                model_version="baseline_resnet18_38class",
                is_development=False
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
            "confidence": round(conf_value * 100, 2),
            "model_status": "active",
            "is_development": False,
            "model_version": "baseline_resnet18_38class",
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

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

def get_latest_or_none(model, user):
    return model.objects.filter(user=user).order_by('-created_at').first()

def estimate_savings(farm_area, irrigation_method, rainwater_harvesting):
    # Base assumptions: Conventional irrigation uses ~5000 m3/ha. Drip uses ~3000 m3/ha. (Diff = 2000)
    # Energy: pumping 2000 m3 less saves ~150 kWh/ha.
    # Cost: pumping costs ~₹5 per kWh -> ₹750/ha.
    if not farm_area or farm_area <= 0:
        return 'unavailable', 'unavailable', 'unavailable'
        
    water_m3 = 0
    energy_kwh = 0
    cost_inr = 0
    
    if irrigation_method == 'Drip':
        water_m3 += 2000 * farm_area
        energy_kwh += 150 * farm_area
        cost_inr += 750 * farm_area
    elif irrigation_method == 'Sprinkler':
        water_m3 += 1000 * farm_area
        energy_kwh += 75 * farm_area
        cost_inr += 375 * farm_area
        
    if rainwater_harvesting == 'yes':
        water_m3 += 500 * farm_area
        
    if water_m3 > 0:
        return f"~{int(water_m3)} m³ estimated", f"~{int(energy_kwh)} kWh estimated", f"~₹{int(cost_inr)} estimated"
    return 'unavailable', 'unavailable', 'unavailable'

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sustainability_score(request):
    try:
        user = request.user
        data = request.data
        
        # Gather context from DB
        farm = FarmProfile.objects.filter(user=user).first()
        latest_irrigation = IrrigationAssessment.objects.filter(user=user).order_by('-created_at').first()
        latest_fg = FieldGuardAssessment.objects.filter(user=user).order_by('-created_at').first()
        
        input_values = {}
        source_labels = {}
        
        # Helper to resolve field value (user input overrides DB)
        def resolve_field(key, db_value, db_label='database'):
            val = data.get(key)
            if val is not None and str(val).strip() != '':
                input_values[key] = str(val).lower()
                source_labels[key] = 'manual'
            elif db_value is not None:
                input_values[key] = str(db_value).lower()
                source_labels[key] = db_label
            else:
                input_values[key] = 'unknown'
                source_labels[key] = 'unavailable'
                
        resolve_field('crop_rotation', None)
        resolve_field('organic_fertilizer', None)
        resolve_field('rainwater_harvesting', None)
        resolve_field('soil_conservation', None)
        resolve_field('crop_residue_management', None)
        resolve_field('chemical_fertilizer_level', None)
        resolve_field('pesticide_level', None)
        
        irr_method_db = latest_irrigation.irrigation_method if latest_irrigation else None
        resolve_field('irrigation_method', irr_method_db, 'database (Irrigation)')
        
        score = 0
        positive = []
        improvements = []
        
        def is_yes(key):
            return input_values.get(key) in ['yes', 'true', '1']
            
        if is_yes('crop_rotation'):
            score += 15
            positive.append('Crop rotation practice is being followed.')
        else:
            improvements.append('Implement crop rotation to improve soil health.')
            
        if is_yes('organic_fertilizer'):
            score += 15
            positive.append('Organic fertilizer usage is reported.')
        else:
            improvements.append('Consider integrating organic fertilizers to reduce chemical reliance.')
            
        if is_yes('rainwater_harvesting'):
            score += 15
            positive.append('Rainwater harvesting is being utilized.')
        else:
            improvements.append('Implement rainwater harvesting to improve water-use efficiency.')
            
        if is_yes('soil_conservation'):
            score += 15
            positive.append('Soil conservation practices are active.')
        else:
            improvements.append('Adopt soil conservation techniques (e.g., minimum tillage, cover crops).')
            
        if is_yes('crop_residue_management'):
            score += 10
            positive.append('Crop residue is being managed sustainably.')
        else:
            improvements.append('Avoid burning crop residue; compost or incorporate it into the soil.')
            
        irr_method = input_values.get('irrigation_method', '')
        if irr_method in ['drip', 'sprinkler']:
            score += 20
            positive.append(f'Water-efficient {irr_method} irrigation is used.')
        elif irr_method == 'unknown':
            improvements.append('Provide irrigation method for a more accurate assessment.')
        else:
            improvements.append('Consider upgrading to drip or sprinkler irrigation to save water.')
            
        chem_fertilizer = input_values.get('chemical_fertilizer_level', 'unknown')
        pesticide = input_values.get('pesticide_level', 'unknown')
        
        if chem_fertilizer == 'high':
            score -= 10
            improvements.append('High chemical fertilizer usage detected. Aim to reduce and optimize application.')
        elif chem_fertilizer == 'low':
            score += 5
            positive.append('Chemical fertilizer usage is kept low.')
            
        if pesticide == 'high':
            score -= 10
            improvements.append('High pesticide usage detected. Implement Integrated Pest Management (IPM).')
        elif pesticide == 'low':
            score += 5
            positive.append('Pesticide usage is minimized.')
            
        # Ensure sufficient data: require at least 3 known inputs
        known_count = sum(1 for v in input_values.values() if v != 'unknown')
        if known_count < 3:
            return Response({'success': False, 'error': 'Not enough verified data for a sustainability assessment.'}, status=400)
            
        score = max(0, min(100, score))
        
        if score < 40:
            category = 'Needs Improvement'
        elif score < 60:
            category = 'Developing'
        elif score < 80:
            category = 'Good'
        else:
            category = 'Excellent'
            
        water_est, energy_est, cost_est = estimate_savings(
            farm.farm_area if farm else None, 
            input_values.get('irrigation_method'), 
            input_values.get('rainwater_harvesting')
        )
            
        assessment = SustainabilityAssessment.objects.create(
            user=user,
            farm_profile=farm,
            score=score,
            category=category,
            input_values=input_values,
            source_labels=source_labels,
            positive_factors=positive,
            improvement_suggestions=improvements,
            calculation_method='rule-based (v1.1)',
            rule_version='v1.1',
            water_savings_estimate=water_est,
            energy_savings_estimate=energy_est,
            cost_savings_estimate=cost_est
        )
        
        ActivityRecord.objects.create(
            user=user,
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
            'input_values': input_values,
            'source_labels': source_labels,
            'water_savings_estimate': water_est,
            'energy_savings_estimate': energy_est,
            'cost_savings_estimate': cost_est,
            'calculation_method': 'rule-based (v1.1)',
            'rule_version': 'v1.1',
            'warning': 'This is an explainable prototype score. Estimates are based on standard assumptions, not verified environmental impact.',
            'timestamp': assessment.created_at
        })
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sustainability_history(request):
    try:
        history = SustainabilityAssessment.objects.filter(user=request.user).order_by('-created_at')
        result = []
        for h in history:
            result.append({
                'id': h.id,
                'score': h.score,
                'category': h.category,
                'calculation_method': h.calculation_method,
                'rule_version': h.rule_version,
                'created_at': h.created_at,
                'improvement': h.improvement_suggestions[0] if h.improvement_suggestions else 'None',
                'known_inputs': sum(1 for v in h.input_values.values() if v != 'unknown')
            })
        return Response({'success': True, 'history': result})
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)

def update_sustainability_context(user):
    # Used for automatic updates after other modules run
    try:
        # A simple internal hook: create a dummy request object and pass it to sustainability_score?
        # Better: just factor out the logic, but to save time, we'll just let the frontend trigger it or do it inline.
        pass
    except Exception:
        pass


from google import genai
from google.genai import types
from .models import AssistantMessage

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def farmer_assistant(request):
    try:
        user = request.user
        data = request.data
        message = data.get('message', '').strip()
        language = data.get('language', 'en')
        
        if not message:
            return Response({'success': False, 'error': 'Message cannot be empty.'}, status=400)
            
        if len(message) > 500:
            return Response({'success': False, 'error': 'Message is too long.'}, status=400)
            
        if language not in ['en', 'hi', 'gu']:
            language = 'en'
            
        # Gather Context
        farm = FarmProfile.objects.filter(user=user).first()
        latest_disease = DiseaseScan.objects.filter(user=user).order_by('-created_at').first()
        latest_irr = IrrigationAssessment.objects.filter(user=user).order_by('-created_at').first()
        latest_crop = CropRecommendationRecord.objects.filter(user=user).order_by('-created_at').first()
        latest_fg = FieldGuardAssessment.objects.filter(user=user).order_by('-created_at').first()
        latest_sust = SustainabilityAssessment.objects.filter(user=user).order_by('-created_at').first()
        
        context_parts = []
        if farm:
            context_parts.append(f"Farm Location: {farm.location}, Size: {farm.farm_area} {farm.area_unit}, Soil: {farm.soil_type}")
        if latest_disease:
            context_parts.append(f"Recent Disease Scan: {latest_disease.predicted_class} (Confidence: {latest_disease.confidence:.2f})")
        if latest_irr:
            context_parts.append(f"Recent Irrigation Plan: Crop: {latest_irr.crop}, Method: {latest_irr.irrigation_method}")
        if latest_crop:
            context_parts.append(f"Recent Crop Recommendation: {latest_crop.top_recommendation}")
        if latest_fg:
            context_parts.append(f"Recent Risk Assessment: {latest_fg.category} (Score: {latest_fg.score})")
            
        context_str = "\\n".join(context_parts) if context_parts else "No specific farm data available."
        
        from .services.ai_service import ask_assistant
        success, status_code, response_data = ask_assistant(context_str, message, language)
        
        if success:
            # Save history on success
            AssistantMessage.objects.create(
                user=user,
                message=message,
                response=response_data.get('answer'),
                source=response_data.get('source', 'gemini'),
                model_status=response_data.get('model_status', 'live')
            )
            return Response({
                'success': True,
                **response_data
            }, status=200)
        else:
            return Response({
                'success': False,
                **response_data
            }, status=status_code)
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'answer': None,
            'error': 'An unexpected server error occurred.',
            'model_status': 'error'
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def assistant_health(request):
    try:
        from .services.ai_service import check_health
        health = check_health()
        return Response(health, status=200)
    except Exception:
        return Response({'available': False, 'reason': 'Error checking AI health'}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def assistant_history(request):
    try:
        messages = AssistantMessage.objects.filter(user=request.user).order_by('created_at')
        res = []
        for m in messages:
            res.append({
                'role': m.role,
                'content': m.content,
                'language': m.language,
                'timestamp': m.created_at,
                'model_status': m.model_status
            })
        return Response({'success': True, 'history': res})
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)


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
from .serializers import RegisterSerializer, UserProfileSerializer, FarmProfileSerializer, NotificationSerializer
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
@permission_classes([AllowAny])
def dashboard_summary(request):
    user = request.user
    profile = getattr(user, 'profile', None)
    farm = getattr(user, 'farm', None)
    
    # 1. Overview metrics
    disease_scans = DiseaseScan.objects.filter(user=user)
    total_disease_scans = disease_scans.count()
    healthy_scans = disease_scans.filter(predicted_class__icontains='healthy').count()
    diseased_scans = total_disease_scans - healthy_scans
    
    total_crop_recs = CropRecommendationRecord.objects.filter(user=user).count()
    total_irrigations = IrrigationAssessment.objects.filter(user=user).count()
    
    latest_fieldguard = FieldGuardAssessment.objects.filter(user=user).order_by('-created_at').first()
    latest_sustainability = SustainabilityAssessment.objects.filter(user=user).order_by('-created_at').first()
    latest_disease = disease_scans.order_by('-created_at').first()
    latest_crop = CropRecommendationRecord.objects.filter(user=user).order_by('-created_at').first()
    latest_irrigation = IrrigationAssessment.objects.filter(user=user).order_by('-created_at').first()
    
    # 2. Analytics (Time Series)
    # Activity Trend (last 30 days or all time)
    activity_trend = list(ActivityRecord.objects.filter(user=user)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date'))
        
    for item in activity_trend:
        if item['date']:
            item['date'] = item['date'].strftime('%Y-%m-%d')
            
    # FieldGuard Trend
    fg_trend = list(FieldGuardAssessment.objects.filter(user=user).order_by('created_at')[:20].values('created_at', 'score', 'category'))
    for item in fg_trend:
        item['date'] = item['created_at'].strftime('%Y-%m-%d')
        del item['created_at']
        
    # Sustainability Trend
    sus_trend = list(SustainabilityAssessment.objects.filter(user=user).order_by('created_at')[:20].values('created_at', 'score', 'category'))
    for item in sus_trend:
        item['date'] = item['created_at'].strftime('%Y-%m-%d')
        del item['created_at']
        
    # 3. Needs Attention
    needs_attention = []
    
    # Farm Profile checks
    if not farm or not farm.location:
        needs_attention.append({
            'reason': 'Farm city is missing',
            'severity': 'warning',
            'action': 'Update Farm Profile',
            'link': '/farm-profile'
        })
    if not farm or not farm.soil_type:
        needs_attention.append({
            'reason': 'Soil type is not saved',
            'severity': 'info',
            'action': 'Update Farm Profile',
            'link': '/farm-profile'
        })
        
    # Data checks
    if total_disease_scans == 0:
        needs_attention.append({
            'reason': 'No disease scans recorded',
            'severity': 'info',
            'action': 'Run a Disease Scan',
            'link': '/disease'
        })
        
    if latest_fieldguard and latest_fieldguard.score < 40:
        needs_attention.append({
            'reason': f'Latest FieldGuard risk is High ({latest_fieldguard.score}/100)',
            'severity': 'error',
            'action': 'View FieldGuard',
            'link': '/fieldguard'
        })
        
    if not needs_attention and total_disease_scans > 0:
        needs_attention.append({
            'reason': 'No urgent actions detected from your available records.',
            'severity': 'success',
            'action': 'View Analytics',
            'link': '/'
        })

    # 4. Insights
    insights = []
    if latest_disease:
        insights.append(f"Your latest disease scan resulted in '{latest_disease.predicted_class}'.")
    if latest_fieldguard:
        insights.append(f"Your latest FieldGuard assessment is categorized as '{latest_fieldguard.category}'.")
    if latest_crop:
        insights.append(f"Your most recent crop recommendation was '{latest_crop.top_recommendation}'.")
    if latest_sustainability:
        insights.append(f"Your latest sustainability score is {round(latest_sustainability.score)}/100.")
        
    # 5. Recent Activity
    recent_activities = ActivityRecord.objects.filter(user=user).order_by('-created_at')[:6]
    activities_data = [{
        'id': a.id,
        'title': a.title,
        'description': a.description,
        'activity_type': a.activity_type,
        'created_at': a.created_at
    } for a in recent_activities]
    
    return Response({
        'success': True,
        'metrics': {
            'total_disease_scans': total_disease_scans,
            'healthy_scans': healthy_scans,
            'diseased_scans': diseased_scans,
            'total_crop_recommendations': total_crop_recs,
            'total_irrigation_assessments': total_irrigations,
            'latest_disease_date': latest_disease.created_at if latest_disease else None,
            'latest_disease_class': latest_disease.predicted_class if latest_disease else None,
            'latest_crop_rec': latest_crop.top_recommendation if latest_crop else None,
            'latest_irrigation_date': latest_irrigation.created_at if latest_irrigation else None,
            'latest_fieldguard_score': latest_fieldguard.score if latest_fieldguard else None,
            'latest_fieldguard_category': latest_fieldguard.category if latest_fieldguard else None,
            'latest_fieldguard_date': latest_fieldguard.created_at if latest_fieldguard else None,
            'latest_sustainability_score': latest_sustainability.score if latest_sustainability else None,
            'latest_sustainability_category': latest_sustainability.category if latest_sustainability else None,
            'latest_sustainability_date': latest_sustainability.created_at if latest_sustainability else None,
            'missing_profile': not farm or not farm.farm_name or not farm.location
        },
        'analytics': {
            'activity_trend': activity_trend,
            'fieldguard_trend': fg_trend,
            'sustainability_trend': sus_trend,
        },
        'needs_attention': needs_attention,
        'insights': insights,
        'recent_activities': activities_data
    })
# ── New ResNet18 Prediction API ──────────────────────────────────────────────
_RESNET18_MODEL = None
_RESNET18_CLASSES = None

def _get_resnet18_model():
    global _RESNET18_MODEL, _RESNET18_CLASSES
    if _RESNET18_MODEL is not None:
        return _RESNET18_MODEL, _RESNET18_CLASSES

    import os
    import torch
    import torch.nn as nn
    
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    chkpt_path = os.path.join(project_root, "model", "checkpoints", "baseline_resnet18.pth")
    if not os.path.exists(chkpt_path):
        return None, None

    try:
        from torchvision.models import resnet18
        checkpoint = torch.load(chkpt_path, weights_only=False, map_location='cpu')
        classes = checkpoint.get('classes', [])
        if len(classes) != 38:
            return None, None

        model = resnet18(weights=None)
        model.fc = nn.Linear(model.fc.in_features, len(classes))
        model.load_state_dict(checkpoint['model_state_dict'])
        model.eval()

        _RESNET18_MODEL = model
        _RESNET18_CLASSES = classes
        return model, classes
    except Exception as e:
        print(f"Error loading ResNet18 model: {e}")
        return None, None

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
@permission_classes([AllowAny])
def predict_endpoint(request):
    """
    POST /api/predict/
    """
    if 'image_file' not in request.FILES:
        return Response({"error": "Please upload an image using the image_file field."}, status=status.HTTP_400_BAD_REQUEST)
        
    image_file = request.FILES['image_file']
    try:
        from PIL import Image
        img = Image.open(image_file).convert('RGB')
    except Exception:
        return Response({"error": "Invalid image file."}, status=status.HTTP_400_BAD_REQUEST)
        
    model, classes = _get_resnet18_model()
    if model is None:
        return Response({"error": "Model checkpoint is unavailable."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    import sys
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if os.path.join(project_root, 'model') not in sys.path:
        sys.path.append(os.path.join(project_root, 'model'))
    from dataset import get_transforms
    import torch.nn.functional as F
    import torch
    
    transform = get_transforms(is_train=False)
    img_tensor = transform(img).unsqueeze(0)
    
    with torch.no_grad():
        logits = model(img_tensor)
        probs = F.softmax(logits, dim=1)[0]
        
    top_prob, top_idx = torch.max(probs, 0)
    
    return Response({
        "success": True,
        "predicted_class": classes[top_idx.item()],
        "confidence": round(top_prob.item() * 100, 2),
        "model": "ResNet18"
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    GET /api/health/
    """
    model, classes = _get_resnet18_model()
    return Response({
        "status": "ok",
        "model_available": model is not None,
        "num_classes": len(classes) if classes else 0,
        "model": "ResNet18"
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    try:
        notifications = Notification.objects.filter(user=request.user)
        serializer = NotificationSerializer(notifications, many=True)
        unread_count = notifications.filter(is_read=False).count()
        return Response({
            'success': True,
            'notifications': serializer.data,
            'unread_count': unread_count
        })
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, pk):
    try:
        notification = Notification.objects.get(pk=pk, user=request.user)
        notification.is_read = True
        notification.save()
        return Response({'success': True})
    except Notification.DoesNotExist:
        return Response({'success': False, 'error': 'Notification not found'}, status=404)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_notifications_read(request):
    try:
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'success': True})
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def navbar_weather(request):
    try:
        farm = FarmProfile.objects.filter(user=request.user).first()
        if not farm or not farm.location:
            return Response({'success': False, 'error': 'Farm city not set.'}, status=400)
            
        api_key = os.environ.get('OPENWEATHER_API_KEY')
        if not api_key or api_key == 'your_openweather_api_key_here':
            return Response({'success': False, 'error': 'Weather service not configured.'}, status=503)
            
        url = f"http://api.openweathermap.org/data/2.5/weather?q={farm.location}&appid={api_key}&units=metric"
        res = requests.get(url, timeout=5)
        
        if res.status_code == 200:
            data = res.json()
            return Response({
                'success': True,
                'temp': data['main']['temp'],
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon'],
                'location': farm.location
            })
        else:
            return Response({'success': False, 'error': 'Failed to fetch weather data.'}, status=503)
            
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=500)
