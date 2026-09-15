import re
import os

with open('backend/api/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_views = """
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
        
        # Super simple check for invalid/corrupted image
        if img.size[0] < 10 or img.size[1] < 10:
            return Response({"success": False, "error": "Image is too small or invalid."}, status=status.HTTP_400_BAD_REQUEST)
            
        transform = get_transforms(is_train=False)
        img_tensor = transform(img).unsqueeze(0)
        
        with torch.no_grad():
            outputs = model(img_tensor)
            probs = torch.nn.functional.softmax(outputs, dim=1)
            confidence, preds = torch.max(probs, 1)
            
        predicted_class = classes[preds.item()]
        conf_value = round(confidence.item(), 4)
        
        # Knowledge Database
        DISEASE_DB = {
            'Tomato___Bacterial_spot': {
                'disease_name': 'Bacterial Spot',
                'symptoms': ['Small, water-soaked, greasy-looking spots on leaves', 'Spots turn brown/black with yellow halos', 'Defoliation in severe cases'],
                'treatment': ['Apply copper-based bactericides early in infection', 'Remove and destroy infected plant debris'],
                'prevention': ['Avoid overhead irrigation', 'Use disease-free seeds and transplants', 'Practice crop rotation'],
                'expert_consult': 'Consult an agronomist if spots spread rapidly despite copper treatments.'
            }
        }
        
        # Parse prediction
        if '___' in predicted_class:
            plant_name, disease_status = predicted_class.split('___', 1)
        else:
            plant_name = "Unknown"
            disease_status = predicted_class
            
        plant_name = plant_name.replace('_', ' ')
        disease_status = disease_status.replace('_', ' ')
        
        prediction_status = 'uncertain'
        knowledge = None
        disease_name = None
        
        if conf_value < 0.85:
            prediction_status = 'uncertain'
        elif disease_status.lower() == 'healthy':
            prediction_status = 'healthy'
            disease_name = None
            knowledge = {
                'disease_name': 'Healthy Plant',
                'symptoms': ['Vibrant green color', 'Firm and upright structure', 'No visible spots, lesions, or pests'],
                'treatment': ['None required. Continue current care regimen.'],
                'prevention': ['Maintain regular monitoring', 'Ensure balanced fertilization', 'Keep field weed-free'],
                'expert_consult': 'No immediate consultation needed. Keep up the good work!'
            }
        else:
            prediction_status = 'diseased'
            disease_name = disease_status
            if predicted_class in DISEASE_DB:
                knowledge = DISEASE_DB[predicted_class]
            else:
                knowledge = {
                    'disease_name': disease_name,
                    'symptoms': ['Abnormal spots or lesions on leaves', 'Discoloration', 'Wilting or stunted growth'],
                    'treatment': ['Isolate affected plants if possible', 'Apply appropriate targeted treatment'],
                    'prevention': ['Ensure proper spacing for air circulation', 'Avoid overhead watering to keep foliage dry'],
                    'expert_consult': 'Consult an agronomist for specific treatment.'
                }
                
        # Save scan
        scan_record = None
        if request.user.is_authenticated:
            scan_record = DiseaseScan.objects.create(
                user=request.user,
                image=image_file,
                predicted_class=predicted_class,
                prediction_status=prediction_status,
                plant_name=plant_name,
                disease_name=disease_name,
                confidence=conf_value,
                model_version="baseline_resnet18",
                is_development=True
            )
            ActivityRecord.objects.create(
                user=request.user,
                activity_type='disease_scan',
                title='Disease Scan Completed',
                description=f'Status: {prediction_status.capitalize()}'
            )
        
        response_data = {
            "success": True,
            "prediction": {
                "status": prediction_status,
                "crop": plant_name,
                "disease": disease_name,
                "confidence": conf_value,
                "model_version": "baseline_resnet18",
                "supported_classes": ["Tomato"]
            },
            "knowledge": knowledge,
            "message": "No disease detected by the current model." if prediction_status == 'healthy' else 
                       "The image could not be classified reliably. Please upload a clear image of a supported crop leaf." if prediction_status == 'uncertain' else
                       "Disease detected by the model."
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
            'prediction_status': scan.prediction_status,
            'plant_name': scan.plant_name,
            'disease_name': scan.disease_name,
            'confidence': scan.confidence,
            'image_url': request.build_absolute_uri(scan.image.url) if scan.image else None,
            'model_version': scan.model_version,
            'is_development': scan.is_development,
            'created_at': scan.created_at
        })
        
    # Analytics
    total_scans = scans.count()
    healthy_scans = scans.filter(prediction_status='healthy').count()
    diseased_scans = scans.filter(prediction_status='diseased').count()
    uncertain_scans = scans.filter(prediction_status='uncertain').count()
    
    most_frequent_disease = "None"
    if diseased_scans > 0:
        most_freq = scans.filter(prediction_status='diseased').values('disease_name').annotate(count=Count('disease_name')).order_by('-count').first()
        if most_freq and most_freq['disease_name']:
            most_frequent_disease = most_freq['disease_name']
            
    analytics = {
        'total_scans': total_scans,
        'healthy_scans': healthy_scans,
        'diseased_scans': diseased_scans,
        'uncertain_scans': uncertain_scans,
        'most_frequent_disease': most_frequent_disease
    }
    
    return Response({'success': True, 'history': history, 'analytics': analytics})
"""

# Replace the views
pattern = re.compile(r'@api_view\(\[\'POST\'\]\)\s*def predict_disease\(request\):.*?return Response\(\{\'success\': True, \'history\': history\}\)', re.DOTALL)
if pattern.search(content):
    new_content = pattern.sub(new_views.strip(), content)
    with open('backend/api/views.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("predict_disease and disease_history updated successfully.")
else:
    print("Could not find the target views to replace.")
