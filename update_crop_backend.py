import re
import os

with open('backend/api/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_knowledge_base = """
CROP_KNOWLEDGE_BASE = {
    'Rice': {
        'name': 'Rice',
        'scientific_name': 'Oryza sativa',
        'soil_type': 'Clayey, Loamy',
        'ph_range': (5.5, 7.0),
        'temp_range': (20, 35),
        'rainfall_range': (100, 250),
        'n_range': (80, 120),
        'p_range': (30, 60),
        'k_range': (30, 60),
        'water_req': 'High',
        'season': 'Kharif',
        'duration': '120-150 days',
        'nutrient_req': 'High Nitrogen, Medium Phosphorus, Low Potassium',
        'deficiency_risks': 'Nitrogen deficiency causes yellowing of older leaves.',
        'excess_risks': 'Excess Nitrogen makes plants susceptible to lodging and pests.',
        'advantages': 'High yield in waterlogged areas.',
        'limitations': 'Extremely water-intensive.',
        'sustainability': 'High methane emissions. Consider Alternate Wetting and Drying (AWD).',
        'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Rice_field_in_the_Philippines.jpg/800px-Rice_field_in_the_Philippines.jpg',
        'reference_url': 'https://www.fao.org/land-water/databases-and-software/crop-information/rice/en/'
    },
    'Wheat': {
        'name': 'Wheat',
        'scientific_name': 'Triticum aestivum',
        'soil_type': 'Loamy, Clay Loam',
        'ph_range': (6.0, 7.5),
        'temp_range': (15, 25),
        'rainfall_range': (50, 100),
        'n_range': (60, 100),
        'p_range': (20, 40),
        'k_range': (20, 40),
        'water_req': 'Moderate',
        'season': 'Rabi',
        'duration': '110-130 days',
        'nutrient_req': 'High Nitrogen, Moderate P & K',
        'deficiency_risks': 'Potassium deficiency leads to poor grain filling.',
        'excess_risks': 'N/A',
        'advantages': 'Staple food crop, highly mechanized.',
        'limitations': 'Sensitive to terminal heat stress.',
        'sustainability': 'Requires balanced NPK for long-term soil health.',
        'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Wheat_Close_Up.JPG/800px-Wheat_Close_Up.JPG',
        'reference_url': 'https://www.fao.org/land-water/databases-and-software/crop-information/wheat/en/'
    },
    'Maize': {
        'name': 'Maize',
        'scientific_name': 'Zea mays',
        'soil_type': 'Well-drained Loam',
        'ph_range': (5.8, 7.0),
        'temp_range': (18, 27),
        'rainfall_range': (60, 110),
        'n_range': (100, 150),
        'p_range': (40, 80),
        'k_range': (40, 80),
        'water_req': 'Moderate',
        'season': 'Kharif / Zaid',
        'duration': '90-120 days',
        'nutrient_req': 'High N and K',
        'deficiency_risks': 'Phosphorus deficiency causes purple leaves.',
        'excess_risks': 'Sensitive to waterlogging.',
        'advantages': 'High yield potential, versatile uses.',
        'limitations': 'Highly sensitive to drought during tasseling.',
        'sustainability': 'Heavy feeder; requires crop rotation.',
        'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Corn_field.jpg/800px-Corn_field.jpg',
        'reference_url': 'https://www.fao.org/land-water/databases-and-software/crop-information/maize/en/'
    },
    'Cotton': {
        'name': 'Cotton',
        'scientific_name': 'Gossypium',
        'soil_type': 'Black soil, Clayey',
        'ph_range': (5.8, 8.0),
        'temp_range': (25, 35),
        'rainfall_range': (40, 75),
        'n_range': (80, 120),
        'p_range': (30, 60),
        'k_range': (40, 80),
        'water_req': 'Moderate to Low',
        'season': 'Kharif',
        'duration': '150-180 days',
        'nutrient_req': 'High N and K',
        'deficiency_risks': 'Magnesium deficiency causes red leaves.',
        'excess_risks': 'Excess Nitrogen promotes vegetative growth over bolls.',
        'advantages': 'High cash value.',
        'limitations': 'Highly susceptible to pests (bollworm).',
        'sustainability': 'Pesticide intensive. IPM strongly recommended.',
        'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Cotton_Plant.jpg/800px-Cotton_Plant.jpg',
        'reference_url': 'https://www.fao.org/land-water/databases-and-software/crop-information/cotton/en/'
    },
    'Millets': {
        'name': 'Millets',
        'scientific_name': 'Pennisetum glaucum / Sorghum bicolor',
        'soil_type': 'Sandy, Loamy (Tolerant to poor soils)',
        'ph_range': (5.5, 7.5),
        'temp_range': (25, 35),
        'rainfall_range': (30, 60),
        'n_range': (20, 50),
        'p_range': (10, 30),
        'k_range': (10, 30),
        'water_req': 'Low',
        'season': 'Kharif',
        'duration': '70-100 days',
        'nutrient_req': 'Low',
        'deficiency_risks': 'Very hardy, minimal deficiency risks.',
        'excess_risks': 'Cannot tolerate waterlogging.',
        'advantages': 'Highly drought resistant and climate-resilient.',
        'limitations': 'Lower yield compared to major cereals.',
        'sustainability': 'Excellent for water conservation and soil restoration.',
        'image_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Pearl_Millet.jpg/800px-Pearl_Millet.jpg',
        'reference_url': 'https://www.fao.org/land-water/databases-and-software/crop-information/sorghum/en/'
    }
}
"""

new_recommend_crop = """
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
            
            # Climate logic
            t_min, t_max = details['temp_range']
            if t_min <= temp <= t_max:
                matching.append(f'Temperature ({temp}°C) is optimal ({t_min}-{t_max}°C).')
            else:
                score -= 15
                non_matching.append(f'Temperature ({temp}°C) is outside optimal range ({t_min}-{t_max}°C).')
                
            r_min, r_max = details['rainfall_range']
            if r_min <= rainfall <= r_max:
                matching.append(f'Rainfall ({rainfall}mm) is optimal ({r_min}-{r_max}mm).')
            else:
                score -= 15
                non_matching.append(f'Rainfall ({rainfall}mm) is outside optimal range ({r_min}-{r_max}mm).')
                
            # Soil Analysis Logic
            soil_analysis = {}
            
            def analyze_nutrient(val, range_tuple, name):
                nonlocal score
                min_v, max_v = range_tuple
                if val < min_v:
                    score -= 10
                    return {"value": val, "status": "below", "message": f"{name} is below preferred range ({min_v}-{max_v})."}
                elif val > max_v:
                    score -= 5
                    return {"value": val, "status": "above", "message": f"{name} is above preferred range ({min_v}-{max_v})."}
                else:
                    return {"value": val, "status": "within", "message": f"{name} is optimal ({min_v}-{max_v})."}

            soil_analysis['nitrogen'] = analyze_nutrient(n, details['n_range'], 'Nitrogen')
            soil_analysis['phosphorus'] = analyze_nutrient(p, details['p_range'], 'Phosphorus')
            soil_analysis['potassium'] = analyze_nutrient(k, details['k_range'], 'Potassium')
            
            ph_min, ph_max = details['ph_range']
            if ph < ph_min:
                score -= 15
                soil_analysis['ph'] = {"value": ph, "status": "below", "message": f"pH is too acidic (optimal {ph_min}-{ph_max})."}
            elif ph > ph_max:
                score -= 15
                soil_analysis['ph'] = {"value": ph, "status": "above", "message": f"pH is too alkaline (optimal {ph_min}-{ph_max})."}
            else:
                soil_analysis['ph'] = {"value": ph, "status": "within", "message": f"pH is optimal ({ph_min}-{ph_max})."}
                
            if score > 0:
                recommendations.append({
                    'crop': crop,
                    'suitability_score': max(0, score),
                    'matching_conditions': matching,
                    'non_matching_conditions': non_matching,
                    'soil_analysis': soil_analysis,
                    'details': details
                })
        
        recommendations.sort(key=lambda x: x['suitability_score'], reverse=True)
        top_rec = recommendations[0]['crop'] if recommendations else None
        explanation = "Based on your inputs, this crop's growing conditions match well." if top_rec else "No suitable crop found."

        if request.user.is_authenticated:
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
            'model_status': 'rule-based',
            'data_quality': {
                'weather_status': 'Live (OpenWeather)' if weather_source == 'openweather' else 'Manual Entry',
                'soil_status': 'User Input'
            },
            'warning': 'Recommendations are rule-based estimates based on generalized crop parameters. Please verify with a local agronomist.'
        })
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
"""

# Replace CROP_KNOWLEDGE_BASE
pattern_kb = re.compile(r'CROP_KNOWLEDGE_BASE = \{.*?^\}', re.DOTALL | re.MULTILINE)
if pattern_kb.search(content):
    content = pattern_kb.sub(new_knowledge_base.strip() + '\n', content)

# Replace recommend_crop
pattern_func = re.compile(r'@api_view\(\[\'POST\'\]\)\s*def recommend_crop\(request\):.*?return Response\(\{\'success\': False, \'error\': str\(e\)\}, status=status\.HTTP_500_INTERNAL_SERVER_ERROR\)', re.DOTALL)
if pattern_func.search(content):
    content = pattern_func.sub(new_recommend_crop.strip(), content)

with open('backend/api/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated backend views for Crop Recommendation")
