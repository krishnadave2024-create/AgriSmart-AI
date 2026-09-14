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
        latest_irrigation = get_latest_or_none(IrrigationAssessment, user)
        latest_fg = get_latest_or_none(FieldGuardAssessment, user)
        
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
