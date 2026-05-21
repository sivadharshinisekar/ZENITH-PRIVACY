from __future__ import annotations

from datetime import UTC, datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from sqlalchemy.orm import Session

from app.config import Settings
from app.models import User
from app.security import decrypt_token, encrypt_token


GMAIL_READONLY = "https://www.googleapis.com/auth/gmail.readonly"


def _creds_for_user(user: User, settings: Settings) -> Credentials | None:
    access = decrypt_token(user.google_access_token_enc, settings)
    refresh = decrypt_token(user.google_refresh_token_enc, settings)
    if not access and not refresh:
        return None
    return Credentials(
        token=access,
        refresh_token=refresh,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        scopes=[GMAIL_READONLY],
    )


def persist_credentials(user: User, creds: Credentials, db: Session, settings: Settings) -> None:
    user.google_access_token_enc = encrypt_token(creds.token, settings)
    user.google_refresh_token_enc = encrypt_token(creds.refresh_token, settings) if creds.refresh_token else user.google_refresh_token_enc
    if creds.expiry:
        user.google_token_expires_at = creds.expiry.replace(tzinfo=UTC) if creds.expiry.tzinfo is None else creds.expiry
    else:
        user.google_token_expires_at = datetime.now(UTC) + timedelta(hours=1)
    db.add(user)
    db.commit()
    db.refresh(user)


def ensure_valid_access_token(user: User, db: Session, settings: Settings) -> str:
    creds = _creds_for_user(user, settings)
    if creds is None:
        raise RuntimeError("Google tokens are missing; sign in again")

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        persist_credentials(user, creds, db, settings)
        if not creds.token:
            raise RuntimeError("Failed to refresh Google access token")
        return creds.token

    if creds.token and not creds.expired:
        return creds.token

    if creds.refresh_token:
        creds.refresh(Request())
        persist_credentials(user, creds, db, settings)
        if creds.token:
            return creds.token

    raise RuntimeError("Google access token is expired and cannot be refreshed")
