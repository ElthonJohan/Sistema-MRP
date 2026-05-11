import streamlit as st
from database import SessionLocal
from services.receipt_service import create_receipt
from models.dispatch import Dispatch
from utils.auth import require_login
from utils.navbar import render_navbar, render_sidebar_menu

st.set_page_config(page_title="Recepciones - MRP System", layout="wide")

require_login()

# Render navbar
render_navbar()
with st.sidebar:
    render_sidebar_menu()


st.title("📥 Recepción de Materiales")

db = SessionLocal()

# -------------------------
# DESPACHOS DISPONIBLES
# -------------------------
dispatches = db.query(Dispatch).all()


if not dispatches:
    st.warning("No hay despachos disponibles")
    st.stop()

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


if dispatch and dispatch.items:
    for item in dispatch.items:
        if item.dispatched_qty > 0:
            st.write(f"Material {item.material_id} - Cantidad: {item.dispatched_qty}")
        else:
            st.write(f"Material {item.material_id} - Cantidad: 0 (ya se ha recibido)")
    if st.button("Confirmar Recepción"):
        success, msg = create_receipt(db, dispatch_id)

        if success:
            st.success(msg)
            st.rerun()
        else:

            st.error(msg)
else:
    st.info("No hay materiales despachados para este despacho o el despacho no existe.")


