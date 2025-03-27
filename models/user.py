from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)  # Cambié 'username' por 'full_name'
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)  # Este campo debería coincidir con el nombre en el controlador
    token = Column(String(512), index=True, nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, full_name={self.full_name}, email={self.email})>"
