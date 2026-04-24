from sqlalchemy.orm import Session
from models.login_log import LoginLog
from datetime import datetime

def log_login(db: Session, user_id: int, username: str, ip_address: str = None):
    """Register a login event"""
    login_log = LoginLog(
        user_id=user_id,
        username=username,
        login_time=datetime.utcnow(),
        ip_address=ip_address
    )
    db.add(login_log)
    db.commit()
    db.refresh(login_log)
    return login_log

def get_login_logs(db: Session, limit: int = 50):
    """Get recent login logs"""
    return db.query(LoginLog).order_by(LoginLog.login_time.desc()).limit(limit).all()

def get_user_login_history(db: Session, user_id: int, limit: int = 20):
    """Get login history for a specific user"""
    return db.query(LoginLog).filter(LoginLog.user_id == user_id).order_by(LoginLog.login_time.desc()).limit(limit).all()
