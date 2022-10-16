from django.shortcuts import render
from apiroutes.models import Searoutes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import action
from apiroutes.serializers import RouteSerializer,RouteGeoSerializer
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
            serializer = RouteGeoSerializer(route)
            return Response(data=serializer.data,status=status.HTTP_202_ACCEPTED)

        except Searoutes.DoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)

          

class ApiRoutesGeos(APIView):
    """
    This API will use a raw SQL query to get the shortest path between two coordinates provided, using the
    PgRouting extension and then return the path as GeoJSON
    """
    def get_route(request,start_lat,start_lng,end_lat,end_lng):
        start_node = getNode(start_lng,start_lat)
        end_node = getNode(end_lng,end_lat)
        route_query =   """
                            SELECT sea.id AS id, 
                            SUM(sea.length) AS length, 
                            SUM(dij.cost) as COST, ST_Collect(geom) AS geom 
                            FROM pgr_dijkstra('SELECT id, source, target, cost FROM searoutes',%s, %s) AS dij,                            
                            searoutes AS sea WHERE dij.edge = sea.id GROUP BY sea.id;
                        """

                        


