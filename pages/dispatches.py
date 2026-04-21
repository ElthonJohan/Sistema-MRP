import streamlit as st
from database import SessionLocal
from services.dispatch_service import create_dispatch
from models.requirement import Requirement
from models.material import Material

st.title("🚚 Despachos")

db = SessionLocal()

# -------------------------
# SELECCIONAR REQUERIMIENTO
# -------------------------
requirements = db.query(Requirement).filter(
    Requirement.status.in_(["partial", "fulfilled"])
).all()

req_dict = {f"Req {r.id}": r.id for r in requirements}

selected_req = st.selectbox("Selecciona requerimiento", list(req_dict.keys()))

req_id = req_dict.get(selected_req, None)

req = db.query(Requirement).filter(Requirement.id == req_id).first()

# -------------------------
# ITEMS A DESPACHAR
# -------------------------
items = []

st.subheader("Materiales")
if req and req.items:
    for item in req.items:
        pendiente = item.requested_qty - item.fulfilled_qty

        if pendiente > 0:
            qty = st.number_input(
                f"Material {item.material_id} (pendiente {pendiente})",
                min_value=0,
                max_value=pendiente,
                key=f"mat_{item.material_id}"
            )

            if qty > 0:
                items.append({
                    "material_id": item.material_id,
                    "qty": qty
                })

    # -------------------------
    # CREAR DESPACHO
    # -------------------------
    if st.button("Generar Despacho"):
        success, msg = create_dispatch(db, req_id, items)

        if success:
            st.success(msg)
            st.rerun()
        else:
            st.error(msg)

else:
    st.info("No hay requerimientos con estado 'partial' o 'fulfilled'.")