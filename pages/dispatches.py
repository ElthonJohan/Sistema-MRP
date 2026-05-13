import streamlit as st
from database import SessionLocal
from services.dispatch_service import create_dispatch, remove_dispatch
from models.requirement import Requirement
from models.material import Material
from utils.auth import require_login
from utils.navbar import render_navbar, render_sidebar_menu
from utils.pdf_generator import generate_dispatch_pdf
import time

st.set_page_config(page_title="Despachos - MRP System", layout="wide")

require_login()

# Render navbar
render_navbar()
with st.sidebar:
    render_sidebar_menu()


st.title("🚚 Despachos")

db = SessionLocal()

# -------------------------
# SELECCIONAR REQUERIMIENTO
# -------------------------
requirements = db.query(Requirement).filter(
    Requirement.status.in_(["partial", "fulfilled"])
).all()


if not requirements:
    st.warning("No hay requerimientos pendientes por despachar")
    st.stop()


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

# -------------------------
# LISTA DE DESPACHOS REALIZADOS
# -------------------------
from services.dispatch_service import get_dispatches
from models.user import User
from models.material import Material

st.subheader("Despachos realizados")
dispatches = get_dispatches(db)

if not dispatches:
    st.info("No hay despachos registrados.")
else:
    for d in dispatches:
        st.markdown(f"**Guía:** {d.guia_number} | **Fecha:** {d.dispatch_date.strftime('%Y-%m-%d %H:%M')} | **Requerimiento:** {d.requirement_id} | **Usuario:** {d.user_id}")
        if d.items:
            mat_rows = []
            for di in d.items:
                # Buscar nombre del material
                mat = db.query(Material).filter(Material.id == di.material_id).first()
                mat_name = mat.name if mat else f"ID {di.material_id}"
                mat_rows.append({
                    "Material": mat_name,
                    "Cantidad despachada": di.dispatched_qty
                })
            st.table(mat_rows)
            
            #PDF
            pdf_path = generate_dispatch_pdf(d)

            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                label=f"📄 Descargar {d.guia_number}",
                data=pdf_file,
                file_name=f"{d.guia_number}.pdf",
                mime="application/pdf",
                key=f"pdf_{d.id}"
            )
            
        delete=st.button("Eliminar despacho", key=f"del_{d.id}")
        if delete:
            success = remove_dispatch(db, d.id)
            if success:
                st.success("Despacho eliminado")
            else:
                st.error("Error al eliminar despacho")
            time.sleep(1)
            st.rerun()

        st.markdown("---")
        st.divider()


