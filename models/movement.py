from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from database import Base

class Movement(Base):
    __tablename__ = "movements"

    id = Column(Integer, primary_key=True, index=True)

    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    material_id = Column(Integer, ForeignKey("materials.id"))

    qty_change = Column(Integer)
    movement_type = Column(String)

    reference_type = Column(String)
    reference_id = Column(Integer)

    user_id = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)