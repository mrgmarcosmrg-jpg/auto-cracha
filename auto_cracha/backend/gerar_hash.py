from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
senha = "Admin0123456"
hash_correto = pwd_context.hash(senha)
print(f"Hash bcrypt: {hash_correto}")
