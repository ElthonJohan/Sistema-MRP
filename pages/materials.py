import streamlit as st
import pandas as pd
import time
from database import SessionLocal
from services.material_service import (
    create_material,
    get_materials,
    delete_material,
    get_materials_filtered,
    update_material,
    delete_material_code
)
from utils.auth import require_login
from utils.navbar import render_navbar, render_sidebar_menu

st.set_page_config(page_title="Materiales - MRP System", layout="wide")

require_login()

# Render navbar
render_navbar()
with st.sidebar:
    render_sidebar_menu()

st.title("📦 Gestión de Materiales")

# Inyectar CSS para personalizar el botón de eliminación (tipo primary)
st.markdown("""
<style>
/* Estilo para el botón de acción destructiva (rojo) */
div[data-testid="stColumn"] button[data-testid="stBaseButton-primary"] {
    background-color: #A63C29 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    transition: all 0.3s ease !important;
}
div[data-testid="stColumn"] button[data-testid="stBaseButton-primary"]:hover {
    background-color: #7A3427 !important;
    transform: scale(1.02) !important;
}
</style>
""", unsafe_allow_html=True)

db = SessionLocal()

# -------------------------
# CREAR MATERIAL
# -------------------------
st.subheader("➕ Crear Material")

with st.expander("⚙️Formulario de creación", expanded=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        code = st.text_input("Código")
    
    with col2:
        name = st.text_input("Nombre")
    with col3:
        unit = st.text_input("Unidad (kg, m, unidad, etc.)")

    col4 = st.columns(1)[0]
    with col4:
        description = st.text_area("Descripción")
    submit = st.button("✅Crear", use_container_width=True)

    if submit:
        if code and name:
            created, info = create_material(db, code, name, unit, description)
            if created:
                st.success("Material creado correctamente")
                time.sleep(2)
                st.rerun()
            else:
                if info == 'code':
                    st.error("El código ya existe")
                elif info == 'name':
                    st.error("El nombre ya existe")
                else:
                    st.error("Error al crear el material")
                time.sleep(2)
                st.rerun()  
        else:
            st.error("Código y nombre son obligatorios")
            time.sleep(2)
            st.rerun()

materials = get_materials(db)
# -------------------------
# EDITAR MATERIAL
# -------------------------
st.subheader("✏️ Editar Material")

with st.expander("⚙️Formulario de edición", expanded=True):
    
    if materials:

        select = st.selectbox(
        "Selecciona un material",
        [m.name for m in materials])
        
            # Obtener el ID del material seleccionado
        selected_id = next((m.id for m in materials if m.name == select), None)

        selected = next((m for m in materials if m.id == selected_id), None)

        if selected:
            col1, col2, col3 = st.columns(3)

            with col1:
                new_code = st.text_input("Código", value=selected.code)
            with col2:
                new_name = st.text_input("Nombre", value=selected.name)
            with col3:
                new_unit = st.text_input("Unidad (kg, m, unidad, etc.)", value=selected.unit)
            col4 = st.columns(1)[0]
            with col4:
                new_description = st.text_area("Descripción", value=selected.description, key="edit_desc")
            submit = st.button("✅Actualizar", use_container_width=True)

            if submit:
                if new_code and new_name:
                    updated, info = update_material(
                        db,
                        selected.id,
                        new_code,
                        new_name,
                        new_unit,
                        new_description
                    )

                    if updated:
                        st.success("Material actualizado correctamente")
                        #st.session_state["refresh"] = True
                        time.sleep(2)
                        st.rerun()
                    else:
                        if info == 'code':
                            st.error("El código ya está en uso")
                        elif info == 'name':
                            st.error("El nombre ya está en uso")
                        else:
                            st.error("Error al actualizar el material")
                        #st.session_state["refresh"] = True
                        time.sleep(2)
                        st.rerun()
                        
                else:
                    st.error("Código y nombre son obligatorios")
                    #st.session_state["refresh"] = True
                    time.sleep(2)
                    st.rerun()
    else:
        st.info("No hay materiales registrados")
        st.write("Agrega un nuevo material usando el formulario de arriba.")
        
    
# -------------------------
# LISTAR MATERIALES
# -------------------------
st.subheader("📋 Lista de Materiales")

# Inicializar estado de paginación
if "page" not in st.session_state:
    st.session_state.page = 0
if "filters_applied" not in st.session_state:
    st.session_state.filters_applied = False

# SECTION: FILTROS
with st.expander("🔍 Filtros", expanded=True):
    col1, col2,col3 = st.columns(3)
    
    with col1:
        code_filter = st.text_input("Filtrar por código", value="", key="m_code",
                                    help="Escribe parte del código para filtrar. Deja vacío para no filtrar por código.")
    
    with col2:
        name_filter = st.text_input("Filtrar por nombre", value="", key="m_name",
                                    help="Escribe parte del nombre para filtrar. Deja vacío para no filtrar por nombre.")
    
    with col3:
        unit_filter = st.text_input("Filtrar por unidad", value="", key="m_unit",
                                    help="Escribe parte de la unidad para filtrar. Deja vacío para no filtrar por unidad.")

    col_search, col_clear = st.columns([1, 1])

    with col_search:
        if st.button("🔎 Buscar", use_container_width=True):
            st.session_state.page = 0
            st.session_state.filters_applied = True
    
    def clear_materials_filters():
        st.session_state["m_code"] = ""
        st.session_state["m_name"] = ""
        st.session_state["m_unit"] = ""
        st.session_state.page = 0
        st.session_state.filters_applied = False

    with col_clear:
        st.button("🔄 Limpiar Filtros", use_container_width=True, on_click=clear_materials_filters)


# SECTION: OBTENER DATOS CON FILTROS
items_per_page = 10

# Aplicar filtros
filter_code_val = code_filter if code_filter else None
filter_name_val = name_filter if name_filter else None
filter_unit_val = unit_filter if unit_filter else None

materials, total_count = get_materials_filtered(
    db,
    skip=st.session_state.page * items_per_page,  
    limit=items_per_page,
    code_filter=filter_code_val,
    name_filter=filter_name_val,
    unit_filter=filter_unit_val
)

# Mostrar información de paginación
st.info(f"📊 Total de materiales: **{total_count}** | Mostrando: **{len(materials)}** | Página: **{st.session_state.page + 1}**")  

# SECTION: MOSTRAR MATERIALES

if materials:
    for m in materials:
        col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
        with col1:
            st.write(f"**Código:** {m.code}")
        with col2:
            st.write(f"**Nombre:** {m.name}")
        with col3:
            st.write(f"**Unidad:** {m.unit}")
        # BOTÓN ELIMINAR
        if col4.button(
            "🗑️ Eliminar", 
            key=f"del_{m.id}", 
            type="primary", 
            use_container_width=True,
            help="Eliminar este material. Ten en cuenta que esta acción no se puede deshacer."
        ):
            
            delete_material(db, m.id)
            st.rerun()
        
        with st.expander(f"👁️ Ver Detalle - Material #{m.id}"):
            st.write(f"**Descripción:** {m.description if m.description else 'Sin descripción'}")
            st.divider()
        

        
else:
    st.warning("❌ No se encontraron materiales con los filtros aplicados." if st.session_state.filters_applied else "No hay materiales registrados.")


# SECTION: PAGINACIÓN
col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

with col1:
    if st.session_state.page > 0:
        if st.button("⬅️ Anterior", use_container_width=True):
            st.session_state.page -= 1
            st.rerun()

with col5:
    if len(materials) == items_per_page and (st.session_state.page + 1) * items_per_page < total_count:
        if st.button("Siguiente ➡️", use_container_width=True):
            st.session_state.page += 1
            st.rerun()

with col3:
    st.markdown(f"<div style='text-align: center; padding: 10px;'>Página **{st.session_state.page + 1}** de **{(total_count + items_per_page - 1) // items_per_page}**</div>", unsafe_allow_html=True)
