import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kay_mama.settings')

app = Celery('kay_mama')

# Configure Celery using settings.py, namespaced with CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
