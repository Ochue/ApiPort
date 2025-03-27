from sqlalchemy import Column, Integer, String, JSON
from database import Base

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)  # Relación con el usuario
    full_name = Column(String)
    description = Column(String, nullable=True)
    type_technologies = Column(String)  # Antes "technologies"
    spoken_languages = Column(String)
    programming_languages = Column(String)
    projects = Column(JSON)  # Guardamos proyectos en formato JSON
    social_links = Column(JSON)  # Guardamos enlaces sociales en formato JSON
    cv_file = Column(String, nullable=True)  # 📌 Nuevo campo para almacenar la ruta del CV
    image_file = Column(String, nullable=True)  # 📌 Nuevo campo para almacenar la ruta de la imagen
