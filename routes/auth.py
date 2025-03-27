from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.portfolio import Portfolio
from schemas.user import UserCreate, UserLogin
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer  # Asegúrate de importar esto

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "@Chuchoman23"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Crear la dependencia oauth2_scheme para obtener el token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")  # Definir oauth2_scheme correctamente

# Función para cifrar contraseñas
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Función para verificar contraseñas
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Función para generar token
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# REGISTRO
@router.post("/register")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user_data.password)
    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Aquí refrescamos el objeto para obtener el ID

    return {"message": "Usuario registrado correctamente", "user_id": new_user.id}

# LOGIN
@router.post("/login")
def login(user_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


# GET USER BY ID (INCLUYENDO EL PORTAFOLIO)
@router.get("/user/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):  # Aquí se pasa el token como dependencia
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado!")

    # Buscar el portafolio asociado a ese usuario
    portfolio = db.query(Portfolio).filter(Portfolio.user_id == user_id).first()

    # Crear respuesta con usuario y portafolio (si existe)
    response = {
        "user_id": user.id,
        "full_name": user.full_name,
        "email": user.email,
    }

    # Si el portafolio existe, lo añadimos a la respuesta
    if portfolio:
        response["portfolio"] = {
            "id": portfolio.id,
            "title": portfolio.title,  # Asumiendo que tu modelo Portfolio tiene estos campos
            "description": portfolio.description,
            "created_at": portfolio.created_at,
        }
    else:
        response["portfolio"] = "No portfolio found"

    return response
