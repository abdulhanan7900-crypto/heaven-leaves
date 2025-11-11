#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Make Python files executable
chmod +x heavenleaves/wsgi.py

echo "Build complete"