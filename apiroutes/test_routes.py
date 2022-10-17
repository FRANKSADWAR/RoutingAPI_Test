"""
In this test file, we will obtain the route from the database, and then get the
results of the route as a GeoJSON result
"""
from django.db import connection
import psycopg2
#from apiroutes.models import Searoutes
import logging
import traceback

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


def get_shortestRoute(start_lat,start_lng,end_lat,end_lng):
    start_node = getNode(start_lng,start_lat)
    end_node = getNode(end_lng,end_lat)
    route_query =  "SELECT sea.id as id, SUM(sea.length) AS length, "
    route_query += "SUM(dij.cost) as COST, ST_Collect(geom) AS geom "
    route_query += "FROM pgr_dijkstra('SELECT id, source, target, cost FROM searoutes',%s, %s) AS dij, "                          
    route_query += "searoutes AS sea WHERE dij.edge = sea.id GROUP BY sea.id "

    try:
        cur = conn.cursor()
        cur.execute(route_query,(start_node,end_node))
        data = cur.fetchall()
        print(data)
    except:
        logger.error('Error while executing the query')
        logger.error(traceback.format_exc())




if __name__=="__main__":
    get_shortestRoute(9.237,75.967,41.718,12.225)
