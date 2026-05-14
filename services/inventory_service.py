from sqlalchemy.orm import Session
from models.inventory import Inventory
from models.material import Material
from models.movement import Movement

from models.warehouse import Warehouse
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
    newly_fulfilled = reprocess_requirements(db)
    return newly_fulfilled
    
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
    """
    Reserva stock para un requerimiento.
    Modifica inventory.reserved en la sesión pero NO hace commit.
    El llamador debe hacer commit después de todos los cambios.
    """
    inventory = db.query(Inventory).filter(
        Inventory.warehouse_id == warehouse_id,
        Inventory.material_id == material_id,
    ).first()

    if not inventory or (inventory.stock - inventory.reserved) < qty:
        return False

    inventory.reserved += qty
    inventory.last_updated = datetime.utcnow()
    db.add(inventory)  # Asegura que SQLAlchemy trackee los cambios
    return True

def release_reservation(db: Session, warehouse_id, material_id, qty):
    inventory = get_or_create_inventory(db, warehouse_id, material_id)

    inventory.reserved -= qty
    if inventory.reserved < 0:
        inventory.reserved = 0

    db.commit()
    
def get_inventory(db: Session):
    return db.query(Inventory).all()


def get_inventory_filtered(db: Session, skip: int = 0, limit: int = 10,
                           warehouse_name: str = None, material_name: str = None, stock: int = None):
    query = db.query(Inventory)

    if warehouse_name:
        query = query.join(Warehouse).filter(Warehouse.name.ilike(f"%{warehouse_name}%"))
    if material_name:
        query = query.join(Material).filter(Material.name.ilike(f"%{material_name}%"))
    if stock is not None:
        query = query.filter(Inventory.stock == stock)

    query = query.order_by(Inventory.last_updated.desc())

    total_count = query.count()

    # Aplicar paginación
    inventory = query.offset(skip).limit(limit).all()

    return inventory, total_count

def delete_inventory_record(db: Session, inventory_id: int) -> bool:
    inv = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if inv:
        db.delete(inv)
        db.commit()
        return True
    return False
