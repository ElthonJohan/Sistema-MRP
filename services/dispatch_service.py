from sqlalchemy.orm import Session
from models.dispatch import Dispatch, DispatchItem
from models.requirement import Requirement
from models.warehouse import Warehouse
from models.inventory import Inventory
from models.movement import Movement
from services.inventory_service import get_or_create_inventory
from datetime import datetime


def create_dispatch(db: Session, requirement_id, items, user_id=1):
    """
    items = [
        {"material_id": 1, "qty": 5},
        {"material_id": 2, "qty": 3}
    ]
    Returns (True, guia_number) on success or (False, error_message) on failure.
    """


    if not items or len(items) == 0:
        return False, "Debe seleccionar al menos un material y cantidad para despachar."

    req = db.query(Requirement).filter(
        Requirement.id == requirement_id
    ).first()

    if not req:
        return False, "Requerimiento no existe"

    obra = db.query(Warehouse).filter(Warehouse.id == req.warehouse_id_obra).first()
    if not obra:
        return False, "Almacén de obra no encontrado"

    principal = db.query(Warehouse).filter(
        Warehouse.owner_id == obra.owner_id,
        Warehouse.type == "principal"
    ).first()

    if not principal:
        return False, "No hay almacén principal configurado"

    # ── Fase 1: validar todo antes de tocar la BD ──────────────────────────────
    for item in items:
        material_id = item["material_id"]
        qty = item["qty"]

        req_item = next(
            (i for i in req.items if i.material_id == material_id), None
        )
        if not req_item:
            continue

        pendiente = req_item.requested_qty - req_item.fulfilled_qty
        if qty > pendiente:
            return False, f"Cantidad {qty} excede lo pendiente ({pendiente}) para el material seleccionado"

        # Validar que el item tiene stock reservado (no está en "pending")
        if req_item.status == "pending":
            material_name = req_item.material.name if req_item.material else f"Material {material_id}"
            return False, f"Material '{material_name}' no tiene stock reservado. Ve a Inventario para agregar stock al almacén principal."
        
        all_inv_check = db.query(Inventory).filter(
            Inventory.warehouse_id == principal.id,
            Inventory.material_id == material_id,
        ).all()
        total_principal_stock = sum(inv.stock for inv in all_inv_check)

        if total_principal_stock < qty:
            return False, "Stock insuficiente en el almacén principal para completar el despacho"

    # ── Fase 2: crear despacho y aplicar cambios en un solo commit ─────────────
    now = datetime.utcnow()

    dispatch = Dispatch(
        requirement_id=requirement_id,
        dispatch_date=now,
        user_id=user_id,
        guia_number="",
    )
    db.add(dispatch)
    db.flush()  # obtiene dispatch.id sin hacer commit

    dispatch.guia_number = f"GR-{now.strftime('%Y%m%d')}-{dispatch.id:05d}"

    for item in items:
        material_id = item["material_id"]
        qty = item["qty"]

        req_item = next(
            (i for i in req.items if i.material_id == material_id), None
        )
        if not req_item:
            continue

        # Distribute stock and reserved reduction across all budget records (FIFO)
        all_inv = db.query(Inventory).filter(
            Inventory.warehouse_id == principal.id,
            Inventory.material_id == material_id,
        ).order_by(Inventory.id).all()

        remaining_s = qty
        remaining_r = qty
        for inv in all_inv:
            if remaining_s <= 0 and remaining_r <= 0:
                break
            if remaining_s > 0:
                reduce_s = min(inv.stock, remaining_s)
                inv.stock -= reduce_s
                remaining_s -= reduce_s
            if remaining_r > 0:
                reduce_r = min(inv.reserved, remaining_r)
                inv.reserved -= reduce_r
                remaining_r -= reduce_r

        req_item.fulfilled_qty += qty
        if req_item.fulfilled_qty >= req_item.requested_qty:
            req_item.status = "fulfilled"
        else:
            req_item.status = "partial"

        dispatch_item = DispatchItem(
            dispatch_id=dispatch.id,
            material_id=material_id,
            dispatched_qty=qty,
        )
        db.add(dispatch_item)

        movement = Movement(
            warehouse_id=principal.id,
            material_id=material_id,
            qty_change=-qty,
            movement_type="OUT",
            reference_type="dispatch",
            reference_id=dispatch.id,
            budget_id=req.budget_id,
            user_id=user_id,
        )
        db.add(movement)

    # "fulfilled" cuando todos los ítems están completamente despachados; "partial" si queda saldo
    all_done = all(ri.fulfilled_qty >= ri.requested_qty for ri in req.items)
    req.status = "fulfilled" if all_done else "partial"

    db.commit()

    return True, dispatch.guia_number


