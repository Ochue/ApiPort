from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Cambia esta URL por la de tu base de datos
DATABASE_URL = "sqlite:///./test.db"

# Crea el motor de conexión
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Crea la sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

# Función para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
