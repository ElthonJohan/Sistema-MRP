from sqlalchemy.orm import Session
from models.receipt import Receipt, ReceiptItem
from models.dispatch import Dispatch
from models.movement import Movement
from services.inventory_service import get_or_create_inventory
from datetime import datetime


def create_receipt(db: Session, dispatch_id, user_id=1):

    dispatch = db.query(Dispatch).filter(
        Dispatch.id == dispatch_id
    ).first()

    if not dispatch:
        return False, "Despacho no existe"

    # 🔒 evitar duplicados
    if dispatch.receipt:
        return False, "Este despacho ya fue recibido"

    requirement = dispatch.requirement
    warehouse_obra = requirement.warehouse_id_obra

    receipt = Receipt(
        dispatch_id=dispatch_id,
        receipt_date=datetime.utcnow(),
        user_id=user_id
    )

    db.add(receipt)
    db.commit()
    db.refresh(receipt)

    for item in dispatch.items:
        material_id = item.material_id
        qty = item.dispatched_qty

        # 📦 INVENTARIO OBRA
        inventory = get_or_create_inventory(
            db, warehouse_obra, material_id
        )

        inventory.stock += qty

        # 📄 ITEM RECEIPT
        receipt_item = ReceiptItem(
            receipt_id=receipt.id,
            material_id=material_id,
            received_qty=qty,
            confirmed=True
        )
        db.add(receipt_item)

        # 🔁 MOVEMENT ENTRADA
        movement = Movement(
            warehouse_id=warehouse_obra,
            material_id=material_id,
            qty_change=qty,
            movement_type="IN",
            reference_type="receipt",
            reference_id=receipt.id,
            user_id=user_id
        )
        db.add(movement)

    db.commit()

    return True, "Recepción registrada correctamente"