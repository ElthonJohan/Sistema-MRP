import streamlit as st
from database import SessionLocal
from services.inventory_service import (
    add_stock,
    remove_stock,
    get_inventory
)
from models.warehouse import Warehouse
from models.material import Material
from utils.auth import require_login
from utils.navbar import render_navbar, render_sidebar_menu

st.set_page_config(page_title="Inventario - MRP System", layout="wide")

require_login()

# Render navbar
render_navbar()
with st.sidebar:
    render_sidebar_menu()

st.title("📊 Gestión de Inventario")

db = SessionLocal()

# -------------------------
# SELECCIONES
# -------------------------
warehouses = db.query(Warehouse).all()
materials = db.query(Material).all()

if not warehouses:
    st.error("No hay almacenes configurados. Por favor crea uno primero.")
    st.stop()

if not materials:
    st.error("No hay materiales configurados. Por favor crea uno primero.")
    st.stop()

warehouse_dict = {w.name: w.id for w in warehouses}
material_dict = {m.name: m.id for m in materials}

selected_wh = st.selectbox("Almacén", list(warehouse_dict.keys()))
selected_mat = st.selectbox("Material", list(material_dict.keys()))

warehouse_id = warehouse_dict[selected_wh]
material_id = material_dict[selected_mat]

# -------------------------
# ENTRADA
# -------------------------
st.subheader("➕ Ingresar Stock")

qty_in = st.number_input("Cantidad a ingresar", min_value=1)

if st.button("Agregar Stock"):
    add_stock(db, warehouse_id, material_id, qty_in, user_id=1)
    st.success("Stock agregado")
    st.rerun()

# -------------------------
# SALIDA
# -------------------------
st.subheader("➖ Retirar Stock")

qty_out = st.number_input("Cantidad a retirar", min_value=1)

if st.button("Retirar Stock"):
    success = remove_stock(db, warehouse_id, material_id, qty_out, user_id=1)

    if success:
        st.success("Stock retirado")
    else:
        st.error("Stock insuficiente")

    st.rerun()

# -------------------------
# TABLA INVENTARIO
# -------------------------
st.subheader("📋 Inventario Actual")

inventory = get_inventory(db)

for inv in inventory:
    col1, col2, col3, col4 = st.columns(4)

    col1.write(inv.warehouse.name)
    #col2.write(inv.material.name)
    col3.write(f"Stock: {inv.stock}")
    col4.write(f"Reservado: {inv.reserved}")