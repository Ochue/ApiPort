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

# 📌 Modelo para proyectos (con el nuevo nombre de campo "type_technologies" dentro de cada proyecto)
class ProjectRequest(BaseModel):
    title: str
    description: Optional[str] = None
    type_technologies: List[str]  # Ahora está dentro del proyecto
    image_file: Optional[UploadFile] = None  # Reemplazo de "image" por "image_file"
    year: Optional[int] = None

    def dict(self, **kwargs):
        return super().dict(**kwargs)

# 📌 Modelo del portafolio (Solicitud)
class PortfolioRequest(BaseModel):
    full_name: str
    description: Optional[str] = None
    spoken_languages: List[str]  
    programming_languages: List[str]  
    projects: List[ProjectRequest]  
    social_links: List[SocialMedia]  
    cv_file: UploadFile = File(...)

# 📌 **Ruta para crear un portafolio con archivos (CV, imagen y proyectos)**
@router.post("/")
async def create_portfolio(
    portfolio_request: PortfolioRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cv_path = None
    image_paths = []

    # 📌 Guardar el archivo CV
    if portfolio_request.cv_file:
        cv_path = f"{UPLOAD_DIR}{portfolio_request.cv_file.filename}"
        with open(cv_path, "wb") as buffer:
            shutil.copyfileobj(portfolio_request.cv_file.file, buffer)

    # 📌 Guardar las imágenes de los proyectos
    for project in portfolio_request.projects:
        if project.image_file:
            image_path = f"{UPLOAD_DIR}{project.image_file.filename}"
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(project.image_file.file, buffer)
            image_paths.append(image_path)

    # 📌 Convertir los datos a formato JSON
    social_links = [{"name": s.name, "link": str(s.link)} for s in portfolio_request.social_links]
    projects = [{"title": p.title, "description": p.description, "type_technologies": p.type_technologies, "image_file": image_paths[i] if i < len(image_paths) else None, "year": p.year} for i, p in enumerate(portfolio_request.projects)]

    # 📌 Crear la instancia del portafolio
    new_portfolio = Portfolio(
        user_id=current_user.id,
        full_name=portfolio_request.full_name,
        description=portfolio_request.description,
        spoken_languages=",".join(portfolio_request.spoken_languages),
        programming_languages=",".join(portfolio_request.programming_languages),
        projects=json.dumps(projects),
        social_links=json.dumps(social_links),
        cv_file=cv_path,
        image_file=image_paths[0] if image_paths else None  # Solo guardamos una imagen principal
    )

    db.add(new_portfolio)
    db.commit()
    db.refresh(new_portfolio)

    return {
        "message": "Portafolio creado correctamente!",
        "portfolio_id": new_portfolio.id,
        "cv_file": cv_path,  # Devuelve la ruta del CV
        "image_file": image_paths[0] if image_paths else None  # Devuelve la ruta de la imagen principal
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
        "spoken_languages": portfolio.spoken_languages.split(","),
        "programming_languages": portfolio.programming_languages.split(","),
        "projects": json.loads(portfolio.projects),
        "social_links": json.loads(portfolio.social_links),
        "cv_file": portfolio.cv_file,  # Ruta del CV
        "image_file": portfolio.image_file  # Ruta de la imagen principal
    }

# 📌 **Ruta para actualizar un portafolio**
@router.put("/{portfolio_id}")
async def update_portfolio(
    portfolio_id: int,
    portfolio_request: PortfolioRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()

    if portfolio is None:
        raise HTTPException(status_code=404, detail="Portafolio no encontrado")

    # 📌 Verificar que el portafolio pertenece al usuario autenticado
    if portfolio.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para actualizar este portafolio")

    cv_path = portfolio.cv_file  # Mantener la ruta del CV si no se cambia
    image_paths = [portfolio.image_file]  # Mantener la ruta de la imagen principal si no se cambia

    # 📌 Guardar el nuevo CV si se sube
    if portfolio_request.cv_file:
        cv_path = f"{UPLOAD_DIR}{portfolio_request.cv_file.filename}"
        with open(cv_path, "wb") as buffer:
            shutil.copyfileobj(portfolio_request.cv_file.file, buffer)
        portfolio.cv_file = cv_path  # Actualizar en la BD

    # 📌 Guardar nuevas imágenes de proyectos si se suben
    for i, project in enumerate(portfolio_request.projects):
        if project.image_file:
            image_path = f"{UPLOAD_DIR}{project.image_file.filename}"
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(project.image_file.file, buffer)
            image_paths[i] = image_path  # Actualizar la ruta de la imagen del proyecto

    # 📌 Actualizar campos
    portfolio.full_name = portfolio_request.full_name
    portfolio.description = portfolio_request.description
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
