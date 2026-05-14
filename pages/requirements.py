# -*- coding: utf-8 -*-
import streamlit as st
from datetime import datetime, timedelta
from database import SessionLocal
from services.requirement_service import create_requirement, get_requirements, cancel_requirement
from services.warehouse_service import get_warehouses
from models.warehouse import Warehouse
from models.material import Material
from models.inventory import Inventory
from utils.auth import require_cliente, get_current_user_id
from utils.navbar import render_navbar, render_sidebar_menu
from datetime import datetime, timedelta

st.set_page_config(page_title="Requerimientos — Sistema MRP", layout="wide", initial_sidebar_state="expanded")

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

/* Status badges */
.badge-pending   { display:inline-block; padding:.18rem .65rem; border-radius:20px; font-size:.70rem; font-weight:700; background:rgba(234,179,8,.18);  color:#fbbf24; }
.badge-fulfilled { display:inline-block; padding:.18rem .65rem; border-radius:20px; font-size:.70rem; font-weight:700; background:rgba(16,185,129,.18); color:#34d399; }
.badge-partial   { display:inline-block; padding:.18rem .65rem; border-radius:20px; font-size:.70rem; font-weight:700; background:rgba(249,115,22,.18);  color:#fb923c; }
.badge-cancelled { display:inline-block; padding:.18rem .65rem; border-radius:20px; font-size:.70rem; font-weight:700; background:rgba(239,68,68,.18);   color:#f87171; }

/* Req card */
.req-card {
    padding: .75rem 1.1rem; border-radius: 12px;
    border: 1px solid rgba(37,99,235,.15); background: rgba(37,99,235,.04);
    margin-bottom: .5rem;
}
.req-id   { font-size: .78rem; font-weight: 800; color: #93c5fd; }
.req-date { font-size: .72rem; opacity: .55; }

/* Pagination */
.pg-info {
    text-align: center; font-size: .80rem; font-weight: 600;
    padding: .5rem 0; opacity: .70;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    render_sidebar_menu()


st.title("📋 Requerimientos")

db       = SessionLocal()
owner_id = get_current_user_id()

all_user_warehouses = get_warehouses(db, owner_id=owner_id)
warehouses          = [w for w in all_user_warehouses if w.type == "obra"]
principal_warehouse = next((w for w in all_user_warehouses if w.type == "principal"), None)
wh_id_to_name       = {w.id: w.name for w in all_user_warehouses}

# Solo materiales que tienen inventario en el almacén principal del usuario
if principal_warehouse:
    _principal_inv     = db.query(Inventory).filter(Inventory.warehouse_id == principal_warehouse.id).all()
    _principal_mat_ids = {inv.material_id for inv in _principal_inv}
    materials          = db.query(Material).filter(Material.id.in_(_principal_mat_ids)).all()
else:
    materials = db.query(Material).all()

# IDs de todos los almacenes del usuario (para filtrar requerimientos)
owner_wh_ids = [w.id for w in all_user_warehouses]

# ── Hero ──────────────────────────────────────────────────────────────────────
_, total_reqs = get_requirements(db, skip=0, limit=1, warehouse_ids=owner_wh_ids)

st.markdown(f"""
<div class="op-hero">
  <div class="op-hero-left">
    <div class="op-hero-icon">&#128203;</div>
    <div>
      <h1>Requerimientos</h1>
      <p>Solicitudes de materiales para almacenes de obra</p>
    </div>
  </div>
  <div class="op-badge">{total_reqs} requerimientos en total</div>
</div>
""", unsafe_allow_html=True)

# ── Instrucciones ─────────────────────────────────────────────────────────────
_, _col_help = st.columns([6, 1])
with _col_help.popover("Instrucciones", use_container_width=True):
    st.markdown("#### Requerimientos — Guía de uso")
    st.markdown("""
**Crear un requerimiento**
1. Selecciona el **almacén de obra** que recibirá los materiales.
2. Indica cuántos materiales necesitas y completa cada línea con material y cantidad.
3. Presiona **Crear Requerimiento**; el sistema reservará automáticamente el stock disponible.

**Estados del requerimiento**
- **Pendiente:** sin stock reservado aún (stock insuficiente o nulo).
- **Parcial:** stock reservado solo en parte; queda saldo pendiente.
- **Cumplido:** todo el stock está reservado y listo para despacho.

**Filtros y paginación**
- Usa los filtros por ID, estado y rango de fechas para localizar requerimientos.
- Navega con los botones **Anterior / Siguiente** para ver más resultados.
- Haz clic en **Ver detalle** de cualquier requerimiento para revisar sus ítems.

> Necesitas al menos un almacén de **obra** y un **material** creados antes de generar requerimientos.
""")

# ── Crear ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-title">Nuevo Requerimiento</div>', unsafe_allow_html=True)


if not warehouses:
#     st.error("No hay almacenes de obra configurados. Por favor crea uno primero.")
#     st.stop()

# if not materials:
#     st.error("No hay materiales configurados. Por favor crea uno primero.")
#     st.stop()


# wh_dict = {w.name: w.id for w in warehouses}
# mat_dict = {m.name: m.id for m in materials}

# selected_wh = st.selectbox("Almacén de obra", list(wh_dict.keys()))

# items = []

# num_items = st.number_input("Cantidad de materiales", min_value=1, step=1)


# if mat_dict: 
#     for i in range(num_items):
#         st.write(f"Material {i+1}")
#         mat = st.selectbox(f"Material {i}", list(mat_dict.keys()), key=f"mat_{i}")
#         qty = st.number_input(f"Cantidad {i}", min_value=1, key=f"qty_{i}")

#         items.append({
#             "material_id": mat_dict[mat],
#             "qty": qty
#         })
    
    
#     if st.button("Crear Requerimiento"):
#         success, msg = create_requirement(db, wh_dict[selected_wh], items)
#         if success:
#             st.success(msg)
#             st.rerun()
#         else:
#             st.error(msg)
# else:
#     st.warning("No hay materiales disponibles para seleccionar")


# # ========================
# # LISTA DE REQUERIMIENTOS CON FILTROS Y PAGINACIÓN
# # ========================
# st.subheader("📋 Lista de Requerimientos")

# # Inicializar estado de paginación
# if "page" not in st.session_state:
#     st.session_state.page = 0
# if "filters_applied" not in st.session_state:
#     st.session_state.filters_applied = False

# # SECTION: FILTROS
# with st.expander("🔍 Filtros", expanded=True):
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         filter_id = st.number_input("ID Requerimiento", value=0, min_value=0,
#                                      help="Dejar en 0 para no filtrar", key="f_id")
    
#     with col2:
#         filter_status = st.selectbox("Estado",
#                                      ["", "pending", "fulfilled", "partial", "cancelled"],
#                                      help="Selecciona un estado o deja en blanco para todos", key="f_status")
    
#     with col3:
#         filter_start_date = st.date_input("Desde", value=datetime.now() - timedelta(days=30), key="f_start")
    
#     with col4:
#         filter_end_date = st.date_input("Hasta", value=datetime.now(), key="f_end")
    
#     col_search, col_clear = st.columns([1, 1])
    
#     with col_search:
#         if st.button("🔎 Buscar", use_container_width=True):
#             st.session_state.page = 0
#             st.session_state.filters_applied = True

#     def clear_filters():
#         st.session_state["f_id"] = 0
#         st.session_state["f_status"] = ""
#         st.session_state["f_start"] = (datetime.now() - timedelta(days=30)).date()
#         st.session_state["f_end"] = datetime.now().date()
#         st.session_state.page = 0
#         st.session_state.filters_applied = False

#     with col_clear:
#         st.button("🔄 Limpiar Filtros", use_container_width=True, on_click=clear_filters)


# # SECTION: OBTENER DATOS CON FILTROS
# items_per_page = 10

# # Convertir a datetime completo
# start_datetime = datetime.combine(filter_start_date, datetime.min.time())
# end_datetime = datetime.combine(filter_end_date, datetime.max.time())

# # Aplicar filtros
# filter_id_val = filter_id if filter_id > 0 else None
# filter_status_val = filter_status if filter_status else None

# requirements, total_count = get_requirements(
#     db,
#     skip=st.session_state.page * items_per_page,
#     limit=items_per_page,
#     requirement_id=filter_id_val,
#     status=filter_status_val,
#     start_date=start_datetime,
#     end_date=end_datetime
# )

# # Mostrar información de paginación
# st.info(f"📊 Total de requerimientos: **{total_count}** | Mostrando: **{len(requirements)}** | Página: **{st.session_state.page + 1}**")

# # SECTION: MOSTRAR REQUERIMIENTOS
# if requirements:
#     for r in requirements:
#         # Formatos para la tarjeta
#         status_colors = {
#             "pending": "🟡",
#             "fulfilled": "🟢",
#             "partial": "🟠",
#             "cancelled": "🔴"
#         }
#         status_icon = status_colors.get(r.status, "⚪")
        
#         col1, col2, col3 = st.columns([2, 2, 2])
        
#         with col1:
#             st.write(f"**ID:** {r.id}")
        
#         with col2:
#             st.write(f"**Estado:** {status_icon} {r.status.upper()}")
        
#         with col3:
#             st.write(f"**Fecha:** {r.created_at.strftime('%d/%m/%Y %H:%M')}")
        
#         with st.expander(f"👁️ Ver Detalle - Requerimiento #{r.id}"):
#             st.write(f"**Almacén:** {r.warehouse_id_obra}")
#             st.write(f"**Notas:** {r.notes if r.notes else 'Sin notas'}")
            
#             st.write("**Ítems:**")
#             for item in r.items:
#                 item_status = f"🟢 {item.status.upper()}" if item.status == "reserved" else f"🟡 {item.status.upper()}"
#                 st.write(
#                     f"- {item.material.name if item.material else 'Material desconocido'} "
#                     f"| Solicitado: {item.requested_qty} "
#                     f"| Cumplido: {item.fulfilled_qty} "
#                     f"| Estado: {item_status}"
#                 )
        
#         st.divider()
# else:
#     st.warning("❌ No se encontraron requerimientos con los filtros aplicados" if st.session_state.filters_applied else "No hay requerimientos registrados.")


# # SECTION: PAGINACIÓN
# col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

# with col1:
#     if st.session_state.page > 0:
#         if st.button("⬅️ Anterior", use_container_width=True):
#             st.session_state.page -= 1
#             st.rerun()

# with col5:
#     if len(requirements) == items_per_page and (st.session_state.page + 1) * items_per_page < total_count:
#         if st.button("Siguiente ➡️", use_container_width=True):
#             st.session_state.page += 1
#             st.rerun()

# with col3:
#     st.markdown(f"<div style='text-align: center; padding: 10px;'>Página **{st.session_state.page + 1}** de **{(total_count + items_per_page - 1) // items_per_page}**</div>", unsafe_allow_html=True)

    if not all_user_warehouses:
        st.error("No tienes almacenes registrados. Ve a **Almacenes** y crea uno de tipo **principal** y otro de tipo **obra**.")
    else:
        tipos = ", ".join(set(w.type for w in all_user_warehouses))
        st.warning(
            f"Tienes {len(all_user_warehouses)} almacén(es) registrado(s) (tipo: {tipos}), "
            "pero ninguno es de tipo **obra**. "
            "Ve a **Almacenes**, crea o edita uno y selecciona tipo **obra**."
        )
elif not principal_warehouse:
    st.error("No tienes un almacén **principal** registrado. Ve a **Almacenes** y crea uno de tipo principal.")
elif not materials:
    st.warning(
        f"El almacén principal **{principal_warehouse.name}** no tiene materiales en inventario. "
        "Ve a **Inventario** y agrega stock primero."
    )
else:
    if st.session_state.get("req_created_msg"):
        st.success(st.session_state.pop("req_created_msg"))

    with st.expander("Crear requerimiento", expanded=False):
        wh_dict  = {w.name: w.id for w in warehouses}
        mat_dict = {m.name: m.id for m in materials}

        selected_wh  = st.selectbox("Almacén de obra", list(wh_dict.keys()), key="req_wh")
        num_items    = st.number_input("Cantidad de materiales", min_value=1, max_value=20, step=1, key="req_num")

        items = []
        for i in range(int(num_items)):
            col_m, col_q = st.columns([3, 1], gap="small")
            mat = col_m.selectbox(f"Material {i+1}", list(mat_dict.keys()), key=f"req_mat_{i}")
            qty = col_q.number_input("Cantidad", min_value=1, key=f"req_qty_{i}", label_visibility="visible")
            items.append({"material_id": mat_dict[mat], "qty": qty})

        if st.button("Crear Requerimiento", type="primary", key="btn_create_req"):
            success, msg = create_requirement(db, wh_dict[selected_wh], items)
            if success:
                for k in ["req_wh", "req_num"] + [f"req_mat_{i}" for i in range(int(num_items))] + [f"req_qty_{i}" for i in range(int(num_items))]:
                    st.session_state.pop(k, None)
                st.session_state["req_created_msg"] = msg
                st.rerun()
            else:
                st.error(msg)

# ── Filtros ───────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-title">Lista de Requerimientos</div>', unsafe_allow_html=True)

with st.expander("Filtros", expanded=False):
    fc1, fc2, fc3, fc4 = st.columns(4, gap="small")
    filter_id     = fc1.number_input("ID", value=0, min_value=0, key="flt_id")
    filter_status = fc2.selectbox("Estado", ["", "pending", "fulfilled", "partial", "cancelled"], key="flt_st")
    filter_start  = fc3.date_input("Desde", value=datetime.now() - timedelta(days=30), key="flt_from")
    filter_end    = fc4.date_input("Hasta", value=datetime.now(), key="flt_to")

    bc1, bc2 = st.columns(2, gap="small")
    if bc1.button("Buscar", type="primary", use_container_width=True, key="btn_search_req"):
        st.session_state["req_page"] = 0
    if bc2.button("Limpiar", use_container_width=True, key="btn_clear_req"):
        for _fk in ["flt_id", "flt_st", "flt_from", "flt_to"]:
            st.session_state.pop(_fk, None)
        st.session_state["req_page"] = 0
        st.rerun()

# ── Paginación ────────────────────────────────────────────────────────────────
ITEMS_PER_PAGE = 10
if "req_page" not in st.session_state:
    st.session_state["req_page"] = 0

start_dt = datetime.combine(filter_start, datetime.min.time())
# +1 día extra cubre diferencias de zona horaria entre datetime.now() (local)
# y posibles registros históricos en UTC que caen un día adelante
end_dt   = datetime.combine(filter_end + timedelta(days=1), datetime.min.time())

requirements, total_count = get_requirements(
    db,
    skip           = st.session_state["req_page"] * ITEMS_PER_PAGE,
    limit          = ITEMS_PER_PAGE,
    requirement_id = int(filter_id) if filter_id > 0 else None,
    status         = filter_status if filter_status else None,
    start_date     = start_dt,
    end_date       = end_dt,
    warehouse_ids  = owner_wh_ids,
)

total_pages = max(1, (total_count + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)

# ── Resultados ────────────────────────────────────────────────────────────────
_STATUS_EMOJI = {
    "pending":   "⏳",
    "fulfilled": "✅",
    "partial":   "🔶",
    "cancelled": "❌",
}
_STATUS_TEXT = {
    "pending":   "Pendiente",
    "fulfilled": "Cumplido",
    "partial":   "Parcial",
    "cancelled": "Cancelado",
}
_ITEM_BADGE = {
    "reserved":  ('<span style="display:inline-block;padding:.15rem .55rem;border-radius:12px;'
                  'font-size:.70rem;font-weight:700;background:rgba(37,99,235,.18);'
                  'color:#93c5fd">Reservado</span>'),
    "pending":   ('<span style="display:inline-block;padding:.15rem .55rem;border-radius:12px;'
                  'font-size:.70rem;font-weight:700;background:rgba(234,179,8,.18);'
                  'color:#fbbf24">Pendiente</span>'),
    "partial":   ('<span style="display:inline-block;padding:.15rem .55rem;border-radius:12px;'
                  'font-size:.70rem;font-weight:700;background:rgba(249,115,22,.18);'
                  'color:#fb923c">Parcial</span>'),
    "fulfilled": ('<span style="display:inline-block;padding:.15rem .55rem;border-radius:12px;'
                  'font-size:.70rem;font-weight:700;background:rgba(16,185,129,.18);'
                  'color:#34d399">Cumplido</span>'),
}
_ITEM_CANCELLED = ('<span style="display:inline-block;padding:.15rem .55rem;border-radius:12px;'
                   'font-size:.70rem;font-weight:700;background:rgba(239,68,68,.18);'
                   'color:#f87171">Cancelado</span>')

if not requirements:
    st.info("No se encontraron requerimientos con los filtros aplicados.")
else:
    for r in requirements:
        wh_name    = wh_id_to_name.get(r.warehouse_id_obra, f"Almacén #{r.warehouse_id_obra}")
        n_items    = len(r.items) if r.items else 0
        fecha      = r.created_at.strftime("%d/%m/%Y %H:%M")
        can_cancel = r.status in ("pending", "partial")  # "fulfilled" = ya despachado, no se puede cancelar
        s_emoji    = _STATUS_EMOJI.get(r.status, "")
        s_text     = _STATUS_TEXT.get(r.status, r.status)

        exp_label = (
            f"#{r.id}  ·  {s_emoji} {s_text}"
            f"  ·  📅 {fecha}"
            f"  ·  🏢 {wh_name}"
            f"  ·  {n_items} ítem{'s' if n_items != 1 else ''}"
        )

        with st.expander(exp_label):
            # ── Cancelar ──────────────────────────────────────────────────
            if can_cancel:
                if st.button(
                    "🗑 Cancelar requerimiento",
                    key=f"cancel_btn_{r.id}",
                    type="secondary",
                ):
                    st.session_state["confirm_cancel_req"] = r.id

            if st.session_state.get("confirm_cancel_req") == r.id:
                c_msg, c_yes, c_no = st.columns([5, 1, 1], gap="small")
                c_msg.warning(
                    f"¿Cancelar el **Requerimiento #{r.id}**? "
                    "Se liberará todo el stock reservado. Esta acción no se puede deshacer."
                )
                if c_yes.button("Sí, cancelar", key=f"yes_cancel_req_{r.id}",
                                type="primary", use_container_width=True):
                    cancel_requirement(db, r.id)
                    del st.session_state["confirm_cancel_req"]
                    st.rerun()
                if c_no.button("No, mantener", key=f"no_cancel_req_{r.id}",
                               use_container_width=True):
                    del st.session_state["confirm_cancel_req"]
                    st.rerun()
                st.markdown("<hr style='margin:.5rem 0;border-color:rgba(37,99,235,.15)'>",
                            unsafe_allow_html=True)

            # ── Notas ─────────────────────────────────────────────────────
            if r.notes:
                st.markdown(
                    f"<div style='font-size:.82rem;color:rgba(148,163,184,.60);"
                    f"margin-bottom:.6rem'><strong>Notas:</strong> {r.notes}</div>",
                    unsafe_allow_html=True,
                )

            # ── Ítems ─────────────────────────────────────────────────────
            if not r.items:
                st.info("Sin ítems.")
            else:
                for it in r.items:
                    mat_name  = it.material.name if it.material else f"Material {it.material_id}"
                    mat_unit  = (it.material.unit or "") if it.material else ""
                    if r.status == "cancelled":
                        it_badge = _ITEM_CANCELLED
                    else:
                        it_badge = _ITEM_BADGE.get(it.status, it.status)
                    cum_color = "#34d399" if it.fulfilled_qty > 0 else "#94a3b8"
                    pct       = int(it.fulfilled_qty / it.requested_qty * 100) if it.requested_qty else 0
                    st.markdown(f"""
<div style="display:flex;align-items:center;gap:1.2rem;padding:.65rem 1rem;
            border-radius:11px;border:1px solid rgba(37,99,235,.13);
            background:rgba(37,99,235,.04);margin-bottom:.35rem;flex-wrap:wrap">
  <div style="flex:1;min-width:140px">
    <span style="font-weight:800;color:#e2e8f0;font-size:.85rem">{mat_name}</span>
    {"<span style='font-size:.71rem;color:rgba(148,163,184,.50);margin-left:.4rem'>" + mat_unit + "</span>" if mat_unit else ""}
  </div>
  <div style="display:flex;gap:1.4rem;align-items:center;flex-wrap:wrap">
    <div style="text-align:center;min-width:48px">
      <div style="font-size:.60rem;font-weight:700;color:rgba(148,163,184,.50);
                  text-transform:uppercase;letter-spacing:.05em">Solicitado</div>
      <div style="font-weight:900;color:#60a5fa;font-size:.95rem">{it.requested_qty}</div>
    </div>
    <div style="text-align:center;min-width:48px">
      <div style="font-size:.60rem;font-weight:700;color:rgba(148,163,184,.50);
                  text-transform:uppercase;letter-spacing:.05em">Cumplido</div>
      <div style="font-weight:900;color:{cum_color};font-size:.95rem">{it.fulfilled_qty}</div>
    </div>
    <div style="text-align:center;min-width:36px">
      <div style="font-size:.60rem;font-weight:700;color:rgba(148,163,184,.50);
                  text-transform:uppercase;letter-spacing:.05em">%</div>
      <div style="font-weight:700;color:rgba(148,163,184,.60);font-size:.85rem">{pct}%</div>
    </div>
    <div>{it_badge}</div>
  </div>
</div>""", unsafe_allow_html=True)

# ── Navegación de páginas ─────────────────────────────────────────────────────
pg_prev, pg_info, pg_next = st.columns([1, 3, 1])

with pg_prev:
    if st.session_state["req_page"] > 0:
        if st.button("← Anterior", use_container_width=True, key="pg_prev_btn"):
            st.session_state["req_page"] -= 1
            st.rerun()

with pg_info:
    st.markdown(
        f'<div class="pg-info">Página {st.session_state["req_page"] + 1} de {total_pages} &nbsp;·&nbsp; {total_count} resultados</div>',
        unsafe_allow_html=True,
    )

with pg_next:
    if (st.session_state["req_page"] + 1) * ITEMS_PER_PAGE < total_count:
        if st.button("Siguiente →", use_container_width=True, key="pg_next_btn"):
            st.session_state["req_page"] += 1
            st.rerun()

db.close()
