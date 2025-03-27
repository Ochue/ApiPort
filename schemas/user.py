from pydantic import BaseModel, EmailStr

# Esquema para el registro de usuario (cuando se crea un nuevo usuario)
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr  # Para validar el email
    password: str

    class Config:
        from_attributes = True  # Cambiar orm_mode por from_attributes

# Esquema para el inicio de sesión
class LoginRequest(BaseModel):
    email: str
    password: str

# Esquema para representar la información de un usuario
class User(BaseModel):
    full_name: str
    email: EmailStr  # Usar EmailStr para validación de correo electrónico

    class Config:
        from_attributes = True  # Cambiar orm_mode por from_attributes
