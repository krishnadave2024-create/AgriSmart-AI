import os

content = """
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
"""

with open('backend/api/views.py', 'a', encoding='utf-8') as f:
    f.write(content)
