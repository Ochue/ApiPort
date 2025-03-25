from database import engine
from models import portfolio

# Crea todas las tablas
portfolio.Base.metadata.create_all(bind=engine)

print("Base de datos creada correctamente.")
