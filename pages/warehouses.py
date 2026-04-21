import streamlit as st
from database import SessionLocal
from services.warehouse_service import (
    create_warehouse,
    get_warehouses,
    delete_warehouse,
    update_warehouse
)
from utils.auth import require_login
from utils.navbar import render_navbar, render_sidebar_menu

st.set_page_config(page_title="Almacenes - MRP System", layout="wide")

require_login()

# Render navbar
render_navbar()
with st.sidebar:
    render_sidebar_menu()

st.title("🏭 Gestión de Almacenes")

db = SessionLocal()

# -------------------------
# FORMULARIO CREAR
# -------------------------
st.subheader("➕ Crear Almacén")

with st.form("create_form"):
    name = st.text_input("Nombre")
    type = st.selectbox("Tipo", ["principal", "obra"])
    location = st.text_input("Ubicación")

    submit = st.form_submit_button("Crear")

    if submit:
        if name:
            create_warehouse(db, name, type, location)
            st.success("Almacén creado correctamente")
        else:
            st.error("El nombre es obligatorio")

# -------------------------
# LISTAR ALMACENES
# -------------------------
st.subheader("📋 Lista de Almacenes")

warehouses = get_warehouses(db)

for w in warehouses:
    col1, col2, col3, col4 = st.columns([3, 2, 3, 2])

    col1.write(w.name)
    col2.write(w.type)
    col3.write(w.location)

    # BOTÓN ELIMINAR
    if col4.button("Eliminar", key=f"del_{w.id}"):
        delete_warehouse(db, w.id)
        st.rerun()

# -------------------------
# EDITAR
# -------------------------
st.subheader("✏️ Editar Almacén")

selected_id = st.selectbox(
    "Selecciona un almacén",
    [w.id for w in warehouses]
)

selected = next((w for w in warehouses if w.id == selected_id), None)

if selected:
    new_name = st.text_input("Nombre", value=selected.name)
    new_type = st.selectbox(
        "Tipo",
        ["principal", "obra"],
        index=0 if selected.type == "principal" else 1
    )
    new_location = st.text_input("Ubicación", value=selected.location)

    if st.button("Actualizar"):
        update_warehouse(db, selected.id, new_name, new_type, new_location)
        st.success("Actualizado correctamente")
        st.rerun()