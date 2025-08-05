from django.urls import path
from .views import create_or_update_room, view_all_rooms, create_or_update_bed, view_all_bed

urlpatterns = [

    path('room/create/', create_or_update_room, name='create-room'),
    path('room/all/', view_all_rooms, name='room all'),

    path('bed/create/', create_or_update_bed, name='create-bed'),
    path('bed/all/', view_all_bed, name='bed all'),
    
]
