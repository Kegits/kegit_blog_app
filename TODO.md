# TODO: Configure Cloudinary for Media Storage

## Completed
- [x] Modified settings.py to require Cloudinary in production (DEBUG=False), fallback to local in development
- [x] Removed optional AWS/S3 settings to focus on Cloudinary
- [x] Copied default.jpg to media/profile_pics/default.jpg for local development compatibility
- [x] Updated scripts/upload_default.py to upload with correct public_id 'profile_pics/default'
- [x] Tested Docker build and startup with Cloudinary configuration - no errors, app starts successfully
- [x] Verified Cloudinary is used in production mode (DEBUG=False) without falling back to local storage

## Next Steps
- [ ] Set Cloudinary environment variables in Vercel deployment:
  - CLOUDINARY_CLOUD_NAME
  - CLOUDINARY_API_KEY
  - CLOUDINARY_API_SECRET
- [ ] Deploy to Vercel with Cloudinary env vars set
- [ ] Test profile picture upload on Vercel to confirm the original OSError is resolved
