# Disease Prediction API

This document describes the primary REST API endpoint for plant leaf disease detection using the trained ResNet18 model.

## Endpoint: Predict Disease
- **URL**: `/api/predict/`
- **Method**: `POST`
- **Authentication**: None (Public)

### Request Format
This endpoint accepts `multipart/form-data`.
- `image_file` (required): The plant leaf image (JPEG, PNG).

### Example cURL Command
```powershell
curl.exe -X POST `
  http://127.0.0.1:8000/api/predict/ `
  -F "image_file=@C:\path\to\leaf_image.jpg"
```

### Success Response
If the image is successfully processed by the ResNet18 model, it returns HTTP 200 with:
```json
{
  "success": true,
  "predicted_class": "Tomato___Early_blight",
  "confidence": 93.42,
  "model": "ResNet18"
}
```

### Error Responses

#### Missing File (HTTP 400)
```json
{
  "error": "Please upload an image using the image_file field."
}
```

#### Invalid File Format (HTTP 400)
```json
{
  "error": "Invalid image file."
}
```

#### Missing Model Checkpoint (HTTP 500)
If the `baseline_resnet18.pth` is missing from `model/checkpoints/`:
```json
{
  "error": "Model checkpoint is unavailable."
}
```

## Important Limitations
> [!WARNING]
> **Field Accuracy vs. Validation Accuracy**
> The model was trained and evaluated on the PlantVillage dataset (~93% validation accuracy), which consists largely of single leaves photographed under controlled laboratory conditions. Real-world field accuracy may differ significantly due to complex backgrounds, lighting variations, and overlapping leaves.

---

## Endpoint: Health Check
- **URL**: `/api/health/`
- **Method**: `GET`
- **Description**: Returns the readiness status of the backend and the ML model.

### Success Response
```json
{
  "status": "ok",
  "model_ready": true
}
```
If `model_ready` is false, it means the `baseline_resnet18.pth` checkpoint was not found on disk.
