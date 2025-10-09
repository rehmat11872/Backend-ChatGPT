#!/bin/bash
# Production Deployment Script
# Run this on your production server

echo "=== Starting Deployment ==="

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
pip install Pillow pytesseract PyMuPDF

# Install system dependencies for OCR
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create media directory
echo "Creating media directories..."
mkdir -p media/avatars
mkdir -p media/protected_pdfs
mkdir -p media/ocr_pdfs
chmod 755 media/

# Restart services
echo "Restarting services..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "=== Deployment Complete ==="
echo "Don't forget to:"
echo "1. Update .env file with production values"
echo "2. Update CORS_ALLOWED_ORIGINS with your frontend domain"
echo "3. Test the endpoints"