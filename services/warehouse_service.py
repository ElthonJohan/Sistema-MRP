from sqlalchemy.orm import Session
from models.warehouse import Warehouse

# Crear
def create_warehouse(db: Session, name, type, location):
    warehouse = Warehouse(
        name=name,
        type=type,
        location=location
    )
    
    already_exists = db.query(Warehouse).filter(Warehouse.name == name).first()
    
    if already_exists:
        return {"error": "El almacén ya existe"}
    
    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)
    return {"value": warehouse}

# Listar
def get_warehouses(db: Session):
    return db.query(Warehouse).all()


def get_warehouse(db: Session, warehouse_id):
    return db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()


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

        exists = db.query(Warehouse).filter(Warehouse.name == name, Warehouse.id != warehouse_id).first()
        
        if exists:
            return {"error": "Otro almacén con ese nombre ya existe"}
        
        warehouse.name = name
        warehouse.type = type
        warehouse.location = location
        db.commit()
        return {"value": "Almacén actualizado correctamente"}

