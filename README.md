# AGRISMART AI
Intelligent Agriculture for a Sustainable Future

## Project Overview
AgriSmart AI is a production-quality agricultural decision-support platform designed to help farmers with crucial, data-driven decisions. The platform leverages modern machine learning and a robust web architecture to deliver accurate, localized insights.

## Development Dataset Information
- **Dataset**: `ayerr/plant-disease-classification` (Hugging Face)
- **Status**: Development and prototyping only. **The official SIH field-condition dataset remains unverified and unavailable.**
- **Preparation**: Run `python extract_ayerr_subset.py` followed by `python inspect_development_dataset.py` and `python create_development_manifest.py`.
- **Storage**: Downloaded images are stored locally in `data/external/development_dataset/raw/`. They are excluded from version control.

## Running the Application

### Backend (Django)
1. Install requirements: `pip install -r requirements.txt`
2. Navigate to backend: `cd backend`
3. Run migrations: `python manage.py migrate`
4. Start server: `python manage.py runserver`

### Frontend (React/Vite)
1. Navigate to frontend: `cd frontend`
2. Install dependencies: `npm install`
3. Start dev server: `npm run dev`

## API Endpoints

### `POST /api/disease/predict/`
**Description**: Analyzes a leaf image for crop disease.
**Note**: This endpoint uses a **development prototype model** trained on ~100 images (2 classes). It is NOT production-ready and does not represent the final SIH evaluation model. The official SIH dataset is unavailable.

**Request**:
- Content-Type: `multipart/form-data`
- Body: `image` (File: JPG/PNG, max 10MB)

**Success Response** (200 OK):
```json
{
  "success": true,
  "predicted_class": "diseased",
  "confidence": 0.985,
  "model_status": "development_prototype",
  "warning": "This model was trained on a very small development dataset and is not production-ready."
}
```

**Error Response** (400/500):
```json
{
  "success": false,
  "error": "Model checkpoint is unavailable. Please run training to generate the checkpoint."
}
```

### `POST /api/crops/recommend/`
**Description**: Provides a ranked list of suitable crops based on soil and climate conditions.
**Note**: This is a transparent rule-based prototype engine.

**Request**:
- Content-Type: `application/json`
- Body: `nitrogen`, `phosphorus`, `potassium`, `ph`, `temperature`, `humidity`, `rainfall`

**Success Response** (200 OK):
```json
{
  "success": true,
  "recommendations": [
    {"crop": "Rice", "suitability_score": 85, "reason": "High rainfall..."}
  ],
  "model_status": "development_prototype",
  "warning": "Recommendations are prototype rule-based estimates..."
}
```

### `POST /api/irrigation/recommend/`
**Description**: Provides irrigation priority and weather-based insights.
**Note**: This is a transparent rule-based prototype. No IoT or hardware sensors are integrated.

**Request**:
- Content-Type: `application/json`
- Body: `crop`, `temperature`, `rainfall`, `soil_moisture` (optional), `humidity` (optional), `growth_stage` (optional)

**Success Response** (200 OK):
```json
{
  "success": true,
  "irrigation_priority": "Urgent irrigation recommended",
  "recommended_action": "Apply irrigation immediately...",
  "insights": [{"type": "weather", "severity": "high", "message": "Heavy rain expected."}],
  "model_status": "development_prototype",
  "warning": "This is a prototype advisory..."
}
```

## Prototype Limitations & Exclusions
- **Development Models Only**: The crop disease model is trained on a tiny development dataset (~100 images, 2 classes). It is not production-ready.
- **Rule-based Logic**: Crop recommendations and irrigation insights are currently generated using explicit, rule-based prototype logic, not trained ML models.
- **No IoT Integration**: There is no live hardware sensor or IoT integration included in this prototype.
- **No Agentic AI**: Agentic AI generation is not yet implemented.
- **Official Dataset**: The official SIH field-condition dataset remains unverified and unavailable.

## Configuration
Optional external services can be configured via environment variables. See `.env.example` for available variables.
- `WEATHER_API_KEY`: (Optional) External weather service key for live mode.

## Testing
- Backend API tests: `cd backend` then `python manage.py test api`
- Frontend Build test: `cd frontend` then `npm run build` on sustainable farming practices.
6. **Farmer Assistant**: A multilingual (English/Hindi/Gujarati) assistant for farmers.
7. **FieldGuard**: An integrated risk engine combining the above modules to assess overall farm risk.

## Tech Stack
- **Backend**: Python, Django, Django REST Framework, PostgreSQL
- **Frontend**: React
- **Machine Learning**: PyTorch, torchvision, scikit-learn
- **Data & Analytics**: numpy, pandas, matplotlib, seaborn

## Setup Instructions

### Environment Setup
To set up the Python environment for the ML and backend components:

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Project Structure
- `frontend/`: React application.
- `backend/`: Django project and APIs.
- `model/`: ML model training code and architectures.
- `data/`: Datasets (raw and processed). *Note: The official held-out test set must never be placed here during training.*
- `report/`: Project reports and documentation.
