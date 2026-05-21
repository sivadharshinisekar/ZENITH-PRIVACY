from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import httpx

from app.config import Settings, get_settings

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


@dataclass
class GoogleTokenBundle:
    access_token: str
    refresh_token: str | None
    expires_in: int | None


def exchange_authorization_code(code: str, redirect_uri: str, settings: Settings | None = None) -> GoogleTokenBundle:
    s = settings or get_settings()
    if not s.google_client_id or not s.google_client_secret:
        raise RuntimeError("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be configured")
    with httpx.Client(timeout=30.0) as client:
        r = client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": s.google_client_id,
                "client_secret": s.google_client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        r.raise_for_status()
        data = r.json()
    return GoogleTokenBundle(
        access_token=data["access_token"],
        refresh_token=data.get("refresh_token"),
        expires_in=data.get("expires_in"),
    )


def refresh_access_token(refresh_token: str, settings: Settings | None = None) -> GoogleTokenBundle:
    s = settings or get_settings()
    with httpx.Client(timeout=30.0) as client:
        r = client.post(
            GOOGLE_TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": s.google_client_id,
                "client_secret": s.google_client_secret,
            },
        )
        r.raise_for_status()
        data = r.json()
    return GoogleTokenBundle(
        access_token=data["access_token"],
        refresh_token=data.get("refresh_token") or refresh_token,
        expires_in=data.get("expires_in"),
    )


def fetch_google_email(access_token: str) -> str:
    with httpx.Client(timeout=30.0) as client:
        r = client.get(GOOGLE_USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"})
        r.raise_for_status()
        data = r.json()
    email = data.get("email")
    if not email:
        raise ValueError("Google userinfo did not return an email")
    return str(email).lower()


def expires_at_from_bundle(bundle: GoogleTokenBundle) -> datetime | None:
    if bundle.expires_in is None:
        return None
    return datetime.now(UTC) + timedelta(seconds=int(bundle.expires_in))
