
class WeatherAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username='weathertester', password='StrongPassword123!', email='weathertester@example.com')
        res = self.client.post(reverse('token_obtain_pair'), {'username': 'weathertester', 'password': 'StrongPassword123!'}, content_type='application/json')
        self.auth_client = Client(HTTP_AUTHORIZATION=f"Bearer {res.json()['access']}")
        self.current_url = reverse('current_weather')
        self.forecast_url = reverse('weather_forecast')
        
    def test_unauthenticated_access(self):
        res = self.client.get(f"{self.current_url}?city=Pune")
        self.assertEqual(res.status_code, 401)
        
    @patch('api.views.requests.get')
    def test_missing_location(self, mock_get):
        res = self.auth_client.get(self.current_url)
        self.assertEqual(res.status_code, 400)
        self.assertIn('Location could not be found.', res.json()['error'])
        
    @patch('api.views.os.environ.get')
    def test_missing_api_key(self, mock_env_get):
        mock_env_get.return_value = None
        res = self.auth_client.get(f"{self.current_url}?city=Pune")
        self.assertEqual(res.status_code, 503)
        self.assertIn('Weather service is not configured', res.json()['error'])
        
    @patch('api.views.requests.get')
    def test_valid_current_weather(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'name': 'Pune',
            'main': {'temp': 28.5, 'feels_like': 30.0, 'humidity': 65, 'temp_min': 25, 'temp_max': 32, 'pressure': 1010},
            'weather': [{'main': 'Clear', 'description': 'clear sky'}],
            'wind': {'speed': 5.0, 'deg': 180},
            'sys': {'sunrise': 123456, 'sunset': 123456},
            'dt': 1618317040
        }
        mock_get.return_value = mock_response
        
        # Need to clear cache to ensure we hit the mock
        from django.core.cache import cache
        cache.clear()
        
        with patch('api.views.os.environ.get', return_value='dummy_key'):
            res = self.auth_client.get(f"{self.current_url}?city=Pune")
        
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['location'], 'Pune')
        self.assertEqual(data['temperature'], 28.5)
        self.assertEqual(data['description'], 'clear sky')
        self.assertFalse(data['cached'])
        
        # Test caching
        with patch('api.views.os.environ.get', return_value='dummy_key'):
            res2 = self.auth_client.get(f"{self.current_url}?city=Pune")
        
        data2 = res2.json()
        self.assertTrue(data2['cached'])
        
    @patch('api.views.requests.get')
    def test_openweather_rate_limit(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_get.return_value = mock_response
        
        from django.core.cache import cache
        cache.clear()
        
        with patch('api.views.os.environ.get', return_value='dummy_key'):
            res = self.auth_client.get(f"{self.current_url}?city=Pune")
            
        self.assertEqual(res.status_code, 429)
        self.assertIn('Weather service rate limit exceeded.', res.json()['error'])
        
    @patch('api.views.requests.get')
    def test_valid_forecast(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'city': {'name': 'Pune'},
            'list': [
                {
                    'dt': 1618317040,
                    'main': {'temp': 28.5, 'humidity': 65},
                    'weather': [{'main': 'Clear'}],
                    'wind': {'speed': 5.0}
                }
            ]
        }
        mock_get.return_value = mock_response
        
        from django.core.cache import cache
        cache.clear()
        
        with patch('api.views.os.environ.get', return_value='dummy_key'):
            res = self.auth_client.get(f"{self.forecast_url}?city=Pune")
            
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['location'], 'Pune')
        self.assertEqual(len(data['forecast']), 1)
        self.assertEqual(data['forecast'][0]['temperature'], 28.5)

class FieldGuardAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username='fgtester', password='StrongPassword123!')
        res = self.client.post(reverse('token_obtain_pair'), {'username': 'fgtester', 'password': 'StrongPassword123!'}, content_type='application/json')
        self.auth_client = Client(HTTP_AUTHORIZATION=f"Bearer {res.json()['access']}")
        self.assess_url = reverse('fieldguard_assess')
        self.history_url = reverse('fieldguard_history')
        
    def test_unauthenticated_access(self):
        res = self.client.post(self.assess_url, {}, content_type='application/json')
        self.assertEqual(res.status_code, 401)
        
    def test_missing_required_data(self):
        # Missing temp and rainfall
        res = self.auth_client.post(self.assess_url, {'soil_moisture': 50}, content_type='application/json')
        self.assertEqual(res.status_code, 400)
        self.assertIn('Insufficient data for a reliable assessment', res.json()['error'])
        
    def test_invalid_numeric_values(self):
        res = self.auth_client.post(self.assess_url, {
            'temperature': 'hot',
            'rainfall': 10
        }, content_type='application/json')
        self.assertEqual(res.status_code, 400)
        self.assertIn('Invalid value for temperature', res.json()['error'])
        
    def test_valid_assessment(self):
        res = self.auth_client.post(self.assess_url, {
            'crop': 'Wheat',
            'growth_stage': 'Vegetative',
            'temperature': 25,
            'humidity': 60,
            'rainfall': 5,
            'soil_moisture': 45
        }, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['category'], 'Low Risk')
        
        # Check history
        res2 = self.auth_client.get(self.history_url)
        self.assertEqual(len(res2.json()['history']), 1)
        self.assertEqual(res2.json()['history'][0]['category'], 'Low Risk')
        
    def test_high_risk_assessment(self):
        res = self.auth_client.post(self.assess_url, {
            'temperature': 38,
            'humidity': 90,
            'rainfall': 150,
            'soil_moisture': 20
        }, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        # base=100, temp(-15) -> 85, soil(-20) -> 65, hum(-10) -> 55, rain(-10) -> 45 (High Risk)
        self.assertEqual(data['score'], 45)
        self.assertEqual(data['category'], 'High Risk')
        
    def test_disease_integration(self):
        from api.models import DiseaseScan
        scan = DiseaseScan.objects.create(user=self.user, predicted_class='Rust', confidence=0.85)
        
        res = self.auth_client.post(self.assess_url, {
            'temperature': 25,
            'rainfall': 10,
            'disease_scan_id': scan.id
        }, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['score'], 70)  # 100 - 30 for disease
        self.assertEqual(data['category'], 'Moderate Risk')
        
    def test_unauthorized_disease_scan(self):
        from api.models import DiseaseScan
        User = get_user_model()
        other_user = User.objects.create_user(username='other', password='pw')
        scan = DiseaseScan.objects.create(user=other_user, predicted_class='Rust', confidence=0.85)
        
        res = self.auth_client.post(self.assess_url, {
            'temperature': 25,
            'rainfall': 10,
            'disease_scan_id': scan.id
        }, content_type='application/json')
        self.assertEqual(res.status_code, 400)
        self.assertIn('Invalid disease scan or unauthorized', res.json()['error'])
