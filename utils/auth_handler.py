from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from models.user import User  # Importa el modelo de usuario
from database import SessionLocal

# 🔑 Clave secreta y algoritmo de cifrado
SECRET_KEY = "@Chuchoman23"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# 🔐 Esquema de autenticación OAuth2 con contraseña
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # URL del endpoint de login

# 🔑 Configuración de bcrypt para el hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 🔹 Función para crear el hash de una contraseña
def hash_password(password: str):
    return pwd_context.hash(password)

# 🔹 Función para verificar la contraseña
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# 🔹 Función para autenticar al usuario
def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()  # Buscar por email
    if not user:
        print("❌ Usuario no encontrado")
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas",
        )
    if not verify_password(password, user.password):
        print("❌ Contraseña incorrecta")
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas",
        )

    print(f"✅ Usuario autenticado: {user.email}")
    return user  # Retorna el usuario si las credenciales son válidas

# 🔹 Función para crear un access token JWT
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta

    email = data.get("email")
    if not email:
        raise ValueError("❌ No se proporcionó un email en los datos del token")

    to_encode.update({"exp": expire, "sub": email})  # 'sub' contiene el email del usuario
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    print(f"🔑 Token generado: {encoded_jwt}")  # Imprimir token para depuración
    
    return encoded_jwt

# 🔹 Función para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🔹 Dependencia para obtener el usuario actual
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    print(f"🔍 Token recibido: {token}")  # Verifica que el token esté llegando
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodificar el token JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"🔍 Payload decodificado: {payload}")  # Verifica el contenido del token
        
        email: str = payload.get("sub")  # Extraer email del token
        if email is None:
            print("❌ No se encontró 'sub' en el token")
            raise credentials_exception
        
        # Buscar usuario en la base de datos
        user = db.query(User).filter(User.email == email).first()
        print(f"👤 Usuario encontrado: {user}")  # Verificar si el usuario existe
        
        if user is None:
            print("❌ Usuario no encontrado en la base de datos")
            raise credentials_exception
        
        return user  # Si el usuario es válido, retornamos el usuario
        
    except JWTError as e:
        print(f"❌ Error al decodificar JWT: {e}")
        raise credentials_exception
