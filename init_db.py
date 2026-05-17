# init_db.py
from database import Base, engine, SessionLocal

# Importar todos tus modelos
from models import (
    warehouse, material, inventory, requirement,
    dispatch, receipt, movement, user,
    login_log, failed_login, session, budget, deleted_inventory
)


def run_migrations():
    """Migraciones manuales para agregar columnas"""
    from sqlalchemy import text, inspect
    from database import DATABASE_URL

    inspector = inspect(engine)
    tables = inspector.get_table_names()
    is_sqlite = DATABASE_URL.startswith("sqlite")

    print("Ejecutando migraciones manuales...")

    def add_col(conn, table, col, col_def):
        # SQLite does not support IF NOT EXISTS in ALTER TABLE ADD COLUMN
        if is_sqlite:
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_def}"))
        else:
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col} {col_def}"))
        print(f"  [OK] Columna {col} añadida en {table}")

    with engine.connect() as conn:
        # users table
        if "users" in tables:
            cols = {c["name"] for c in inspector.get_columns("users")}
            if "role" not in cols:
                add_col(conn, "users", "role", "VARCHAR NOT NULL DEFAULT 'cliente'")
            if "is_active" not in cols:
                add_col(conn, "users", "is_active", "BOOLEAN NOT NULL DEFAULT true")

        # user_sessions table
        if "user_sessions" in tables:
            cols = {c["name"] for c in inspector.get_columns("user_sessions")}
            if "role" not in cols:
                add_col(conn, "user_sessions", "role", "VARCHAR NOT NULL DEFAULT 'cliente'")

        # warehouses table
        if "warehouses" in tables:
            cols = {c["name"] for c in inspector.get_columns("warehouses")}
            if "owner_id" not in cols:
                add_col(conn, "warehouses", "owner_id", "INTEGER")
            if "address" not in cols:
                add_col(conn, "warehouses", "address", "VARCHAR")

        # materials table — precio unitario para cálculo de costos
        if "materials" in tables:
            cols = {c["name"] for c in inspector.get_columns("materials")}
            if "unit_price" not in cols:
                add_col(conn, "materials", "unit_price", "FLOAT DEFAULT 0.0")
            if "unit_price_dolares" not in cols:
                add_col(conn, "materials", "unit_price_dolares", "FLOAT DEFAULT 0.0")

        # budgets table — estado activo/inactivo y finalización de obra
        if "budgets" in tables:
            cols = {c["name"] for c in inspector.get_columns("budgets")}
            if "is_active" not in cols:
                default_val = "1" if is_sqlite else "true"
                add_col(conn, "budgets", "is_active", f"BOOLEAN NOT NULL DEFAULT {default_val}")
            if "is_finished" not in cols:
                default_val = "0" if is_sqlite else "false"
                add_col(conn, "budgets", "is_finished", f"BOOLEAN NOT NULL DEFAULT {default_val}")
            if "finished_at" not in cols:
                dt_type = "DATETIME" if is_sqlite else "TIMESTAMP"
                add_col(conn, "budgets", "finished_at", dt_type)

        # inventory table — per-budget tracking and freeze flag
        if "inventory" in tables:
            cols = {c["name"] for c in inspector.get_columns("inventory")}
            if "budget_id" not in cols:
                add_col(conn, "inventory", "budget_id", "INTEGER")
            if "budget_name" not in cols:
                add_col(conn, "inventory", "budget_name", "VARCHAR")
            if "is_active" not in cols:
                default_val = "1" if is_sqlite else "true"
                add_col(conn, "inventory", "is_active", f"BOOLEAN NOT NULL DEFAULT {default_val}")

        # requirements table — vínculo opcional a un proyecto/budget
        if "requirements" in tables:
            cols = {c["name"] for c in inspector.get_columns("requirements")}
            if "budget_id" not in cols:
                add_col(conn, "requirements", "budget_id", "INTEGER")
            if "budget_name" not in cols:
                add_col(conn, "requirements", "budget_name", "VARCHAR")

        # deleted_inventory — registros eliminados con resolución pendiente
        # (tabla nueva — creada por Base.metadata.create_all; sin columnas extra que migrar)

        conn.commit()
    print("Migraciones manuales completadas.\n")


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
                print("SUPERADMIN CREADO EXITOSAMENTE")
                print("="*70)
                print("   Usuario:     superadmin")
                print("   Email:       admin@sistema-mrp.com")
                print("   Contrasena:  Admin123!")
                print("   Cambia esta contrasena en el primer inicio de sesion!")
                print("="*70)
            else:
                print(f"[WARN] No se pudo crear superadmin: {msg}")
        else:
            print("[INFO] El superadmin ya existe.")
    finally:
        db.close()


def init_db():
    print("Iniciando base de datos...\n")

    run_migrations()

    # Crear todas las tablas (solo crea las que no existen)
    Base.metadata.create_all(bind=engine)
    print("Todas las tablas han sido verificadas/creadas.\n")

    bootstrap_superadmin()
    print("Inicializacion de la base de datos completada.")


if __name__ == "__main__":
    init_db()
