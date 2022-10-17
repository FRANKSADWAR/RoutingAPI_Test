from atexit import register
from apiroutes import converters
from apiroutes.views import RoutesApi, ApiRoutesGeos
from django.urls import path, register_converter

register_converter(converters.FloatUrlParameterConverter,'float')

urlpatterns = [
    path('routes/<int:pk>/',RoutesApi.as_view()),
    path('params/<float:start_lat>/<float:start_lng>/<float:end_lat>/<float:end_lng>/',ApiRoutesGeos.as_view()),
    
]