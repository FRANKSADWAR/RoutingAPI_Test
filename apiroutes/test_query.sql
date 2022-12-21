WITH route_dij AS (SELECT sea.id AS id, SUM(sea.length) AS length,SUM (dij.cost) AS cost, ST_Collect(sea.geom) AS geom FROM 
pgr_astar('SELECT id,source,target,cost,x1,y1,x2,y2,reverse_cost FROM searoutes_noded_noded WHERE NOT ST_Intersects(sea.geom,suez.geom)',631460,627932) AS dij,searoutes AS sea WHERE dij.edge = sea.id GROUP BY sea.id) 
SELECT route_dij.id,route_dij.cost, ST_AsGeoJSON(route_dij.geom) AS the_geom,
route_dij.length,(SELECT SUM(ST_Length( (ST_Intersection(route.geom,eca.geom))::geography)/1852)
FROM eca_areas AS eca, route_dij AS route WHERE ST_Intersects(route.geom,eca.geom)) AS eca_distance FROM route_dij






WITH route_dij AS (SELECT sea.id AS id, SUM(sea.length) AS length,SUM (dij.cost) AS cost, 
ST_Collect(sea.geom) AS geom FROM 
pgr_astar('SELECT id,source,target,cost,x1,y1,x2,y2,reverse_cost FROM searoutes_noded_noded, suez
WHERE NOT ST_Intersects(searoutes_noded_noded.geom,suez.geom)',631460,627932) AS dij,searoutes_noded_noded AS sea 
WHERE dij.edge = sea.id GROUP BY sea.id) 
SELECT route_dij.id,route_dij.cost, ST_AsGeoJSON(route_dij.geom) AS the_geom,
route_dij.length,(SELECT SUM(ST_Length((ST_Intersection(route.geom,eca.geom))::geography)/1852)
FROM eca_areas AS eca, route_dij AS route WHERE ST_Intersects(route.geom,eca.geom)) AS eca_distance FROM route_dij;
