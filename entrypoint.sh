#!/bin/sh

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Create a superuser if it doesn't exist
echo "Creating superuser if it doesn't exist..."
python manage.py shell << END
from django.contrib.auth.models import User
import os
username = os.getenv('ADMIN_USER', 'admin')
email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
password = os.getenv('ADMIN_PASSWORD', 'password123')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
END

# Start the server
echo "Starting the server..."
python manage.py runserver 0.0.0.0:8000
