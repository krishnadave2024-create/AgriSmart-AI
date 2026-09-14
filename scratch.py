import re

with open('backend/api/tests.py', 'r', encoding='utf-8') as f:
    c = f.read()

setup_str = """class RecommendIrrigationAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('recommend_irrigation')"""

new_setup_str = """class RecommendIrrigationAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(username='irrtester', password='pw')
        res = self.client.post(reverse('token_obtain_pair'), {'username': 'irrtester', 'password': 'pw'}, content_type='application/json')
        self.auth_client = Client(HTTP_AUTHORIZATION=f"Bearer {res.json()['access']}")
        self.url = reverse('recommend_irrigation')"""

c = c.replace(setup_str, new_setup_str)

c = re.sub(r'(def test_missing_weather_fields.*?response = )self.client.post', r'\1self.auth_client.post', c, flags=re.DOTALL)
c = re.sub(r'(def test_invalid_moisture_percentage.*?response = )self.client.post', r'\1self.auth_client.post', c, flags=re.DOTALL)
c = re.sub(r'(def test_valid_irrigation_request.*?response = )self.client.post', r'\1self.auth_client.post', c, flags=re.DOTALL)

with open('backend/api/tests.py', 'w', encoding='utf-8') as f:
    f.write(c)

print('Done')
