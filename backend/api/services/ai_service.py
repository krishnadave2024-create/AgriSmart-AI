import os
from google import genai
from google.genai import types
from google.genai.errors import APIError

def get_ai_config():
    """Retrieve AI configuration from environment variables."""
    return {
        'provider': os.environ.get('AI_PROVIDER', '').strip().lower(),
        'model': os.environ.get('AI_MODEL', '').strip(),
        'api_key': os.environ.get('AI_API_KEY', '').strip(),
        'timeout': int(os.environ.get('AI_REQUEST_TIMEOUT', 15))
    }

def check_health():
    """Check if the AI configuration is minimally valid (without calling the LLM)."""
    config = get_ai_config()
    
    if not config['provider'] or not config['model'] or not config['api_key'] or config['api_key'] == 'your_ai_api_key_here':
        return {
            'available': False,
            'reason': 'AI provider is not properly configured in the backend environment.',
            'provider': config['provider'] or None,
            'model': config['model'] or None
        }
        
    return {
        'available': True,
        'provider': config['provider'],
        'model': config['model']
    }

def ask_assistant(context_str, message, language='en'):
    """
    Query the configured AI provider.
    Returns: (success_bool, status_code, response_data_dict)
    """
    config = get_ai_config()
    health = check_health()
    
    if not health['available']:
        return False, 503, {
            'error': 'Farmer Assistant is not configured. Please configure the AI provider and model.',
            'model_status': 'unavailable'
        }

    system_prompt = f"""You are AgriSmart AI, a helpful and safe agricultural assistant.
Reply in the following language code: {language} (en=English, hi=Hindi, gu=Gujarati).
Use simple language suitable for farmers.
Do not prescribe exact chemical dosages unless absolutely certain based on context.
Recommend consulting a local agricultural expert for high-risk issues.
Do not pretend to be a government officer or medical professional.
Do not claim to use live IoT or satellite data.
Here is the user's verified farm context (use it only if relevant to their question):
{context_str}
"""

    if config['provider'] == 'gemini':
        try:
            client = genai.Client(api_key=config['api_key'])
            
            response = client.models.generate_content(
                model=config['model'],
                contents=message,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                )
            )
            return True, 200, {
                'answer': response.text,
                'source': 'gemini',
                'model_status': 'live'
            }
            
        except APIError as e:
            err_code = e.code if hasattr(e, 'code') else 500
            err_message = e.message if hasattr(e, 'message') else str(e)
            
            if err_code == 404 or 'not found' in err_message.lower():
                return False, 502, {
                    'error': 'The configured AI model is unavailable. Please check the provider and model configuration.',
                    'model_status': 'unavailable'
                }
            elif err_code == 429:
                return False, 429, {
                    'error': 'The AI service is temporarily busy. Please try again shortly.',
                    'model_status': 'busy',
                    'retryable': True
                }
            elif err_code in [400, 401, 403]:
                return False, 503, {
                    'error': 'Farmer Assistant is not configured correctly (Invalid API Key or permissions).',
                    'model_status': 'error'
                }
            else:
                return False, 500, {
                    'error': 'The AI service encountered an unexpected error.',
                    'model_status': 'error'
                }
                
        except Exception as e:
            err_str = str(e).lower()
            if 'timeout' in err_str:
                return False, 504, {
                    'error': 'The AI service took too long to respond. Please try again.',
                    'model_status': 'timeout',
                    'retryable': True
                }
            return False, 500, {
                'error': 'An unexpected server error occurred while contacting the AI provider.',
                'model_status': 'error'
            }
            
    else:
        return False, 503, {
            'error': f"AI Provider '{config['provider']}' is not supported.",
            'model_status': 'error'
        }
