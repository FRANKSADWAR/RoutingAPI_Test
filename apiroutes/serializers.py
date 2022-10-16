from rest_framework import serializers
from apiroutes.models import Searoutes
from rest_framework_gis.serializers import GeoFeatureModelSerializer

class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Searoutes
        fields = '__all__'

class RouteGeoSerializer(GeoFeatureModelSerializer):
    """ Serializing the route data as GeoJSON compatible data"""
    class Meta:
        model = Searoutes
        geo_field = "linestring"
        fields = '__all__'