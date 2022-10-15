from django.db import models
from django.contrib.gis.db import models as gis_models



class Searoutes(gis_models.Model):
    id = models.IntegerField(blank=False,primary_key=True)
    fid = models.IntegerField(blank=True, null=True)
    geom = gis_models.LineStringField(srid=4326,blank=True, null=True)
    cost = models.FloatField(blank=True, null=True)
    reverse_cost = models.FloatField(blank=True, null=True)
    x1 = models.FloatField(blank=True, null=True)
    y1 = models.FloatField(blank=True, null=True)
    x2 = models.FloatField(blank=True, null=True)
    y2 = models.FloatField(blank=True, null=True)
    length = models.FloatField(blank=True, null=True)
    source = models.BigIntegerField(blank=True, null=True)
    target = models.BigIntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.target)

    class Meta:
        verbose_name_plural='Sea Routes'
        db_table = 'searoutes'
