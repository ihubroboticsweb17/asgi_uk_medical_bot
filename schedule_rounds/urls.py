from django.urls import path
from .views import *
from django.conf import settings

urlpatterns = [

    path('create-scheduled-rounds/', create_or_update_scheduler, name='create scheduled rounds for patients'),
    path('view-all-scheduled-rounds/', view_all_scheduled_rounds, name='view every scheduled rounds'),
    path('view-patient-scheduled-rounds/<int:patient_id>/', view_patient_scheduled_rounds, name='view particular patient scheduled rounds'),

]