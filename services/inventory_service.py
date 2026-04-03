from sqlalchemy.orm import Session
from models.inventory import Inventory
from models.movement import Movement
from datetime import datetime

def get_or_create_inventory(db: Session, warehouse_id, material_id):
    inventory = db.query(Inventory).filter(
        Inventory.warehouse_id == warehouse_id,
        Inventory.material_id == material_id
    ).first()

    if not inventory:
        inventory = Inventory(
            warehouse_id=warehouse_id,
            material_id=material_id,
            stock=0,
            reserved=0
        )
        db.add(inventory)
        db.commit()
        db.refresh(inventory)

    return inventory

def add_stock(db: Session, warehouse_id, material_id, qty, user_id):
    inventory = get_or_create_inventory(db, warehouse_id, material_id)

    from services.requirement_service import reprocess_requirements

    inventory.stock += qty
    inventory.last_updated = datetime.utcnow()

    movement = Movement(
        warehouse_id=warehouse_id,
        material_id=material_id,
        qty_change=qty,
        movement_type="IN",
        reference_type="manual",
        reference_id=None,
        user_id=user_id
    )

    db.add(movement)
    db.commit()
    reprocess_requirements(db)
    
def remove_stock(db: Session, warehouse_id, material_id, qty, user_id):
    inventory = get_or_create_inventory(db, warehouse_id, material_id)

    if inventory.stock < qty:
        return False

    inventory.stock -= qty
    inventory.last_updated = datetime.utcnow()

    movement = Movement(
        warehouse_id=warehouse_id,
        material_id=material_id,
        qty_change=-qty,
        movement_type="OUT",
        reference_type="manual",
        reference_id=None,
        user_id=user_id
    )

    db.add(movement)
    db.commit()
    return True

def reserve_stock(db: Session, warehouse_id, material_id, qty):
    inventory = get_or_create_inventory(db, warehouse_id, material_id)

    available = inventory.stock - inventory.reserved

    if available < qty:
        return False

    inventory.reserved += qty
    db.commit()
    return True

def release_reservation(db: Session, warehouse_id, material_id, qty):
    inventory = get_or_create_inventory(db, warehouse_id, material_id)

    inventory.reserved -= qty
    if inventory.reserved < 0:
        inventory.reserved = 0

    db.commit()
    
def get_inventory(db: Session):
    return db.query(Inventory).all()