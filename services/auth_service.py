import bcrypt
import re
from sqlalchemy.orm import Session
from models.user import User
from models.failed_login import FailedLoginAttempt
from datetime import datetime, timedelta

# Configuración de seguridad
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15
MIN_PASSWORD_LENGTH = 8
PASSWORD_REGEX = re.compile(
    r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$'
)
EMAIL_REGEX = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)
USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_]{3,20}$')

def hash_password(password: str) -> str:
    """Hash a password using bcrypt with strong salt rounds"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False

def validate_email(email: str) -> tuple[bool, str]:
    """Validate email format"""
    if not email or len(email) > 255:
        return False, "Email inválido"
    
    if not EMAIL_REGEX.match(email):
        return False, "Formato de email inválido (ejemplo: usuario@empresa.com)"
    
    return True, ""

def validate_username(username: str) -> tuple[bool, str]:
    """Validate username format and length"""
    if not username:
        return False, "El usuario es requerido"
    
    if len(username) < 3:
        return False, "El usuario debe tener al menos 3 caracteres"
    
    if len(username) > 20:
        return False, "El usuario no puede tener más de 20 caracteres"
    
    if not USERNAME_REGEX.match(username):
        return False, "El usuario solo puede contener letras, números y guiones bajos"
    
    return True, ""

def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength"""
    if not password:
        return False, "La contraseña es requerida"
    
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres"
    
    if len(password) > 128:
        return False, "La contraseña es muy larga (máximo 128 caracteres)"
    
    # Validate password complexity
    if not PASSWORD_REGEX.match(password):
        return False, (
            "La contraseña debe contener: "
            "- Al menos una mayúscula (A-Z)\n"
            "- Al menos una minúscula (a-z)\n"
            "- Al menos un número (0-9)\n"
            "- Al menos un símbolo especial (@$!%*?&)"
        )
    
    return True, ""

def check_account_locked(db: Session, username: str) -> tuple[bool, str]:
    """Check if account is temporarily locked due to failed attempts"""
    lockout_time = datetime.utcnow() - timedelta(minutes=LOCKOUT_DURATION_MINUTES)
    
    recent_failures = db.query(FailedLoginAttempt).filter(
        FailedLoginAttempt.username == username,
        FailedLoginAttempt.attempt_time > lockout_time
    ).count()
    
    if recent_failures >= MAX_LOGIN_ATTEMPTS:
        return True, (
            f"Cuenta temporalmente bloqueada. "
            f"Demasiados intentos fallidos. "
            f"Intenta de nuevo en {LOCKOUT_DURATION_MINUTES} minutos."
        )
    
    return False, ""

def log_failed_attempt(db: Session, username: str, reason: str, ip_address: str = None):
    """Log a failed login attempt"""
    failed_attempt = FailedLoginAttempt(
        username=username,
        reason=reason,
        ip_address=ip_address,
        attempt_time=datetime.utcnow()
    )
    db.add(failed_attempt)
    db.commit()

def register_user(db: Session, username: str, email: str, password: str, password_confirm: str = None):
    """Register a new user with strong validation"""
    
    # Validate username
    valid_user, user_msg = validate_username(username)
    if not valid_user:
        return False, user_msg
    
    # Validate email
    valid_email, email_msg = validate_email(email)
    if not valid_email:
        return False, email_msg
    
    # Validate password
    valid_pass, pass_msg = validate_password(password)
    if not valid_pass:
        return False, pass_msg
    
    # Validate password confirmation if provided
    if password_confirm and password != password_confirm:
        return False, "Las contraseñas no coinciden"
    
    # Check if user already exists (case-insensitive)
    existing_user = db.query(User).filter(
        (User.username.ilike(username)) | (User.email.ilike(email))
    ).first()
    
    if existing_user:
        if existing_user.username.lower() == username.lower():
            return False, f"El usuario '{username}' ya está registrado"
        else:
            return False, f"El email '{email}' ya está registrado con otro usuario"
    
    # Create new user with hashed password
    try:
        password_hash = hash_password(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            created_at=datetime.utcnow()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return True, "Usuario registrado exitosamente"
    except Exception as e:
        db.rollback()
        return False, "Error al registrar el usuario. Intenta de nuevo."

def login_user(db: Session, username: str, password: str, ip_address: str = None):
    """Authenticate a user with security checks"""
    
    # Basic field validation
    if not username or not password:
        return False, None, "Usuario y contraseña son requeridos"
    
    # Check if account is locked
    is_locked, lock_msg = check_account_locked(db, username)
    if is_locked:
        return False, None, lock_msg
    
    # Find user (case-insensitive for username)
    user = db.query(User).filter(User.username.ilike(username)).first()
    
    if not user:
        log_failed_attempt(db, username, "Usuario no encontrado", ip_address)
        return False, None, "Usuario o contraseña incorrectos"
    
    # Verify password
    if not verify_password(password, user.password_hash):
        log_failed_attempt(db, username, "Contraseña incorrecta", ip_address)
        return False, None, "Usuario o contraseña incorrectos"
    
    # Successful login - clear failed attempts for this user
    db.query(FailedLoginAttempt).filter(
        FailedLoginAttempt.username == username
    ).delete()
    db.commit()
    
    return True, user, "Login exitoso"

def get_user(db: Session, user_id: int):
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    """Get user by username (case-insensitive)"""
    return db.query(User).filter(User.username.ilike(username)).first()
