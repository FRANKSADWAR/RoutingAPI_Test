from django.shortcuts import render
from apiroutes.models import Searoutes
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import action
from apiroutes.serializers import RouteSerializer,RouteGeoSerializer, CustomSerializer
from django.core.serializers import serialize
from django.db import connection
import psycopg2


database = 'testsdb'
user='postgres'
password='RootRender90'

conn = psycopg2.connect(database=database,user=user,password=password)
def getNode(x_coords,y_coords):
    query = """
            SELECT id FROM searoutes_vertices_pgr ORDER BY 
            the_geom <-> ST_SetSRID(ST_MakePoint(%s, %s),4326) LIMIT 1;
            """
    cur = conn.cursor()
    cur.execute(query,(x_coords,y_coords))
    point = cur.fetchone()
    return point        

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns,row))
        for row in cursor.fetchall()
    ]


class RoutesApi(APIView):
    """
    Get a routes object from the database
    """
    def get(self,request,pk,format=None):   
        try:
            route=Searoutes.objects.get(pk=pk)
            serializer = RouteGeoSerializer(route)
            return Response(data=serializer.data,status=status.HTTP_202_ACCEPTED)

        except Searoutes.DoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)

          

class ApiRoutesGeos(APIView):
    """
    This API will use a raw SQL query to get the shortest path between two coordinates provided, using the
    PgRouting extension and then return the path as GeoJSON
    """
    def get(self,request,start_lat,start_lng,end_lat,end_lng):
        
        def custom_query():
            start_node = getNode(start_lng,start_lat)
            end_node = getNode(end_lng,end_lat)
            route_query =  "SELECT sea.id AS id, SUM(sea.length) AS length, "
            route_query += "SUM(dij.cost) as COST, ST_AsText(ST_Collect(geom)) AS geom "
            route_query += "FROM pgr_dijkstra('SELECT id, source, target, cost FROM searoutes',%s, %s) AS dij, "                          
            route_query += "searoutes AS sea WHERE dij.edge = sea.id GROUP BY sea.id "
            with connection.cursor() as cursor:
                cursor.execute(route_query,[start_node,end_node])
                rows = dictfetchall(cursor)    
            return rows
          
        route_data = custom_query()
        route_info = serialize('geojson',route_data)
        #data = CustomSerializer(route_data)
        #serializer = CustomSerializer(route_data)
        return Response(data=route_info.data,status=status.HTTP_200_OK)
      
        
        #return Response(route_info.data, status=status.HTTP_200_OK, content_type='json')            
    




