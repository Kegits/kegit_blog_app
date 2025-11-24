Deploying this Django app to Vercel (serverless) — Notes

Overview
- This repo includes a minimal `vercel.json` and a serverless WSGI entry at `api/wsgi.py`.
- The app uses Cloudinary for media (recommended) in production; local development continues to use the `media/` folder unless you set Cloudinary env vars.
- Important: Vercel serverless functions run on ephemeral storage — you MUST use Cloudinary (or other external storage) for user uploads and a managed Postgres for the database.

Required environment variables (set these in the Vercel Project > Settings > Environment Variables)
- `SECRET_KEY` — your Django secret key
- `DEBUG` — set to `0` in production
- `DATABASE_URL` — a Postgres connection URL (e.g. from Supabase, Railway, Neon)
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

Optional (only if you use S3-compatible storage instead of Cloudinary)
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_STORAGE_BUCKET_NAME`
- `AWS_S3_ENDPOINT_URL` (for R2/Spaces when needed)

Build & runtime behavior
- Vercel will route all traffic to the Python function at `api/wsgi.py` (see `vercel.json`).
- During the build, Vercel will install dependencies from `requirements.txt`.

Recommended workflow
1. Provision a managed Postgres database (Supabase, Neon, Railway, Render) and set `DATABASE_URL` in Vercel.
2. Create a Cloudinary account and set the three `CLOUDINARY_*` env vars in Vercel.
3. Add `SECRET_KEY` and set `DEBUG=0`.
4. Deploy the project from the repository to Vercel.

Notes about migrations & collectstatic
- Because Vercel serverless functions are not persistent and deployments are ephemeral, running migrations automatically on every deploy is brittle.
- Recommended: run migrations from a CI job, or run them manually via a managed runner (Railway, Supabase SQL, or an administrative container). Example using `psql`/Supabase is documented by your DB provider.
- Static files: if you use Cloudinary for media and static files, set `STATICFILES_STORAGE` accordingly. Otherwise run `python manage.py collectstatic --noinput` in CI and upload results to your static CDN/storage.

Troubleshooting
- If the function fails with import errors, ensure `requirements.txt` lists all runtime packages and that Vercel installed them (check deployment logs).
- If uploads disappear, confirm Cloudinary env vars are set and `DEFAULT_FILE_STORAGE` is `cloudinary_storage.storage.MediaCloudinaryStorage`.

If you'd like, I can:
- Add a simple GitHub Actions workflow to run migrations and collectstatic during CI before telling Vercel to redeploy.
- Convert static files to be uploaded to Cloudinary during the build step.
- Test a local simulated serverless run.

