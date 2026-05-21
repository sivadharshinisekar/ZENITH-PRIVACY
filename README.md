# Zenith Privacy

Full-stack privacy intelligence platform that connects to a user’s Gmail account (read-only), scans recent emails for signup/activity patterns, and displays a deduplicated list of connected websites, apps, and services inside a modern dashboard.

FastAPI handles OAuth authentication, encrypted token storage, Gmail API integration, and PostgreSQL persistence. Next.js powers the frontend experience.

---

# Architecture

| Layer | Stack |
| --- | --- |
| Frontend | Next.js 16, React, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python, SQLAlchemy |
| Database | PostgreSQL (Supabase) |
| Authentication | Google OAuth 2.0 |
| Deployment | Render + Vercel |

---

# Features

- Google OAuth Login
- Gmail Read-Only Scanning
- Dynamic Website/App Detection
- Privacy Cleanup Dashboard
- Search & Filter
- Responsive UI
- Dark Mode
- JWT Authentication
- Encrypted Google Tokens
- PostgreSQL Persistence

---

# Google Cloud Setup

## 1. Create Google Cloud Project

Go to:

https://console.cloud.google.com/

---

## 2. Enable Gmail API

Enable:
- Gmail API

---

## 3. Configure OAuth Consent Screen

Add scopes:

- openid
- email
- profile
- https://www.googleapis.com/auth/gmail.readonly

---

## 4. Create OAuth Client ID

Type:
- Web Application

Authorized redirect URIs:

### Local
http://localhost:3000/auth/callback

### Production
https://your-frontend-domain.vercel.app/auth/callback

---

# Backend Setup

## Navigate to backend

```bash
cd backend
```

---

## Create virtual environment

### Windows

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## Install dependencies

```bash
pip install -r requirements.txt
```

---

## Create `.env`

Create:

```bash
backend/.env
```

Example:

```env
DATABASE_URL=your_supabase_database_url

GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

JWT_SECRET=your_jwt_secret

ENCRYPTION_KEY=your_encryption_key

FRONTEND_ORIGIN=http://localhost:3000
```

---

## Generate Encryption Key

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy generated key into:

```env
ENCRYPTION_KEY=
```

---

## Run Backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend runs at:

```bash
http://127.0.0.1:8000
```

---

# Frontend Setup

## Navigate to frontend

```bash
cd frontend
```

---

## Install dependencies

```bash
npm install
```

---

## Create `.env.local`

Create:

```bash
frontend/.env.local
```

Example:

```env
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id

NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Run Frontend

```bash
npm run dev
```

Frontend runs at:

```bash
http://localhost:3000
```

---

# API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/auth/google` | Google OAuth token exchange |
| POST | `/scan-emails` | Scan Gmail messages |
| GET | `/accounts` | Get detected services |
| GET | `/health` | Health check |

---

# Security

- Gmail Read-Only Access
- Encrypted Google Tokens
- JWT Authentication
- No Password Storage
- Secure OAuth Flow
- Environment Variable Protection

---

# Project Structure

```bash
backend/
├── app/
│   ├── routers/
│   ├── services/
│   ├── models.py
│   ├── database.py
│   └── main.py
│
├── requirements.txt
└── .env

frontend/
├── app/
├── lib/
├── public/
├── components/
└── .env.local
```

---

# Deployment

## Backend
- Render

## Frontend
- Vercel

## Database
- Supabase PostgreSQL

---

# Future Enhancements

- AI Privacy Risk Scoring
- Automatic Unsubscribe System
- Data Breach Monitoring
- Browser Extension
- One-Click Cleanup
- Multi-Provider Support (Outlook/Yahoo)

---


# License

This project is developed for educational, research, and privacy-awareness purposes.
