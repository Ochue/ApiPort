from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)  # Renombramos la columna
    token = Column(String(512), index=True, nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, full_name={self.full_name}, email={self.email})>"
