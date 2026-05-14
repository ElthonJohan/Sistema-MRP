from database import Base, engine, SessionLocal

# Importar todos los modelos para que SQLAlchemy los registre
from models import warehouse, material, inventory
from models import requirement, dispatch, receipt, movement
from models import user, login_log, failed_login
from models import session


def run_migrations():
    """Agrega columnas nuevas a tablas existentes sin destruir datos."""
    from sqlalchemy import text, inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    with engine.connect() as conn:
        # users: role + is_active
        if "users" in tables:
            cols = [c["name"] for c in inspector.get_columns("users")]
            if "role" not in cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR NOT NULL DEFAULT 'cliente'"))
                print("  [migración] users.role añadido")
            if "is_active" not in cols:
                conn.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 1"))
                print("  [migración] users.is_active añadido")

        # user_sessions: role
        if "user_sessions" in tables:
            cols = [c["name"] for c in inspector.get_columns("user_sessions")]
            if "role" not in cols:
                conn.execute(text("ALTER TABLE user_sessions ADD COLUMN role VARCHAR NOT NULL DEFAULT 'cliente'"))
                print("  [migración] user_sessions.role añadido")

        # warehouses: owner_id, address
        if "warehouses" in tables:
            cols = [c["name"] for c in inspector.get_columns("warehouses")]
            if "owner_id" not in cols:
                conn.execute(text("ALTER TABLE warehouses ADD COLUMN owner_id INTEGER"))
                print("  [migración] warehouses.owner_id añadido")
            if "address" not in cols:
                conn.execute(text("ALTER TABLE warehouses ADD COLUMN address VARCHAR"))
                print("  [migración] warehouses.address añadido")

        conn.commit()


def bootstrap_superadmin():
    """Crea el superadmin inicial si no existe ninguno."""
    from services.auth_service import superadmin_exists, register_user

    db = SessionLocal()
    try:
        if not superadmin_exists(db):
            ok, msg = register_user(
                db,
                username="superadmin",
                email="admin@sistema-mrp.com",
                password="Admin@12345",
                role="superadmin",
            )
            if ok:
                print("\n" + "=" * 50)
                print("  SUPERADMIN CREADO")
                print("  Usuario:    superadmin")
                print("  Email:      admin@sistema-mrp.com")
                print("  Contraseña: Admin@12345")
                print("  ¡Cambia la contraseña después del primer inicio de sesión!")
                print("=" * 50 + "\n")
            else:
                print(f"  [advertencia] No se pudo crear superadmin: {msg}")
        else:
            print("  Superadmin ya existe — no se creó uno nuevo.")
    finally:
        db.close()


def init_db():
    run_migrations()
    Base.metadata.create_all(bind=engine)
    bootstrap_superadmin()


if __name__ == "__main__":
    print("Inicializando base de datos...")
    init_db()
    print("Base de datos lista.")
