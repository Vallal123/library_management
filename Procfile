web: gunicorn config.wsgi:application --blind 0.0.0.0:$PORT
workder: celery -A config worker --loglevel=info
beat: celery -A config beat --loglevel=info