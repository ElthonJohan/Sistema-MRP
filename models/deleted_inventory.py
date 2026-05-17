from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
from datetime import datetime


class DeletedInventory(Base):
    __tablename__ = "deleted_inventory"

    id             = Column(Integer, primary_key=True, index=True)
    original_id    = Column(Integer, nullable=True)
    warehouse_id   = Column(Integer, nullable=True)
    material_id    = Column(Integer, nullable=True)
    warehouse_name = Column(String, nullable=False)
    material_name  = Column(String, nullable=False)
    material_unit  = Column(String, nullable=True)
    unit_price     = Column(Float, default=0.0)
    unit_price_dol = Column(Float, default=0.0)
    stock          = Column(Integer, default=0)
    total_value    = Column(Float, default=0.0)
    deleted_at     = Column(DateTime, default=datetime.utcnow)
    status         = Column(String, default="pending")  # pending, lost, returned
    owner_id       = Column(Integer, nullable=True)
