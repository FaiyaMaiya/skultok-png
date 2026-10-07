# SkulTok

A Flask-based bilingual tutor for Papua New Guinea, served with a single-origin HTML frontend and Gemini API backend.

## Run locally on Windows

Use Python 3.13 or another supported Python version. From this directory:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Set `GEMINI_API_KEY` in a local `.env` file for development. The `.env` file is ignored by Docker and gcloud deployment contexts; do not copy it into the image or commit it. The app listens on `http://localhost:8080` by default and honors `PORT` when set.

## Deploy to Cloud Run

1. Enable the Cloud Run, Cloud Build, and Secret Manager APIs in your Google Cloud project.
2. Create a Secret Manager secret named `gemini-api-key` containing your Gemini API key. Do not put the key in a deploy command, Dockerfile, or source file.
3. Ensure the Cloud Run runtime service account has the **Secret Manager Secret Accessor** role on that secret.
4. From this directory, deploy the source (Cloud Build uses the included Dockerfile):

```powershell
gcloud run deploy skultok `
  --source . `
  --region us-central1 `
  --allow-unauthenticated `
  --set-secrets GEMINI_API_KEY=gemini-api-key:latest
```

Choose the region appropriate for your users and data requirements. Remove `--allow-unauthenticated` if the service should require authentication. The app defaults to the stable Gemini model `gemini-3.8-flash`; override it with the `GEMINI_MODEL` environment variable if needed for your account or model availability.

After deployment, test the returned service URL:

```powershell
Invoke-RestMethod "$SERVICE_URL/health"
Invoke-RestMethod -Method Post "$SERVICE_URL/api/chat" `
  -ContentType 'application/json' `
  -Body (@{message='Explain fractions using kaukau'; grade='Grade 8'; lang='English + Tok Pisin'} | ConvertTo-Json)
```

The frontend is served by Flask at `/`, and calls `/api/chat` on the same origin. `/health` is a lightweight liveness check. The service uses Gunicorn and binds to Cloud Run's injected `PORT`.
