from sqlalchemy.orm import Session
from models.inventory import Inventory
from models.material import Material
from models.movement import Movement

from models.warehouse import Warehouse
from datetime import datetime

def get_or_create_inventory(db: Session, warehouse_id, material_id,
                            budget_id=None, budget_name=None):
    """Returns the inventory record matching (warehouse, material, budget).
    When budget_id is provided, separate records are kept per project so each
    one appears as its own card. When budget_id is None, falls back to the
    record without a project."""
    q = db.query(Inventory).filter(
        Inventory.warehouse_id == warehouse_id,
        Inventory.material_id == material_id,
    )
    if budget_id is not None:
        q = q.filter(Inventory.budget_id == budget_id)
    else:
        q = q.filter(Inventory.budget_id == None)
    inventory = q.first()

    if not inventory:
        inventory = Inventory(
            warehouse_id=warehouse_id,
            material_id=material_id,
            stock=0,
            reserved=0,
            budget_id=budget_id,
            budget_name=budget_name,
        )
        db.add(inventory)
        db.commit()
        db.refresh(inventory)

    return inventory

def add_stock(db: Session, warehouse_id, material_id, qty, user_id,
              budget_id=None, budget_name=None):
    """Add stock to the appropriate inventory record.
    Creates separate records per budget_id so they appear as distinct cards."""
    if budget_id is not None:
        inventory = db.query(Inventory).filter(
            Inventory.warehouse_id == warehouse_id,
            Inventory.material_id == material_id,
            Inventory.budget_id == budget_id,
        ).first()
        if not inventory:
            inventory = Inventory(
                warehouse_id=warehouse_id,
                material_id=material_id,
                stock=0,
                reserved=0,
                budget_id=budget_id,
                budget_name=budget_name,
            )
            db.add(inventory)
            db.commit()
            db.refresh(inventory)
    else:
        inventory = db.query(Inventory).filter(
            Inventory.warehouse_id == warehouse_id,
            Inventory.material_id == material_id,
            Inventory.budget_id == None,
        ).first()
        if not inventory:
            inventory = Inventory(
                warehouse_id=warehouse_id,
                material_id=material_id,
                stock=0,
                reserved=0,
            )
            db.add(inventory)
            db.commit()
            db.refresh(inventory)

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
    """Remove stock, distributing the reduction across all active budget records (FIFO)."""
    records = db.query(Inventory).filter(
        Inventory.warehouse_id == warehouse_id,
        Inventory.material_id == material_id,
        Inventory.is_active == True,
    ).order_by(Inventory.id).all()

    total_stock = sum(inv.stock for inv in records)
    if total_stock < qty:
        return False

    remaining = qty
    for inv in records:
        if remaining <= 0:
            break
        reduce = min(inv.stock, remaining)
        inv.stock -= reduce
        inv.last_updated = datetime.utcnow()
        remaining -= reduce

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
    Agrega reservas distribuidas entre todos los registros activos del material (FIFO).
    No hace commit — el llamador debe hacer commit después de todos los cambios.
    """
    records = db.query(Inventory).filter(
        Inventory.warehouse_id == warehouse_id,
        Inventory.material_id == material_id,
        Inventory.is_active == True,
    ).order_by(Inventory.id).all()

    total_available = sum(max(0, inv.stock - inv.reserved) for inv in records)
    if not records or total_available < qty:
        return False

    remaining = qty
    for inv in records:
        available = max(0, inv.stock - inv.reserved)
        if available <= 0:
            continue
        to_reserve = min(available, remaining)
        inv.reserved += to_reserve
        inv.last_updated = datetime.utcnow()
        db.add(inv)
        remaining -= to_reserve
        if remaining <= 0:
            break
    return True

def release_reservation(db: Session, warehouse_id, material_id, qty):
    """Libera reservas distribuidas entre registros activos del material (FIFO)."""
    records = db.query(Inventory).filter(
        Inventory.warehouse_id == warehouse_id,
        Inventory.material_id == material_id,
        Inventory.is_active == True,
    ).order_by(Inventory.id).all()

    remaining = qty
    for inv in records:
        if remaining <= 0:
            break
        release = min(inv.reserved, remaining)
        inv.reserved -= release
        remaining -= release

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

def delete_inventory_record(db: Session, inventory_id: int, owner_id: int = None) -> bool:
    from models.deleted_inventory import DeletedInventory
    from datetime import datetime as _dt
    inv = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if inv:
        mat = inv.material
        wh  = inv.warehouse
        unit_price     = float(mat.unit_price     or 0.0) if mat else 0.0
        unit_price_dol = float(mat.unit_price_dolares or 0.0) if mat else 0.0
        db.add(DeletedInventory(
            original_id    = inv.id,
            warehouse_id   = inv.warehouse_id,
            material_id    = inv.material_id,
            warehouse_name = wh.name  if wh  else f"Almacén {inv.warehouse_id}",
            material_name  = mat.name if mat else f"Material {inv.material_id}",
            material_unit  = (mat.unit or "uds") if mat else "uds",
            unit_price     = unit_price,
            unit_price_dol = unit_price_dol,
            stock          = inv.stock,
            total_value    = inv.stock * unit_price,
            deleted_at     = _dt.utcnow(),
            status         = "pending",
            owner_id       = owner_id,
        ))
        db.delete(inv)
        db.commit()
        return True
    return False


def get_deleted_inventory(db: Session, owner_id: int = None):
    from models.deleted_inventory import DeletedInventory
    q = db.query(DeletedInventory).filter(DeletedInventory.status == "pending")
    if owner_id is not None:
        q = q.filter(DeletedInventory.owner_id == owner_id)
    return q.order_by(DeletedInventory.deleted_at.desc()).all()


def resolve_deleted_inventory(db: Session, deleted_id: int, resolution: str) -> bool:
    from models.deleted_inventory import DeletedInventory
    rec = db.query(DeletedInventory).filter(DeletedInventory.id == deleted_id).first()
    if not rec:
        return False
    rec.status = resolution
    db.commit()
    return True


def get_frozen_inventory_for_owner(db: Session, owner_id: int):
    """Return inventory records that are frozen (project deleted) for a given client."""
    from models.warehouse import Warehouse
    return (
        db.query(Inventory)
        .join(Warehouse, Inventory.warehouse_id == Warehouse.id)
        .filter(
            Inventory.is_active == False,
            Warehouse.owner_id == owner_id,
            Warehouse.type == "principal",
        )
        .order_by(Inventory.id)
        .all()
    )


def redirect_frozen_inventory(db: Session, inventory_id: int, new_budget_id: int) -> bool:
    """Reassign a frozen inventory record to a new project and reactivate it."""
    from models.budget import Budget
    inv = db.query(Inventory).filter(
        Inventory.id == inventory_id,
        Inventory.is_active == False,
    ).first()
    if not inv:
        return False
    budget = db.query(Budget).filter(Budget.id == new_budget_id).first()
    if not budget:
        return False
    inv.budget_id   = new_budget_id
    inv.budget_name = budget.name
    inv.is_active   = True
    db.commit()
    return True


def assign_project_to_inventory(db: Session, inventory_id: int, budget_id) -> bool:
    """Asigna o reasigna el proyecto de un registro de inventario.
    - budget_id puede ser un int (proyecto destino) o None (quitar proyecto).
    - Si ya existe otro registro con la misma combinación (almacén/material/proyecto),
      fusiona stock y reservas en él y elimina el actual.
    """
    from models.budget import Budget
    inv = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not inv:
        return False

    bud_name = None
    if budget_id is not None:
        bud = db.query(Budget).filter(Budget.id == budget_id).first()
        if not bud:
            return False
        bud_name = bud.name

    # Buscar si ya existe un registro destino al que fusionar
    target_q = db.query(Inventory).filter(
        Inventory.warehouse_id == inv.warehouse_id,
        Inventory.material_id  == inv.material_id,
        Inventory.id           != inv.id,
    )
    if budget_id is None:
        target_q = target_q.filter(Inventory.budget_id == None)
    else:
        target_q = target_q.filter(Inventory.budget_id == budget_id)
    target = target_q.first()

    if target:
        target.stock    += inv.stock
        target.reserved += inv.reserved
        target.last_updated = datetime.utcnow()
        db.delete(inv)
    else:
        inv.budget_id    = budget_id
        inv.budget_name  = bud_name
        inv.last_updated = datetime.utcnow()

    db.commit()
    return True


def unfreeze_inventory(db: Session, inventory_id: int) -> bool:
    """Reactivate a frozen inventory record without assigning a project (budget_id=None)."""
    inv = db.query(Inventory).filter(
        Inventory.id == inventory_id,
        Inventory.is_active == False,
    ).first()
    if not inv:
        return False
    inv.budget_id   = None
    inv.budget_name = None
    inv.is_active   = True
    db.commit()
    return True
