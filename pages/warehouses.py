import streamlit as st
from database import SessionLocal
from services.warehouse_service import (
    create_warehouse,
    get_warehouses,
    delete_warehouse,
    update_warehouse
)
import time
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
        mensaje_container = st.empty()  # Contenedor para el mensaje
        
        if name:
            create=create_warehouse(db, name, type, location)
            if "error" in create:
                mensaje_container.error(create["error"])
            else:
                mensaje_container.success("Almacén creado correctamente")
        else:
            mensaje_container.error("El nombre es obligatorio")

         # Esperar 2 segundos y luego limpiar
        time.sleep(2)
        mensaje_container.empty() 
        st.rerun()


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

if warehouses:

    selected_name = st.selectbox(
        "Selecciona un almacén",
        [w.name for w in warehouses]
    )

    selected = next((w for w in warehouses if w.name == selected_name), None)

    if selected:
        new_name = st.text_input("Nombre", value=selected.name)
        new_type = st.selectbox(
            "Tipo",
            ["principal", "obra"],
            index=0 if selected.type == "principal" else 1
        )
        new_location = st.text_input("Ubicación", value=selected.location)

        if st.button("Actualizar"):
            accept=update_warehouse(db, selected.id, new_name, new_type, new_location)
            
            # Crear un contenedor para el mensaje
            mensaje_container = st.empty()
            
            if "error" in accept:
                mensaje_container.error(accept["error"])
            else:
                mensaje_container.success(accept["value"])
            
            # Esperar 2 segundos y luego limpiar
            time.sleep(2)
            mensaje_container.empty()
            st.rerun()
else:
    st.info("No hay almacenes registrados. Por favor, crea uno primero.")
    st.write("Para crear un almacén, completa el formulario en la sección '➕ Crear Almacén' y haz clic en 'Crear'.")
