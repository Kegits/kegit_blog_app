# Production-ready Django Dockerfile for Vercel
# Uses Python 3.12, installs dependencies, runs collectstatic, exposes WSGI

FROM python:3.12-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Provide SECRET_KEY as a runtime environment variable; do not bake it into the image.


# Allow passing DEBUG at build time (defaults to True for build/runtime convenience)
ARG DEBUG=0
ENV DEBUG=${DEBUG}
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

# Ensure Django settings module is set before running management commands
ENV DJANGO_SETTINGS_MODULE=coolweb.settings

# Use an entrypoint script to run migrations and collectstatic at container start.
# Copy the script into the image and make it executable; the script will run
# `migrate` and `collectstatic` then exec the container CMD.
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# Expose port (for local dev; Vercel will handle routing)
EXPOSE 8000

# Set environment variables for Django

# Run gunicorn on startup (production-ready WSGI server)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "coolweb.wsgi:application"]
