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
    allow_origins=["http://localhost:5173", "https://apiport.onrender.com"],  # Dominios permitidos
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Métodos permitidos
    allow_headers=["*"],  # Cabeceras permitidas
    expose_headers=["*"],  # Cabeceras que se pueden exponer al cliente
    max_age=600,  # Tiempo en segundos que el navegador puede almacenar los resultados de la comprobación de CORS
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
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=HOST, port=PORT)
