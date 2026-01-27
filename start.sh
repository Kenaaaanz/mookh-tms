#!/usr/bin/env bash

echo "Starting application..."

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start Gunicorn
exec gunicorn mookh_system.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --worker-class sync \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -