# utils.py
import bcrypt

# Función para encriptar la contraseña
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()  # Genera un salt aleatorio
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

# Función para verificar la contraseña
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
