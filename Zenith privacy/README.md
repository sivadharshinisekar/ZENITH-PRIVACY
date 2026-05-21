# Zenith Privacy

Full-stack app that connects a user’s Gmail (read-only), scans recent messages for common signup patterns, and shows a deduplicated list of services in a Next.js dashboard. FastAPI handles OAuth token exchange, encrypted token storage, Gmail API access, and persistence in PostgreSQL.

## Architecture

| Layer | Stack |
| --- | --- |
| Frontend | Next.js 16 (App Router), TypeScript, Tailwind CSS 4 |
| Backend | FastAPI, SQLAlchemy, Gmail API client |
| Database | PostgreSQL 16 |
| Auth | Google OAuth 2.0 (`gmail.readonly` + profile scopes), app-issued JWT for API calls |

## Prerequisites

- Node.js 20+ and npm
- Python 3.12+
- Docker (optional, for PostgreSQL)
- A [Google Cloud OAuth client](https://console.cloud.google.com/apis/credentials) (Web application)

### Google Cloud setup

1. Create a project and enable **Gmail API**.
2. OAuth consent screen: add scopes `openid`, `email`, `profile`, `https://www.googleapis.com/auth/gmail.readonly`.
3. Create **OAuth 2.0 Client ID** (Web). Authorized redirect URIs must include:
   - `http://localhost:3000/auth/callback` (local Next.js)
4. Copy **Client ID** and **Client secret** for the backend; copy **Client ID** for the frontend public env.

## Quick start

### 1. Database

```bash
docker compose up -d
```

This starts PostgreSQL on port `5432` with user/password/db `zenith` / `zenith` / `zenith_privacy` (see `docker-compose.yml`).

### 2. Backend

```bash
cd backend
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

Create `backend/.env` (see `backend/.env.example`):

- `DATABASE_URL` — default matches `docker-compose.yml`
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- `JWT_SECRET` — long random string
- `ENCRYPTION_KEY` — Fernet key, generate with:
  `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
- `FRONTEND_ORIGIN` — `http://localhost:3000`

Run API:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend

```bash
cd frontend
cp .env.local.example .env.local
# Edit .env.local: NEXT_PUBLIC_GOOGLE_CLIENT_ID, NEXT_PUBLIC_API_URL (default http://localhost:8000)

npm install
npm run dev
```

Open `http://localhost:3000`, sign in with Google (consent screen must return a **refresh token**; the app uses `prompt=consent` and `access_type=offline`), open the dashboard, then **Scan my emails**.

## API (FastAPI)

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/auth/google` | Body: `{ "code", "redirect_uri" }`. Exchanges Google code, stores encrypted Google tokens, returns JWT. |
| `POST` | `/scan-emails` | `Authorization: Bearer <jwt>`. Pulls recent messages (metadata + snippet only), runs detectors, upserts `accounts`. |
| `GET` | `/accounts` | `Authorization: Bearer <jwt>`. Query: `q`, `page`, `page_size`. |
| `GET` | `/health` | Liveness. |

## Security notes

- Only message **metadata** (From, Subject, internal date) and the Gmail **snippet** are processed in memory; full MIME bodies are not persisted.
- Google **refresh** and **access** tokens are encrypted at rest (Fernet) using `ENCRYPTION_KEY`.
- API access after login uses a **JWT** (`JWT_SECRET`). Use HTTPS in production and rotate secrets regularly.

## Project layout

```
backend/app/          # FastAPI application package
  routers/            # auth, scan, accounts
  services/           # Gmail client, OAuth exchange, heuristics
frontend/app/         # Next.js routes (login, dashboard, OAuth callback)
frontend/lib/         # API client, session storage, Google URL builder
```

## License

Provided as sample application code for evaluation and extension.
