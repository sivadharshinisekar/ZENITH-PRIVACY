import re
from dataclasses import dataclass
from email.utils import parseaddr


@dataclass(frozen=True)
class DetectionResult:
    service_name: str
    sender_address: str
    email_used: str


SIGNUP_KEYWORDS = (
    "welcome to",
    "verify your email",
    "confirm your account",
    "thanks for signing up",
    "confirm your email",
    "activate your account",
    "complete your registration",
)


def _normalize_service_name(name: str) -> str:
    n = re.sub(r"\s+", " ", name.strip())
    if len(n) > 120:
        n = n[:117] + "..."
    return n


def _service_key(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip()).lower()


def _domain_from_address(addr: str) -> str:
    if "@" in addr:
        return addr.rsplit("@", 1)[-1].lower()
    return addr.lower()


def _title_from_domain(domain: str) -> str:
    parts = domain.split(".")
    if len(parts) >= 2:
        return parts[-2].replace("-", " ").title()
    return domain.title()


def _extract_welcome_service(subject: str, snippet: str) -> str | None:
    combined = f"{subject}\n{snippet}"
    m = re.search(
        r"welcome\s+to\s+([^\n\r\.!?\[\]<>\"]{2,80})",
        combined,
        flags=re.IGNORECASE,
    )
    if m:
        return _normalize_service_name(m.group(1))
    return None


def _extract_from_display_name(from_header: str) -> str | None:
    display, addr = parseaddr(from_header)
    if display and len(display.strip()) > 1:
        # Drop common automated prefixes
        d = re.sub(r"^(no-?reply|notifications?|mailer|support)\s*[|:,-]?\s*", "", display, flags=re.I).strip()
        if len(d) > 1 and "@" not in d:
            return _normalize_service_name(d)
    if addr:
        return _title_from_domain(_domain_from_address(addr))
    return None


def detect_account(
    *,
    subject: str,
    snippet: str,
    from_header: str,
    user_email: str,
) -> DetectionResult | None:
    text = f"{subject}\n{snippet}".lower()
    if not any(k in text for k in SIGNUP_KEYWORDS):
        return None

    service = _extract_welcome_service(subject, snippet) or _extract_from_display_name(from_header)
    if not service:
        return None

    _, sender_addr = parseaddr(from_header)
    sender_addr = (sender_addr or "").strip().lower()
    if not sender_addr:
        return None

    return DetectionResult(
        service_name=service,
        sender_address=sender_addr,
        email_used=user_email.lower(),
    )


def service_key_for(name: str) -> str:
    return _service_key(name)
