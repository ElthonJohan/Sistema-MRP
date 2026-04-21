from sqlalchemy.orm import Session
from models.warehouse import Warehouse
from models.requirement import Requirement, RequirementItem
from services.inventory_service import reserve_stock
from datetime import datetime

def create_requirement(db: Session, warehouse_id, items):
    """
    items = [
        {"material_id": 1, "qty": 10},
        {"material_id": 2, "qty": 5}
    ]
    """

    requirement = Requirement(
        warehouse_id_obra=warehouse_id,
        created_at=datetime.utcnow(),
        status="pending"
    )

    db.add(requirement)
    db.commit()
    db.refresh(requirement)

    all_fulfilled = True
    
    principal_warehouse = db.query(Warehouse).filter(Warehouse.type == "principal").first()
    
    if not principal_warehouse:
        return False, "No hay almacén principal configurado. Por favor crea uno primero."
    
    principal_id = principal_warehouse.id

    for item in items:
        material_id = item["material_id"]
        qty = item["qty"]
        
    

        reserved = reserve_stock(db, principal_id, material_id, qty)

        status = "reserved" if reserved else "pending"

        if not reserved:
            all_fulfilled = False

        req_item = RequirementItem(
            requirement_id=requirement.id,
            material_id=material_id,
            requested_qty=qty,
            fulfilled_qty=0,
            status=status
        )

        db.add(req_item)

    # estado global
    if all_fulfilled:
        requirement.status = "fulfilled"
    else:
        requirement.status = "partial"

    db.commit()
    return True, "Requerimiento creado exitosamente"

def get_requirements(db: Session):
    return db.query(Requirement).all()

def get_requirement_detail(db: Session, requirement_id):
    return db.query(Requirement).filter(
        Requirement.id == requirement_id
    ).first()
    
from services.inventory_service import release_reservation

def cancel_requirement(db: Session, requirement_id):
    req = get_requirement_detail(db, requirement_id)

    if not req:
        return False

    for item in req.items:
        release_reservation(
            db,
            req.warehouse_id_obra,
            item.material_id,
            item.requested_qty
        )

    req.status = "cancelled"
    db.commit()
    return True


def reprocess_requirements(db: Session):
    from models.requirement import Requirement
    from models.warehouse import Warehouse
    from services.inventory_service import reserve_stock

    principal = db.query(Warehouse).filter(
        Warehouse.type == "principal"
    ).first()

    requirements = db.query(Requirement).filter(
        Requirement.status.in_(["pending", "partial"])
    ).all()

    for req in requirements:
        all_reserved = True

        for item in req.items:
            if item.status == "pending":

                success = reserve_stock(
                    db,
                    principal.id,
                    item.material_id,
                    item.requested_qty
                )

                if success:
                    item.status = "reserved"
                else:
                    all_reserved = False

        # estado global
        if all_reserved:
            req.status = "fulfilled"
        else:
            req.status = "partial"

    db.commit()

# def reprocess_requirements(db: Session):
    from models.requirement import Requirement
    from services.inventory_service import reserve_stock

    requirements = db.query(Requirement).filter(
        Requirement.status.in_(["pending", "partial"])
    ).all()

    for req in requirements:
        all_reserved = True

        for item in req.items:
            
            if item.status == "pending":
                faltante = item.requested_qty - item.fulfilled_qty
                success = reserve_stock(
                    db,
                    req.warehouse_id_obra,  # ⚠️ idealmente almacén principal
                    item.material_id,
                    faltante
                )

                if success:
                    item.status = "reserved"
                else:
                    all_reserved = False

        # actualizar estado global
        if all_reserved:
            req.status = "fulfilled"
        else:
            req.status = "partial"

    db.commit()