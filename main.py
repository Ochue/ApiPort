import os
from fastapi import FastAPI
from routes import auth, portfolio
from database import engine
from models.portfolio import Portfolio
import uvicorn

app = FastAPI()

# Crear las tablas en la base de datos al iniciar la aplicación
Portfolio.metadata.create_all(bind=engine)

# Incluir los routers para auth y portfolio
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(portfolio.router, prefix="/portfolio", tags=["Portfolio"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Portfolio API!"}

if __name__ == "__main__":
    # Obtener el puerto desde las variables de entorno de Render (o usar 8000 por defecto)
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
