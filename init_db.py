# init_db.py
from database import Base, engine, SessionLocal

# Importar todos tus modelos
from models import (
    warehouse, material, inventory, requirement, 
    dispatch, receipt, movement, user, 
    login_log, failed_login, session
)


def run_migrations():
    """Migraciones manuales para agregar columnas"""
    from sqlalchemy import text, inspect

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    print("🔧 Ejecutando migraciones manuales...")

    with engine.connect() as conn:
        # users table
        if "users" in tables:
            cols = {c["name"] for c in inspector.get_columns("users")}
            if "role" not in cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR NOT NULL DEFAULT 'cliente'"))
                print("  [✓] Columna role añadida en users")
            if "is_active" not in cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT true"))
                print("  [✓] Columna is_active añadida en users")

        # user_sessions table
        if "user_sessions" in tables:
            cols = {c["name"] for c in inspector.get_columns("user_sessions")}
            if "role" not in cols:
                conn.execute(text("ALTER TABLE user_sessions ADD COLUMN IF NOT EXISTS role VARCHAR NOT NULL DEFAULT 'cliente'"))
                print("  [✓] Columna role añadida en user_sessions")

        # warehouses table
        if "warehouses" in tables:
            cols = {c["name"] for c in inspector.get_columns("warehouses")}
            if "owner_id" not in cols:
                conn.execute(text("ALTER TABLE warehouses ADD COLUMN IF NOT EXISTS owner_id INTEGER"))
                print("  [✓] Columna owner_id añadida en warehouses")
            if "address" not in cols:
                conn.execute(text("ALTER TABLE warehouses ADD COLUMN IF NOT EXISTS address VARCHAR"))
                print("  [✓] Columna address añadida en warehouses")

        conn.commit()
    print("✅ Migraciones manuales completadas.\n")


def bootstrap_superadmin():
    """Crea el usuario superadmin"""
    from services.auth_service import superadmin_exists, register_user

    db = SessionLocal()
    try:
        if not superadmin_exists(db):
            ok, msg = register_user(
                db,
                username="superadmin",
                email="admin@sistema-mrp.com",
                password="Admin123!",
                role="superadmin",
            )
            if ok:
                print("="*70)
                print("🎉 SUPERADMIN CREADO EXITOSAMENTE")
                print("="*70)
                print("   Usuario:     superadmin")
                print("   Email:       admin@sistema-mrp.com")
                print("   Contraseña:  Admin123!")
                print("   ¡Cambia esta contraseña en el primer inicio de sesión!")
                print("="*70)
            else:
                print(f"⚠️  No se pudo crear superadmin: {msg}")
        else:
            print("ℹ️  El superadmin ya existe.")
    finally:
        db.close()


def init_db():
    print("🚀 Iniciando base de datos PostgreSQL...\n")
    
    run_migrations()
    
    # Crear todas las tablas (solo crea las que no existen)
    Base.metadata.create_all(bind=engine)
    print("✅ Todas las tablas han sido verificadas/creadas.\n")
    
    bootstrap_superadmin()
    print("🎯 Inicialización de la base de datos completada.")


if __name__ == "__main__":
    init_db()