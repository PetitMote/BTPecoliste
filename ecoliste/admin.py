from django.contrib.gis import admin
from . import models

admin.site.register(models.Enterprise)
admin.site.register(models.Address, admin.GISModelAdmin)
admin.site.register(models.MaterialByEnterprise)
admin.site.register(models.Contact)
admin.site.register(models.MaterialType)
admin.site.register(models.MaterialTypeCategory)
admin.site.register(models.BiobasedOriginMaterial)
