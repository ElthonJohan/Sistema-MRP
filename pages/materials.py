# -*- coding: utf-8 -*-
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
from utils.auth import require_cliente
from utils.navbar import render_navbar, render_sidebar_menu

st.set_page_config(page_title="Materiales — Sistema MRP", layout="wide", initial_sidebar_state="expanded")

render_navbar()
require_cliente()

st.markdown("""
<style>
[data-testid="stHeader"]     { background: transparent !important; }
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stAppViewBlockContainer"] { padding-top: 1.2rem !important; }
.op-hero {
    display: flex; align-items: center; justify-content: space-between;
    flex-wrap: wrap; gap: .5rem;
    padding: 1rem 1.5rem 1.2rem; border-radius: 20px;
    background: linear-gradient(135deg, #0a1628 0%, #1a3470 50%, #2563eb 100%);
    margin-bottom: 1.5rem; box-shadow: 0 8px 32px rgba(37,99,235,.28);
}
.op-hero-left { display: flex; align-items: center; gap: 1rem; }
.op-hero-icon {
    width: 52px; height: 52px; border-radius: 14px;
    background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,.18);
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; font-size: 1.5rem;
}
.op-hero h1 { font-size: 1.45rem; font-weight: 900; color: #fff; margin: 0; }
.op-hero p  { font-size: .80rem; color: rgba(255,255,255,.65); margin: 3px 0 0; }
.op-badge {
    background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,.22);
    border-radius: 30px; padding: .32rem .9rem;
    font-size: .75rem; font-weight: 700; color: rgba(255,255,255,.85); white-space: nowrap;
}
.sec-title {
    font-size: .95rem; font-weight: 800;
    display: flex; align-items: center; gap: .55rem;
    padding-left: .8rem; border-left: 4px solid #2563eb;
    margin: 1.8rem 0 .85rem;
}
[data-testid="stExpander"] {
    border-radius: 16px !important; border: 1px solid rgba(37,99,235,.18) !important;
    background: rgba(6,13,28,.35) !important; overflow: hidden !important;
    transition: border-color .2s !important;
}
[data-testid="stExpander"]:hover { border-color: rgba(37,99,235,.32) !important; }
details[data-testid="stExpander"] > summary {
    padding: .82rem 1.2rem !important; font-size: .88rem !important;
    font-weight: 700 !important; color: #93c5fd !important;
}
details[data-testid="stExpander"][open] > summary {
    border-bottom: 1px solid rgba(37,99,235,.15) !important;
}
label[data-testid="stWidgetLabel"] p { font-size: .80rem !important; font-weight: 600 !important; }
[data-testid="stBaseButton-primary"],
[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
    color: #fff !important; border: none !important; border-radius: 10px !important;
    font-weight: 700 !important; box-shadow: 0 2px 14px rgba(37,99,235,.35) !important;
    transition: all .2s !important;
}
[data-testid="stBaseButton-primary"]:hover,
[data-testid="stFormSubmitButton"] button:hover {
    opacity: .9 !important; transform: translateY(-1px) !important;
}
[data-testid="stAlert"] { border-radius: 10px !important; }
.mat-table { border-radius: 12px; overflow: hidden; border: 1px solid rgba(37,99,235,.15); }

/* ── Alineación vertical de botones con tarjeta de material ── */
[data-testid="stHorizontalBlock"]:has(.mat-info-card) {
    align-items: center !important;
}
[data-testid="stHorizontalBlock"]:has(.mat-info-card) > [data-testid="stVerticalBlock"] {
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    render_sidebar_menu()

# st.title("📦 Gestión de Materiales")

# # Inyectar CSS para personalizar el botón de eliminación (tipo primary)
# st.markdown("""
# <style>
# /* Estilo para el botón de acción destructiva (rojo) */
# div[data-testid="stColumn"] button[data-testid="stBaseButton-primary"] {
#     background-color: #A63C29 !important;
#     color: white !important;
#     border: none !important;
#     border-radius: 8px !important;
#     transition: all 0.3s ease !important;
# }
# div[data-testid="stColumn"] button[data-testid="stBaseButton-primary"]:hover {
#     background-color: #7A3427 !important;
#     transform: scale(1.02) !important;
# }
# </style>
# """, unsafe_allow_html=True)


db = SessionLocal()
materials = get_materials(db)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="op-hero">
  <div class="op-hero-left">
    <div class="op-hero-icon">&#128230;</div>
    <div>
      <h1>Materiales</h1>
      <p>Catálogo de materiales disponibles en el sistema</p>
    </div>
  </div>
  <div class="op-badge">{len(materials)} materiales registrados</div>
</div>
""", unsafe_allow_html=True)


# with st.expander("⚙️Formulario de creación", expanded=True):
#     col1, col2, col3 = st.columns(3)

#     with col1:
#         code = st.text_input("Código")
    
#     with col2:
#         name = st.text_input("Nombre")
#     with col3:
#         unit = st.text_input("Unidad (kg, m, unidad, etc.)")

#     col4 = st.columns(1)[0]
#     with col4:
#         description = st.text_area("Descripción")
#     submit = st.button("✅Crear", use_container_width=True)

#     if submit:
#         if code and name:
#             created, info = create_material(db, code, name, unit, description)
#             if created:
#                 st.success("Material creado correctamente")
#                 time.sleep(2)
#                 st.rerun()

# ── Instrucciones ─────────────────────────────────────────────────────────────
_, _col_help = st.columns([6, 1])
with _col_help.popover("Instrucciones", use_container_width=True):
    st.markdown("#### Materiales — Guía de uso")
    st.markdown("""
**Crear un material**
1. Despliega **Nuevo material** e ingresa: Código, Nombre, Unidad y Descripción.
2. El **Código** debe ser único (por ejemplo: MAT-001). El **Nombre** también debe ser único.
3. En **Unidad** indica la unidad de medida (kg, m, unidad, litro, etc.).
4. Presiona **Crear Material**; aparecerá en el catálogo de inmediato.

**Catálogo**
- La tabla muestra todos los materiales con código, nombre, unidad y descripción.

**Editar y eliminar**
- En **Editar material existente** selecciona uno y modifica sus campos.
- En **Eliminar material existente** selecciona uno y confirma; la eliminación es permanente.

> Si eliminas un material que ya tiene stock en inventario, los registros de inventario quedarán huérfanos. Verifica primero.
""")

# ── Crear ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-title">Crear Material</div>', unsafe_allow_html=True)

with st.expander("Nuevo material", expanded=False):
    with st.form("create_material_form"):
        col_a, col_b = st.columns(2, gap="medium")
        code        = col_a.text_input("Código", placeholder="Ej: MAT-001")
        name        = col_b.text_input("Nombre", placeholder="Ej: Cemento Portland")
        unit        = col_a.text_input("Unidad", placeholder="Ej: kg, m, unidad")
        description = col_b.text_input("Descripción", placeholder="Descripción breve")
        submit      = st.form_submit_button("Crear Material", use_container_width=True)

    if submit:
        if code and name:
            unit_clean = unit.strip()
            if unit_clean.startswith("-") and unit_clean.lstrip("-").replace(".", "").isdigit():
                st.error("La unidad no puede ser un número negativo.")

            else:
                created, info = create_material(db, code, name, unit_clean, description)
                if created:
                    st.success("Material creado correctamente.")
                    st.rerun()
                else:
#                     st.error("Error al crear el material")
#                 time.sleep(2)
#                 st.rerun()  
#         else:
#             st.error("Código y nombre son obligatorios")
#             time.sleep(2)
#             st.rerun()

# materials = get_materials(db)
# # -------------------------
# # EDITAR MATERIAL
# # -------------------------
# st.subheader("✏️ Editar Material")

# with st.expander("⚙️Formulario de edición", expanded=True):
    
#     if materials:

#         select = st.selectbox(
#         "Selecciona un material",
#         [m.name for m in materials])
        
#             # Obtener el ID del material seleccionado
#         selected_id = next((m.id for m in materials if m.name == select), None)

#         selected = next((m for m in materials if m.id == selected_id), None)

#         if selected:
#             col1, col2, col3 = st.columns(3)

#             with col1:
#                 new_code = st.text_input("Código", value=selected.code)
#             with col2:
#                 new_name = st.text_input("Nombre", value=selected.name)
#             with col3:
#                 new_unit = st.text_input("Unidad (kg, m, unidad, etc.)", value=selected.unit)
#             col4 = st.columns(1)[0]
#             with col4:
#                 new_description = st.text_area("Descripción", value=selected.description, key="edit_desc")
#             submit = st.button("✅Actualizar", use_container_width=True)

#             if submit:
#                 if new_code and new_name:
#                     updated, info = update_material(
#                         db,
#                         selected.id,
#                         new_code,
#                         new_name,
#                         new_unit,
#                         new_description
#                     )

#                     if updated:
#                         st.success("Material actualizado correctamente")
#                         #st.session_state["refresh"] = True
#                         time.sleep(2)
#                         st.rerun()
#                     else:
#                         if info == 'code':
#                             st.error("El código ya está en uso")
#                         elif info == 'name':
#                             st.error("El nombre ya está en uso")
#                         else:
#                             st.error("Error al actualizar el material")
#                         #st.session_state["refresh"] = True
#                         time.sleep(2)
#                         st.rerun()
                        
#                 else:
#                     st.error("Código y nombre son obligatorios")
#                     #st.session_state["refresh"] = True
#                     time.sleep(2)
#                     st.rerun()
#     else:
#         st.info("No hay materiales registrados")
#         st.write("Agrega un nuevo material usando el formulario de arriba.")
        
    
# # -------------------------
# # LISTAR MATERIALES
# # -------------------------
# st.subheader("📋 Lista de Materiales")

# # Inicializar estado de paginación
# if "page" not in st.session_state:
#     st.session_state.page = 0
# if "filters_applied" not in st.session_state:
#     st.session_state.filters_applied = False

# # SECTION: FILTROS
# with st.expander("🔍 Filtros", expanded=True):
#     col1, col2,col3 = st.columns(3)
    
#     with col1:
#         code_filter = st.text_input("Filtrar por código", value="", key="m_code",
#                                     help="Escribe parte del código para filtrar. Deja vacío para no filtrar por código.")
    
#     with col2:
#         name_filter = st.text_input("Filtrar por nombre", value="", key="m_name",
#                                     help="Escribe parte del nombre para filtrar. Deja vacío para no filtrar por nombre.")
    
#     with col3:
#         unit_filter = st.text_input("Filtrar por unidad", value="", key="m_unit",
#                                     help="Escribe parte de la unidad para filtrar. Deja vacío para no filtrar por unidad.")

#     col_search, col_clear = st.columns([1, 1])

#     with col_search:
#         if st.button("🔎 Buscar", use_container_width=True):
#             st.session_state.page = 0
#             st.session_state.filters_applied = True
    
#     def clear_materials_filters():
#         st.session_state["m_code"] = ""
#         st.session_state["m_name"] = ""
#         st.session_state["m_unit"] = ""
#         st.session_state.page = 0
#         st.session_state.filters_applied = False

#     with col_clear:
#         st.button("🔄 Limpiar Filtros", use_container_width=True, on_click=clear_materials_filters)


# # SECTION: OBTENER DATOS CON FILTROS
# items_per_page = 10

# # Aplicar filtros
# filter_code_val = code_filter if code_filter else None
# filter_name_val = name_filter if name_filter else None
# filter_unit_val = unit_filter if unit_filter else None

# materials, total_count = get_materials_filtered(
#     db,
#     skip=st.session_state.page * items_per_page,  
#     limit=items_per_page,
#     code_filter=filter_code_val,
#     name_filter=filter_name_val,
#     unit_filter=filter_unit_val
# )

# # Mostrar información de paginación
# st.info(f"📊 Total de materiales: **{total_count}** | Mostrando: **{len(materials)}** | Página: **{st.session_state.page + 1}**")  

# # SECTION: MOSTRAR MATERIALES

# if materials:
#     for m in materials:
#         col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
#         with col1:
#             st.write(f"**Código:** {m.code}")
#         with col2:
#             st.write(f"**Nombre:** {m.name}")
#         with col3:
#             st.write(f"**Unidad:** {m.unit}")
#         # BOTÓN ELIMINAR
#         if col4.button(
#             "🗑️ Eliminar", 
#             key=f"del_{m.id}", 
#             type="primary", 
#             use_container_width=True,
#             help="Eliminar este material. Ten en cuenta que esta acción no se puede deshacer."
#         ):
            
#             delete_material(db, m.id)
#             st.rerun()
        
#         with st.expander(f"👁️ Ver Detalle - Material #{m.id}"):
#             st.write(f"**Descripción:** {m.description if m.description else 'Sin descripción'}")
#             st.divider()
        

        
# else:
#     st.warning("❌ No se encontraron materiales con los filtros aplicados." if st.session_state.filters_applied else "No hay materiales registrados.")


# # SECTION: PAGINACIÓN
# col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

# with col1:
#     if st.session_state.page > 0:
#         if st.button("⬅️ Anterior", use_container_width=True):
#             st.session_state.page -= 1
#             st.rerun()

# with col5:
#     if len(materials) == items_per_page and (st.session_state.page + 1) * items_per_page < total_count:
#         if st.button("Siguiente ➡️", use_container_width=True):
#             st.session_state.page += 1
#             st.rerun()

# with col3:
#     st.markdown(f"<div style='text-align: center; padding: 10px;'>Página **{st.session_state.page + 1}** de **{(total_count + items_per_page - 1) // items_per_page}**</div>", unsafe_allow_html=True)

                    msgs = {"code": "El código ya está en uso.", "name": "El nombre ya está en uso."}
                    st.error(msgs.get(info, "Error al crear el material."))
        else:
            st.error("Código y nombre son obligatorios.")

# ── Catálogo + Gestión ────────────────────────────────────────────────────────
st.markdown(f'<div class="sec-title">Catálogo de Materiales ({len(materials)})</div>', unsafe_allow_html=True)

if st.session_state.get("mat_op_msg"):
    st.success(st.session_state.pop("mat_op_msg"))

if not materials:
    st.info("No hay materiales registrados. Crea el primero con el formulario de arriba.")
else:
    for m in materials:
        col_card, col_edit, col_del = st.columns([9, 1, 1], gap="small", vertical_alignment="center")

        with col_card:
            desc_row = (
                f"<div style='margin-top:.22rem;font-size:.71rem;color:rgba(148,163,184,.45);"
                f"white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>{m.description}</div>"
            ) if m.description else ""
            st.markdown(f"""
<div class="mat-info-card" style="padding:.6rem 1.1rem;border-radius:12px;
            border:1px solid rgba(37,99,235,.14);background:rgba(37,99,235,.04)">
  <div style="display:grid;grid-template-columns:max-content 1fr max-content;
              align-items:center;gap:.75rem">
    <span style="display:inline-flex;align-items:center;padding:.17rem .6rem;border-radius:20px;
                 font-size:.67rem;font-weight:700;background:rgba(37,99,235,.18);color:#60a5fa;
                 border:1px solid rgba(37,99,235,.22);white-space:nowrap;flex-shrink:0">{m.code}</span>
    <span style="font-weight:800;color:#f1f5f9;font-size:.88rem;white-space:nowrap;
                 overflow:hidden;text-overflow:ellipsis">{m.name}</span>
    <span style="font-size:.74rem;color:rgba(148,163,184,.55);white-space:nowrap;
                 padding-left:.2rem;flex-shrink:0">{m.unit or '—'}</span>
  </div>
  {desc_row}
</div>""", unsafe_allow_html=True)

        with col_edit:
            editing = st.session_state.get("edit_mat_id") == m.id
            if st.button("✏", key=f"edit_mat_btn_{m.id}", use_container_width=True,
                         help="Editar material", type="primary" if editing else "secondary"):
                if editing:
                    st.session_state.pop("edit_mat_id", None)
                else:
                    st.session_state["edit_mat_id"] = m.id
                    st.session_state.pop("confirm_del_mat", None)
                st.rerun()

        with col_del:
            if st.button("✕", key=f"del_mat_btn_{m.id}", use_container_width=True,
                         help="Eliminar material"):
                st.session_state["confirm_del_mat"] = m.id
                st.session_state.pop("edit_mat_id", None)

        # ── Formulario de edición inline ──────────────────────────────────────
        if st.session_state.get("edit_mat_id") == m.id:
            with st.container():
                st.markdown(
                    "<div style='border-left:3px solid rgba(37,99,235,.40);padding-left:.8rem;"
                    "margin:.2rem 0 .5rem .1rem'>",
                    unsafe_allow_html=True)
                col_a, col_b = st.columns(2, gap="medium")
                new_code = col_a.text_input("Código *",      value=m.code,              key=f"ed_code_{m.id}")
                new_name = col_b.text_input("Nombre *",      value=m.name,              key=f"ed_name_{m.id}")
                new_unit = col_a.text_input("Unidad",        value=m.unit or "",        key=f"ed_unit_{m.id}")
                new_desc = col_b.text_input("Descripción",   value=m.description or "", key=f"ed_desc_{m.id}")
                st.markdown("</div>", unsafe_allow_html=True)

                s_col, c_col = st.columns(2, gap="small")
                if s_col.button("Guardar cambios", type="primary", key=f"save_mat_{m.id}", use_container_width=True):
                    if new_code.strip() and new_name.strip():
                        unit_clean = new_unit.strip()
                        updated, info = update_material(db, m.id, new_code.strip(), new_name.strip(), unit_clean, new_desc.strip())
                        if updated:
                            st.session_state.pop("edit_mat_id", None)
                            st.session_state["mat_op_msg"] = "Material actualizado correctamente."
                            st.rerun()
                        else:
                            msgs = {"code": "El código ya está en uso.", "name": "El nombre ya está en uso."}
                            st.error(msgs.get(info, "Error al actualizar."))
                    else:
                        st.error("Código y nombre son obligatorios.")
                if c_col.button("Cancelar edición", key=f"cancel_edit_{m.id}", use_container_width=True):
                    st.session_state.pop("edit_mat_id", None)
                    st.rerun()

        # ── Confirmación de eliminación ───────────────────────────────────────
        if st.session_state.get("confirm_del_mat") == m.id:
            c_msg, c_yes, c_no = st.columns([5, 1, 1], gap="small")
            c_msg.error(f"¿Eliminar permanentemente **{m.name}** ({m.code})? No se puede deshacer.")
            if c_yes.button("Sí, eliminar", key=f"yes_del_mat_{m.id}", type="primary", use_container_width=True):
                delete_material_code(db, m.code)
                st.session_state.pop("confirm_del_mat", None)
                st.session_state["mat_op_msg"] = f"Material **{m.name}** eliminado correctamente."
                st.rerun()
            if c_no.button("Cancelar", key=f"no_del_mat_{m.id}", use_container_width=True):
                st.session_state.pop("confirm_del_mat", None)
                st.rerun()

db.close()
