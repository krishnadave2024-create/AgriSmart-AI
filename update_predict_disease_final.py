import re
import os

with open('backend/api/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_views = """
@api_view(['POST'])
def predict_disease(request):
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
        
        DISEASE_DB = {
            'Tomato___Bacterial_spot': {
                'disease_name': 'Bacterial Spot',
                'symptoms': ['Small, water-soaked, greasy-looking spots on leaves', 'Spots turn brown/black with yellow halos', 'Defoliation in severe cases'],
                'treatment': ['Apply copper-based bactericides early in infection', 'Remove and destroy infected plant debris'],
                'prevention': ['Avoid overhead irrigation', 'Use disease-free seeds and transplants', 'Practice crop rotation'],
                'safe_next_steps': ['Isolate plant if in container', 'Sanitize tools'],
                'expert_consult': 'Consult an agronomist if spots spread rapidly despite copper treatments.'
            }
        }
        
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
                'safe_next_steps': ['Continue monitoring'],
                'expert_consult': 'No immediate consultation needed. Keep up the good work!'
            }
        else:
            prediction_status = 'diseased'
            disease_name = disease_status
            if predicted_class in DISEASE_DB:
                knowledge = DISEASE_DB[predicted_class]
            else:
                knowledge = None
                
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
                "crop": plant_name if prediction_status != 'uncertain' else None,
                "disease": disease_name,
                "class_id": predicted_class if prediction_status != 'uncertain' else None,
                "confidence": conf_value if prediction_status != 'uncertain' else None,
                "model_version": "baseline_resnet18",
                "supported_classes": ["Tomato"]
            },
            "knowledge": knowledge,
            "message": "No disease detected by the current model. Continue monitoring the crop." if prediction_status == 'healthy' else 
                       "The image could not be classified reliably. Upload a clear image of a supported crop leaf." if prediction_status == 'uncertain' else
                       "The model detected the listed disease. Verify the result with an agricultural expert."
        }
        
        if scan_record and scan_record.image:
            response_data['image_url'] = request.build_absolute_uri(scan_record.image.url)
            
        return Response(response_data)
    except Exception as e:
        return Response({"success": False, "error": f"Inference failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        if os.path.exists(temp_img_path):
            os.remove(temp_img_path)
"""

pattern = re.compile(r'@api_view\(\[\'POST\'\]\)\s*def predict_disease\(request\):.*?finally:\n.*?os\.remove\(temp_img_path\)', re.DOTALL)
if pattern.search(content):
    new_content = pattern.sub(new_views.strip(), content)
    with open('backend/api/views.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("predict_disease updated successfully.")
else:
    print("Could not find predict_disease to replace.")
