# -*- coding: utf-8 -*-
import streamlit as st
from utils.navbar import render_navbar, render_sidebar_menu
from utils.session_manager import init_session

st.set_page_config(page_title="MRP System", layout="wide")

# Ocultar navegador nativo de páginas de Streamlit del sidebar
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# Verificar/restaurar sesión desde cookie
session_valid = init_session()

# Render navbar at the top
st.markdown("---")
render_navbar()
st.markdown("---")

# Check if user is logged in
if not session_valid:
    st.info("👋 Bienvenido. Por favor inicia sesión para continuar.")
    st.switch_page("pages/login.py")

# Render sidebar menu
with st.sidebar:
    render_sidebar_menu()

# Main dashboard content
st.title("📊 Dashboard Logístico")
st.write(f"¡Bienvenido **{st.session_state.username}**!")

from database import SessionLocal
from services.dashboard_service import (
    get_kpis,
    get_recent_movements,
    get_stock_by_warehouse
)

db = SessionLocal()

# -------------------------
# KPIs
# -------------------------
st.subheader("📈 KPIs")

kpis = get_kpis(db)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📦 Stock Total", kpis["total_stock"])

with col2:
    st.metric("⚠️ Críticos", kpis["critical"])

with col3:
    st.metric("📋 Pendientes", kpis["pending_req"])

with col4:
    st.metric("🚚 Salidas", kpis["dispatch_today"])

# -------------------------
# Gráfico de Stock
# -------------------------
st.subheader("📊 Stock por Almacén")

stock_by_wh = get_stock_by_warehouse(db)

if stock_by_wh:
    import pandas as pd
    df_stock = pd.DataFrame(
        list(stock_by_wh.items()), columns=["warehouse_name", "total_quantity"]
    )
    st.bar_chart(df_stock.set_index("warehouse_name")["total_quantity"])
else:
    st.info("No hay datos de stock disponibles")