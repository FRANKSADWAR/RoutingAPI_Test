from apiroutes.views import RoutesApi, ApiRoutesGeos
from django.urls import path, include

urlpatterns = [
    path('routes/<int:pk>/',RoutesApi.as_view()),
    path('params/<float:start_lat>/<float:start_lng>/<float:end_lat>/<float:end_lng>/',ApiRoutesGeos.as_view()),
    
]