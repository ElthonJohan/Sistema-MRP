from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)

    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    material_id = Column(Integer, ForeignKey("materials.id"))

    stock = Column(Integer, default=0)
    reserved = Column(Integer, default=0)

    last_updated = Column(DateTime, default=datetime.utcnow)
    
    warehouse = relationship("Warehouse", back_populates="inventory")
    material = relationship("Material", back_populates="inventory")