from datetime import datetime, timedelta
from typing import Optional

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_pin_hasher = PasswordHasher()


def hash_password(senha: str) -> str:
    return pwd_context.hash(senha)


def verify_password(senha: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha, senha_hash)


def create_access_token(payload: dict, expires_minutes: Optional[int] = None) -> str:
    to_encode = payload.copy()
    expira_em = datetime.utcnow() + timedelta(minutes=expires_minutes or settings.JWT_EXPIRE_MINUTES)
    to_encode["exp"] = expira_em
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def hash_pin(pin: str) -> str:
    """Argon2id — usado para o PIN de 4 dígitos da Ficha SOS. O PIN em si nunca é
    armazenado; a chave de descriptografia dos dados médicos é derivada dele via PBKDF2
    em tempo de requisição (ver app.core.encryption)."""
    return _pin_hasher.hash(pin)


def verificar_pin(pin: str, pin_hash: str) -> bool:
    try:
        return _pin_hasher.verify(pin_hash, pin)
    except VerifyMismatchError:
        return False
