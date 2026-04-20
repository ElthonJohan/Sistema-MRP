import streamlit as st
from database import SessionLocal
from services.inventory_service import (
    add_stock,
    remove_stock,
    get_inventory
)
from models.warehouse import Warehouse
from models.material import Material

st.title("📊 Gestión de Inventario")

db = SessionLocal()

# -------------------------
# SELECCIONES
# -------------------------
warehouses = db.query(Warehouse).all()
materials = db.query(Material).all()

warehouse_dict = {w.name: w.id for w in warehouses}
material_dict = {m.name: m.id for m in materials}

selected_wh = st.selectbox("Almacén", list(warehouse_dict.keys()) if warehouse_dict else ["No hay almacenes"])
selected_mat = st.selectbox("Material", list(material_dict.keys()) if material_dict else ["No hay materiales"])

warehouse_id = warehouse_dict[selected_wh] if selected_wh in warehouse_dict else None
material_id = material_dict[selected_mat] if selected_mat in material_dict else None

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

    col1.write(inv.warehouse.name if inv.warehouse else "Sin almacén")
    col2.write(inv.material.name if inv.material else "Sin material")
    col3.write(f"Stock: {inv.stock}")
    col4.write(f"Reservado: {inv.reserved}")