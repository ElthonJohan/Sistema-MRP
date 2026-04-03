import streamlit as st
from database import SessionLocal
from services.dashboard_service import (
    get_kpis,
    get_recent_movements,
    get_stock_by_warehouse
)
import pandas as pd

st.title("📊 Dashboard Logístico")

db = SessionLocal()

# -------------------------
# KPIs
# -------------------------
kpis = get_kpis(db)

col1, col2, col3, col4 = st.columns(4)

col1.metric("📦 Stock Total", kpis["total_stock"])
col2.metric("⚠️ Críticos", kpis["critical"])
col3.metric("📋 Pendientes", kpis["pending_req"])
col4.metric("🚚 Salidas", kpis["dispatch_today"])

# -------------------------
# STOCK POR ALMACÉN
# -------------------------
st.subheader("📦 Stock por Almacén")

stock_data = get_stock_by_warehouse(db)

df = pd.DataFrame(
    list(stock_data.items()),
    columns=["Almacén", "Stock"]
)

st.bar_chart(df.set_index("Almacén"))

# -------------------------
# MOVIMIENTOS RECIENTES
# -------------------------
st.subheader("🔁 Últimos Movimientos")

movs = get_recent_movements(db)

for m in movs:
    if m.movement_type == 'IN':
        st.success(f"{m.timestamp} | "
        f"Almacén: {m.warehouse.name} | "
        f"Material: {m.material.name} | "
        f"{m.movement_type} {m.qty_change}")
    else:
        st.error(f"{m.timestamp} | "
        f"Almacén: {m.warehouse.name} | "
        f"Material: {m.material.name} | "
        f"{m.movement_type} {m.qty_change}")
    