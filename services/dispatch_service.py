from sqlalchemy.orm import Session
from models.dispatch import Dispatch, DispatchItem
from models.requirement import Requirement
from models.warehouse import Warehouse
from models.movement import Movement
from services.inventory_service import get_or_create_inventory
from datetime import datetime


def create_dispatch(db: Session, requirement_id, items, user_id=1):
    """
    items = [
        {"material_id": 1, "qty": 5},
        {"material_id": 2, "qty": 3}
    ]
    """


    if not items or len(items) == 0:
        return False, "Debe seleccionar al menos un material y cantidad para despachar."

    req = db.query(Requirement).filter(
        Requirement.id == requirement_id
    ).first()

    if not req:
        return False, "Requerimiento no existe"

    # Obtener almacén principal
    principal = db.query(Warehouse).filter(
        Warehouse.type == "principal"
    ).first()

    dispatch = Dispatch(
        requirement_id=requirement_id,
        dispatch_date=datetime.utcnow(),
        user_id=user_id,
        guia_number=f"GR-{datetime.utcnow().timestamp()}"
    )

    db.add(dispatch)
    db.commit()
    db.refresh(dispatch)

    all_fulfilled = True

    for item in items:
        material_id = item["material_id"]
        qty = item["qty"]

        # Buscar item del requerimiento
        req_item = next(
            (i for i in req.items if i.material_id == material_id),
            None
        )

        if not req_item:
            continue

        pendiente = req_item.requested_qty - req_item.fulfilled_qty

        if qty > pendiente:
            return False, "Cantidad excede lo solicitado"

        # INVENTARIO
        inventory = get_or_create_inventory(
            db, principal.id, material_id
        )

        if inventory.stock < qty:
            return False, "Stock insuficiente"

        # 🔥 CONSUMO REAL
        inventory.stock -= qty
        inventory.reserved -= qty
        if inventory.reserved < 0:
            inventory.reserved = 0

        # actualizar requerimiento item
        req_item.fulfilled_qty += qty

        if req_item.fulfilled_qty == req_item.requested_qty:
            req_item.status = "fulfilled"
        else:
            req_item.status = "partial"
            all_fulfilled = False

        # guardar dispatch item
        dispatch_item = DispatchItem(
            dispatch_id=dispatch.id,
            material_id=material_id,
            dispatched_qty=qty
        )
        db.add(dispatch_item)

        # 🔁 MOVIMIENTO
        movement = Movement(
            warehouse_id=principal.id,
            material_id=material_id,
            qty_change=-qty,
            movement_type="OUT",
            reference_type="dispatch",
            reference_id=dispatch.id,
            user_id=user_id
        )
        db.add(movement)

    # estado del requerimiento
    if all_fulfilled:
        req.status = "fulfilled"
    else:
        req.status = "partial"

    db.commit()

    return True, "Despacho realizado correctamente"

def get_dispatches(db: Session):
    return db.query(Dispatch).all()

def cancel_dispatch(db: Session, dispatch_id):
    dispatch = db.query(Dispatch).filter(
        Dispatch.id == dispatch_id
    ).first()

    if not dispatch:
        return False

    for item in dispatch.items:
        # Revertir inventario
        inventory = get_or_create_inventory(
            db, dispatch.requirement.warehouse_id_obra, item.material_id
        )
        inventory.stock += item.dispatched_qty

        # Revertir requerimiento item
        req_item = next(
            (i for i in dispatch.requirement.items if i.material_id == item.material_id),
            None
        )

        if req_item:
            req_item.fulfilled_qty -= item.dispatched_qty
            if req_item.fulfilled_qty < 0:
                req_item.fulfilled_qty = 0

            req_item.status = "pending" 
            if req_item.fulfilled_qty == 0 :
                req_item.status = "fulfilled"
            else:
                req_item.status = "partial"

    dispatch.status = "cancelled"
    db.commit()
    return True


def get_dispatch_detail(db: Session, dispatch_id):
    return db.query(Dispatch).filter(
        Dispatch.id == dispatch_id
    ).first()

def remove_dispatch(db: Session, dispatch_id):
    dispatch = db.query(Dispatch).filter(
        Dispatch.id == dispatch_id
    ).first()

    if not dispatch:
        return False

    db.delete(dispatch)
    db.commit()
    return True