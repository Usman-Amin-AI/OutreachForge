import json
from typing import Dict
from cryptography.fernet import Fernet, InvalidToken
from .config import settings
from .compliance import redact_pii, audit_event, is_opted_out
from .logger import log


def _get_cipher() -> Fernet:
    return Fernet(settings.data_encryption_key.encode("utf-8"))


def encrypt_data(data: str) -> str:
    cipher = _get_cipher()
    encrypted = cipher.encrypt(data.encode("utf-8")).decode("utf-8")
    log("data_encrypted", length=len(encrypted))
    return encrypted


def decrypt_data(payload: str) -> str:
    cipher = _get_cipher()
    try:
        decrypted = cipher.decrypt(payload.encode("utf-8")).decode("utf-8")
        log("data_decrypted", length=len(decrypted))
        return decrypted
    except InvalidToken as exc:
        log("decryption_failed", error=str(exc))
        raise


def validate_contact(contact: str) -> bool:
    if not contact:
        return False
    opted_out = is_opted_out(contact)
    if opted_out:
        log("contact_opted_out", contact=contact)
    return not opted_out


def write_audit(action: str, data: Dict[str, str]) -> None:
    event = audit_event(action, data)
    with open(settings.audit_log_path, "a", encoding="utf-8") as writer:
        writer.write(json.dumps(event) + "\n")
