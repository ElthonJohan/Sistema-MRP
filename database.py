from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

# === Prioridad de conexión ===
if "DATABASE_URL" in st.secrets:
    DATABASE_URL = st.secrets["DATABASE_URL"]
    print("✅ Usando DATABASE_URL desde Streamlit Secrets")
elif os.getenv("DATABASE_URL"):
    DATABASE_URL = os.getenv("DATABASE_URL")
    print("✅ Usando DATABASE_URL desde .env")
else:
    raise ValueError("❌ No se encontró DATABASE_URL")

print(f"URL cargada: {DATABASE_URL[:60]}...")   # Para debug

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    connect_args={"sslmode": "disable"}  # Ajusta según tu configuración de PostgreSQL
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