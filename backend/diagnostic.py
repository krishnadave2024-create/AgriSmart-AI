import os
import sys
import django
import time

# Add the project directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

print("Django settings: OK")
print(f"Environment file loaded: {os.environ.get('SECRET_KEY') is not None}")

from api.services.ai_service import get_ai_config
config = get_ai_config()

print(f"Provider: {config['provider']}")
is_configured = config['api_key'] not in ['', 'your_gemini_api_key_here', 'your_ai_api_key_here', 'your_key_here']
print(f"API key configured: {is_configured}")
if is_configured:
    print(f"API key length: {len(config['api_key'])}")
print(f"Model configured: {bool(config['model'])}")
print(f"Model: {config['model']}")

if not is_configured:
    print("Failure: Missing API key")
    sys.exit(1)

if config['provider'] != 'gemini':
    print("Failure: Provider not supported")
    sys.exit(1)

try:
    from google import genai
    from google.genai import types
    from google.genai.errors import APIError
    
    client = genai.Client(api_key=config['api_key'])
    print("Gemini client: OK")
    
    start = time.time()
    
    print("Listing available models...")
    for m in client.models.list():
        if 'gemini' in m.name.lower():
            print(f" - {m.name}")
            
    response = client.models.generate_content(
        model=config['model'],
        contents="Reply with exactly: AgriSmart connection successful",
    )
    duration = time.time() - start
    
    print(f"Real Gemini request: SUCCESS ({duration:.2f}s)")
    print(f"Response: {response.text.strip()}")
    
    
except ImportError as e:
    print(f"Failure: SDK compatibility error - {e}")
except APIError as e:
    err_code = e.code if hasattr(e, 'code') else getattr(e, 'status_code', 500)
    err_message = e.message if hasattr(e, 'message') else str(e)
    
    print(f"APIError caught. Code: {err_code}, Message: {err_message}")
    if err_code == 404 or 'not found' in err_message.lower():
        print("Failure: Invalid model")
    elif err_code == 429:
        print("Failure: Rate limited")
    elif err_code in [400, 401, 403]:
        print("Failure: Invalid API key or Permission denied")
    else:
        print(f"Failure: Unexpected API error - {e}")
except Exception as e:
    err_str = str(e).lower()
    if 'timeout' in err_str:
        print("Failure: Timeout")
    else:
        print(f"Failure: Network error or unexpected exception - {e}")
