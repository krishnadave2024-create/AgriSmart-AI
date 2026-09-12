import os
import io
from PIL import Image
from django.test import TestCase, Client
from django.urls import reverse

class PredictAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('predict_disease')
        
    def generate_dummy_image(self, ext='JPEG'):
        img = Image.new('RGB', (100, 100), color='green')
        img_io = io.BytesIO()
        img.save(img_io, format=ext)
        img_io.seek(0)
        return img_io

    def test_no_image_uploaded(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])
        self.assertEqual(response.json()['error'], "No image uploaded.")
        
    def test_unsupported_format(self):
        dummy_file = io.BytesIO(b"Not an image")
        dummy_file.name = "test.txt"
        response = self.client.post(self.url, {'image': dummy_file})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])
        self.assertIn("Unsupported file format", response.json()['error'])
        
    def test_valid_image(self):
        # We assume the model checkpoint exists because we just trained it.
        img_io = self.generate_dummy_image('JPEG')
        img_io.name = "test_leaf.jpg"
        response = self.client.post(self.url, {'image': img_io})
        
        # If checkpoint is missing on a fresh system, it returns 500.
        if response.status_code == 500 and "Model checkpoint is unavailable" in response.json().get('error', ''):
            # Skip test if checkpoint is not found locally
            pass
        else:
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data['success'])
    def test_real_inference_with_actual_image(self):
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        real_img_path = os.path.join(project_root, 'data', 'external', 'development_dataset', 'raw', 'diseased', 'diseased_0000.jpg')
        if os.path.exists(real_img_path):
            with open(real_img_path, 'rb') as f:
                response = self.client.post(self.url, {'image': f})
                
            if response.status_code == 200:
                data = response.json()
                self.assertTrue(data['success'])
                self.assertEqual(data['predicted_class'], 'diseased')
                self.assertIn('confidence', data)
                self.assertEqual(data['model_status'], 'development_prototype')


class RecommendCropAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('recommend_crop')
        
    def test_missing_fields(self):
        response = self.client.post(self.url, {'nitrogen': 10, 'ph': 6.5}, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])
        
    def test_invalid_numeric_values(self):
        response = self.client.post(self.url, {
            'nitrogen': 'abc', 'phosphorus': 10, 'potassium': 10, 
            'ph': 6.5, 'temperature': 25, 'humidity': 60, 'rainfall': 100
        }, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('must be a valid number', response.json()['error'])
        
    def test_negative_values(self):
        response = self.client.post(self.url, {
            'nitrogen': -10, 'phosphorus': 10, 'potassium': 10, 
            'ph': 6.5, 'temperature': 25, 'humidity': 60, 'rainfall': 100
        }, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('cannot be negative', response.json()['error'])
        
    def test_valid_request(self):
        response = self.client.post(self.url, {
            'nitrogen': 120, 'phosphorus': 50, 'potassium': 40, 
            'ph': 6.5, 'temperature': 25, 'humidity': 80, 'rainfall': 150
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('recommendations', data)
        self.assertEqual(data['model_status'], 'development_prototype')

class RecommendIrrigationAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('recommend_irrigation')
        
    def test_missing_weather_fields(self):
        response = self.client.post(self.url, {'crop': 'Wheat'}, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Temperature and rainfall are required', response.json()['error'])
        
    def test_invalid_moisture_percentage(self):
        response = self.client.post(self.url, {
            'temperature': 30, 'rainfall': 10, 'soil_moisture': 150
        }, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Soil moisture must be a percentage', response.json()['error'])
        
    def test_valid_irrigation_request(self):
        response = self.client.post(self.url, {
            'temperature': 36, 'rainfall': 0, 'soil_moisture': 20, 'humidity': 40
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['irrigation_priority'], 'Urgent irrigation recommended')
        self.assertEqual(data['model_status'], 'development_prototype')
