from django.contrib import admin
from apiroutes.models import Searoutes

@admin.register(Searoutes)
class SearoutesAdmin(admin.ModelAdmin):
    list_display = ('id','fid','source','target','cost')
    search_fields = ('id','fid','source','target','cost')
    filter_fields = ('id','fid','source','target','cost')