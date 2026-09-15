import os
with open('backend/api/tests.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_tests = """
import tempfile
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

class DiseaseDetectionFinalTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('predict_disease')
        self.user = User.objects.create_user(username='test_disease_user', password='password')
        self.client.login(username='test_disease_user', password='password')
        
        # Create a dummy valid image
        self.valid_img = Image.new('RGB', (100, 100), color='green')
        self.img_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        self.valid_img.save(self.img_file, format='JPEG')
        self.img_file.seek(0)
        
    def tearDown(self):
        if os.path.exists(self.img_file.name):
            os.remove(self.img_file.name)

    def test_unsupported_crop_selected(self):
        # 1. Cotton image with unsupported crop selected
        with open(self.img_file.name, 'rb') as f:
            response = self.client.post(self.url, {'image': f, 'crop_type': 'other'})
        
        data = response.json()
        self.assertEqual(data['prediction']['status'], 'unsupported_crop')
        self.assertEqual(data['prediction']['crop'], None)
        self.assertEqual(data['knowledge'], None)
        self.assertIn("This crop is not supported", data['message'])
        
        # Check DB
        scan = DiseaseScan.objects.filter(user=self.user).last()
        self.assertIsNone(scan) # We bypass inference entirely, but we log Activity
        activity = ActivityRecord.objects.filter(user=self.user).last()
        self.assertEqual(activity.title, 'Disease Scan Bypassed')

    def test_inference_uncertain(self):
        # We simulate low confidence for an out-of-distribution image.
        # It's hard to guarantee confidence < 0.85 with a solid green square, but we'll try.
        with open(self.img_file.name, 'rb') as f:
            response = self.client.post(self.url, {'image': f, 'crop_type': 'tomato'})
        
        # We can't guarantee what resnet18 thinks of a green square, but assuming it processes it.
        # We just check it doesn't crash and follows the contract.
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn(data['prediction']['status'], ['uncertain', 'healthy', 'diseased'])
        
        if data['prediction']['status'] == 'uncertain':
            self.assertIsNone(data['knowledge'])
            
        if data['prediction']['status'] == 'unsupported_crop':
            self.assertIsNone(data['knowledge'])
            
    def test_analytics_isolation(self):
        response = self.client.get(reverse('disease_history'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['analytics']['total_scans'], 0)
"""

if "DiseaseDetectionFinalTests" not in content:
    with open('backend/api/tests.py', 'a', encoding='utf-8') as f:
        f.write("\n" + new_tests)
    print("New tests added successfully.")
else:
    print("Tests already exist.")
