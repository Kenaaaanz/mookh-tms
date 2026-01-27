#!/usr/bin/env bash
set -o errexit

echo "Starting build process..."

# Upgrade pip and install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Create superuser non-interactively
echo "Creating superuser if not exists..."
cat > create_superuser.py << 'EOF'
import os
import django
from django.contrib.auth.models import User

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mookh_system.settings')
django.setup()

if not User.objects.filter(username='Kenani').exists():
    User.objects.create_superuser(
        username='Kenani',
        email='gichabakenani@gmail.com',
        password='admin123'
    )
    print("Superuser created successfully!")
else:
    print("Superuser already exists.")
EOF

python create_superuser.py

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Build completed successfully!"