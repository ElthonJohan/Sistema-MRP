from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
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

    # Optional link to the budget/project this stock belongs to
    budget_id   = Column(Integer, ForeignKey("budgets.id"), nullable=True)
    budget_name = Column(String, nullable=True)

    # False when the linked project was deleted — stock is frozen until redirected
    is_active = Column(Boolean, default=True, nullable=False)

    last_updated = Column(DateTime, default=datetime.utcnow)

    warehouse = relationship("Warehouse", back_populates="inventory")
    material  = relationship("Material", back_populates="inventory")
    budget    = relationship("Budget", foreign_keys=[budget_id])