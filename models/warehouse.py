from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # principal | obra
    location = Column(String)
    
    movements = relationship("Movement", back_populates="warehouse")