from django.urls import path
from .views import *
from django.conf import settings

urlpatterns = [

    path('update-scheduled-rounds/<int:pk>/', update_round_schedule, name='update scheduled rounds for patients'),
    path('view-all-scheduled-rounds/', view_all_scheduled_rounds, name='view every scheduled rounds'),
    path('view-patient-scheduled-rounds/<int:patient_id>/', view_patient_scheduled_rounds, name='view particular patient scheduled rounds'),

]