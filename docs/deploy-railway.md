# Deploying AdminFlow to Railway

Live demo: [add URL after first deploy]

1. Push the repo to GitHub if it is not there already.
2. In Railway, create a new project and pick "Deploy from GitHub repo".
3. Select this repository and let Railway detect the Dockerfile.
4. In the Railway variables tab, add the values from `.env.example` that make sense for deployment:
   - `APP_NAME`
   - `APP_ENV=production`
   - `DATABASE_URL`
   - `SEED_ON_STARTUP`
   - `APP_HOST`
   - `APP_PORT`
   - `LOG_LEVEL`
   - `SECRET_KEY`
   - `ALLOWED_ORIGINS`
5. Deploy and wait for the build to finish.
6. Open `https://your-service-url/api/health` and make sure it returns `{"status":"ok"}` or the same JSON with spacing.
7. If that works, try `https://your-service-url/api/dashboard` and `https://your-service-url/api/reconciliation/suggestions`.

One honest note about SQLite on Railway: if you do not attach a volume, the DB file is ephemeral and you can lose it on redeploy. If you want the demo data to stick around, use a volume. For anything more serious than a demo, I would move this to PostgreSQL.
