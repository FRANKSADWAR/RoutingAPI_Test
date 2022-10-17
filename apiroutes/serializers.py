from rest_framework import serializers
from apiroutes.models import Searoutes
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework_gis.fields import GeometryField

class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Searoutes
        fields = '__all__'

class RouteGeoSerializer(GeoFeatureModelSerializer):
    """ Serializing the route data as GeoJSON compatible data"""
    class Meta:
        model = Searoutes
        geo_field = "geom"
        fields = '__all__'

class CustomSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Searoutes
        geo_field = 'geom'
        fields = ['cost','geom','length']        