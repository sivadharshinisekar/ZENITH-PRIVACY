from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Encrypted at rest (Fernet); access token rotated via refresh
    google_refresh_token_enc: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    google_access_token_enc: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    google_token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    accounts: Mapped[List["Account"]] = relationship("Account", back_populates="user", cascade="all, delete-orphan")


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (UniqueConstraint("user_id", "service_key", name="uq_user_service_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    service_name: Mapped[str] = mapped_column(String(255), nullable=False)
    service_key: Mapped[str] = mapped_column(String(255), nullable=False)  # normalized for dedupe
    sender_email: Mapped[str] = mapped_column(String(512), nullable=False)
    email_used: Mapped[str] = mapped_column(String(320), nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="accounts")
