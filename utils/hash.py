from passlib.context import CryptContext

# Crear un contexto para hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Función para hashear contraseñas"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Función para verificar contraseñas hasheadas"""
    return pwd_context.verify(plain_password, hashed_password)
