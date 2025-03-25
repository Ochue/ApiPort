from database import engine, Base  # Importa 'engine' y 'Base' de tu archivo de base de datos
from models.user import User  # Importa el modelo de 'User'

# Crea las tablas en la base de datos
Base.metadata.create_all(bind=engine)
