from django.urls import path
from .views import predict_disease, recommend_crop, recommend_irrigation

urlpatterns = [
    path('disease/predict/', predict_disease, name='predict_disease'),
    path('crops/recommend/', recommend_crop, name='recommend_crop'),
    path('irrigation/recommend/', recommend_irrigation, name='recommend_irrigation'),
]
