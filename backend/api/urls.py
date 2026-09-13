from django.urls import path
from .views import predict_disease, recommend_crop, recommend_irrigation, sustainability_score, farmer_assistant, fieldguard_assess

urlpatterns = [
    path('disease/predict/', predict_disease, name='predict_disease'),
    path('crops/recommend/', recommend_crop, name='recommend_crop'),
    path('irrigation/recommend/', recommend_irrigation, name='recommend_irrigation'),
    path('sustainability/score/', sustainability_score, name='sustainability_score'),
    path('assistant/message/', farmer_assistant, name='farmer_assistant'),
    path('fieldguard/assess/', fieldguard_assess, name='fieldguard_assess'),
]
