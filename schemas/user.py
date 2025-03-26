from pydantic import BaseModel, EmailStr

# Esquema para el registro de usuario
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str

# Esquema para el inicio de sesión
class UserLogin(BaseModel):
    email: EmailStr
    password: str
