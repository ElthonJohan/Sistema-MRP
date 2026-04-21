import streamlit as st
import pandas as pd
from database import SessionLocal
from services.material_service import (
    create_material,
    get_materials,
    delete_material,
    update_material
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

db = SessionLocal()

# -------------------------
# CREAR MATERIAL
# -------------------------
st.subheader("➕ Crear Material")

with st.form("create_material"):
    code = st.text_input("Código")
    name = st.text_input("Nombre")
    unit = st.text_input("Unidad (kg, m, unidad, etc.)")
    description = st.text_area("Descripción")

    submit = st.form_submit_button("Crear")

    if submit:
        if code and name:
            created, info = create_material(db, code, name, unit, description)
            if created:
                st.success("Material creado correctamente")
            else:
                if info == 'code':
                    st.error("El código ya existe")
                elif info == 'name':
                    st.error("El nombre ya existe")
                else:
                    st.error("Error al crear el material")
        else:
            st.error("Código y nombre son obligatorios")

# -------------------------
# LISTAR MATERIALES
# -------------------------
st.subheader("📋 Lista de Materiales")

materials = get_materials(db)


# 2. Convertir la lista de objetos a una lista de diccionarios
# Usamos __dict__ para extraer los datos de cada objeto automáticamente
data = [m.__dict__ for m in materials]

# 3. Crear el DataFrame
df = pd.DataFrame(data)

# 4. Limpieza (Importante)
# Si usas SQLAlchemy, elimina la columna interna '_sa_instance_state' para que no se vea
if '_sa_instance_state' in df.columns:
    df = df.drop(columns=['_sa_instance_state'])

# 5. Mostrar en Streamlit
st.subheader("Inventario de Materiales")

nuevo_orden = ['code', 'name', 'unit', 'description'] 
df = df[nuevo_orden]
st.dataframe(df, use_container_width=True,hide_index=True)



for m in materials:
    col1, col2, col3, col4, col5 = st.columns([2, 3, 2, 3, 2])

    col1.write(m.code)
    col2.write(m.name)
    col3.write(m.unit)
    col4.write(m.description)

    if col5.button("Eliminar", key=f"del_mat_{m.id}"):
        delete_material(db, m.id)
        st.rerun()


# -------------------------
# EDITAR MATERIAL
# -------------------------
st.subheader("✏️ Editar Material")

if materials:
    select = st.selectbox(
        "Selecciona un material",
        [m.name for m in materials]
    )
    
    selected_id = next((m.id for m in materials if m.name == select), None)

    selected = next((m for m in materials if m.id == selected_id), None)

    if selected:
        new_code = st.text_input("Código", value=selected.code)
        new_name = st.text_input("Nombre", value=selected.name)
        new_unit = st.text_input("Unidad", value=selected.unit)
        new_description = st.text_area("Descripción", value=selected.description)

        if st.button("Actualizar"):
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
                st.rerun()
            else:
                if info == 'code':
                    st.error("El código ya está en uso")
                elif info == 'name':
                    st.error("El nombre ya está en uso")
                else:
                    st.error("Error al actualizar el material")
else:
    st.info("No hay materiales registrados")