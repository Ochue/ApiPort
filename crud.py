# crud.py
from sqlalchemy.orm import Session
from models.user import User
from utils import hash_password, verify_password  # Asegúrate de importar la función de hash
from fastapi import HTTPException

def create_user(db: Session, username: str, password: str):
    # Encriptar la contraseña antes de guardarla
    hashed_password = hash_password(password)
    
    # Crear el nuevo usuario
    db_user = User(username=username, password=hashed_password)
    
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Error creating user")
    
    return db_user


def authenticate_user(db: Session, username: str, password: str):
    db_user = db.query(User).filter(User.username == username).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verificar la contraseña
    if not verify_password(password, db_user.password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    
    return db_user