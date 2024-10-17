FROM python:3.11-slim
WORKDIR /app
COPY ./back_end/back_end/celery_service /app/
RUN pip install --no-cache-dir -r /app/requirements.txt
CMD ["celery", "-A", "celery_config.celery_app", "worker", "--loglevel=info"]
