from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.deps import get_current_user
from app.models import Account, User
from app.schemas import ScanEmailsResponse
from app.security import decrypt_token, encrypt_token
from app.services.account_detector import detect_account, service_key_for
from app.services.gmail_scanner import iter_recent_messages

router = APIRouter(tags=["scan"])


@router.post("/scan-emails", response_model=ScanEmailsResponse)
def scan_emails(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ScanEmailsResponse:
    settings = get_settings()
    refresh = decrypt_token(user.google_refresh_token_enc, settings)
    access = decrypt_token(user.google_access_token_enc, settings) or ""
    if not refresh:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Google refresh token. Sign in again with offline access (prompt=consent).",
        )
    try:
        messages, fresh_access, fresh_exp = iter_recent_messages(
            access_token=access,
            refresh_token=refresh,
            token_expiry=user.google_token_expires_at,
            max_messages=settings.gmail_max_messages,
            settings=settings,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e

    user.google_access_token_enc = encrypt_token(fresh_access, settings)
    user.google_token_expires_at = fresh_exp
    db.add(user)

    found = 0
    for msg in messages:
        hit = detect_account(
            subject=msg.subject,
            snippet=msg.snippet,
            from_header=msg.from_header,
            user_email=user.email,
        )
        if hit is None:
            continue
        detected_at = msg.internal_date or datetime.now(UTC)
        sk = service_key_for(hit.service_name)
        stmt = insert(Account).values(
            user_id=user.id,
            service_name=hit.service_name,
            service_key=sk,
            sender_email=hit.sender_address,
            email_used=hit.email_used,
            detected_at=detected_at,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=[Account.user_id, Account.service_key],
            set_={
                "service_name": stmt.excluded.service_name,
                "sender_email": stmt.excluded.sender_email,
                "email_used": stmt.excluded.email_used,
                "detected_at": stmt.excluded.detected_at,
            },
        )
        db.execute(stmt)
        found += 1

    db.commit()
    return ScanEmailsResponse(scanned_messages=len(messages), accounts_found=found)
