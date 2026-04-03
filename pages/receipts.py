import streamlit as st
from database import SessionLocal
from services.receipt_service import create_receipt
from models.dispatch import Dispatch

st.title("📥 Recepción de Materiales")

db = SessionLocal()

# -------------------------
# DESPACHOS DISPONIBLES
# -------------------------
dispatches = db.query(Dispatch).all()

disp_dict = {f"Despacho {d.id}": d.id for d in dispatches}

selected = st.selectbox("Selecciona despacho", list(disp_dict.keys()))

dispatch_id = disp_dict[selected]

# -------------------------
# DETALLE
# -------------------------
dispatch = db.query(Dispatch).filter(
    Dispatch.id == dispatch_id
).first()

st.subheader("Materiales despachados")

for item in dispatch.items:
    st.write(f"Material {item.material_id} - Cantidad: {item.dispatched_qty}")

# -------------------------
# CONFIRMAR
# -------------------------
if st.button("Confirmar Recepción"):
    success, msg = create_receipt(db, dispatch_id)

    if success:
        st.success(msg)
        st.rerun()
    else:
        st.error(msg)