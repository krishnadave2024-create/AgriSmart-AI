# AgriSmart AI - AI Setup Guide

AgriSmart AI's Farmer Assistant uses an artificial intelligence model to provide contextual agricultural advice to farmers based on their history.

## Configured Provider
By default, the backend is configured to use the **Google Gemini** provider.

## Required Environment Variables
To enable the AI Assistant, you must configure the following variables in the `backend/.env` file:

```env
AI_PROVIDER=gemini
AI_MODEL=gemini-1.5-flash
AI_API_KEY=your_gemini_api_key_here
AI_REQUEST_TIMEOUT=15
```

### Steps to configure:
1. Locate the `backend/.env` file in the root of the Django backend directory. If it doesn't exist, copy `backend/.env.example` to `backend/.env`.
2. Replace `your_gemini_api_key_here` with a real Google Gemini API Key from Google AI Studio.
3. Restart the Django development server:
   ```bash
   python manage.py runserver
   ```
4. Visit the **Farmer Assistant** page in the frontend to verify that the badge shows `ONLINE`.

## Troubleshooting
- **Badge says OFFLINE**: The backend did not find the `AI_API_KEY`, or it is invalid.
- **Model Unavailable Error**: The `AI_MODEL` specified is misspelled or deprecated. We recommend using `gemini-1.5-flash` for high speed and contextual understanding.
- **Timeouts**: If you frequently experience timeouts, increase the `AI_REQUEST_TIMEOUT` value in `.env`.

## Modifying the Provider later
Currently, only `gemini` is supported by the `ai_service.py` module. To add a new provider like OpenAI or Anthropic, you will need to extend `backend/api/services/ai_service.py` and map it to `AI_PROVIDER=openai` or similar.
