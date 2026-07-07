import base64
import hashlib
import hmac
import os
from typing import Optional

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from sqlalchemy import String
from sqlalchemy.types import TypeDecorator

from app.core.config import settings


def _chave_aes() -> bytes:
    return hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()


def _iv_deterministico(valor: str) -> bytes:
    # IV derivado via HMAC(chave, valor) -> mesma entrada sempre gera o mesmo IV,
    # tornando a cifra determinística sem recorrer a ECB.
    return hmac.new(_chave_aes(), valor.encode("utf-8"), hashlib.sha256).digest()[:16]


def criptografar(valor: str) -> str:
    chave = _chave_aes()
    iv = _iv_deterministico(valor)
    padder = padding.PKCS7(128).padder()
    dados_paddados = padder.update(valor.encode("utf-8")) + padder.finalize()
    cifrador = Cipher(algorithms.AES(chave), modes.CBC(iv)).encryptor()
    cifrado = cifrador.update(dados_paddados) + cifrador.finalize()
    return base64.b64encode(iv + cifrado).decode("utf-8")


def descriptografar(valor_cifrado: str) -> str:
    bruto = base64.b64decode(valor_cifrado)
    iv, cifrado = bruto[:16], bruto[16:]
    decifrador = Cipher(algorithms.AES(_chave_aes()), modes.CBC(iv)).decryptor()
    dados_paddados = decifrador.update(cifrado) + decifrador.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    return (unpadder.update(dados_paddados) + unpadder.finalize()).decode("utf-8")


def gerar_cpf_hash(cpf_limpo: str) -> str:
    return hashlib.sha256(cpf_limpo.encode("utf-8")).hexdigest()


def criptografar_com_chave(valor: str, chave: bytes) -> str:
    """AES-256-CBC com IV aleatório e uma chave arbitrária (ex: derivada de um PIN via
    PBKDF2). Usado para os dados médicos da Ficha SOS — a chave nunca é persistida."""
    iv = os.urandom(16)
    padder = padding.PKCS7(128).padder()
    dados_paddados = padder.update(valor.encode("utf-8")) + padder.finalize()
    cifrador = Cipher(algorithms.AES(chave), modes.CBC(iv)).encryptor()
    cifrado = cifrador.update(dados_paddados) + cifrador.finalize()
    return base64.b64encode(iv + cifrado).decode("utf-8")


def descriptografar_com_chave(valor_cifrado: str, chave: bytes) -> str:
    bruto = base64.b64decode(valor_cifrado)
    iv, cifrado = bruto[:16], bruto[16:]
    decifrador = Cipher(algorithms.AES(chave), modes.CBC(iv)).decryptor()
    dados_paddados = decifrador.update(cifrado) + decifrador.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    return (unpadder.update(dados_paddados) + unpadder.finalize()).decode("utf-8")


class CpfCriptografado(TypeDecorator):
    """Criptografa/descriptografa CPF com AES-256-CBC determinístico.

    A chave vem de SECRET_KEY (global, nunca por tenant) para permitir busca
    global do Super Admin via cpf_hash (SHA-256), que deve ser indexado.
    """

    impl = String
    cache_ok = True

    def process_bind_param(self, value: Optional[str], dialect) -> Optional[str]:
        if value is None:
            return None
        return criptografar(value)

    def process_result_value(self, value: Optional[str], dialect) -> Optional[str]:
        if value is None:
            return None
        return descriptografar(value)