def get_dispatches(db: Session):
    return db.query(Dispatch).all()


def cancel_dispatch(db: Session, dispatch_id):
    dispatch = db.query(Dispatch).filter(
        Dispatch.id == dispatch_id
    ).first()

    if not dispatch:
        return False

    _req = dispatch.requirement
    _bud_id   = getattr(_req, "budget_id", None) if _req else None
    _bud_name = getattr(_req, "budget_name", None) if _req else None
    for item in dispatch.items:
        # Revertir inventario (mismo proyecto que el requerimiento, si aplica)
        inventory = get_or_create_inventory(
            db, _req.warehouse_id_obra, item.material_id,
            budget_id=_bud_id, budget_name=_bud_name,
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



def delete_dispatch(db: Session, dispatch_id: int, owner_id: int):
    dispatch = (
        db.query(Dispatch)
        .join(Requirement, Dispatch.requirement_id == Requirement.id)
        .join(Warehouse, Requirement.warehouse_id_obra == Warehouse.id)
        .filter(Dispatch.id == dispatch_id, Warehouse.owner_id == owner_id)
        .first()
    )
    if not dispatch:
        return False, "Despacho no encontrado."

    req  = dispatch.requirement
    obra = db.query(Warehouse).filter(Warehouse.id == req.warehouse_id_obra).first()
    principal = (
        db.query(Warehouse)
        .filter(Warehouse.owner_id == obra.owner_id, Warehouse.type == "principal")
        .first()
    ) if obra else None

    has_receipt = dispatch.receipt is not None

    for d_item in list(dispatch.items):
        qty    = d_item.dispatched_qty
        mat_id = d_item.material_id

        if principal:
            p_inv = db.query(Inventory).filter(
                Inventory.warehouse_id == principal.id,
                Inventory.material_id  == mat_id,
            ).first()
            if p_inv:
                p_inv.stock    += qty
                p_inv.reserved += qty

        if has_receipt and obra:
            o_inv = db.query(Inventory).filter(
                Inventory.warehouse_id == obra.id,
                Inventory.material_id  == mat_id,
            ).first()
            if o_inv:
                o_inv.stock = max(0, o_inv.stock - qty)

        req_item = next((i for i in req.items if i.material_id == mat_id), None)
        if req_item:
            req_item.fulfilled_qty = max(0, req_item.fulfilled_qty - qty)
            if req_item.fulfilled_qty >= req_item.requested_qty:
                req_item.status = "fulfilled"
            elif req_item.fulfilled_qty > 0:
                req_item.status = "partial"
            else:
                req_item.status = "reserved"

    all_done = all(ri.fulfilled_qty >= ri.requested_qty for ri in req.items)
    any_done = any(
        ri.fulfilled_qty > 0 or ri.status in ("reserved", "partial")
        for ri in req.items
    )
    req.status = "fulfilled" if all_done else ("partial" if any_done else "pending")

    if has_receipt:
        db.delete(dispatch.receipt)

    db.query(Movement).filter(
        Movement.reference_type == "dispatch",
        Movement.reference_id   == dispatch_id,
    ).delete(synchronize_session=False)

    for d_item in list(dispatch.items):
        db.delete(d_item)
    db.delete(dispatch)
    db.commit()
    return True, ""
