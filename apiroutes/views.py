from django.shortcuts import render
from apiroutes.models import Searoutes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import action


class RoutesApi(APIView):
    """
    Get a routes object from the database
    """
    def get_object(self,request,pk,format=None):
        try:
            return Searoutes.objects.get(pk=pk)
        except Searoutes.DoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)
    def get(self,request,pk,format=None):   
        try:
            route=Searoutes.objects.get(pk=pk)
            serializer = RoutesSerializer(route)
            
        except Searoutes.DoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)






