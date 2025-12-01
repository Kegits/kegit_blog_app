# Production-ready Django Dockerfile for Vercel
# Uses Python 3.12, installs dependencies, runs collectstatic, exposes WSGI

FROM python:3.12-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv (if using Pipfile) or fallback to pip
RUN pip install --upgrade pip

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run migrations (optional: can be done in entrypoint)
RUN python manage.py migrate --noinput

# Expose port (for local dev; Vercel will handle routing)
EXPOSE 8000

# Set environment variables for Django
ENV DJANGO_SETTINGS_MODULE=coolweb.settings

# Run gunicorn on startup (production-ready WSGI server)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "coolweb.wsgi:application"]
