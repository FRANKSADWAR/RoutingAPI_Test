"""
In this test file, we will obtain the route from the database, and then get the
results of the route as a GeoJSON result
"""

from time import time
from django.db import connection
import psycopg2
#from apiroutes.models import Searoutes
import logging
import traceback
from geojson import loads, Feature, FeatureCollection

logger = logging.getLogger(__name__)
database = 'testsdb'
user = 'postgres'
password = 'RootRender90'
conn = psycopg2.connect(database=database,user=user,password=password)

def getNode(x_coords,y_coords):
    query = """
            SELECT id FROM searoutes_vertices_pgr ORDER BY 
            the_geom <-> ST_SetSRID(ST_MakePoint(%s, %s),4326) LIMIT 1;
            """
    cur = conn.cursor()
    cur.execute(query,(x_coords,y_coords))
    node_id = cur.fetchone()
    return node_id

def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns,row))
        for row in cursor.fetchall()
    ]

def get_shortestRoute(start_lat,start_lng,end_lat,end_lng):
    local_vars = locals()
    #print(local_vars)
    start_coords = [local_vars['start_lat'],local_vars['start_lng']]
    end_coords = [local_vars['end_lat'],local_vars['end_lng']]
    start_node = getNode(start_lng,start_lat)
    end_node = getNode(end_lng,end_lat)
    
    coordinates = Feature(properties={'start_coordinates':start_coords,'end_coordinates':end_coords})
    
    
    try:
        route_query =  "SELECT SUM(sea.length) AS length, "
        route_query += "SUM(dij.cost) as COST, ST_AsGeoJSON(ST_Collect(sea.geom)) AS geom "
        route_query += "FROM pgr_dijkstra('SELECT id, source, target, cost FROM searoutes',%s, %s) AS dij, "                          
        route_query += "searoutes AS sea WHERE dij.edge = sea.id GROUP BY sea.id "
        with conn.cursor() as cursor:
            cursor.execute(route_query,(start_node,end_node))
            rows = cursor.fetchall()

        #print(rows)    
        return [rows ,coordinates]
        
    except:
        logger.error('Error while executing the query')
        logger.error(traceback.format_exc())
    


def getFeatures():
    data = get_shortestRoute(9.237,75.967,41.718,12.225)
    route_result = []
    total_length = []
    total_cost = []
    for segment in data[0]:
        length = segment[0]
        cost = segment[1]
        geom = segment[2]

        total_length.append(length)
        total_cost.append(cost)

        geom_geojson = loads(geom)
        segment_feature = Feature(geometry=geom_geojson)
        route_result.append(segment_feature)

    total_length = round(sum(total_length),3)
    total_cost = round(sum(total_cost))          

    ## Create a feature collection from the features returned

    route_data = FeatureCollection(route_result, distance=total_length, time=total_cost,node_coordinates=data[1] )
    print(route_data)

if __name__=="__main__":
    ##get_shortestRoute(9.237,75.967,41.718,12.225)
    getFeatures()

