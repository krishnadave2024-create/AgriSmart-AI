with open('backend/api/tests.py', 'r', encoding='utf-8') as f:
    c = f.read()

tests_code = """
class DashboardAPITests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', email='test1@example.com', password='password123')
        self.user2 = User.objects.create_user(username='testuser2', email='test2@example.com', password='password123')
        
        # User 1 profiles
        self.profile1 = UserProfile.objects.create(user=self.user1, full_name='Test User 1')
        self.farm1 = FarmProfile.objects.create(user=self.user1, farm_name='Farm 1', location='Pune')
        
        # User 2 profiles
        self.profile2 = UserProfile.objects.create(user=self.user2, full_name='Test User 2')
        self.farm2 = FarmProfile.objects.create(user=self.user2, farm_name='Farm 2', location='Mumbai')
        
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)
        self.dashboard_url = reverse('dashboard_summary')

    def test_dashboard_no_records(self):
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertTrue(data['success'])
        self.assertEqual(data['metrics']['total_disease_scans'], 0)
        self.assertEqual(data['metrics']['total_crop_recommendations'], 0)
        
        # Should have a "needs attention" for no disease scans
        needs_att = [n['reason'] for n in data['needs_attention']]
        self.assertIn('No disease scans recorded', needs_att)

    def test_dashboard_with_records(self):
        DiseaseScan.objects.create(user=self.user1, predicted_class='healthy', confidence=0.99)
        DiseaseScan.objects.create(user=self.user1, predicted_class='diseased_blight', confidence=0.85)
        CropRecommendationRecord.objects.create(user=self.user1, nitrogen=10, phosphorus=10, potassium=10, ph=6.5, temperature=25, humidity=50, rainfall=100, top_recommendation='Wheat')
        FieldGuardAssessment.objects.create(user=self.user1, score=30, category='High Risk', temperature=25, rainfall=10, score=35)
        ActivityRecord.objects.create(user=self.user1, activity_type='disease_scan', title='Scan completed')
        
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        
        self.assertEqual(data['metrics']['total_disease_scans'], 2)
        self.assertEqual(data['metrics']['healthy_scans'], 1)
        self.assertEqual(data['metrics']['diseased_scans'], 1)
        self.assertEqual(data['metrics']['total_crop_recommendations'], 1)
        self.assertEqual(data['metrics']['latest_fieldguard_category'], 'High Risk')
        
        # Needs attention for High risk
        needs_att = [n['reason'] for n in data['needs_attention'] if 'FieldGuard' in n['reason']]
        self.assertTrue(len(needs_att) > 0)
        
        # Recent activities
        self.assertEqual(len(data['recent_activities']), 1)
        
        # Analytics trend
        self.assertTrue(len(data['analytics']['activity_trend']) > 0)

    def test_dashboard_user_isolation(self):
        # Create record for user2
        DiseaseScan.objects.create(user=self.user2, predicted_class='healthy', confidence=0.99)
        
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['metrics']['total_disease_scans'], 0) # User1 shouldn't see user2's scans

    def test_dashboard_missing_farm_profile(self):
        # Remove farm location
        self.farm1.location = ''
        self.farm1.save()
        
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        needs_att = [n['reason'] for n in response.data['needs_attention']]
        self.assertIn('Farm city is missing', needs_att)
"""

if 'class DashboardAPITests' not in c:
    with open('backend/api/tests.py', 'a', encoding='utf-8') as f:
        f.write('\n' + tests_code)
    print("Tests added")
else:
    print("Tests already exist")
