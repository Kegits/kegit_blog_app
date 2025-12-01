# Django + Vercel Production Docker Setup

This repo includes a production-ready Docker setup for deploying Django on Vercel or running locally with Docker Compose.

## Files
- `Dockerfile`: Builds a production Django image, runs collectstatic and migrations, and serves via Gunicorn (WSGI).
- `.dockerignore`: Excludes unnecessary files from the Docker build context.
- `docker-compose.yml`: For local development with Django and Postgres.

## Vercel Deployment Steps
1. **Push your code to GitHub.**
2. **Connect your repo to Vercel.**
3. **Set Vercel project environment variables:**
   - `SECRET_KEY`, `DATABASE_URL`, `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`, etc.
4. **Vercel will build using the Dockerfile.**
   - It will run migrations and collectstatic during build.
   - Gunicorn will serve your Django app via WSGI.
5. **Static/media files:**
   - Use Cloudinary for media/static in production (see your settings.py).
   - Local `media/` and `staticfiles/` are ignored in Docker builds.

## Local Development
- Run with Docker Compose:
  ```bash
  docker-compose up --build
  ```
- Access the app at [http://localhost:8000](http://localhost:8000)
- Database is Postgres (see `docker-compose.yml` for env vars).

## Notes
- For production, always set strong secrets and DB credentials in Vercel env vars.
- The Dockerfile is compatible with Vercel's build system and can be used on other platforms (Render, Railway, etc.).
- If you use Pipfile, adapt the Dockerfile to install with pipenv.
