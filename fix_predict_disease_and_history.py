import re

with open('backend/api/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix predict_disease check order
# Move image checks before crop_type check
new_predict_disease = """
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
        
    crop_type = request.POST.get('crop_type', '').lower()
    
    if crop_type != 'tomato':
        # Bypass inference for unsupported crops
        response_data = {
            "success": True,
            "prediction": {
                "status": "unsupported_crop",
                "crop": None,
                "disease": None,
                "class_id": None,
                "confidence": None,
                "model_version": "baseline_resnet18"
            },
            "knowledge": None,
            "supported_crops": ["Tomato"],
            "message": "This crop is not supported by the current model."
        }
        if request.user.is_authenticated:
            ActivityRecord.objects.create(
                user=request.user,
                activity_type='disease_scan',
                title='Disease Scan Bypassed',
                description='Unsupported crop selected.'
            )
        return Response(response_data)
        
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
"""
# We just replace the start of predict_disease up to "try:"
pattern1 = re.compile(r'@api_view\(\[\'POST\'\]\)\s*def predict_disease\(request\):.*?temp_img_path = temp_img\.name\s*try:', re.DOTALL)
if pattern1.search(content):
    content = pattern1.sub(new_predict_disease.strip() + '\n    try:', content)

# Fix disease_history to include analytics
new_disease_history = """
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def disease_history(request):
    scans = DiseaseScan.objects.filter(user=request.user).order_by('-created_at')
    history = []
    for scan in scans:
        history.append({
            'id': scan.id,
            'predicted_class': scan.predicted_class,
            'prediction_status': getattr(scan, 'prediction_status', 'unknown'),
            'disease_name': getattr(scan, 'disease_name', ''),
            'confidence': scan.confidence,
            'image_url': request.build_absolute_uri(scan.image.url) if scan.image else None,
            'model_version': scan.model_version,
            'is_development': scan.is_development,
            'created_at': scan.created_at
        })
        
    total_scans = scans.count()
    healthy_scans = scans.filter(prediction_status='healthy').count()
    diseased_scans = scans.filter(prediction_status='diseased').count()
    uncertain_scans = scans.filter(prediction_status='uncertain').count()
    
    analytics = {
        'total_scans': total_scans,
        'healthy_scans': healthy_scans,
        'diseased_scans': diseased_scans,
        'uncertain_scans': uncertain_scans,
        'most_frequent_disease': 'None'
    }
    
    if diseased_scans > 0:
        from django.db.models import Count
        most_freq = scans.filter(prediction_status='diseased').values('disease_name').annotate(count=Count('disease_name')).order_by('-count').first()
        if most_freq and most_freq['disease_name']:
            analytics['most_frequent_disease'] = most_freq['disease_name']
            
    return Response({'success': True, 'history': history, 'analytics': analytics})
"""
pattern2 = re.compile(r'@api_view\(\[\'GET\'\]\)\s*@permission_classes\(\[IsAuthenticated\]\)\s*def disease_history\(request\):.*?return Response\(\{\'success\': True, \'history\': history\}\)', re.DOTALL)
if pattern2.search(content):
    content = pattern2.sub(new_disease_history.strip(), content)

with open('backend/api/views.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Views fixed.")
