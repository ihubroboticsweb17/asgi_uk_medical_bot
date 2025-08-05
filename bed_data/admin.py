from django.contrib import admin
from .models import BedDataModel, RoomDataModel
# Register your models here.

admin.site.register(BedDataModel)
admin.site.register(RoomDataModel)