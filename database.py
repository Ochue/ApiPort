from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_base import Base  # Importa 'Base' desde db_base.py

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # Cambia esto si usas otro tipo de base de datos

# Crear el motor de base de datos
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Crear sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear las tablas
Base.metadata.create_all(bind=engine)
