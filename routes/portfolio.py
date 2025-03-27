from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import json
import os
from io import BytesIO
from database import get_db
from models.portfolio import Portfolio
from models.user import User
from utils.auth_handler import get_current_user

router = APIRouter()

# 📌 Modelo para redes sociales
class SocialMedia(BaseModel):
    name: str
    link: HttpUrl  

    def dict(self, **kwargs):
        result = super().dict(**kwargs)
        result["link"] = str(result["link"])
        return result

# 📌 Modelo para proyectos
class ProjectRequest(BaseModel):
    title: str
    description: Optional[str] = None
    type_technologies: List[str]
    year: Optional[int] = None

# 📌 Modelo del portafolio (Solicitud)
class PortfolioRequest(BaseModel):
    full_name: str
    description: Optional[str] = None
    spoken_languages: List[str]  
    programming_languages: List[str]  
    projects: List[ProjectRequest]  
    social_links: List[SocialMedia]  

# 📌 **Ruta para crear un portafolio con archivos**
@router.post("/")
async def create_portfolio(
    portfolio_request: PortfolioRequest,
    cv_file: UploadFile = File(...),
    image_files: List[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 📌 Leer el archivo CV y convertirlo en binario
    cv_content = await cv_file.read()

    # 📌 Leer las imágenes y convertirlas en binario
    image_contents = []
    if image_files:
        for image in image_files:
            image_content = await image.read()
            image_contents.append(image_content)

    # 📌 Convertir los datos a formato JSON
    social_links = [{"name": s.name, "link": str(s.link)} for s in portfolio_request.social_links]
    projects = [
        {
            "title": p.title,
            "description": p.description,
            "type_technologies": p.type_technologies,
            "image_file": image_contents[i] if i < len(image_contents) else None,
            "year": p.year
        }
        for i, p in enumerate(portfolio_request.projects)
    ]

    # 📌 Crear la instancia del portafolio
    new_portfolio = Portfolio(
        user_id=current_user.id,
        full_name=portfolio_request.full_name,
        description=portfolio_request.description,
        spoken_languages=",".join(portfolio_request.spoken_languages),
        programming_languages=",".join(portfolio_request.programming_languages),
        projects=json.dumps(projects),
        social_links=json.dumps(social_links),
        cv_file=cv_content,
        image_files=image_contents
    )

    db.add(new_portfolio)
    db.commit()
    db.refresh(new_portfolio)

    return {
        "message": "Portafolio creado correctamente!",
        "portfolio_id": new_portfolio.id
    }

# 📌 **Ruta para obtener un portafolio**
@router.get("/{portfolio_id}")
async def get_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if portfolio is None:
        raise HTTPException(status_code=404, detail="Portafolio no encontrado")
    
    # 📌 Convertir archivos binarios a imágenes o archivos descargables
    cv_file = portfolio.cv_file
    image_files = portfolio.image_files

    return {
        "id": portfolio.id,
        "user_id": portfolio.user_id,
        "full_name": portfolio.full_name,
        "description": portfolio.description,
        "spoken_languages": portfolio.spoken_languages.split(","),
        "programming_languages": portfolio.programming_languages.split(","),
        "projects": json.loads(portfolio.projects),
        "social_links": json.loads(portfolio.social_links),
        "cv_file": cv_file,  # En formato binario
        "image_files": image_files  # Lista de archivos binarios
    }

# 📌 **Ruta para actualizar un portafolio**
@router.put("/{portfolio_id}")
async def update_portfolio(
    portfolio_id: int,
    portfolio_request: PortfolioRequest,
    cv_file: Optional[UploadFile] = File(None),
    image_files: List[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()

    if portfolio is None:
        raise HTTPException(status_code=404, detail="Portafolio no encontrado")

    if portfolio.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para actualizar este portafolio")

    # 📌 Leer el nuevo CV y convertirlo en binario si es necesario
    if cv_file:
        cv_content = await cv_file.read()
        portfolio.cv_file = cv_content

    # 📌 Leer las nuevas imágenes y convertirlas en binario si es necesario
    if image_files:
        image_contents = []
        for image in image_files:
            image_content = await image.read()
            image_contents.append(image_content)
        portfolio.image_files = image_contents

    # 📌 Actualizar campos
    portfolio.full_name = portfolio_request.full_name
    portfolio.description = portfolio_request.description
    portfolio.spoken_languages = ",".join(portfolio_request.spoken_languages)
    portfolio.programming_languages = ",".join(portfolio_request.programming_languages)

    projects = [
        {
            "title": p.title,
            "description": p.description,
            "type_technologies": p.type_technologies,
            "image_file": image_contents[i] if i < len(image_contents) else None,
            "year": p.year
        }
        for i, p in enumerate(portfolio_request.projects)
    ]
    
    portfolio.projects = json.dumps(projects)
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

    if portfolio.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este portafolio")

    db.delete(portfolio)
    db.commit()

    return {"message": "Portafolio eliminado correctamente!"}
