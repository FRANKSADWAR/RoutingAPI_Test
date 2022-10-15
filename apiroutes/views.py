from django.shortcuts import render
from apiroutes.models import Searoutes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import action
from apiroutes.serializers import RouteSerializer


class RoutesApi(APIView):
    """
    Get a routes object from the database
    """
    def get(self,request,pk):   
        try:
            route=Searoutes.objects.get(pk=pk)
            serializer = RouteSerializer(route)
            return Response(data=serializer.data,status=status.HTTP_202_ACCEPTED)

        except Searoutes.DoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)






