from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, portfolio
from database import engine
from models.portfolio import Portfolio
import os

app = FastAPI()

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Prueba con ["http://localhost:3000", "https://tudominio.com"]
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],  # Agrega esto
    max_age=600,  # Agrega esto para mejorar rendimiento
)


# Crear las tablas en la base de datos al iniciar la aplicación
Portfolio.metadata.create_all(bind=engine)

# Incluir los routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Portfolio API!"}

if __name__ == "__main__":
    import uvicorn
    HOST = os.getenv("HOST", "127.0.0.1")  # Por defecto localhost
    PORT = int(os.getenv("PORT", 8000))    # Por defecto puerto 8000
    uvicorn.run(app, host=HOST, port=PORT)
