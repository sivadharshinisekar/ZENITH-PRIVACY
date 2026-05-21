from datetime import UTC, datetime, timedelta

from cryptography.fernet import Fernet, InvalidToken
from jose import JWTError, jwt

from app.config import Settings, get_settings


def _fernet(settings: Settings) -> Fernet:
    key = (settings.encryption_key or "").strip()
    if not key:
        raise RuntimeError(
            "ENCRYPTION_KEY is not set. Generate one with: "
            "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_token(plaintext: str | None, settings: Settings | None = None) -> str | None:
    if plaintext is None:
        return None
    f = _fernet(settings or get_settings())
    return f.encrypt(plaintext.encode()).decode()


def decrypt_token(ciphertext: str | None, settings: Settings | None = None) -> str | None:
    if not ciphertext:
        return None
    f = _fernet(settings or get_settings())
    try:
        return f.decrypt(ciphertext.encode()).decode()
    except InvalidToken:
        return None


def create_access_token(user_id: int, settings: Settings | None = None) -> str:
    s = settings or get_settings()
    expire = datetime.now(UTC) + timedelta(hours=s.jwt_exp_hours)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, s.jwt_secret, algorithm=s.jwt_algorithm)


def decode_access_token(token: str, settings: Settings | None = None) -> int | None:
    s = settings or get_settings()
    try:
        data = jwt.decode(token, s.jwt_secret, algorithms=[s.jwt_algorithm])
        sub = data.get("sub")
        return int(sub) if sub is not None else None
    except JWTError:
        return None
