from sqlalchemy import Column, Integer, String
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    firstName = Column(String, index=True)
    lastName = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True) # Assuming phone is optional
    username = Column(String, unique=True, index=True, nullable=False)
