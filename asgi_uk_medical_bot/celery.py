import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE','asgi_uk_medical_bot.settings')

app = Celery('asgi_uk_medical_bot')
app.config_from_object('django.conf:settings',namespace='CELERY')
app.autodiscover_tasks()