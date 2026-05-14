from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("No se encontró DATABASE_URL en el archivo .env")

engine = create_engine(
    DATABASE_URL,
    echo=False,           # Cambia a True si quieres ver las consultas SQL
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
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