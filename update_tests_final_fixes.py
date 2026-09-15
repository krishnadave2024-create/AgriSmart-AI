import os
with open('backend/api/tests.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix WinError 32 by ensuring file is closed
content = content.replace("self.img_file.seek(0)", "self.img_file.close()")

# Fix PredictAPITestCase to include crop_type='tomato'
content = content.replace("response = self.client.post(self.url)", "response = self.client.post(self.url, {'crop_type': 'tomato'})")
content = content.replace("response = self.client.post(self.url, {'image': f})", "response = self.client.post(self.url, {'image': f, 'crop_type': 'tomato'})")
# Fix test_unsupported_format which sends a text file
content = content.replace("response = self.client.post(self.url, {'image': f})", "response = self.client.post(self.url, {'image': f, 'crop_type': 'tomato'})")

# Fix DiseaseDetectionFinalTests authentication
from_code = """class DiseaseDetectionFinalTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('predict_disease')
        self.user = User.objects.create_user(username='test_disease_user', password='password')
        self.client.login(username='test_disease_user', password='password')"""

to_code = """from rest_framework.test import APIClient
class DiseaseDetectionFinalTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('predict_disease')
        self.user = User.objects.create_user(username='test_disease_user', password='password')
        self.client.force_authenticate(user=self.user)"""

content = content.replace(from_code, to_code)

with open('backend/api/tests.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("tests.py updated.")
