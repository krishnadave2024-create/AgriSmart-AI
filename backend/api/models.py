from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255)
    preferred_language = models.CharField(max_length=10, default='en', choices=(
        ('en', 'English'),
        ('hi', 'Hindi'),
        ('gu', 'Gujarati'),
    ))
    profile_image = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class FarmProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farm')
    farm_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default='India')
    farm_area = models.FloatField(blank=True, null=True)
    area_unit = models.CharField(max_length=20, default='acres', choices=(
        ('acres', 'Acres'),
        ('hectares', 'Hectares'),
        ('sq_meters', 'Square Meters'),
    ))
    soil_type = models.CharField(max_length=100, blank=True, null=True)
    irrigation_method = models.CharField(max_length=100, blank=True, null=True)
    main_crops = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.farm_name

class DiseaseScan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='disease_scans')
    image = models.ImageField(upload_to='disease_scans/', blank=True, null=True)
    predicted_class = models.CharField(max_length=255)
    prediction_status = models.CharField(max_length=50, default='uncertain')
    plant_name = models.CharField(max_length=100, blank=True, null=True)
    disease_name = models.CharField(max_length=100, blank=True, null=True)
    confidence = models.FloatField(blank=True, null=True)
    model_version = models.CharField(max_length=50, default='baseline_resnet18')
    is_development = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.predicted_class} ({self.confidence:.2f})"

class CropRecommendationRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crop_recommendations')
    farm_profile = models.ForeignKey('FarmProfile', on_delete=models.SET_NULL, null=True, blank=True)
    nitrogen = models.FloatField()
    phosphorus = models.FloatField()
    potassium = models.FloatField()
    ph = models.FloatField()
    temperature = models.FloatField()
    humidity = models.FloatField()
    rainfall = models.FloatField()
    weather_source = models.CharField(max_length=50, default='manual')
    recommendation_method = models.CharField(max_length=50, default='rule-based')
    top_recommendation = models.CharField(max_length=100, blank=True, null=True)
    explanation = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class IrrigationAssessment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='irrigation_assessments')
    farm_profile = models.ForeignKey('FarmProfile', on_delete=models.SET_NULL, null=True, blank=True)
    crop = models.CharField(max_length=100, blank=True, null=True)
    growth_stage = models.CharField(max_length=100, blank=True, null=True)
    field_area = models.FloatField(blank=True, null=True)
    irrigation_method = models.CharField(max_length=100, blank=True, null=True)
    soil_moisture = models.FloatField(blank=True, null=True)
    temperature = models.FloatField()
    humidity = models.FloatField(blank=True, null=True)
    rainfall = models.FloatField()
    priority = models.CharField(max_length=100)
    reasoning = models.TextField(blank=True, null=True)
    input_sources = models.CharField(max_length=100, default='manual')
    rule_version = models.CharField(max_length=50, default='v1.0')
    created_at = models.DateTimeField(auto_now_add=True)

class FieldGuardAssessment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fieldguard_assessments')
    farm_profile = models.ForeignKey('FarmProfile', on_delete=models.SET_NULL, null=True, blank=True)
    crop = models.CharField(max_length=100, blank=True, null=True)
    growth_stage = models.CharField(max_length=100, blank=True, null=True)
    disease_scan = models.ForeignKey('DiseaseScan', on_delete=models.SET_NULL, null=True, blank=True)
    temperature = models.FloatField(blank=True, null=True)
    humidity = models.FloatField(blank=True, null=True)
    rainfall = models.FloatField(blank=True, null=True)
    soil_moisture = models.FloatField(blank=True, null=True)
    weather_source = models.CharField(max_length=50, default='manual')
    score = models.FloatField()
    category = models.CharField(max_length=50)
    factors = models.JSONField(default=list)
    preventive_actions = models.JSONField(default=list)
    rule_version = models.CharField(max_length=50, default='v1.0')
    created_at = models.DateTimeField(auto_now_add=True)

class SustainabilityAssessment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sustainability_assessments')
    farm_profile = models.ForeignKey(FarmProfile, on_delete=models.SET_NULL, null=True, blank=True)
    score = models.FloatField()
    category = models.CharField(max_length=50)
    input_values = models.JSONField(default=dict)
    source_labels = models.JSONField(default=dict)
    positive_factors = models.JSONField(default=list)
    improvement_suggestions = models.JSONField(default=list)
    calculation_method = models.CharField(max_length=100, default='rule-based')
    rule_version = models.CharField(max_length=50, default='v1.0')
    water_savings_estimate = models.CharField(max_length=100, default='unavailable')
    energy_savings_estimate = models.CharField(max_length=100, default='unavailable')
    cost_savings_estimate = models.CharField(max_length=100, default='unavailable')
    created_at = models.DateTimeField(auto_now_add=True)

class ActivityRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class AssistantMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assistant_messages')
    role = models.CharField(max_length=20)
    content = models.TextField()
    language = models.CharField(max_length=10, default='en')
    provider_source = models.CharField(max_length=50, default='system')
    model_status = models.CharField(max_length=50, default='live')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=50) # e.g., 'disease_scan', 'irrigation_assessment'
    severity = models.CharField(max_length=20, default='info') # 'info', 'warning', 'error', 'success'
    related_route = models.CharField(max_length=255, blank=True, null=True) # e.g., '/disease'
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
