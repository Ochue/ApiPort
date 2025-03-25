from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from crud import authenticate_user, create_user
from database import SessionLocal
from passlib.context import CryptContext  # Importar la librería correcta
from models.user import User
from typing import Optional
from datetime import timedelta
from utils.auth_handler import create_access_token  # Asegúrate de importar esta función

router = APIRouter()

# Configuración del contexto para hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Modelo para los datos de registro
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

# Ruta para registrar un nuevo usuario
@router.post("/register")
async def register_user(register_request: RegisterRequest):
    db = SessionLocal()
    try:
        # Hash de la contraseña
        hashed_password = pwd_context.hash(register_request.password)

        # Crear el usuario
        user = User(username=register_request.username, email=register_request.email, password=hashed_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"message": "Usuario creado correctamente", "user_id": user.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error al crear el usuario: " + str(e))
    finally:
        db.close()

# Modelo para los datos de login
class LoginRequest(BaseModel):
    username: str
    password: str

# Ruta de login
@router.post("/login")
async def login(login_request: LoginRequest):
    db = SessionLocal()
    try:
        # Intentar autenticar al usuario
        user = authenticate_user(db, login_request.username, login_request.password)

        # Generar el token de acceso
        access_token_expires = timedelta(minutes=30)  # Expira en 30 minutos
        access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

        return {"message": "Login successful", "access_token": access_token, "token_type": "bearer"}

    except HTTPException as e:
        raise e
    finally:
        db.close()
