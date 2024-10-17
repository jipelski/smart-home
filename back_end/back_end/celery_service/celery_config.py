from celery import Celery
from celery.schedules import crontab 
import os
from tasks import update_daily_aggregates
from dotenv import load_dotenv

load_dotenv()

celery_app = Celery(
    'sensor_aggregator',
    broker=os.getenv('REDIS_FOR_CELERY'),
    backend=None
)

@celery_app.task
def run_daily_aggregation():
    update_daily_aggregates()

celery_app.conf.beat_schedule = {
    'daily-aggregation-task': {
        'task': 'sensor_aggregator.run_daily_aggregation',
        'schedule': crontab(hour=0, minute=0),
    }
}


