import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch, MagicMock

User = get_user_model()
user, created = User.objects.get_or_create(username='aitester4')
if created:
    user.set_password('pw')
    user.save()

# Manually execute the function logic to see the error
from api.views import farmer_assistant
from django.test import RequestFactory
import json

factory = RequestFactory()
request = factory.post('/api/assistant/message/', json.dumps({'message': 'hello', 'language': 'en'}), content_type='application/json')
request.user = user

with patch('api.views.os.environ.get') as mock_env_get, patch('api.views.genai.GenerativeModel') as mock_generative_model_cls:
    mock_env_get.return_value = 'dummy_key'
    
    mock_model_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.text = 'Mocked response'
    mock_model_instance.generate_content.return_value = mock_response
    mock_generative_model_cls.return_value = mock_model_instance
    
    response = farmer_assistant(request)
    print("STATUS:", response.status_code)
    print("DATA:", response.data)
