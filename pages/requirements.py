import streamlit as st
from database import SessionLocal
from services.requirement_service import create_requirement, get_requirements
from models.warehouse import Warehouse
from models.material import Material
from utils.auth import require_login
from utils.navbar import render_navbar, render_sidebar_menu
from datetime import datetime, timedelta

st.set_page_config(page_title="Requerimientos - MRP System", layout="wide")

require_login()

# Render navbar
render_navbar()
with st.sidebar:
    render_sidebar_menu()


st.title("📋 Requerimientos")

db = SessionLocal()

# -------------------------
# CREAR
# -------------------------
st.subheader("➕ Nuevo Requerimiento")

warehouses = db.query(Warehouse).filter(Warehouse.type == "obra").all()
materials = db.query(Material).all()


if not warehouses:
    st.error("No hay almacenes de obra configurados. Por favor crea uno primero.")
    st.stop()

if not materials:
    st.error("No hay materiales configurados. Por favor crea uno primero.")
    st.stop()


wh_dict = {w.name: w.id for w in warehouses}
mat_dict = {m.name: m.id for m in materials}

selected_wh = st.selectbox("Almacén de obra", list(wh_dict.keys()))

items = []

num_items = st.number_input("Cantidad de materiales", min_value=1, step=1)


if mat_dict: 
    for i in range(num_items):
        st.write(f"Material {i+1}")
        mat = st.selectbox(f"Material {i}", list(mat_dict.keys()), key=f"mat_{i}")
        qty = st.number_input(f"Cantidad {i}", min_value=1, key=f"qty_{i}")

        items.append({
            "material_id": mat_dict[mat],
            "qty": qty
        })
    if st.button("Crear Requerimiento"):
        success, msg = create_requirement(db, wh_dict[selected_wh], items)
        if success:
            st.success(msg)
            st.rerun()
        else:
            st.error(msg)
else:
    st.warning("No hay materiales disponibles para seleccionar")


# ========================
# LISTA DE REQUERIMIENTOS CON FILTROS Y PAGINACIÓN
# ========================
st.subheader("📋 Lista de Requerimientos")

# Inicializar estado de paginación
if "page" not in st.session_state:
    st.session_state.page = 0
if "filters_applied" not in st.session_state:
    st.session_state.filters_applied = False

# SECTION: FILTROS
with st.expander("🔍 Filtros", expanded=True):
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        filter_id = st.number_input("ID Requerimiento", value=0, min_value=0, 
                                     help="Dejar en 0 para no filtrar")
    
    with col2:
        filter_status = st.selectbox("Estado", 
                                     ["", "pending", "fulfilled", "partial", "cancelled"],
                                     help="Selecciona un estado o deja en blanco para todos")
    
    with col3:
        filter_start_date = st.date_input("Desde", value=datetime.now() - timedelta(days=30))
    
    with col4:
        filter_end_date = st.date_input("Hasta", value=datetime.now())
    
    col_search, col_clear = st.columns([1, 1])
    
    with col_search:
        if st.button("🔎 Buscar", use_container_width=True):
            st.session_state.page = 0
            st.session_state.filters_applied = True
    
    with col_clear:
        if st.button("🔄 Limpiar Filtros", use_container_width=True):
            st.session_state.page = 0
            st.session_state.filters_applied = False
            st.rerun()


# SECTION: OBTENER DATOS CON FILTROS
items_per_page = 10

# Convertir a datetime completo
start_datetime = datetime.combine(filter_start_date, datetime.min.time())
end_datetime = datetime.combine(filter_end_date, datetime.max.time())

# Aplicar filtros
filter_id_val = filter_id if filter_id > 0 else None
filter_status_val = filter_status if filter_status else None

requirements, total_count = get_requirements(
    db,
    skip=st.session_state.page * items_per_page,
    limit=items_per_page,
    requirement_id=filter_id_val,
    status=filter_status_val,
    start_date=start_datetime,
    end_date=end_datetime
)

# Mostrar información de paginación
st.info(f"📊 Total de requerimientos: **{total_count}** | Mostrando: **{len(requirements)}** | Página: **{st.session_state.page + 1}**")

# SECTION: MOSTRAR REQUERIMIENTOS
if requirements:
    for r in requirements:
        # Formatos para la tarjeta
        status_colors = {
            "pending": "🟡",
            "fulfilled": "🟢",
            "partial": "🟠",
            "cancelled": "🔴"
        }
        status_icon = status_colors.get(r.status, "⚪")
        
        col1, col2, col3 = st.columns([2, 2, 2])
        
        with col1:
            st.write(f"**ID:** {r.id}")
        
        with col2:
            st.write(f"**Estado:** {status_icon} {r.status.upper()}")
        
        with col3:
            st.write(f"**Fecha:** {r.created_at.strftime('%d/%m/%Y %H:%M')}")
        
        with st.expander(f"👁️ Ver Detalle - Requerimiento #{r.id}"):
            st.write(f"**Almacén:** {r.warehouse_id_obra}")
            st.write(f"**Notas:** {r.notes if r.notes else 'Sin notas'}")
            
            st.write("**Ítems:**")
            for item in r.items:
                item_status = f"🟢 {item.status.upper()}" if item.status == "reserved" else f"🟡 {item.status.upper()}"
                st.write(
                    f"- {item.material.name if item.material else 'Material desconocido'} "
                    f"| Solicitado: {item.requested_qty} "
                    f"| Cumplido: {item.fulfilled_qty} "
                    f"| Estado: {item_status}"
                )
        
        st.divider()
else:
    st.warning("❌ No se encontraron requerimientos con los filtros aplicados")


# SECTION: PAGINACIÓN
col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

with col1:
    if st.session_state.page > 0:
        if st.button("⬅️ Anterior", use_container_width=True):
            st.session_state.page -= 1
            st.rerun()

with col5:
    if len(requirements) == items_per_page and (st.session_state.page + 1) * items_per_page < total_count:
        if st.button("Siguiente ➡️", use_container_width=True):
            st.session_state.page += 1
            st.rerun()

with col3:
    st.markdown(f"<div style='text-align: center; padding: 10px;'>Página **{st.session_state.page + 1}** de **{(total_count + items_per_page - 1) // items_per_page}**</div>", unsafe_allow_html=True)