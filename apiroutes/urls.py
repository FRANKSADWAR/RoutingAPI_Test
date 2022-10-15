from apiroutes.views import RoutesApi
from django.urls import path, include

urlpatterns = [
    path('routes/<int:pk>/',RoutesApi.as_view()),
]