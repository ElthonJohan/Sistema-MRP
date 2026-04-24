import streamlit as st
from database import SessionLocal
from services.login_log_service import get_login_logs
from models.user import User
from utils.auth import require_login
from utils.navbar import render_navbar, render_sidebar_menu
import pandas as pd

st.set_page_config(page_title="Registros de Acceso - MRP System", layout="wide")

require_login()

# Render navbar
render_navbar()
with st.sidebar:
    render_sidebar_menu()

st.title("📊 Registros de Acceso")

db = SessionLocal()

# Get login logs
logs = get_login_logs(db, limit=100)

if not logs:
    st.info("No hay registros de acceso aún")
else:
    # Convert to DataFrame
    logs_data = []
    for log in logs:
        logs_data.append({
            "ID": log.id,
            "Usuario": log.username,
            "Hora de Acceso": log.login_time.strftime("%Y-%m-%d %H:%M:%S"),
            "IP": log.ip_address or "N/A"
        })
    
    df = pd.DataFrame(logs_data)
    
    st.subheader("Últimos Accesos")
    st.dataframe(df, use_container_width=True)
    
    # Download option
    csv = df.to_csv(index=False)
    st.download_button(
        label="Descargar como CSV",
        data=csv,
        file_name="login_logs.csv",
        mime="text/csv"
    )

# Users section
st.subheader("👥 Usuarios Registrados")
users = db.query(User).all()

if users:
    users_data = []
    for user in users:
        users_data.append({
            "ID": user.id,
            "Usuario": user.username,
            "Email": user.email,
            "Fecha Registro": user.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    df_users = pd.DataFrame(users_data)
    st.dataframe(df_users, use_container_width=True)
else:
    st.info("No hay usuarios registrados")
