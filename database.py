from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Base de datos (SQLite)
DATABASE_URL = "sqlite:///./mrp.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # necesario para SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Función para obtener sesión
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()