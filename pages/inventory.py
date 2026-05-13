import streamlit as st
from database import SessionLocal
from services.inventory_service import (
    add_stock,
    remove_stock,
    get_inventory_filtered
)
from models.warehouse import Warehouse
from models.material import Material
from utils.auth import require_login
from utils.navbar import render_navbar, render_sidebar_menu
import time

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

with st.expander("⚙️ Configuración de Almacén y Material"):
    if not warehouses:
        st.error("No hay almacenes configurados. Por favor crea uno primero.")
        st.stop()

    if not materials:
        st.error("No hay materiales configurados. Por favor crea uno primero.")
        st.stop()
    warehouse_dict = {w.name: w.id for w in warehouses}
    material_dict = {m.name: m.id for m in materials}
    col1, col2 = st.columns(2)
    with col1:
        selected_wh = st.selectbox("Almacén", list(warehouse_dict.keys()))
    with col2:
        selected_mat = st.selectbox("Material", list(material_dict.keys()))
    warehouse_id = warehouse_dict[selected_wh]
    material_id = material_dict[selected_mat]
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("➕ Ingresar Stock")
        qty_in = st.number_input("Cantidad a ingresar", min_value=1)
        if st.button("Agregar Stock"):
            add_stock(db, warehouse_id, material_id, qty_in, user_id=1)
            st.success("Stock agregado")
            time.sleep(2)
            st.rerun()
    with col2:
        st.subheader("➖ Retirar Stock")
        qty_out = st.number_input("Cantidad a retirar", min_value=1)
        if st.button("Retirar Stock"):
            success = remove_stock(db, warehouse_id, material_id, qty_out, user_id=1)
            if success:
                st.success("Stock retirado")

            else:
                st.error("Stock insuficiente")
            time.sleep(2)
            st.rerun()



# -------------------------
# TABLA INVENTARIO
# -------------------------
st.subheader("📋 Inventario Actual")

# Inicializar estado de paginación
if "page" not in st.session_state:
    st.session_state.page = 0
if "filters_applied" not in st.session_state:
    st.session_state.filters_applied = False


<<<<<<< HEAD
    col1.write(inv.warehouse.name)
    #col2.write(inv.material.name)
    col3.write(f"Stock: {inv.stock}")
    col4.write(f"Reservado: {inv.reserved}")
=======
# SECTION: FILTROS
with st.expander("🔍 Filtros", expanded=True):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_warehouse_name = st.text_input("Nombre Almacén", key="f_warehouse")
    
    with col2:
        filter_material_name = st.text_input("Nombre Material", key="f_material")
    
    with col3:
        filter_stock = st.number_input("Stock", min_value=0, key="f_stock")
    

    
    col_search, col_clear = st.columns([1, 1])
    
    with col_search:
        if st.button("🔎 Buscar", use_container_width=True):
            st.session_state.page = 0
            st.session_state.filters_applied = True

    def clear_filters():
        st.session_state["f_warehouse"] = ""
        st.session_state["f_material"] = ""
        st.session_state["f_stock"] = 0
        st.session_state.page = 0
        st.session_state.filters_applied = False

    with col_clear:
        st.button("🔄 Limpiar Filtros", use_container_width=True, on_click=clear_filters)


# SECTION: OBTENER DATOS CON FILTROS
items_per_page = 10

#Aplicar filtros
filter_warehouse_name_val = filter_warehouse_name if filter_warehouse_name else None
filter_material_name_val = filter_material_name if filter_material_name else None
filter_stock_val = filter_stock if filter_stock else None

inventory, total_count = get_inventory_filtered(
    db,
    skip=st.session_state.page * items_per_page,
    limit=items_per_page,
    warehouse_name=filter_warehouse_name_val,
    material_name=filter_material_name_val,
    stock=filter_stock_val
)

if inventory:
    for inv in inventory:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write("**Almacén:**", inv.warehouse.name)
        with col2:
            st.write("**Material:**", inv.material.name)
        with col3:
            st.write("**Stock:**", inv.stock)
        with col4:
            st.write("**Reservado:**", inv.reserved)

        with st.expander(f"👁️ Ver Detalle - Inventario #{inv.id}"):
            st.write("**Última actualización:**", inv.last_updated.strftime("%Y-%m-%d %H:%M:%S"))
            st.write("**ID Inventario:**", inv.id)
            st.write("**ID Almacén:**", inv.warehouse_id)
            st.write("**ID Material:**", inv.material_id)

        st.divider()

else:
    st.info("❌ No se encontraron registros con los filtros aplicados." if st.session_state.filters_applied else "No hay registros de inventario disponibles.")


# SECTION: PAGINACIÓN
col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

with col1:
    if st.session_state.page > 0:
        if st.button("⬅️ Anterior", use_container_width=True):
            st.session_state.page -= 1
            st.rerun()

with col5:
    if len(inventory) == items_per_page and (st.session_state.page + 1) * items_per_page < total_count:
        if st.button("Siguiente ➡️", use_container_width=True):
            st.session_state.page += 1
            st.rerun()

with col3:
    st.markdown(f"<div style='text-align: center; padding: 10px;'>Página **{st.session_state.page + 1}** de **{(total_count + items_per_page - 1) // items_per_page}**</div>", unsafe_allow_html=True)
>>>>>>> ac4f38607ff2b4a8766defa63c00f7409ea88f3a
