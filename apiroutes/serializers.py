from rest_framework import serializers
from apiroutes.models import Searoutes

class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Searoutes
        fields = '__all__'

        