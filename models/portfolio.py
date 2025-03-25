from sqlalchemy import Column, Integer, String
from sqlalchemy import JSON
from database import Base

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)  # Relación con el usuario
    full_name = Column(String)
    description = Column(String, nullable=True)
    technologies = Column(String)
    spoken_languages = Column(String)
    programming_languages = Column(String)
    projects = Column(JSON)  # Guardamos proyectos en formato JSON
    social_links = Column(JSON)  # Guardamos enlaces sociales en formato JSON
    image_url = Column(String, nullable=True)
