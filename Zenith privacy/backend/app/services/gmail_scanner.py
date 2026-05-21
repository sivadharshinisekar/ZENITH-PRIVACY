from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.config import Settings, get_settings

GMAIL_READONLY = "https://www.googleapis.com/auth/gmail.readonly"


@dataclass
class GmailMessageMeta:
    message_id: str
    subject: str
    snippet: str
    from_header: str
    internal_date: datetime | None


def _build_credentials(
    access_token: str,
    refresh_token: str | None,
    token_expiry: datetime | None,
    settings: Settings,
) -> Credentials:

    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        scopes=[GMAIL_READONLY],
    )

    # REMOVE expiry completely
    creds.expiry = None

    return creds


def ensure_fresh_access_token(
    access_token: str,
    refresh_token: str | None,
    token_expiry: datetime | None,
    settings: Settings | None = None,
) -> tuple[str, datetime | None]:

    s = settings or get_settings()

    creds = _build_credentials(
        access_token,
        refresh_token,
        token_expiry,
        s,
    )

    try:
        creds.refresh(Request())
    except Exception:
        pass

    return creds.token or access_token, creds.expiry


def iter_recent_messages(
    access_token: str,
    refresh_token: str | None,
    token_expiry: datetime | None,
    max_messages: int,
    settings: Settings | None = None,
) -> tuple[list[GmailMessageMeta], str, datetime | None]:
    """
    Fetches up to max_messages recent message metadata (no full bodies).
    Returns (messages, fresh_access_token, fresh_expiry).
    """
    s = settings or get_settings()
    token, exp = ensure_fresh_access_token(access_token, refresh_token, token_expiry, s)
    creds = _build_credentials(token, refresh_token, exp, s)
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)

    out: list[GmailMessageMeta] = []
    page_token: str | None = None

    try:
        while len(out) < max_messages:
            batch = max(0, min(100, max_messages - len(out)))
            if batch == 0:
                break
            lst = (
                service.users()
                .messages()
                .list(userId="me", maxResults=batch, pageToken=page_token)
                .execute()
            )
            messages = lst.get("messages") or []
            page_token = lst.get("nextPageToken")
            for m in messages:
                mid = m.get("id")
                if not mid:
                    continue
                meta = (
                    service.users()
                    .messages()
                    .get(
                        userId="me",
                        id=mid,
                        format="metadata",
                        metadataHeaders=["From", "Subject", "Date"],
                    )
                    .execute()
                )
                headers = {h["name"].lower(): h["value"] for h in (meta.get("payload", {}) or {}).get("headers", [])}
                internal_ms = meta.get("internalDate")
                internal_dt: datetime | None = None
                if internal_ms:
                    internal_dt = datetime.fromtimestamp(int(internal_ms) / 1000.0, tz=UTC)
                out.append(
                    GmailMessageMeta(
                        message_id=mid,
                        subject=headers.get("subject", "") or "",
                        snippet=meta.get("snippet") or "",
                        from_header=headers.get("from", "") or "",
                        internal_date=internal_dt,
                    )
                )
                if len(out) >= max_messages:
                    break
            if not page_token:
                break
    except HttpError as e:
        raise RuntimeError(f"Gmail API error: {e}") from e

    # If refresh happened inside client, creds.token may have rotated
    final_token = creds.token or token
    final_exp = creds.expiry
    if final_exp and final_exp.tzinfo is None:
        final_exp = final_exp.replace(tzinfo=UTC)
    return out, final_token, final_exp
