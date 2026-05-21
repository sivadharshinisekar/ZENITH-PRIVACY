from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Account, User
from app.schemas import AccountOut, AccountsPage

router = APIRouter(tags=["accounts"])


@router.get("/accounts", response_model=AccountsPage)
def list_accounts(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    q: str | None = Query(None, description="Filter by service name (case-insensitive contains)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
) -> AccountsPage:
    stmt = select(Account).where(Account.user_id == user.id)
    count_stmt = select(func.count()).select_from(Account).where(Account.user_id == user.id)
    if q and q.strip():
        like = f"%{q.strip()}%"
        stmt = stmt.where(Account.service_name.ilike(like))
        count_stmt = count_stmt.where(Account.service_name.ilike(like))

    total = int(db.scalar(count_stmt) or 0)
    stmt = stmt.order_by(Account.detected_at.desc()).offset((page - 1) * page_size).limit(page_size)
    rows = db.scalars(stmt).all()
    return AccountsPage(items=[AccountOut.model_validate(r) for r in rows], total=total, page=page, page_size=page_size)
