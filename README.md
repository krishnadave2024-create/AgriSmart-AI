# 🌱 AgriSmart AI

### Intelligent Agriculture for a Sustainable Future

> **Smart Farming • Better Decisions**

```{=html}
<p align="center">
```
`<a href="https://drive.google.com/file/d/1HlXGWUtpl7usZgeoltVGg5c7qiq0_Kg7/view?usp=sharing">`{=html}
🎥 Watch the Project Screen Recording `</a>`{=html}
```{=html}
</p>
```
AgriSmart AI is an AI-powered agricultural decision-support platform
designed to help Indian farmers make informed, efficient, and
sustainable farming decisions.

The platform brings crop disease detection, agricultural guidance,
irrigation support, weather intelligence, sustainability insights,
farm-risk monitoring, and an AI-powered Farmer Assistant into one
unified, farmer-friendly application.

This project is being developed as a software solution for **Smart India
Hackathon 2026**.

------------------------------------------------------------------------

## 🎥 Project Demonstration

A complete screen recording of the project is available here:

### [▶️ Watch AgriSmart AI --- Project Demo](https://drive.google.com/file/d/1HlXGWUtpl7usZgeoltVGg5c7qiq0_Kg7/view?usp=sharing)

The recording demonstrates the application interface and its major
agricultural modules.

> **Access note:** Set the Google Drive file permission to **Anyone with
> the link → Viewer** so evaluators can open the recording.

------------------------------------------------------------------------

## 📌 Contents

