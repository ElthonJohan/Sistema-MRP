import streamlit as st
from database import SessionLocal
from services.requirement_service import create_requirement, get_requirements
from models.warehouse import Warehouse
from models.material import Material

st.title("📋 Requerimientos")

db = SessionLocal()

# -------------------------
# CREAR
# -------------------------
st.subheader("➕ Nuevo Requerimiento")

warehouses = db.query(Warehouse).filter(Warehouse.type == "obra").all()
materials = db.query(Material).all()

wh_dict = {w.name: w.id for w in warehouses}
mat_dict = {m.name: m.id for m in materials}

selected_wh = st.selectbox("Almacén de obra", list(wh_dict.keys()))

items = []

num_items = st.number_input("Cantidad de materiales", min_value=1, step=1)

for i in range(num_items):
    st.write(f"Material {i+1}")
    mat = st.selectbox(f"Material {i}", list(mat_dict.keys()), key=f"mat_{i}")
    qty = st.number_input(f"Cantidad {i}", min_value=1, key=f"qty_{i}")

    items.append({
        "material_id": mat_dict[mat],
        "qty": qty
    })

if st.button("Crear Requerimiento"):
    create_requirement(db, wh_dict[selected_wh], items)
    st.success("Requerimiento creado")
    st.rerun()
    
st.subheader("📋 Lista de Requerimientos")

requirements = get_requirements(db)

for r in requirements:
    st.write(f"ID: {r.id} | Estado: {r.status} | Fecha: {r.created_at}")

    with st.expander("Ver detalle"):
        for item in r.items:
            st.write(
                f"Material: {item.material_id} | "
                f"Solicitado: {item.requested_qty} | "
                f"Estado: {item.status}"
            )