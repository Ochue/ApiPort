from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
import json
from database import SessionLocal
from models.portfolio import Portfolio
from models.user import User
from utils.auth_handler import get_current_user  # Importar la dependencia de autenticación

router = APIRouter()

# Modelo para redes sociales
class SocialMedia(BaseModel):
    name: str
    link: HttpUrl  # Validación para asegurarse de que sea un enlace válido

    def dict(self, **kwargs):
        # Convertir el enlace de la red social a string
        result = super().dict(**kwargs)
        result["link"] = str(result["link"])  # Asegúrate de convertir la URL a cadena
        return result

# Modelo para proyectos
class ProjectRequest(BaseModel):
    title: str
    description: Optional[str] = None
    link: HttpUrl

    def dict(self, **kwargs):
        # Convertir el enlace del proyecto a string
        result = super().dict(**kwargs)
        result["link"] = str(result["link"])  # Asegúrate de convertir la URL a cadena
        return result

# Modelo del portafolio
class PortfolioRequest(BaseModel):
    full_name: str
    description: Optional[str] = None
    technologies: List[str]  # Tecnologías usadas
    spoken_languages: List[str]  # Idiomas hablados
    programming_languages: List[str]  # Lenguajes de programación
    projects: List[ProjectRequest]  # Lista de proyectos
    social_links: List[SocialMedia]  # Redes sociales

# Ruta para crear un portafolio
@router.post("/")
async def create_portfolio(
    portfolio_request: PortfolioRequest,
    current_user: User = Depends(get_current_user),  # Cambiado a User, no dict
):
    db = SessionLocal()

    try:
        # Convertir los enlaces de redes sociales a texto (cadena de caracteres)
        social_links = [
            {"name": s.name, "link": str(s.link)} for s in portfolio_request.social_links
        ]
        
        # Convertir los enlaces de proyectos a texto (cadena de caracteres)
        projects = [
            {"title": p.title, "description": p.description, "link": str(p.link)} for p in portfolio_request.projects
        ]

        # Crear la instancia del portafolio
        new_portfolio = Portfolio(
            user_id=current_user.id,  # Ahora accedemos correctamente al id del usuario
            full_name=portfolio_request.full_name,
            description=portfolio_request.description,
            technologies=",".join(portfolio_request.technologies),
            spoken_languages=",".join(portfolio_request.spoken_languages),
            programming_languages=",".join(portfolio_request.programming_languages),
            projects=json.dumps(projects),  # Guardar proyectos como JSON
            social_links=json.dumps(social_links),  # Guardar redes sociales como JSON
            image_url=None  # No se manejará imagen
        )

        db.add(new_portfolio)
        db.commit()
        db.refresh(new_portfolio)

        return {"message": "Portafolio creado correctamente!", "portfolio_id": new_portfolio.id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error al crear el portafolio: {str(e)}")
    
    finally:
        db.close()

# Ruta para obtener un portafolio por ID
@router.get("/{portfolio_id}")
async def get_portfolio(portfolio_id: int):
    db = SessionLocal()
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if portfolio is None:
        raise HTTPException(status_code=404, detail="Portafolio no encontrado")
    return portfolio

# Ruta para actualizar un portafolio
@router.put("/{portfolio_id}")
async def update_portfolio(portfolio_id: int, portfolio_request: PortfolioRequest):
    db = SessionLocal()
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()

    if portfolio is None:
        raise HTTPException(status_code=404, detail="Portafolio no encontrado")

    # Actualizar campos
    portfolio.full_name = portfolio_request.full_name
    portfolio.description = portfolio_request.description
    portfolio.technologies = ",".join(portfolio_request.technologies)
    portfolio.spoken_languages = ",".join(portfolio_request.spoken_languages)
    portfolio.programming_languages = ",".join(portfolio_request.programming_languages)

    # Convertir proyectos y redes sociales a JSON serializable
    portfolio.projects = json.dumps([p.dict() for p in portfolio_request.projects])
    portfolio.social_links = json.dumps([s.dict() for s in portfolio_request.social_links])

    db.commit()
    db.refresh(portfolio)

    return portfolio

# Ruta para eliminar un portafolio
@router.delete("/{portfolio_id}")
async def delete_portfolio(portfolio_id: int):
    db = SessionLocal()
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()

    if portfolio is None:
        raise HTTPException(status_code=404, detail="Portafolio no encontrado")

    db.delete(portfolio)
    db.commit()

    return {"message": "Portafolio eliminado correctamente!"}