-   [Problem Statement](#-problem-statement)
-   [Proposed Solution](#-proposed-solution)
-   [Objectives](#-objectives)
-   [Features](#-features)
-   [Explainable AI](#-explainable-ai)
-   [System Architecture](#-system-architecture)
-   [Technology Stack](#-technology-stack)
-   [Project Structure](#-project-structure)
-   [Dataset and Model](#-dataset-and-model)
-   [Installation](#-installation)
-   [Running the Project](#-running-the-project)
-   [API Overview](#-api-overview)
-   [Security and Privacy](#-security-and-privacy)
-   [Current Limitations](#-current-limitations)
-   [Future Scope](#-future-scope)
-   [Contributing](#-contributing)
-   [Project Information](#-project-information)

------------------------------------------------------------------------

## 🚜 Problem Statement

Farmers face several challenges that can affect productivity, income,
and resource efficiency:

-   Crop diseases are often detected too late.
-   Agricultural expertise may not be easily accessible.
-   Weather conditions make farm decisions uncertain.
-   Irrigation is frequently based on estimation or habit.
-   Excessive water and agricultural-input usage increases costs.
-   Agricultural information is distributed across disconnected
    platforms.
-   Technical applications may be difficult for farmers to understand.
-   Farmers need timely, localized, and practical guidance.

A unified, accessible, and explainable agricultural platform can help
farmers make better day-to-day decisions.

------------------------------------------------------------------------

## 💡 Proposed Solution

AgriSmart AI combines artificial intelligence, machine learning, and
agricultural decision-support features in one platform.

The platform allows a farmer to:

1.  Upload a crop or plant-leaf image.
2.  Receive an AI-based disease prediction.
3.  View disease details, symptoms, prevention, and management guidance.
4.  Ask agriculture-related questions in natural language.
5.  Review farm information and recent disease scans.
6.  Explore crop, irrigation, weather, and sustainability insights.
7.  Understand why a recommendation was made.
8.  Make more informed and resource-efficient decisions.

The interface is designed for accessibility and future support for
**English, Hindi, and Gujarati**.

------------------------------------------------------------------------

## 🎯 Objectives

-   Encourage early crop-disease identification.
-   Improve access to agricultural knowledge.
-   Support informed farm-management decisions.
-   Reduce avoidable water wastage.
-   Promote sustainable farming practices.
-   Provide explainable AI recommendations.
-   Combine agricultural utilities in one application.
-   Improve access to digital agricultural services.
-   Create a foundation for localized and multilingual support.

------------------------------------------------------------------------

## ✨ Features

### 🔬 AI-Powered Disease Detection

The Disease Detection module enables users to upload plant or crop-leaf
images for analysis.

**Capabilities include:**

-   Image upload and preview
-   Crop selection
-   AI-based disease classification
-   Prediction confidence score
-   Crop and disease identification
-   Disease description
-   Disease prevention details
-   Management recommendations
-   Recent scan history
-   Disease analytics from available scan records
-   Safe handling when the model or checkpoint is unavailable

The backend is designed not to generate fabricated predictions. If the
model is unavailable or incompatible, the system should return a clear
error.

> The current model is a development model trained using a
> PlantVillage-based dataset. Controlled-dataset performance may differ
> from real field performance.

### 🌾 Crop Recommendation

The Crop Recommendation module is designed to support crop-selection
decisions using factors such as:

-   Soil characteristics
-   Seasonal conditions
-   Weather information
-   Water availability
-   Crop type
-   Farming objectives
-   Sustainability requirements
-   Regional agricultural conditions

### 💧 Smart Irrigation

The Smart Irrigation module focuses on efficient water management.

It is designed to support:

-   Avoidance of unnecessary irrigation
-   Reduction of overwatering
-   Understanding of crop water requirements
-   Consideration of crop growth stages
-   Better water-use efficiency
-   Explainable irrigation suggestions

The current project does not depend on physical IoT devices. Optional
sensor integration may be considered in the future.

### 🌦️ Weather Intelligence

The Weather Intelligence module is intended to help farmers understand
conditions that may affect agricultural activities, including:

-   Temperature
-   Humidity
-   Rainfall probability
-   Current weather conditions
-   Weather-related crop risks
-   Irrigation planning
-   Disease-risk context

### 🛡️ FieldGuard

FieldGuard is an agricultural risk-monitoring concept that presents
potential farm risks in a simple format.

Potential indicators include:

-   Foliar disease risk
-   Moisture-related risk
-   Microclimate conditions
-   Crop growth stage
-   Weather-related threats
-   Recent crop-health information

### 🤖 Farmer Assistant

The Farmer Assistant provides agriculture-focused conversational
guidance through a configurable AI provider.

Example questions include:

-   How can I prevent fungal diseases in tomato plants?
-   When should I irrigate my crop?
-   How can I improve soil health?
-   What should I do if my plant leaves turn yellow?
-   Which crop is suitable for the current season?
-   How can I reduce water wastage?
-   How can I manage common crop diseases?

**Assistant capabilities:**

-   Natural-language interaction
-   Agriculture-focused answers
-   Context-aware guidance
-   Simple explanations
-   Practical suggestions
-   Safety-conscious recommendations
-   Configurable provider and model
-   React-to-Django API communication

### 📊 Farmer Dashboard

The dashboard provides a centralized overview of farm information, such
as:

-   Crop-health indicators
-   Disease-risk information
-   Soil-moisture information
-   Weather summary
-   Sustainability metrics
-   Recent disease scans
-   Farm and plot details
-   Quick-access feature cards

### ♻️ Sustainability Insights

The platform can present understandable impact indicators such as:

-   Estimated water conserved in litres
-   Estimated electricity saved in kWh
-   Estimated financial savings in ₹
-   Reduced unnecessary input usage
-   Improved resource efficiency

Values that are not calculated from verified field measurements must be
clearly labelled as estimates.

------------------------------------------------------------------------

## 🧠 Explainable AI

AgriSmart AI follows the principle:

> **Every important AI recommendation should explain why it was
> suggested.**

The platform aims to communicate:

-   What was detected
-   Why the result may matter
-   What action can be considered
-   Which conditions may increase risk
-   What the farmer should monitor
-   What environmental benefit may be possible
-   What financial benefit may be possible
-   What uncertainty or limitation exists

This approach helps farmers understand recommendations instead of
blindly following them.

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
                         │ Authentication/API   │
                         └──────────┬───────────┘
                                    │
                   ┌────────────────┴────────────────┐
                   │                                 │
                   ▼                                 ▼
        ┌──────────────────────┐        ┌──────────────────────┐
        │ Disease Detection   │        │ Farmer Assistant      │
        │ PyTorch ResNet18     │        │ Gemini AI Service     │
        └──────────┬───────────┘        └──────────┬───────────┘
                   │                               │
                   └────────────────┬──────────────┘
                                    ▼
                         ┌──────────────────────┐
                         │ Data and Model Files │
                         │ Datasets and Records │
                         └──────────────────────┘
```

------------------------------------------------------------------------

## 🛠️ Technology Stack

  Layer              Technologies
  ------------------ -----------------------------------------------
  Frontend           React, JavaScript, Tailwind CSS, Lucide Icons
  Backend            Python, Django, Django REST Framework
  Machine Learning   PyTorch, Torchvision, ResNet18, Pillow
  AI Assistant       Google Gemini API, `google-genai` SDK
  Data Processing    Python, CSV manifests, image preprocessing
  Development        Google Colab, Git, GitHub, Antigravity
  Communication      REST APIs

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
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── ...
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

### Dataset

The current development model uses a cleaned PlantVillage-based dataset.

The preparation workflow includes:

-   Image inspection
-   Invalid-image checking
-   Duplicate detection
-   Image-path validation
-   Manifest generation
-   Train/validation/test splitting
-   Class-label verification
-   Image preprocessing

The current development setup contains **38 disease and healthy-leaf
classes**.

### Model

The disease-classification model uses:

-   ResNet18
-   Transfer learning
-   PyTorch
-   Torchvision
-   Image resizing and normalization
-   Multi-class classification

The trained checkpoint is expected at:

``` text
model/checkpoints/baseline_resnet18.pth
```

### Development Result

A development training run achieved approximately **93.28% validation
accuracy after two epochs** on the prepared validation split.

This is not a guarantee of real-world field accuracy. Further evaluation
is required using field images, different lighting conditions, complex
backgrounds, different cameras, crop varieties, and disease stages.

> The official SIH held-out dataset has not yet been verified or
> integrated into the current development workflow.

------------------------------------------------------------------------

## ⚙️ Installation

### 1. Clone the Repository

``` bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd AgriSmart-AI
```

### 2. Create a Virtual Environment

``` bash
python -m venv venv
```

**Windows:**

``` powershell
venv\Scripts\activate
```

**Linux/macOS:**

``` bash
source venv/bin/activate
```

### 3. Install Backend Dependencies

``` bash
pip install -r requirements.txt
```

If required:

``` bash
pip install django djangorestframework django-cors-headers python-dotenv google-genai torch torchvision pillow
```

### 4. Configure Environment Variables

Create:

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

Never commit real API keys, passwords, tokens, or secrets.

### 5. Install Frontend Dependencies

``` bash
cd frontend
npm install
```

------------------------------------------------------------------------

## ▶️ Running the Project

### Start the Django Backend

``` bash
cd backend
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

Backend URL:

``` text
http://127.0.0.1:8000
```

### Start the React Frontend

Open another terminal:

``` bash
cd frontend
npm run dev
```

Frontend URL:

``` text
http://localhost:5173
```

Log in before using protected features.

------------------------------------------------------------------------

## 🔌 API Overview

  Feature                      Method Endpoint
  -------------------------- -------- ---------------------------
  Backend health check          `GET` `/api/health/`
  Disease prediction           `POST` `/api/predict/`
  Farmer Assistant health       `GET` `/api/assistant/health/`
  Farmer Assistant message     `POST` `/api/assistant/message/`

### Farmer Assistant Request

``` json
{
  "message": "How can I prevent fungal diseases in tomato plants?"
}
```

Protected endpoints must use the authentication method configured by the
application.

### API Principles

-   Validate all incoming data.
-   Require authentication for protected routes.
-   Never expose API keys.
-   Return consistent JSON responses.
-   Handle provider failures safely.
-   Use appropriate HTTP status codes.
-   Do not return fake predictions or fake AI responses.
-   Validate uploaded files on the server.

------------------------------------------------------------------------

## 🔐 Security and Privacy

-   Keep `.env` files private.
-   Do not commit API keys.
-   Do not expose JWT tokens or session cookies.
-   Validate uploaded file types and sizes.
-   Validate user input on the server.
-   Configure CORS carefully.
-   Configure allowed hosts before deployment.
-   Avoid logging sensitive information.
-   Do not present uncertain predictions as confirmed diagnoses.
-   Verify high-impact agricultural advice with qualified experts.

------------------------------------------------------------------------

## ⚠️ Current Limitations

-   The disease model is trained on a controlled development dataset.
-   Real-world field-image performance requires additional validation.
-   The official SIH held-out dataset has not been verified or
    integrated.
-   Some modules may use mock or demonstration data.
-   Weather features may require reliable external data sources.
-   Sustainability values may be estimates.
-   Disease predictions may be affected by image quality, lighting,
    background, and camera type.
-   Farmer Assistant responses depend on API configuration, network
    connectivity, provider availability, and model availability.
-   Multilingual support is planned for further development.
-   IoT sensor integration is not currently included.

------------------------------------------------------------------------

## 🚀 Future Scope

-   Evaluation using real field images
-   Integration of the official SIH dataset
-   Improved model accuracy and confidence calibration
-   Explainable disease-localization techniques
-   Additional crops and disease classes
-   English, Hindi, and Gujarati language support
-   Voice-based Farmer Assistant
-   Offline and low-connectivity support
-   Reliable weather-data integration
-   Personalized farmer profiles
-   Regional crop calendars
-   Improved irrigation recommendations
-   Expert consultation workflows
-   Farmer feedback and model-improvement loops
-   Optional IoT and sensor integration
-   Cloud deployment and scalable infrastructure

------------------------------------------------------------------------

## 🌍 Expected Impact

AgriSmart AI aims to support:

-   Earlier awareness of crop diseases
-   Better access to agricultural information
-   More informed farm-management decisions
-   Reduced avoidable water consumption
-   Better resource efficiency
-   Sustainable farming practices
-   Improved access to digital agricultural services
-   More transparent and understandable AI recommendations

The long-term vision is to make agricultural intelligence accessible,
explainable, and useful for farmers across India.

------------------------------------------------------------------------

## 🤝 Contributing

1.  Fork the repository.
2.  Create a feature branch:

``` bash
git checkout -b feature/your-feature-name
```

3.  Make and test your changes.
4.  Commit your work:

``` bash
git commit -m "Add meaningful feature"
```

5.  Push the branch:

``` bash
git push origin feature/your-feature-name
```

6.  Open a pull request.

Please keep contributions focused, tested, documented, secure, and
consistent with the existing architecture.

------------------------------------------------------------------------

## 📄 License

Add an appropriate license before public distribution.

Until a license is added, the project should not be assumed to be freely
reusable, modified, or redistributed.

------------------------------------------------------------------------

## 👥 Project Information

  Field               Details
  ------------------- --------------------------------------------------------
  Project Name        AgriSmart AI
  Tagline             Smart Farming • Better Decisions
  Event               Smart India Hackathon 2026
  Domain              Artificial Intelligence and Agriculture
  Focus Areas         Crop Health, Sustainability, Agricultural Intelligence
  Frontend            React
  Backend             Django and Django REST Framework
  Disease Model       PyTorch ResNet18
  AI Assistant        Google Gemini API
  Development Tools   Google Colab, GitHub, Antigravity

------------------------------------------------------------------------

## 🙏 Acknowledgements

AgriSmart AI uses open-source technologies, machine-learning frameworks,
and development datasets to explore the application of artificial
intelligence in agriculture.

The project is intended to support farmers and agricultural stakeholders
through accessible, explainable, and sustainability-focused digital
tools.

------------------------------------------------------------------------

```{=html}
<p align="center">
```
`<strong>`{=html}🌱 AgriSmart AI --- Smart Farming • Better
Decisions`</strong>`{=html}
```{=html}
</p>
```
