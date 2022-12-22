from __future__ import print_function
import time
from geojson import Feature, FeatureCollection, loads
import psycopg2
import logging, traceback

logger = logging.getLogger(__name__)


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


"""
Arguments in Python
The * and the ** are designed to supoort functions that take any number of arguments. Both can appear in either function definition
or a function call
"""

## collects all the positional arguments into a new tuple and assigns the variable args to that tuple
def func(*args):
    print(args)


## collects the keyword arguments into a dictionary, it only works for keyword arguments
def funct(**args):
    print(args)
    

## both the normal arguments, the * and the ** can be combined
def functi(a, *pargs,**kwargs):
    print(a,pargs,kwargs)

## keyword-only arguments with defaults are optional, but those without defaults effectively become required keywords for the function
def kwonly(a,*args,b,c='spam'):
    print(a,b,c)
    """
    the kwonly() function needs keyword-only argument b
    """
    
## Ordering Rules
"""
Finally note thaat keyword-only arguments must be specified after a single start not two,
names arguments cannot appear after the **args arbitrary keywords form and a ** can't appear by itself in the argument list
for example def kwonly(a,**kargs,b,c) will generate an error
            def kwonly(a, **, b,c) will also generate an error

When an argument name appears before the *args, it is possibly default positional argument, not keyword-only        
"""
def f(a,*b,c=6,**d):
    print(a,b,c,d)


def test_route_options(start_lat, start_lng, end_lat, end_lng,*args,suez=False,panama=False,singapore=False):
        local_vars = locals()
        start_coords = [local_vars['start_lat'],local_vars['end_lng']]
        end_coords = [local_vars['end_lat'],local_vars['end_lng']]

        coordinates = Feature(properties={'start_coordinates':start_coords,'end_coordinates':end_coords})
        
        start_node = getNode(start_lng,start_lat)
        end_node = getNode(end_lng,end_lat)

        query_url = """ WITH route_dij AS (SELECT sea.id AS id, SUM(sea.length) AS length,SUM (dij.cost) AS cost, ST_Collect(sea.geom) AS geom FROM pgr_astar('SELECT id,source,target,cost,x1,y1,x2,y2,reverse_cost
                        FROM searoutes_noded_noded',%s,%s) AS dij,searoutes AS sea WHERE dij.edge = sea.id GROUP BY sea.id) SELECT route_dij.id,route_dij.cost, ST_AsGeoJSON(route_dij.geom) AS the_geom,
                        route_dij.length,(SELECT SUM(ST_Length( (ST_Intersection(route.geom,eca.geom))::geography)/1852)
                        FROM eca_areas AS eca, route_dij AS route WHERE ST_Intersects(route.geom,eca.geom)) AS eca_distance FROM route_dij
                    """

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

        try:
            with conn.cursor() as cursor:
                cursor.execute(query_url,(start_node,end_node))
                rows = cursor.fetchall()
            return [rows, coordinates]   
        except:
            logger.error('Error while exceuting the query,try again later')
            logger.error(traceback.format_exc())



if __name__=="__main__":
    test_routes(4567,1223,suez=False,panama=True,singapore=True)

        
    
         
    





