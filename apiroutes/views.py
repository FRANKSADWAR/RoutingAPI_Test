from django.shortcuts import render
from apiroutes.models import Searoutes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import action
from apiroutes.serializers import RouteSerializer
import psycopg2


database = 'testsdb'
user='postgres'
password='RootRender90'

conn = psycopg2.connect(database=database,user=user,password=password)
def getNode(x_coords,y_coords):
    query = """
            SELECT id FROM searoutes_vertices_pgr ORDER BY 
            geom <-> ST_SetSRID(ST_MakePoint(%s, %s),4326) LIMIT 1;
            """
    cur = conn.cursor()
    cur.execute(query,(x_coords,y_coords))
    point = cur.fetchone()
    return point        


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

    def get_route(lat_1,lng_1,lat_2,lng_2):
        pass        





