from django.urls import path
from .views import predict_disease, recommend_crop, recommend_irrigation, sustainability_score, farmer_assistant, fieldguard_assess, register_user, user_profile, farm_profile, logout_user, current_user
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('auth/register/', register_user, name='register_user'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', logout_user, name='logout_user'),
    path('auth/me/', current_user, name='current_user'),
    path('profile/', user_profile, name='user_profile'),
    path('farm/', farm_profile, name='farm_profile'),
    path('disease/predict/', predict_disease, name='predict_disease'),
    path('crops/recommend/', recommend_crop, name='recommend_crop'),
    path('irrigation/recommend/', recommend_irrigation, name='recommend_irrigation'),
    path('sustainability/score/', sustainability_score, name='sustainability_score'),
    path('assistant/message/', farmer_assistant, name='farmer_assistant'),
    path('fieldguard/assess/', fieldguard_assess, name='fieldguard_assess'),
]
