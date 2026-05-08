from sqlalchemy.orm import Session
from sqlalchemy import func
from models.inventory import Inventory
from models.requirement import Requirement
from models.movement import Movement
from models.warehouse import Warehouse
from datetime import datetime, date, timedelta


#KPIs
def get_kpis(db: Session):

    total_stock = db.query(Inventory).with_entities(
        Inventory.stock
    ).all()

    total_stock = sum([s[0] for s in total_stock])
    
    critical = (
        db.query(Inventory)

        .join(Inventory.warehouse)
        .filter(Warehouse.type == "principal", Inventory.stock <= 5)
        .count()
    )

    pending_req = db.query(Requirement).filter(
        Requirement.status.in_(["pending", "partial"])
    ).count()

    today = date.today()


    dispatch_today = db.query(Movement).filter(
        Movement.movement_type == "OUT"
    ).count()

    return {
        "total_stock": total_stock,
        "critical": critical,
        "pending_req": pending_req,
        "dispatch_today": dispatch_today
    }

    #Movimientos recientes
def get_recent_movements(db: Session):
    return db.query(Movement).order_by(
        Movement.timestamp.desc()
    ).limit(10).all()



def get_stock_by_warehouse(db: Session):
    data = db.query(Inventory).all()

    result = {}
    for inv in data:
        name = inv.warehouse.name
        result[name] = result.get(name, 0) + inv.stock
    return result


def get_movements_last_7_days(db: Session):
    """Retorna entradas y salidas agrupadas por día de los últimos 7 días."""
    today = date.today()
    days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    
    result = []
    for day in days:
        start = datetime(day.year, day.month, day.day, 0, 0, 0)
        end   = datetime(day.year, day.month, day.day, 23, 59, 59)
        ins = db.query(Movement).filter(
            Movement.movement_type == "IN",
            Movement.timestamp >= start,
            Movement.timestamp <= end,
        ).count()
        outs = db.query(Movement).filter(
            Movement.movement_type == "OUT",
            Movement.timestamp >= start,
            Movement.timestamp <= end,
        ).count()
        result.append({
            "Día": day.strftime("%d/%m"),
            "Entradas": ins,
            "Salidas": outs,
        })
    return result


def get_top_materials_by_movement(db: Session, limit: int = 5):
    """Top materiales con más movimientos."""
    rows = (
        db.query(Movement.material_id, func.count(Movement.id).label("total"))
        .group_by(Movement.material_id)
        .order_by(func.count(Movement.id).desc())
        .limit(limit)
        .all()
    )
    from models.material import Material
    result = []
    for r in rows:
        mat = db.query(Material).filter(Material.id == r.material_id).first()
        if mat:
            result.append({"Material": mat.name, "Movimientos": r.total})

    return result

