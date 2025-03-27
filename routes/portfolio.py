from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import json
import shutil
import os
from database import get_db
from models.portfolio import Portfolio
from models.user import User
from utils.auth_handler import get_current_user

router = APIRouter()

UPLOAD_DIR = "uploads/"
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Crear la carpeta si no existe

# 📌 Modelo para redes sociales
class SocialMedia(BaseModel):
    name: str
    link: HttpUrl  

    def dict(self, **kwargs):
        result = super().dict(**kwargs)
        result["link"] = str(result["link"])
        return result

# 📌 Modelo para proyectos (SIN link, con imagen)
class ProjectRequest(BaseModel):
    title: str
    description: Optional[str] = None
    image: Optional[str] = None  # Reemplazo del "link"

    def dict(self, **kwargs):
        return super().dict(**kwargs)

# 📌 Modelo del portafolio (Solicitud)
class PortfolioRequest(BaseModel):
    full_name: str
    description: Optional[str] = None
    type_technologies: List[str]  
    spoken_languages: List[str]  
    programming_languages: List[str]  
    projects: List[ProjectRequest]  
    social_links: List[SocialMedia]  

# 📌 **Ruta para crear un portafolio con archivos (CV, imagen y proyectos)**
@router.post("/")
async def create_portfolio(
    portfolio_request: PortfolioRequest,
    cv_file: UploadFile = File(None),
    image_file: UploadFile = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cv_path = None
    image_path = None

    # 📌 Guardar el archivo CV
    if cv_file:
        cv_path = f"{UPLOAD_DIR}{cv_file.filename}"
        with open(cv_path, "wb") as buffer:
            shutil.copyfileobj(cv_file.file, buffer)

    # 📌 Guardar el archivo de imagen
    if image_file:
        image_path = f"{UPLOAD_DIR}{image_file.filename}"
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image_file.file, buffer)

    # 📌 Convertir los datos a formato JSON
    social_links = [{"name": s.name, "link": str(s.link)} for s in portfolio_request.social_links]
    projects = [{"title": p.title, "description": p.description, "image": p.image} for p in portfolio_request.projects]

    # 📌 Crear la instancia del portafolio
    new_portfolio = Portfolio(
        user_id=current_user.id,
        full_name=portfolio_request.full_name,
        description=portfolio_request.description,
        type_technologies=",".join(portfolio_request.type_technologies),
        spoken_languages=",".join(portfolio_request.spoken_languages),
        programming_languages=",".join(portfolio_request.programming_languages),
        projects=json.dumps(projects),
        social_links=json.dumps(social_links),
        cv_file=cv_path,
        image_file=image_path
    )

    db.add(new_portfolio)
    db.commit()
    db.refresh(new_portfolio)

    return {
        "message": "Portafolio creado correctamente!",
        "portfolio_id": new_portfolio.id
    }

# 📌 **Ruta para obtener un portafolio con su CV e imagen**
@router.get("/{portfolio_id}")
async def get_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if portfolio is None:
        raise HTTPException(status_code=404, detail="Portafolio no encontrado")
    
    return {
        "id": portfolio.id,
        "user_id": portfolio.user_id,
        "full_name": portfolio.full_name,
        "description": portfolio.description,
        "type_technologies": portfolio.type_technologies.split(","),
        "spoken_languages": portfolio.spoken_languages.split(","),
        "programming_languages": portfolio.programming_languages.split(","),
        "projects": json.loads(portfolio.projects),
        "social_links": json.loads(portfolio.social_links),
        "cv_file": portfolio.cv_file,  # Ruta del CV
        "image_file": portfolio.image_file  # Ruta de la imagen
    }

# 📌 **Ruta para actualizar un portafolio**
@router.put("/{portfolio_id}")
async def update_portfolio(
    portfolio_id: int,
    portfolio_request: PortfolioRequest,
    cv_file: UploadFile = File(None),
    image_file: UploadFile = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()

    if portfolio is None:
        raise HTTPException(status_code=404, detail="Portafolio no encontrado")

    # 📌 Verificar que el portafolio pertenece al usuario autenticado
    if portfolio.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para actualizar este portafolio")

    # 📌 Guardar el nuevo CV si se sube
    if cv_file:
        cv_path = f"{UPLOAD_DIR}{cv_file.filename}"
        with open(cv_path, "wb") as buffer:
            shutil.copyfileobj(cv_file.file, buffer)
        portfolio.cv_file = cv_path  # Actualizar en la BD

    # 📌 Guardar la nueva imagen si se sube
    if image_file:
        image_path = f"{UPLOAD_DIR}{image_file.filename}"
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image_file.file, buffer)
        portfolio.image_file = image_path  # Actualizar en la BD

    # 📌 Actualizar campos
    portfolio.full_name = portfolio_request.full_name
    portfolio.description = portfolio_request.description
    portfolio.type_technologies = ",".join(portfolio_request.type_technologies)
    portfolio.spoken_languages = ",".join(portfolio_request.spoken_languages)
    portfolio.programming_languages = ",".join(portfolio_request.programming_languages)

    portfolio.projects = json.dumps([p.dict() for p in portfolio_request.projects])
    portfolio.social_links = json.dumps([s.dict() for s in portfolio_request.social_links])

    db.commit()
    db.refresh(portfolio)

    return {"message": "Portafolio actualizado correctamente!"}

# 📌 **Ruta para eliminar un portafolio**
@router.delete("/{portfolio_id}")
async def delete_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()

    if portfolio is None:
        raise HTTPException(status_code=404, detail="Portafolio no encontrado")

    # 📌 Verificar que el portafolio pertenece al usuario autenticado
    if portfolio.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este portafolio")

    # 📌 Eliminar archivos asociados
    if portfolio.cv_file and os.path.exists(portfolio.cv_file):
        os.remove(portfolio.cv_file)
    if portfolio.image_file and os.path.exists(portfolio.image_file):
        os.remove(portfolio.image_file)

    db.delete(portfolio)
    db.commit()

    return {"message": "Portafolio eliminado correctamente!"}
