from sqlalchemy.orm import Session
from models.inventory import Inventory
from models.requirement import Requirement
from models.movement import Movement
from datetime import datetime, date


#KPIs
def get_kpis(db: Session):

    total_stock = db.query(Inventory).with_entities(
        Inventory.stock
    ).all()

    total_stock = sum([s[0] for s in total_stock])

    critical = db.query(Inventory).filter(
        Inventory.stock <= 5
    ).count()

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

#Stock por almacén
def get_stock_by_warehouse(db: Session):
    data = db.query(Inventory).all()

    result = {}
    for inv in data:
        name = inv.warehouse.name
        result[name] = result.get(name, 0) + inv.stock

    return result

