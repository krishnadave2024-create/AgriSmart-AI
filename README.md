# AGRISMART AI
Intelligent Agriculture for a Sustainable Future

## Project Overview
AgriSmart AI is a production-quality agricultural decision-support platform designed to help farmers with crucial, data-driven decisions. The platform leverages modern machine learning and a robust web architecture to deliver accurate, localized insights.

## Dataset Information
- **Development Dataset**: `ayerr/plant-disease-classification` (Hugging Face)
- **Status**: Development and prototyping only. **The official SIH field-condition dataset remains unverified and unavailable.**
- **Preparation**: Run `python extract_ayerr_subset.py` followed by `python inspect_development_dataset.py` and `python create_development_manifest.py`.
- **Storage**: Downloaded images are stored locally in `data/external/development_dataset/raw/`. They are excluded from version control to save space.
- The official test set must be evaluated separately when provided.

## Planned Modules
1. **Crop Disease Detection (Core)**: A computer vision model to classify crop diseases from leaf imagery.
2. **Crop Recommendation**: ML-based recommendations on which crops to plant based on soil and environmental factors.
3. **Smart Irrigation**: Predictive modeling to suggest optimal irrigation schedules.
4. **Weather-Based Intelligence**: Forecasting and weather-driven insights.
5. **Sustainability Score**: Metrics and advice on sustainable farming practices.
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
