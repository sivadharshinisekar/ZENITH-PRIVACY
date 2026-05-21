from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import User
from app.schemas import GoogleAuthRequest, TokenResponse
from app.security import create_access_token, encrypt_token
from app.services.google_oauth import exchange_authorization_code, expires_at_from_bundle, fetch_google_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/google", response_model=TokenResponse)
def auth_google(payload: GoogleAuthRequest, db: Session = Depends(get_db)) -> TokenResponse:
    settings = get_settings()
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured on the server",
        )
    try:
        bundle = exchange_authorization_code(payload.code, payload.redirect_uri, settings)
        email = fetch_google_email(bundle.access_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google authentication failed: {e}",
        ) from e

    user = db.scalar(select(User).where(User.email == email))
    if user is None:
        user = User(email=email)
        db.add(user)
        db.flush()

    if bundle.refresh_token:
        user.google_refresh_token_enc = encrypt_token(bundle.refresh_token, settings)
    user.google_access_token_enc = encrypt_token(bundle.access_token, settings)
    user.google_token_expires_at = expires_at_from_bundle(bundle)
    if user.google_token_expires_at is None and bundle.expires_in is not None:
        user.google_token_expires_at = datetime.now(UTC) + timedelta(seconds=int(bundle.expires_in))
    db.commit()
    db.refresh(user)

    if not user.google_refresh_token_enc:
        # First-time login must request offline access (prompt=consent) so we receive refresh_token
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No refresh token returned. Re-authorize with prompt=consent to allow Gmail scans.",
        )

    token = create_access_token(user.id, settings)
    return TokenResponse(access_token=token, user_email=user.email)
