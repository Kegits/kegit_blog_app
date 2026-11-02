Deploying this Django app to Vercel (serverless) — Notes

Overview
- This repo includes a `vercel.json` routing requests through the serverless entry at `api/index.py`.
- The app uses Cloudinary for media (recommended) in production; local development continues to use the `media/` folder unless you set Cloudinary env vars.
- Important: Vercel serverless functions run on ephemeral storage — you MUST use Cloudinary (or other external storage) for user uploads and a managed Postgres for the database.

Required environment variables (set these in the Vercel Project > Settings > Environment Variables)
- `SECRET_KEY` — your Django secret key
- `DEBUG` — set to `0` in production
- `DATABASE_URL` — a Postgres connection URL (e.g. from Supabase, Railway, Neon)
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

For the GitHub Actions deployment workflow, configure these as repository Actions secrets: `DATABASE_URL`, `SECRET_KEY`, all three `CLOUDINARY_*` variables, `VERCEL_TOKEN`, `VERCEL_ORG_ID`, and `VERCEL_PROJECT_ID`.

Optional (only if you use S3-compatible storage instead of Cloudinary)
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_STORAGE_BUCKET_NAME`
- `AWS_S3_ENDPOINT_URL` (for R2/Spaces when needed)

Build & runtime behavior
- Vercel routes application requests to the Python function at `api/index.py` (see `vercel.json`).
- During the build, Vercel will install dependencies from `requirements.txt`.

Recommended workflow
1. Provision a managed Postgres database (Supabase, Neon, Railway, Render) and set `DATABASE_URL` in Vercel.
2. Create a Cloudinary account and set the three `CLOUDINARY_*` env vars in Vercel.
3. Add `SECRET_KEY` and set `DEBUG=0`.
4. Deploy the project from the repository to Vercel.

Notes about migrations & collectstatic
- Because Vercel serverless functions are not persistent and deployments are ephemeral, running migrations automatically on every deploy is brittle.
- Migrations run in the GitHub Actions workflow before deployment. Avoid running them during Vercel's build because build attempts can be retried.
- Vercel serves `/static/*` from the tracked `staticfiles/` directory. After changing files under `portfolio/static/`, run `python manage.py collectstatic --noinput` and include the updated files in `staticfiles/` in the deployment commit. To store static files in Cloudinary instead, set `CLOUDINARY_USE_FOR_STATIC=1`; Django 5.2 selects that backend through `STORAGES`.

Troubleshooting
- If the function fails with import errors, ensure `requirements.txt` lists all runtime packages and that Vercel installed them (check deployment logs).
- If uploads disappear, confirm the three `CLOUDINARY_*` environment variables are set. With Django 5.2, media storage is selected through `STORAGES` and uses `coolweb.storage.CloudinaryDirectStorage`.

Community features
- Signed-in users can comment on public posts. `@username` mentions link to that user's public stories and create an in-app notification.
- Private one-to-one conversations are visible only to their two participants in the app. Messages are stored as regular database text and are not end-to-end encrypted.
- Apply the new `portfolio` and `messaging` migrations to the configured Postgres database before using these features. The GitHub Actions workflow runs migrations before deployment when its database secret is configured.
