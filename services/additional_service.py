from sqlalchemy.orm import Session
from models.budget_additional import BudgetAdditional
from datetime import datetime


def create_additional(db: Session, budget_id: int, request_date: datetime,
                      concept: str, notes: str = None) -> BudgetAdditional:
    a = BudgetAdditional(
        budget_id    = budget_id,
        request_date = request_date,
        concept      = (concept or "").strip(),
        notes        = (notes or "").strip() or None,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def get_additionals(db: Session, budget_id: int = None):
    q = db.query(BudgetAdditional)
    if budget_id is not None:
        q = q.filter(BudgetAdditional.budget_id == budget_id)
    return q.order_by(BudgetAdditional.request_date.desc(), BudgetAdditional.id.desc()).all()


def update_additional(db: Session, additional_id: int,
                      request_date: datetime = None,
                      concept: str = None,
                      notes: str = None) -> bool:
    a = db.query(BudgetAdditional).filter(BudgetAdditional.id == additional_id).first()
    if not a:
        return False
    if request_date is not None:
        a.request_date = request_date
    if concept is not None:
        a.concept = (concept or "").strip()
    if notes is not None:
        a.notes = (notes or "").strip() or None
    db.commit()
    return True


def delete_additional(db: Session, additional_id: int) -> bool:
    a = db.query(BudgetAdditional).filter(BudgetAdditional.id == additional_id).first()
    if not a:
        return False
    db.delete(a)
    db.commit()
    return True
