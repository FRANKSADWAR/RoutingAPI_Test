from atexit import register
from apiroutes import converters
from apiroutes.views import RoutesApi, ApiRoutesGeos
from django.urls import path, register_converter
from rest_framework.urlpatterns import format_suffix_patterns

register_converter(converters.FloatUrlParameterConverter,'float')

urlpatterns = [
    path('routes/<int:pk>/',RoutesApi.as_view()),
    path('params/<float:start_lat>/<float:start_lng>/<float:end_lat>/<float:end_lng>/<str:suez>/<str:panama>/<str:singapore>/',ApiRoutesGeos.as_view()),
]
urlpatterns = format_suffix_patterns(urlpatterns)