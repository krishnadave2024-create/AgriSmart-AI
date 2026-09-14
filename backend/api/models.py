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
