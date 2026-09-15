# 🌱 AgriSmart AI

## Intelligent Agriculture for a Sustainable Future

> **Smart Farming • Better Decisions**

AgriSmart AI is an AI-powered agricultural decision-support platform
designed to help farmers make better, faster, and more sustainable
farming decisions.

The platform brings important agricultural tools into one
farmer-friendly application, including:

-   AI-powered crop disease detection
-   Agricultural recommendations
-   Smart irrigation guidance
-   Weather intelligence
-   Sustainability insights
-   Field-risk monitoring
-   AI-powered Farmer Assistant
-   Farm dashboard and recent scan history

AgriSmart AI is being developed as a software solution for the **Smart
India Hackathon 2026**.

------------------------------------------------------------------------

## 📌 Table of Contents

-   [Problem Statement](#-problem-statement)
-   [Our Solution](#-our-solution)
-   [Objectives](#-objectives)
-   [Key Features](#-key-features)
-   [System Architecture](#-system-architecture)
-   [Technology Stack](#-technology-stack)
-   [AI Disease Detection](#-ai-disease-detection)
-   [Farmer Assistant](#-farmer-assistant)
-   [Explainable AI](#-explainable-ai)
-   [Sustainability Focus](#-sustainability-focus)
-   [Project Structure](#-project-structure)
-   [Dataset and Model](#-dataset-and-model)
-   [Installation](#-installation)
-   [Running the Application](#-running-the-application)
-   [API Overview](#-api-overview)
-   [Model Training](#-model-training)
-   [Current Limitations](#-current-limitations)
-   [Future Scope](#-future-scope)
-   [Contributing](#-contributing)
-   [License](#-license)

------------------------------------------------------------------------

## 🚜 Problem Statement

Farmers regularly face challenges that directly affect crop
productivity, income, and sustainability:

-   Crop diseases are often identified too late.
-   Agricultural expertise may not be easily accessible.
-   Weather conditions can make farming decisions uncertain.
-   Irrigation is sometimes based on guesswork.
-   Excessive water and agricultural-input usage increases costs.
-   Technical agricultural platforms can be difficult to understand.
-   Farmers may receive information from multiple disconnected sources.

There is a need for a unified, accessible, and explainable agricultural
platform that supports practical day-to-day farming decisions.

------------------------------------------------------------------------

## 💡 Our Solution

AgriSmart AI combines agricultural intelligence and machine learning
into a single digital platform.

A farmer can use the platform to:

1.  Upload a crop or plant-leaf image.
2.  Receive an AI-based disease prediction.
3.  Understand the detected disease and its possible symptoms.
4.  View prevention and management guidance.
5.  Ask agriculture-related questions in natural language.
6.  Review farm information and recent scans.
7.  Explore irrigation, weather, crop, and sustainability insights.
8.  Make more informed decisions using understandable explanations.

The application is designed for Indian farmers and is planned to support
**English, Hindi, and Gujarati**.

------------------------------------------------------------------------

## 🎯 Objectives

The main objectives of AgriSmart AI are to:

-   Encourage early crop-disease identification.
-   Make agricultural information easier to access.
-   Reduce avoidable water wastage.
-   Support sustainable farming practices.
-   Provide simple and understandable AI recommendations.
-   Improve farmer decision-making through contextual information.
-   Combine multiple agricultural utilities in one platform.
-   Build a foundation for future multilingual and regional agricultural
    services.

------------------------------------------------------------------------

## ✨ Key Features

### 🔬 1. AI-Powered Disease Detection

The Disease Detection module allows users to upload a plant or crop-leaf
image for analysis.

Main capabilities include:

-   Image upload and preview
-   Crop selection
-   AI-based disease classification
-   Prediction confidence
-   Crop and disease information
-   Disease description
-   Prevention guidance
-   Management recommendations
-   Recent scan history
-   Disease analytics based on available scan records

The system is designed to avoid displaying fabricated predictions. If
the trained model or required configuration is unavailable, the backend
should return an appropriate error instead of generating a fake result.

> **Important:** The current model is a development model trained on a
> PlantVillage-based dataset. Performance on controlled dataset images
> may differ from performance on real field images.

------------------------------------------------------------------------

### 🌾 2. Crop Recommendation

The Crop Recommendation module is intended to support crop-selection
decisions using information such as:

-   Crop type
-   Soil characteristics
-   Seasonal conditions
-   Weather information
-   Water availability
-   Farming objectives
-   Sustainability considerations

The recommendation process is designed to become more useful as reliable
local agricultural and farm data are integrated.

------------------------------------------------------------------------

### 💧 3. Smart Irrigation

The Smart Irrigation module focuses on better water-management
decisions.

Planned and supported concepts include:

-   Avoiding unnecessary irrigation
-   Reducing overwatering
-   Considering crop growth stages
-   Understanding soil-moisture requirements
-   Supporting efficient water usage
-   Providing reasons behind irrigation suggestions

The current project does not depend on physical IoT devices. Sensor
integration may be considered as a future enhancement.

------------------------------------------------------------------------

### 🌦️ 4. Weather Intelligence

Weather Intelligence is intended to help farmers understand weather
conditions that may affect farming activities.

Possible information includes:

-   Temperature
-   Humidity
-   Rainfall probability
-   Weather conditions
-   Weather-related crop risks
-   Irrigation planning support
-   Disease-risk context

------------------------------------------------------------------------

### 🛡️ 5. FieldGuard

FieldGuard is an agricultural risk-monitoring concept designed to
present farm risks in a simple and understandable way.

Potential risk indicators include:

-   Foliar disease risk
-   Moisture-related risk
-   Microclimate conditions
-   Crop growth stage
-   Weather-related threats
-   Recent crop-health information

The feature is intended to help farmers identify risks early and take
preventive action.

------------------------------------------------------------------------

### 🤖 6. Farmer Assistant

The Farmer Assistant provides agriculture-focused conversational
guidance using a configured AI provider.

Farmers can ask questions such as:

-   How can I prevent fungal diseases in tomato plants?
-   When should I irrigate my crop?
-   How can I improve soil health?
-   What should I do if my plant leaves turn yellow?
-   Which crop is suitable for the current season?
-   How can I reduce water wastage?
-   How can I manage common crop diseases?

The assistant is designed to provide:

-   Natural-language responses
-   Context-aware agricultural guidance
-   Simple explanations
-   Practical suggestions
-   Safety-conscious recommendations
-   Future multilingual support

The current implementation uses a configurable AI service so that the
provider and model can be changed without redesigning the entire
application.

> AI-generated guidance should be verified with a qualified local
> agricultural expert before making high-impact farming decisions.

------------------------------------------------------------------------

### 📊 7. Farmer Dashboard

The dashboard provides a central overview of important farm information.

It may include:

-   Crop health indicators
-   Disease-risk information
-   Soil-moisture indicators
-   Weather summary
-   Sustainability metrics
-   Recent disease scans
-   Quick-access feature cards
-   Farm and plot information

The dashboard is designed with a clean, farmer-friendly interface rather
than a complex technical administration panel.

------------------------------------------------------------------------

### ♻️ 8. Sustainability Insights

AgriSmart AI follows a sustainability-focused design approach.

Recommendations may include understandable impact indicators such as:

-   Estimated water conserved in litres
-   Estimated electricity saved in kWh
-   Estimated financial savings in ₹
-   Reduced unnecessary input usage
-   Improved resource efficiency

All estimated values should be clearly labelled as estimates unless they
are calculated from verified field measurements.

------------------------------------------------------------------------

## 🧠 Explainable AI

AgriSmart AI is built around the principle:

> **Every important AI recommendation should explain why it was
> suggested.**

Instead of showing only a prediction or recommendation, the platform
aims to communicate:

-   What was detected
-   Why it may matter
-   What action can be considered
-   What conditions may increase the risk
-   What the farmer should monitor
-   What environmental or financial benefit may be possible

This approach improves transparency and helps farmers make informed
decisions instead of blindly trusting an AI output.

------------------------------------------------------------------------

## 🏗️ System Architecture

``` text
                         ┌──────────────────────┐
                         │      Farmer/User     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   React Frontend     │
                         │ Dashboard and UI     │
                         └──────────┬───────────┘
                                    │ REST API
                                    ▼
                         ┌──────────────────────┐
                         │   Django Backend     │
                         │ Auth and API Layer   │
                         └───────┬───────┬──────┘
                                 │       │
                    ┌────────────▼─┐   ┌─▼────────────────┐
                    │ Disease AI   │   │ Farmer Assistant  │
                    │ PyTorch CNN  │   │ Configurable AI   │
                    └──────────────┘   └──────────────────┘
                                 │       │
                                 ▼       ▼
                         ┌──────────────────────┐
                         │ Data and Model Files │
                         │ Datasets and Records  │
                         └──────────────────────┘
```

------------------------------------------------------------------------

## 🛠️ Technology Stack

### Frontend

-   React
-   JavaScript
-   Tailwind CSS
-   Lucide Icons
-   Responsive component-based UI
-   REST API integration

### Backend

-   Python
-   Django
-   Django REST Framework
-   Django CORS Headers
-   Environment-based configuration

### Machine Learning

-   PyTorch
-   Torchvision
-   ResNet18
-   Image preprocessing and classification
-   CSV-based dataset manifests

### AI Assistant

-   Google Gemini API
-   `google-genai` SDK
-   Configurable provider and model settings

### Development Tools

-   Google Colab
-   Git and GitHub
-   Visual Studio Code or Antigravity
-   Browser Developer Tools

------------------------------------------------------------------------

## 📁 Project Structure

``` text
AgriSmart-AI/
│
├── backend/
│   ├── api/
│   │   ├── services/
│   │   │   └── ai_service.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── ...
│   │
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── ...
│   │
│   ├── .env
│   ├── manage.py
│   └── AI_SETUP.md
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── ...
│   ├── package.json
│   └── ...
│
├── data/
│   ├── external/
│   ├── manifests/
│   ├── reports/
│   └── README.md
│
├── model/
│   ├── dataset.py
│   ├── train.py
│   ├── evaluate.py
│   ├── predict.py
│   └── checkpoints/
│
├── docs/
│   └── DISEASE_PREDICTION_API.md
│
├── requirements.txt
├── task.md
└── README.md
```

------------------------------------------------------------------------

## 🧪 Dataset and Model

### Development Dataset

The current development model uses a cleaned PlantVillage-based dataset.

The dataset preparation process includes:

-   Image inspection
-   Duplicate detection
-   Manifest generation
-   Train/validation/test splitting
-   Image-path validation
-   Class-label verification
-   Image preprocessing

The dataset contains **38 disease and healthy-leaf classes** in the
current development setup.

### Model

The current disease-classification model is based on:

-   ResNet18 architecture
-   Transfer learning
-   Image resizing and normalization
-   Multi-class classification
-   PyTorch inference

The trained checkpoint is stored under:

``` text
model/checkpoints/baseline_resnet18.pth
```

### Model Evaluation

The development training run achieved approximately **93.28% validation
accuracy after two epochs** on the prepared validation split.

This result should not be interpreted as real-world field accuracy.
Further testing with diverse field images, lighting conditions,
backgrounds, camera devices, and regional crop varieties is required.

------------------------------------------------------------------------

## ⚙️ Installation

### 1. Clone the Repository

``` bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd AgriSmart-AI
```

### 2. Create a Python Virtual Environment

``` bash
python -m venv venv
```

Activate it on Windows:

``` powershell
venv\Scripts\activate
```

Activate it on Linux or macOS:

``` bash
source venv/bin/activate
```

### 3. Install Backend Dependencies

``` bash
pip install -r requirements.txt
```

If required, install the main backend packages:

``` bash
pip install django djangorestframework django-cors-headers python-dotenv google-genai torch torchvision pillow
```

### 4. Configure Environment Variables

Create or update:

``` text
backend/.env
```

Example:

``` env
SECRET_KEY=your-django-secret-key
DEBUG=True
AI_PROVIDER=gemini
AI_API_KEY=your-gemini-api-key
AI_MODEL=gemini-2.5-flash
```

Never commit real API keys or passwords to GitHub.

### 5. Install Frontend Dependencies

``` bash
cd frontend
npm install
```

------------------------------------------------------------------------

## ▶️ Running the Application

### Start the Django Backend

Open a terminal:

``` bash
cd backend
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

The backend will be available at:

``` text
http://127.0.0.1:8000
```

### Start the React Frontend

Open another terminal:

``` bash
cd frontend
npm run dev
```

The frontend will normally be available at:

``` text
http://localhost:5173
```

Open the application in a browser and log in before using protected
features.

------------------------------------------------------------------------

## 🔌 API Overview

The exact routes may change as development continues. Current API
functionality includes:

  Feature                      Method Endpoint
  -------------------------- -------- ---------------------------
  Backend health check            GET `/api/health/`
  Disease prediction             POST `/api/predict/`
  Farmer Assistant health         GET `/api/assistant/health/`
  Farmer Assistant message       POST `/api/assistant/message/`

### Farmer Assistant Request Example

``` json
{
  "message": "How can I prevent fungal diseases in tomato plants?"
}
```

The request must use the authentication method configured by the
application.

### Important API Practices

-   Validate incoming data.
-   Require authentication for protected routes.
-   Never expose API keys.
-   Return consistent JSON responses.
-   Handle provider failures safely.
-   Do not return fake predictions or fake AI responses.
-   Use appropriate HTTP status codes.
-   Log only safe diagnostic information.

------------------------------------------------------------------------

## 🧠 Model Training

The model-training workflow is designed to run locally or in Google
Colab.

Typical steps include:

1.  Prepare the dataset.
2.  Inspect image paths and labels.
3.  Remove invalid or duplicate records.
4.  Generate train, validation, and test manifests.
5.  Create PyTorch data loaders.
6.  Train the ResNet18 model.
7.  Evaluate the model.
8.  Save the checkpoint.
9.  Copy the verified checkpoint into:

``` text
model/checkpoints/baseline_resnet18.pth
```

Before using the checkpoint in the Django API, verify that it matches
the expected number of classes and model architecture.

------------------------------------------------------------------------

## 🔐 Security Considerations

-   Keep `.env` files private.
-   Do not commit API keys.
-   Do not expose authentication tokens in logs.
-   Validate uploaded image types and file sizes.
-   Do not trust client-side crop or disease labels.
-   Use server-side validation for model inputs.
-   Avoid presenting uncertain predictions as confirmed diagnoses.
-   Verify high-impact agricultural recommendations with experts.
-   Configure CORS and allowed hosts correctly before deployment.

------------------------------------------------------------------------

## ⚠️ Current Limitations

The current development version has several limitations:

-   The model is trained on a controlled development dataset.
-   Field-image performance has not yet been fully validated.
-   The official SIH held-out dataset has not been verified or
    integrated.
-   Some features use mock or demonstration data.
-   Weather and sustainability outputs may require reliable external
    data sources.
-   Disease detection may be sensitive to image quality and lighting.
-   AI Assistant responses depend on provider availability, model
    availability, network connectivity, and API configuration.
-   IoT sensor integration is not currently included.
-   Multilingual support may be expanded in later versions.

------------------------------------------------------------------------

## 🚀 Future Scope

Planned improvements include:

-   Evaluation using real field images
-   Integration of the official SIH dataset when available
-   Improved model accuracy and calibration
-   Explainable disease-localization techniques
-   More crop and disease classes
-   Regional-language support
-   Voice-based Farmer Assistant
-   Offline or low-connectivity support
-   Reliable weather and agricultural data integration
-   Personalized farm profiles
-   Better irrigation recommendations
-   Regional crop calendars
-   Expert consultation workflows
-   Farmer feedback and model-improvement loops
-   Optional IoT and sensor integration
-   Deployment on scalable cloud infrastructure

------------------------------------------------------------------------

## 🌍 Impact

AgriSmart AI aims to contribute to:

-   Earlier disease awareness
-   Better access to agricultural information
-   Reduced avoidable resource consumption
-   More informed farm-management decisions
-   Improved digital access for farmers
-   Sustainable and technology-enabled agriculture

The long-term goal is to make agricultural intelligence more accessible,
understandable, and useful for farmers.

------------------------------------------------------------------------

## 🤝 Contributing

Contributions are welcome.

To contribute:

1.  Fork the repository.
2.  Create a feature branch.

``` bash
git checkout -b feature/your-feature-name
```

3.  Make your changes.
4.  Test the changes locally.
5.  Commit your work.

``` bash
git commit -m "Add meaningful feature"
```

6.  Push the branch.

``` bash
git push origin feature/your-feature-name
```

7.  Open a pull request.

Please keep contributions focused, documented, tested, and consistent
with the project architecture.

------------------------------------------------------------------------

## 📄 License

Add the appropriate project license before public distribution.

If a license has not yet been selected, the project should not be
assumed to be freely reusable or redistributable.

------------------------------------------------------------------------

## 👥 Project

**Project Name:** AgriSmart AI\
**Tagline:** Smart Farming • Better Decisions\
**Event:** Smart India Hackathon 2026\
**Domain:** Artificial Intelligence, Agriculture, Sustainable Technology

------------------------------------------------------------------------

## ⭐ Acknowledgement

AgriSmart AI uses open-source technologies and development datasets to
explore the application of artificial intelligence in agriculture.

The project is intended to support farmers and agricultural stakeholders
through accessible, explainable, and sustainability-focused digital
tools.
