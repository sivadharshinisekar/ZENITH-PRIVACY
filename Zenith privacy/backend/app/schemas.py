from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class GoogleAuthRequest(BaseModel):
    code: str = Field(min_length=1)
    redirect_uri: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_email: EmailStr


class UserPublic(BaseModel):
    id: int
    email: EmailStr

    model_config = {"from_attributes": True}


class AccountOut(BaseModel):
    id: int
    service_name: str
    sender_email: str
    email_used: str
    detected_at: datetime

    model_config = {"from_attributes": True}


class AccountsPage(BaseModel):
    items: list[AccountOut]
    total: int
    page: int = 1
    page_size: int = 50


class ScanEmailsResponse(BaseModel):
    scanned_messages: int
    accounts_found: int
