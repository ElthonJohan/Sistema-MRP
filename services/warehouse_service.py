from sqlalchemy.orm import Session
from models.warehouse import Warehouse

# Crear
def create_warehouse(db: Session, name, type, location):
    warehouse = Warehouse(
        name=name,
        type=type,
        location=location
    )
    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)
    return warehouse

# Listar
def get_warehouses(db: Session):
    return db.query(Warehouse).all()

# Eliminar
def delete_warehouse(db: Session, warehouse_id):
    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if warehouse:
        db.delete(warehouse)
        db.commit()

# Actualizar
def update_warehouse(db: Session, warehouse_id, name, type, location):
    warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if warehouse:
        warehouse.name = name
        warehouse.type = type
        warehouse.location = location
        db.commit()