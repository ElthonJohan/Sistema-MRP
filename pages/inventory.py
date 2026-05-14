# -*- coding: utf-8 -*-
import streamlit as st
from database import SessionLocal
from services.inventory_service import add_stock, remove_stock, get_inventory, delete_inventory_record
from models.warehouse import Warehouse
from models.material import Material
from utils.auth import require_cliente, get_current_user_id
from utils.navbar import render_navbar, render_sidebar_menu

st.set_page_config(page_title="Inventario Principal — Sistema MRP", layout="wide", initial_sidebar_state="expanded")

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
[data-testid="stBaseButton-primary"]:hover { opacity: .9 !important; transform: translateY(-1px) !important; }
[data-testid="stAlert"] { border-radius: 10px !important; }

/* Stock level indicators */
.stock-ok   { color: #34d399; font-weight: 700; }
.stock-low  { color: #fbbf24; font-weight: 700; }
.stock-zero { color: #f87171; font-weight: 700; }

/* Remove stock expander border override */
.remove-exp details[data-testid="stExpander"] {
    border-color: rgba(239,68,68,.25) !important;
}
.remove-exp details[data-testid="stExpander"] > summary { color: #f87171 !important; }

/* Delete button — danger style */
[data-testid="stBaseButton-secondary"].del-btn button,
button[kind="secondary"].del-btn {
    background: rgba(239,68,68,.12) !important;
    color: #f87171 !important;
    border: 1px solid rgba(239,68,68,.30) !important;
    border-radius: 8px !important;
    font-size: .75rem !important;
    font-weight: 700 !important;
    box-shadow: none !important;
}
button[kind="secondary"].del-btn:hover {
    background: rgba(239,68,68,.22) !important;
}
/* Confirmation strip */
.del-confirm-strip {
    display: flex; align-items: center; gap: .7rem;
    padding: .65rem 1rem; border-radius: 10px;
    border: 1px solid rgba(239,68,68,.28);
    background: rgba(239,68,68,.07);
    margin-bottom: .4rem; flex-wrap: wrap;
}
.del-confirm-strip span {
    flex: 1; font-size: .82rem; color: #fca5a5; font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    render_sidebar_menu()

db       = SessionLocal()
owner_id = get_current_user_id()

all_warehouses      = db.query(Warehouse).filter(Warehouse.owner_id == owner_id).all()
principal_warehouses = [w for w in all_warehouses if w.type == "principal"]
materials            = db.query(Material).all()

# ── Hero ──────────────────────────────────────────────────────────────────────
all_inventory    = get_inventory(db)
principal_wh_ids = {w.id for w in principal_warehouses}
own_inventory    = [inv for inv in all_inventory if inv.warehouse_id in principal_wh_ids]
total_stock      = sum(inv.stock for inv in own_inventory)

st.markdown(f"""
<div class="op-hero">
  <div class="op-hero-left">
    <div class="op-hero-icon">&#128202;</div>
    <div>
      <h1>Inventario Principal</h1>
      <p>Stock y reservas del almacén principal</p>
    </div>
  </div>
  <div class="op-badge">Stock total: {total_stock} unidades</div>
</div>
""", unsafe_allow_html=True)

if not principal_warehouses:
    st.error("No hay almacén principal configurado. Crea uno en la sección Almacenes.")
    db.close()
    st.stop()

if not materials:
    st.error("No hay materiales configurados. Crea uno primero en la sección Materiales.")
    db.close()
    st.stop()

warehouse_dict = {w.name: w.id for w in principal_warehouses}
material_dict  = {m.name: m.id for m in materials}
wh_id_to_name  = {w.id: w.name for w in all_warehouses}

# ── Instrucciones ─────────────────────────────────────────────────────────────
_, _col_help = st.columns([6, 1])
with _col_help.popover("Instrucciones", use_container_width=True):
    st.markdown("#### Inventario — Guía de uso")
    st.markdown("""
**Ingresar stock**
1. Despliega **Agregar stock a un almacén** y selecciona el almacén, el material y la cantidad.
2. Presiona **Agregar Stock**; el inventario se actualiza al instante y el sistema reprocesa automáticamente los requerimientos pendientes.

**Retirar stock**
1. Despliega **Retirar stock de un almacén** y selecciona almacén, material y cantidad.
2. Solo puedes retirar hasta el stock **disponible** (no el reservado). Si hay stock insuficiente verás un aviso de error.

**Tabla de inventario**
- **Stock:** total físico en el almacén.
- **Reservado:** comprometido para requerimientos pendientes de despacho.
- **Disponible:** Stock menos Reservado; es el stock libre para nuevos requerimientos.

> El stock **disponible** es el único que puede asignarse a nuevos requerimientos. El stock **reservado** ya está comprometido para despachos en curso.
""")

# ── Mensajes post-acción ──────────────────────────────────────────────────────
if st.session_state.get("inv_add_msgs"):
    _msgs = st.session_state.pop("inv_add_msgs")
    st.success(_msgs[0])
    for _m in _msgs[1:]:
        st.info(f"Requerimiento satisfecho — {_m}")

if st.session_state.get("inv_rem_msg"):
    st.success(st.session_state.pop("inv_rem_msg"))

# ── Ingresar stock ────────────────────────────────────────────────────────────
st.markdown('<div class="sec-title">Ingresar Stock</div>', unsafe_allow_html=True)

_add_n = st.session_state.get("add_form_n", 0)
with st.expander("Agregar stock a un almacén", expanded=False):
    col_wh, col_mat, col_qty = st.columns(3, gap="medium")
    in_wh  = col_wh.selectbox("Almacén",  list(warehouse_dict.keys()), key=f"in_wh_{_add_n}")
    in_mat = col_mat.selectbox("Material", list(material_dict.keys()),  key=f"in_mat_{_add_n}")
    in_qty = col_qty.number_input("Cantidad", min_value=1, key=f"in_qty_{_add_n}")

    if st.button("Agregar Stock", type="primary", key=f"btn_add_stock_{_add_n}"):
        newly_fulfilled = add_stock(db, warehouse_dict[in_wh], material_dict[in_mat], in_qty, user_id=owner_id)
        msgs = [f"Se agregaron **{in_qty}** unidades de **{in_mat}** a **{in_wh}**."]
        if newly_fulfilled:
            for _req in newly_fulfilled:
                _obra_name = wh_id_to_name.get(_req.warehouse_id_obra,
                                               f"Almacén #{_req.warehouse_id_obra}")
                msgs.append(
                    f"**Requerimiento #{_req.id}** para **{_obra_name}** "
                    f"quedó completamente reservado y listo para despacho."
                )
        st.session_state["inv_add_msgs"] = msgs
        st.session_state["add_form_n"] = _add_n + 1
        st.rerun()

# ── Retirar stock ─────────────────────────────────────────────────────────────
st.markdown('<div class="sec-title">Retirar Stock</div>', unsafe_allow_html=True)

_rem_n = st.session_state.get("rem_form_n", 0)
with st.expander("Retirar stock de un almacén", expanded=False):
    col_wh2, col_mat2, col_qty2 = st.columns(3, gap="medium")
    out_wh  = col_wh2.selectbox("Almacén",  list(warehouse_dict.keys()), key=f"out_wh_{_rem_n}")
    out_mat = col_mat2.selectbox("Material", list(material_dict.keys()),  key=f"out_mat_{_rem_n}")
    out_qty = col_qty2.number_input("Cantidad", min_value=1, key=f"out_qty_{_rem_n}")

    if st.button("Retirar Stock", type="primary", key=f"btn_rem_stock_{_rem_n}"):
        success = remove_stock(db, warehouse_dict[out_wh], material_dict[out_mat], out_qty, user_id=owner_id)
        if success:
            st.session_state["inv_rem_msg"] = f"Se retiraron **{out_qty}** unidades de **{out_mat}** de **{out_wh}**."
            st.session_state["rem_form_n"] = _rem_n + 1
            st.rerun()
        else:
            st.error("Stock insuficiente para realizar el retiro.")

# ── Inventario Actual ─────────────────────────────────────────────────────────
st.markdown('<div class="sec-title">Inventario Actual</div>', unsafe_allow_html=True)

# Reload after potential mutations (only principal warehouses)
own_inventory = [inv for inv in get_inventory(db) if inv.warehouse_id in principal_wh_ids]

if not own_inventory:
    st.info("Aún no hay registros de inventario. Agrega stock con el formulario de arriba.")
else:
    # ── KPI summary ───────────────────────────────────────────────────────────
    _ts = sum(inv.stock for inv in own_inventory)
    # Reservado solo aplica en almacenes principales
    _tr = sum(inv.reserved for inv in own_inventory
              if inv.warehouse and inv.warehouse.type == "principal")
    _td = _ts - _tr
    st.markdown(f"""
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-bottom:1.2rem">
  <div style="background:linear-gradient(135deg,rgba(37,99,235,.13),rgba(79,70,229,.06));
              border:1px solid rgba(37,99,235,.25);border-radius:16px;padding:1.1rem 1.3rem">
    <div style="font-size:.68rem;font-weight:700;color:rgba(148,163,184,.65);
                text-transform:uppercase;letter-spacing:.07em;margin-bottom:.4rem">Total en stock</div>
    <div style="font-size:2rem;font-weight:900;color:#60a5fa;line-height:1">{_ts}</div>
    <div style="font-size:.70rem;color:rgba(148,163,184,.45);margin-top:.25rem">unidades en todos los almacenes</div>
  </div>
  <div style="background:linear-gradient(135deg,rgba(234,179,8,.12),rgba(249,115,22,.05));
              border:1px solid rgba(234,179,8,.22);border-radius:16px;padding:1.1rem 1.3rem">
    <div style="font-size:.68rem;font-weight:700;color:rgba(148,163,184,.65);
                text-transform:uppercase;letter-spacing:.07em;margin-bottom:.4rem">Total reservado</div>
    <div style="font-size:2rem;font-weight:900;color:#fbbf24;line-height:1">{_tr}</div>
    <div style="font-size:.70rem;color:rgba(148,163,184,.45);margin-top:.25rem">comprometido para despachos</div>
  </div>
  <div style="background:linear-gradient(135deg,rgba(16,185,129,.11),rgba(5,150,105,.05));
              border:1px solid rgba(16,185,129,.22);border-radius:16px;padding:1.1rem 1.3rem">
    <div style="font-size:.68rem;font-weight:700;color:rgba(148,163,184,.65);
                text-transform:uppercase;letter-spacing:.07em;margin-bottom:.4rem">Total disponible</div>
    <div style="font-size:2rem;font-weight:900;color:#34d399;line-height:1">{_td}</div>
    <div style="font-size:.70rem;color:rgba(148,163,184,.45);margin-top:.25rem">libre para nuevos requerimientos</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Alerta: reservas superan stock ───────────────────────────────────────
    _overreserved = [
        inv for inv in own_inventory
        if inv.warehouse and inv.warehouse.type == "principal"
        and inv.reserved > inv.stock
    ]
    if _overreserved:
        st.markdown(
            "<div style='margin-bottom:.6rem'></div>",
            unsafe_allow_html=True,
        )
        for _oi in _overreserved:
            _mat  = _oi.material.name  if _oi.material  else f"Material {_oi.material_id}"
            _unit = _oi.material.unit  if _oi.material  else ""
            _wh   = _oi.warehouse.name if _oi.warehouse else f"Almacén {_oi.warehouse_id}"
            _diff = _oi.reserved - _oi.stock
            st.warning(
                f"**⚠️ Material faltante — {_mat}** en **{_wh}**:  \n"
                f"Reservado ({_oi.reserved} {_unit}) supera el stock actual "
                f"({_oi.stock} {_unit}). "
                f"Se necesitan al menos **{_diff} {_unit}** adicionales para "
                f"cubrir los despachos pendientes.",
                icon=None,
            )

    def _render_inv_group(inv_list):
        for inv in inv_list:
            wh_name     = inv.warehouse.name if inv.warehouse else f"Almacén {inv.warehouse_id}"
            wh_type     = inv.warehouse.type if inv.warehouse else "principal"
            mat_name    = inv.material.name  if inv.material  else f"Material {inv.material_id}"
            mat_unit    = inv.material.unit  if inv.material  else ""
            is_obra     = wh_type == "obra"
            border_c    = "rgba(13,148,136,.16)"  if is_obra else "rgba(37,99,235,.16)"
            bg_c        = "rgba(13,148,136,.05)"  if is_obra else "rgba(37,99,235,.05)"

            # Para almacenes de obra no existe "Reservado" — toda reserva se gestiona en principal
            if is_obra:
                available    = inv.stock
                avail_color  = "#34d399" if available > 0 else "#f87171"
                stats_html   = f"""
      <div>
        <span style="font-size:.63rem;font-weight:700;color:rgba(148,163,184,.55);
                     text-transform:uppercase;letter-spacing:.05em">Stock</span>
        <span style="font-weight:900;color:#60a5fa;font-size:1rem;margin-left:.4rem">{inv.stock}</span>
      </div>
      <div>
        <span style="font-size:.63rem;font-weight:700;color:rgba(148,163,184,.55);
                     text-transform:uppercase;letter-spacing:.05em">Disponible</span>
        <span style="font-weight:900;color:{avail_color};font-size:1rem;margin-left:.4rem">{available}</span>
      </div>"""
            else:
                available   = inv.stock - inv.reserved
                avail_color = "#34d399" if available > 0 else ("#fbbf24" if inv.stock > 0 else "#f87171")
                stats_html  = f"""
      <div>
        <span style="font-size:.63rem;font-weight:700;color:rgba(148,163,184,.55);
                     text-transform:uppercase;letter-spacing:.05em">Stock</span>
        <span style="font-weight:900;color:#60a5fa;font-size:1rem;margin-left:.4rem">{inv.stock}</span>
      </div>
      <div>
        <span style="font-size:.63rem;font-weight:700;color:rgba(148,163,184,.55);
                     text-transform:uppercase;letter-spacing:.05em">Reservado</span>
        <span style="font-weight:900;color:#fbbf24;font-size:1rem;margin-left:.4rem">{inv.reserved}</span>
      </div>
      <div>
        <span style="font-size:.63rem;font-weight:700;color:rgba(148,163,184,.55);
                     text-transform:uppercase;letter-spacing:.05em">Disponible</span>
        <span style="font-weight:900;color:{avail_color};font-size:1rem;margin-left:.4rem">{available}</span>
      </div>"""

            confirming = st.session_state.get("confirm_del_inv") == inv.id

            if not confirming:
                col_card, col_del = st.columns([9, 1], gap="small")
                with col_card:
                    st.markdown(f"""
<div style="display:flex;align-items:center;gap:1.2rem;padding:.85rem 1.2rem;
            border-radius:14px;border:1px solid {border_c};background:{bg_c};
            flex-wrap:wrap">
  <div style="flex:1;min-width:180px">
    <div style="display:flex;align-items:center;gap:.55rem;margin-bottom:.4rem;flex-wrap:wrap">
      <span style="font-weight:800;color:#f1f5f9;font-size:.88rem">{wh_name}</span>
      <span style="color:rgba(148,163,184,.35)">·</span>
      <span style="font-weight:700;color:#93c5fd;font-size:.84rem">{mat_name}</span>
      {"<span style='color:rgba(148,163,184,.45);font-size:.76rem'>" + mat_unit + "</span>" if mat_unit else ""}
    </div>
    <div style="display:flex;gap:2rem;flex-wrap:wrap">{stats_html}
    </div>
  </div>
</div>""", unsafe_allow_html=True)
                with col_del:
                    st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)
                    if st.button(
                        "🗑",
                        key=f"del_inv_{inv.id}",
                        use_container_width=True,
                        help=f"Eliminar inventario de {mat_name} en {wh_name}",
                    ):
                        st.session_state["confirm_del_inv"] = inv.id
                        st.rerun()
            else:
                st.markdown(
                    f"<div class='del-confirm-strip'>"
                    f"<span>¿Eliminar <strong>{mat_name}</strong> en <strong>{wh_name}</strong>? "
                    f"Esta acción no se puede deshacer.</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                c_yes, c_no = st.columns(2, gap="small")
                if c_yes.button("Confirmar eliminación", key=f"yes_inv_{inv.id}",
                                type="primary", use_container_width=True):
                    delete_inventory_record(db, inv.id)
                    del st.session_state["confirm_del_inv"]
                    st.rerun()
                if c_no.button("Cancelar", key=f"no_inv_{inv.id}",
                               use_container_width=True):
                    del st.session_state["confirm_del_inv"]
                    st.rerun()

            st.markdown("<div style='margin-bottom:.25rem'></div>", unsafe_allow_html=True)

    _render_inv_group(own_inventory)

db.close()
