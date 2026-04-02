from sqlalchemy import Column, Integer, String
from database import Base

class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    unit = Column(String)
    description = Column(String)