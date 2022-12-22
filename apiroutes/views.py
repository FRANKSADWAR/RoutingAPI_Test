from dataclasses import fields
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
from geojson import loads, Feature, FeatureCollection


database = 'searouting'
user='postgres'
password='RootRender90'

conn = psycopg2.connect(database=database,user=user,password=password)
def getNode(x_coords,y_coords):
    query = """
            SELECT id FROM searoutes_noded_noded_vertices_pgr ORDER BY 
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
    def get(self,request,pk):   
        try:
            route=Searoutes.objects.get(pk=pk)
            serializer = RouteGeoSerializer(route)
            return Response(data=serializer.data,status=status.HTTP_202_ACCEPTED)

        except Searoutes.DoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)

          

class ApiRoutesGeos(APIView):
    """
    To use this API, simply input the coordinates of the starting point and the destination point, in latitude and longitude.
    The start coordinates are designated as start_lat and start_lng, the destination coordinates are designated as end_lat and
    end_lng.  This API will get the shortest path between the two pairs of coordinates provided, using the
    and then return the route data as GeoJSON. Further improvements will include avoidance of obstacles such as High Risk Areas (HRA)
    """
    def test_route_options(self, start_lat, start_lng, end_lat, end_lng, *args,suez=False,panama=False,singapore=False):
        local_vars = locals()
        start_coords = [local_vars['start_lat'],local_vars['end_lng']]
        end_coords = [local_vars['end_lat'],local_vars['end_lng']]
        
        start_node = getNode(start_lng,start_lat)
        end_node = getNode(end_lng,end_lat)


        query_url = """ WITH route_dij AS (SELECT sea.id AS id, SUM(sea.length) AS length,SUM (dij.cost) AS cost, ST_Collect(sea.geom) AS geom FROM pgr_astar('SELECT id,source,target,cost,x1,y1,x2,y2,reverse_cost
                        FROM searoutes_noded_noded',%s,%s) AS dij,searoutes AS sea WHERE dij.edge = sea.id GROUP BY sea.id) SELECT route_dij.id,route_dij.cost, ST_AsGeoJSON(route_dij.geom) AS the_geom,
                        route_dij.length,(SELECT SUM(ST_Length( (ST_Intersection(route.geom,eca.geom))::geography)/1852)
                        FROM eca_areas AS eca, route_dij AS route WHERE ST_Intersects(route.geom,eca.geom)) AS eca_distance FROM route_dij
                    """

        query_ = " WITH route_dij AS (SELECT sea.id AS id, SUM(sea.length) AS length, "
        query_ +=  "SUM (dij.cost) AS cost, ST_Collect(sea.geom) AS geom "
        query_ +=  "FROM pgr_astar('SELECT id,source,target,cost,x1,y1,x2,y2,reverse_cost "
        query_ += "FROM searoutes_noded_noded',%s,%s) AS dij, "
        query_ += " searoutes AS sea WHERE dij.edge = sea.id GROUP BY sea.id) SELECT route_dij.id,"
        query_ +=  " route_dij.cost, ST_AsGeoJSON(route_dij.geom) AS the_geom, "          
        query_ += "route_dij.length,(SELECT SUM(ST_Length( (ST_Intersection(route.geom,eca.geom))::geography)/1852)"        
        query_ += " FROM eca_areas AS eca, route_dij AS route WHERE ST_Intersects(route.geom,eca.geom)) AS eca_distance FROM route_dij"

        if (suez==False) and (panama==False) and (singapore==False):
            query_url = query_url  ## this is the case when they are are all false, meaning to ignore them in the routing

        if(suez==True) and (panama == True) and (singapore==True):
            query_url = """ WITH route_dij AS (SELECT sea.id AS id, SUM(sea.length) AS length,SUM (dij.cost) AS cost, ST_Collect(sea.geom) AS geom FROM pgr_astar('SELECT id,source,target,cost,x1,y1,x2,y2,
                            reverse_cost FROM avoid_suez_panama_singapore',%s,%s) AS dij, avoid_suez_panama_singapore AS sea WHERE dij.edge = sea.id GROUP BY sea.id) SELECT route_dij.id,route_dij.cost, 
                            ST_AsGeoJSON(route_dij.geom) AS the_geom,
                            route_dij.length,(SELECT SUM(ST_Length( (ST_Intersection(route.geom,eca.geom))::geography)/1852)
                            FROM eca_areas AS eca, route_dij AS route WHERE ST_Intersects(route.geom,eca.geom)) AS eca_distance FROM route_dij
                        """

        if (suez == True) and (panama==False) and (singapore==False):
            print('only suez true')
            query_url = """WITH route_dij AS (SELECT sea.id AS id, SUM(sea.length) AS length, SUM(dij.cost) AS cost, ST_Collect(sea.geom) AS geom FROM pgr_astar('SELECT id,source,target,cost,x1,y1,x2,y2,
                            reverse_cost FROM avoid_suez_canal',%s,%s) AS dij, avoid_suez_canal AS sea WHERE dij.edge = sea.id GROUP BY sea.id) SELECT route_dij.id,route_dij.cost, 
                            ST_AsGeoJSON(route_dij.geom) AS the_geom,
                            route_dij.length, (SELECT SUM(ST_Length((ST_Intersection(route.geom,eca.geom))::geography)/1852)
                            FROM eca_areas AS eca, route_dij AS route WHERE ST_Intersects(route.geom,eca.geom)) AS eca_distance FROM route_dij
                        """
            
        if (suez == True) and (panama==True) and (singapore==False):
            print('suez and panama true')
            query_url = """WITH route_dij AS (SELECT sea.id AS id, SUM(sea.length) AS length, SUM(dij.cost) AS cost, ST_Collect(sea.geom) AS geom FROM pgr_astar('SELECT id,source,target,cost,x1,y1,x2,y2,
                            reverse_cost FROM avoid_suez_panama',%s,%s) AS dij, avoid_suez_panama AS sea WHERE dij.edge = sea.id GROUP BY sea.id) SELECT route_dij.id,route_dij.cost, 
                            ST_AsGeoJSON(route_dij.geom) AS the_geom,
                            route_dij.length, (SELECT SUM(ST_Length((ST_Intersection(route.geom,eca.geom))::geography)/1852)
                            FROM eca_areas AS eca, route_dij AS route WHERE ST_Intersects(route.geom,eca.geom)) AS eca_distance FROM route_dij
                        """
            
        if(suez == False) and (panama == False) and (singapore==True):
            print('only singapore true')
            query_url = """WITH route_dij AS (SELECT sea.id AS id, SUM(sea.length) AS length, SUM(dij.cost) AS cost, ST_Collect(sea.geom) AS geom FROM pgr_astar('SELECT id,source,target,cost,x1,y1,x2,y2,
                            reverse_cost FROM avoid_singapore',%s,%s) AS dij, avoid_singapore AS sea WHERE dij.edge = sea.id GROUP BY sea.id) SELECT route_dij.id,route_dij.cost, 
                            ST_AsGeoJSON(route_dij.geom) AS the_geom,
                            route_dij.length, (SELECT SUM(ST_Length((ST_Intersection(route.geom,eca.geom))::geography)/1852)
                            FROM eca_areas AS eca, route_dij AS route WHERE ST_Intersects(route.geom,eca.geom)) AS eca_distance FROM route_dij
                        """
            
        if(suez == False) and (panama == True) and (singapore == False):
            print('only panama true')
            query_url = """WITH route_dij AS (SELECT sea.id AS id, SUM(sea.length) AS length, SUM(dij.cost) AS cost, ST_Collect(sea.geom) AS geom FROM pgr_astar('SELECT id,source,target,cost,x1,y1,x2,y2,
                            reverse_cost FROM avoid_panama',%s,%s) AS dij, avoid_panama AS sea WHERE dij.edge = sea.id GROUP BY sea.id) SELECT route_dij.id,route_dij.cost, 
                            ST_AsGeoJSON(route_dij.geom) AS the_geom,
                            route_dij.length, (SELECT SUM(ST_Length((ST_Intersection(route.geom,eca.geom))::geography)/1852)
                            FROM eca_areas AS eca, route_dij AS route WHERE ST_Intersects(route.geom,eca.geom)) AS eca_distance FROM route_dij
                        """

        if(suez == True) and (panama==False) and (singapore==True):
            print('suez and singapore true')
            query_url = """WITH route_dij AS (SELECT sea.id AS id, SUM(sea.length) AS length, SUM(dij.cost) AS cost, ST_Collect(sea.geom) AS geom FROM pgr_astar('SELECT id,source,target,cost,x1,y1,x2,y2,
                            reverse_cost FROM avoid_suez_singapore',%s,%s) AS dij, avoid_suez_singapore AS sea WHERE dij.edge = sea.id GROUP BY sea.id) SELECT route_dij.id,route_dij.cost, 
                            ST_AsGeoJSON(route_dij.geom) AS the_geom,
                            route_dij.length, (SELECT SUM(ST_Length((ST_Intersection(route.geom,eca.geom))::geography)/1852)
                            FROM eca_areas AS eca, route_dij AS route WHERE ST_Intersects(route.geom,eca.geom)) AS eca_distance FROM route_dij
                        """

        if(suez==False) and (panama==True) and (singapore==True):
            print('panama and singapore true')
            query_url = """WITH route_dij AS (SELECT sea.id AS id, SUM(sea.length) AS length, SUM(dij.cost) AS cost, ST_Collect(sea.geom) AS geom FROM pgr_astar('SELECT id,source,target,cost,x1,y1,x2,y2,
                            reverse_cost FROM avoid_panama_singapore',%s,%s) AS dij, avoid_panama_singapore AS sea WHERE dij.edge = sea.id GROUP BY sea.id) SELECT route_dij.id,route_dij.cost, 
                            ST_AsGeoJSON(route_dij.geom) AS the_geom,
                            route_dij.length, (SELECT SUM(ST_Length((ST_Intersection(route.geom,eca.geom))::geography)/1852)
                            FROM eca_areas AS eca, route_dij AS route WHERE ST_Intersects(route.geom,eca.geom)) AS eca_distance FROM route_dij
                        """


    def test_routes(start,end,*args,suez=False,panama=False,singapore=False):
        var_args = locals()
        print(var_args['suez'],var_args['panama'],var_args['singapore'])

        route_options = Feature(options={'suez':var_args['suez'],'panama':var_args['panama'],'singapore':var_args['singapore']})
        print(route_options)
        

    







    
    def get_route_data(self,start_lat,start_lng,end_lat,end_lng):
        local_vars = locals()
        start_coords = [local_vars['start_lat'],local_vars['start_lng']]
        end_coords = [local_vars['end_lat'],local_vars['end_lng']]
        ##to_coords = local_vars['args']
        ##print(to_coords)

        coordinates = Feature(properties={'start_coordinates':start_coords,'end_coordinates':end_coords})



        start_node = getNode(start_lng,start_lat)
        end_node = getNode(end_lng,end_lat)
        route_query =  "SELECT SUM(sea.length) AS length, "
        route_query += "SUM(dij.cost) as COST, ST_AsGeoJSON(ST_Collect(geom)) AS geom "
        route_query += "FROM pgr_dijkstra('SELECT id, source, target, cost FROM searoutes',%s, %s) AS dij, "                          
        route_query += "searoutes AS sea WHERE dij.edge = sea.id GROUP BY sea.id "


        with connection.cursor() as cursor:
                cursor.execute(route_query,(start_node,end_node))
                rows = cursor.fetchall()

        ## return the SQL values from the query and also the feature        
        return [rows,coordinates]

    def get(self,request,start_lat,start_lng,end_lat,end_lng):
        try:
            data = self.get_route_data(start_lat,start_lng,end_lat,end_lng)
            route_result = []
            total_length = []
            total_cost = []

            for segment in data[0]:
                length = segment[0]
                cost = segment[1]
                total_length.append(length)
                total_cost.append(cost)

                geom = segment[2]
                geom_json = loads(geom)
                segment_geom = Feature(geometry=geom_json)
                route_result.append(segment_geom)

            total_length = round(sum(total_length),4)
            total_cost = round(sum(total_cost),4)
            route_data = FeatureCollection(route_result,distance=total_length,time=total_cost,node_coordinates=data[1])
        
            return Response(route_data, status=status.HTTP_201_CREATED, content_type='application/json')  
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)              
        


