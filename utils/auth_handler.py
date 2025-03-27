from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from models.user import User  # Importa el modelo de usuario
from database import SessionLocal

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Esquema de autenticación OAuth2 con contraseña
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # Cambié "token" a "login", la URL de tu ruta de login

# Configuración de bcrypt para el hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Función para crear el hash de una contraseña
def hash_password(password: str):
    return pwd_context.hash(password)

# Función para verificar la contraseña
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# Función para autenticar al usuario
def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()  # Buscar por email
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas",
        )
    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas",
        )

    return user  # Retorna el usuario si las credenciales son válidas

# Función para crear un access token JWT
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire, "sub": data["email"]})  # Usamos 'email' en lugar de 'sub' como identificador
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    # Imprimir el token generado para depuración
    print(f"Token generado: {encoded_jwt}")
    
    return encoded_jwt

# Función para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependencia para obtener el usuario actual
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    print(f"Token recibido: {token}")  # Verifica que el token esté llegando
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodificar el token JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")  # El email debe estar en el campo 'sub' del token
        
        if email is None:
            raise credentials_exception
        
        # Verificar que el usuario exista en la base de datos
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise credentials_exception
        
        return user  # Si el usuario es válido, retornamos el usuario
        
    except JWTError as e:
        print(f"Error al decodificar JWT: {e}")
        raise credentials_exception
