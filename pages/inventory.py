# -*- coding: utf-8 -*-
import streamlit as st
from database import SessionLocal
from services.inventory_service import (
    add_stock, remove_stock, get_inventory, delete_inventory_record,
    get_deleted_inventory, resolve_deleted_inventory,
    get_frozen_inventory_for_owner, redirect_frozen_inventory, unfreeze_inventory,
    assign_project_to_inventory,
)
from services.budget_service import get_budgets, deduct_budget, credit_budget
from models.warehouse import Warehouse
from models.material import Material
from utils.auth import require_cliente, get_current_user_id
from utils.navbar import render_navbar, render_sidebar_menu
import time

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
.sec-title-danger {
    font-size: .95rem; font-weight: 800;
    display: flex; align-items: center; gap: .55rem;
    padding-left: .8rem; border-left: 4px solid #ef4444;
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
/* Deleted inventory panel */
.del-inv-card {
    padding: .85rem 1.2rem; border-radius: 14px;
    border: 1px solid rgba(239,68,68,.22);
    background: rgba(239,68,68,.04);
    margin-bottom: .5rem;
}
/* Pagination */
.pag-info {
    text-align: center; font-size: .80rem;
    color: rgba(148,163,184,.65); font-weight: 600;
    padding: .3rem 0;
}

/* Frozen inventory */
.frozen-card {
    display: flex; align-items: center; gap: 1.2rem;
    padding: .85rem 1.2rem; border-radius: 14px;
    border: 1px solid rgba(100,116,139,.30);
    background: rgba(100,116,139,.07);
    margin-bottom: .45rem; flex-wrap: wrap; opacity: .88;
}
.frozen-badge {
    display: inline-flex; align-items: center; gap: .28rem;
    padding: .15rem .55rem; border-radius: 20px;
    font-size: .63rem; font-weight: 700;
    background: rgba(100,116,139,.20); color: #94a3b8;
    border: 1px solid rgba(148,163,184,.25); white-space: nowrap;
}
.sec-title-frozen {
    font-size: .95rem; font-weight: 800;
    display: flex; align-items: center; gap: .55rem;
    padding-left: .8rem; border-left: 4px solid #64748b;
    margin: 1.8rem 0 .85rem;
}

/* ── Inventory card ── */
.inv-card {
    display: flex; flex-direction: column; gap: .55rem;
    padding: .85rem 1.2rem;
    border-radius: 14px;
    flex-wrap: wrap;
}
.inv-card-head {
    display: flex; align-items: center; gap: .55rem;
    flex-wrap: wrap;
}
.inv-wh   { font-weight: 800; color: #f1f5f9; font-size: .88rem; }
.inv-mat  { font-weight: 700; color: #93c5fd; font-size: .84rem; }
.inv-sep  { color: rgba(148,163,184,.35); }
.inv-unit { color: rgba(148,163,184,.55); font-size: .74rem; }
.inv-stats {
    display: flex; gap: 1.6rem; flex-wrap: wrap;
}
.inv-stat {
    display: flex; align-items: baseline; gap: .42rem;
}
.inv-stat-lbl {
    font-size: .63rem; font-weight: 700;
    color: rgba(148,163,184,.55);
    text-transform: uppercase; letter-spacing: .05em;
}
.inv-stat-val { font-weight: 900; font-size: 1rem; line-height: 1; }
.inv-proj-chip {
    display: inline-flex; align-items: center;
    padding: .18rem .6rem; border-radius: 20px;
    font-size: .65rem; font-weight: 700;
    background: rgba(5,150,105,.18); color: #6ee7b7;
    border: 1px solid rgba(5,150,105,.30);
    white-space: nowrap;
}
.inv-noproj-chip {
    display: inline-flex; align-items: center;
    padding: .15rem .55rem; border-radius: 20px;
    font-size: .62rem; font-weight: 700;
    background: rgba(148,163,184,.10); color: rgba(148,163,184,.65);
    border: 1px dashed rgba(148,163,184,.30);
    white-space: nowrap;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    render_sidebar_menu()

db       = SessionLocal()
owner_id = get_current_user_id()

all_warehouses       = db.query(Warehouse).filter(Warehouse.owner_id == owner_id).all()
principal_warehouses = [w for w in all_warehouses if w.type == "principal"]
materials            = db.query(Material).all()

# ── Hero ──────────────────────────────────────────────────────────────────────
all_inventory    = get_inventory(db)
principal_wh_ids = {w.id for w in principal_warehouses}
_all_principal   = [inv for inv in all_inventory if inv.warehouse_id in principal_wh_ids]
own_inventory    = [inv for inv in _all_principal if getattr(inv, "is_active", True)]
total_stock      = sum(inv.stock for inv in own_inventory)

st.markdown(f"""
<div class="op-hero">
  <div class="op-hero-left">
    <div class="op-hero-icon">&#128202;</div>
    <div>
      <h1>Inventario Principal</h1>
      <p>Stock, reservas y costos del almacén principal</p>
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
mat_id_to_obj  = {m.id: m for m in materials}

# ── Instrucciones + Presupuestos Activos ──────────────────────────────────────
_, _col_budgets, _col_help = st.columns([4.6, 1.5, 1])
with _col_budgets.popover("Presupuestos", use_container_width=True):
    st.markdown("#### Presupuestos Activos")
    _active_buds = [b for b in get_budgets(db) if b.is_active]
    if not _active_buds:
        st.info("No hay presupuestos activos registrados.")
    else:
        for _b in _active_buds:
            st.markdown(f"""
<div style="padding:.55rem .8rem;border-radius:10px;border:1px solid rgba(5,150,105,.25);
            background:rgba(5,150,105,.07);margin-bottom:.45rem">
  <div style="font-weight:800;font-size:.88rem;color:#6ee7b7">{_b.name}</div>
  <div style="font-size:.75rem;color:rgba(255,255,255,.55);margin-top:.18rem">
    S/ {_b.budget_soles:,.2f} &nbsp;·&nbsp; $ {_b.budget_dolares:,.2f}
  </div>
</div>""", unsafe_allow_html=True)
with _col_help.popover("Instrucciones", use_container_width=True):
    st.markdown("#### Inventario — Guía de uso")
    st.markdown("""
**Ingresar stock**
1. Despliega **Agregar stock a un almacén** y selecciona el almacén, material, cantidad y opcionalmente el presupuesto a descontar.
2. El costo (cantidad × precio unitario) se resta automáticamente del presupuesto elegido.

**Retirar stock**
1. Despliega **Retirar stock de un almacén** y selecciona almacén, material y cantidad.
2. Solo puedes retirar hasta el stock **disponible** (no el reservado).

**Tabla de inventario**
- **Stock:** total físico · **Reservado:** comprometido · **Disponible:** libre.
- **Precio unitario** y **Valor total** se muestran cuando el material tiene precio registrado.

**Inventario eliminado**
- Al borrar un registro aparece en el panel de *Inventario Eliminado*.
- **Se perdió:** marca el material como perdido (sin cambio en presupuesto).
- **Se devolvió:** suma el valor de vuelta al presupuesto seleccionado.

> El stock **disponible** es el único que puede asignarse a nuevos requerimientos.
""")

# ── Mensajes post-acción ──────────────────────────────────────────────────────
if st.session_state.get("inv_add_msgs"):
    _msgs = st.session_state.pop("inv_add_msgs")
    st.success(_msgs[0])
    for _m in _msgs[1:]:
        st.info(f"Requerimiento satisfecho — {_m}")

if st.session_state.get("inv_rem_msg"):
    st.success(st.session_state.pop("inv_rem_msg"))

if st.session_state.get("inv_bud_msg"):
    st.info(st.session_state.pop("inv_bud_msg"))

# ── Ingresar stock ────────────────────────────────────────────────────────────
st.markdown('<div class="sec-title">Ingresar Stock</div>', unsafe_allow_html=True)

_active_buds    = [b for b in get_budgets(db) if b.is_active]
_bud_opts_map   = {"No descontar del presupuesto": None}
for _b in _active_buds:
    _bud_opts_map[_b.name] = _b.id

_add_n = st.session_state.get("add_form_n", 0)
with st.expander("Agregar stock a un almacén", expanded=False):
    if len(_bud_opts_map) > 1:
        col_wh, col_mat, col_qty, col_bud = st.columns(4, gap="medium")
    else:
        col_wh, col_mat, col_qty = st.columns(3, gap="medium")
        col_bud = None

    in_wh  = col_wh.selectbox("Almacén",  list(warehouse_dict.keys()), key=f"in_wh_{_add_n}")
    in_mat = col_mat.selectbox("Material", list(material_dict.keys()),  key=f"in_mat_{_add_n}")
    in_qty = col_qty.number_input("Cantidad", min_value=1, key=f"in_qty_{_add_n}")
    in_bud_label = col_bud.selectbox(
        "Descontar de presupuesto", list(_bud_opts_map.keys()), key=f"in_bud_{_add_n}"
    ) if col_bud else "No descontar del presupuesto"

    # Preview cost
    _prev_mat = mat_id_to_obj.get(material_dict[in_mat])
    _prev_price = (_prev_mat.unit_price or 0.0) if _prev_mat else 0.0
    _prev_cost  = in_qty * _prev_price
    if _prev_price > 0:
        st.caption(f"Costo estimado: S/ {_prev_cost:,.2f}  ({in_qty} × S/ {_prev_price:,.2f}/unidad)")

    if st.button("Agregar Stock", type="primary", key=f"btn_add_stock_{_add_n}"):
        _bud_id_stock   = _bud_opts_map.get(in_bud_label)
        _bud_name_stock = in_bud_label if _bud_id_stock is not None else None
        newly_fulfilled = add_stock(
            db, warehouse_dict[in_wh], material_dict[in_mat], in_qty,
            user_id=owner_id,
            budget_id=_bud_id_stock,
            budget_name=_bud_name_stock,
        )
        msgs = [f"Se agregaron **{in_qty}** unidades de **{in_mat}** a **{in_wh}**."]
        if newly_fulfilled:
            for _req in newly_fulfilled:
                _obra_name = wh_id_to_name.get(_req.warehouse_id_obra,
                                               f"Almacén #{_req.warehouse_id_obra}")
                msgs.append(
                    f"**Requerimiento #{_req.id}** para **{_obra_name}** "
                    f"quedó completamente reservado y listo para despacho."
                )

        # Budget deduction
        _bud_id = _bud_opts_map.get(in_bud_label)
        if _bud_id is not None and _prev_mat:
            _cost_s = in_qty * (_prev_mat.unit_price         or 0.0)
            _cost_d = in_qty * (_prev_mat.unit_price_dolares or 0.0)
            if _cost_s > 0 or _cost_d > 0:
                deduct_budget(db, _bud_id, _cost_s, _cost_d)
                st.session_state["inv_bud_msg"] = (
                    f"Se descontó **S/ {_cost_s:,.2f}** del presupuesto **{in_bud_label}**."
                )

        st.session_state["inv_add_msgs"] = msgs
        st.session_state["add_form_n"] = _add_n + 1
        st.session_state.pop("inv_page", None)  # reset pagination
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

# Reload after potential mutations (active records only)
own_inventory = [
    inv for inv in get_inventory(db)
    if inv.warehouse_id in principal_wh_ids and getattr(inv, "is_active", True)
]

if not own_inventory:
    st.info("Aún no hay registros de inventario. Agrega stock con el formulario de arriba.")
else:
    # ── KPI summary ───────────────────────────────────────────────────────────
    _ts = sum(inv.stock for inv in own_inventory)
    _tr = sum(inv.reserved for inv in own_inventory
              if inv.warehouse and inv.warehouse.type == "principal")
    _td = _ts - _tr
    _tv = sum(
        inv.stock * (inv.material.unit_price or 0.0)
        for inv in own_inventory if inv.material
    )
    st.markdown(f"""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:1.2rem">
  <div style="background:linear-gradient(135deg,rgba(37,99,235,.13),rgba(79,70,229,.06));
              border:1px solid rgba(37,99,235,.25);border-radius:16px;padding:1.1rem 1.3rem">
    <div style="font-size:.68rem;font-weight:700;color:rgba(148,163,184,.65);
                text-transform:uppercase;letter-spacing:.07em;margin-bottom:.4rem">Total en stock</div>
    <div style="font-size:2rem;font-weight:900;color:#60a5fa;line-height:1">{_ts}</div>
    <div style="font-size:.70rem;color:rgba(148,163,184,.45);margin-top:.25rem">unidades</div>
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
  <div style="background:linear-gradient(135deg,rgba(168,85,247,.12),rgba(139,92,246,.05));
              border:1px solid rgba(168,85,247,.22);border-radius:16px;padding:1.1rem 1.3rem">
    <div style="font-size:.68rem;font-weight:700;color:rgba(148,163,184,.65);
                text-transform:uppercase;letter-spacing:.07em;margin-bottom:.4rem">Valor total</div>
    <div style="font-size:1.55rem;font-weight:900;color:#c4b5fd;line-height:1">S/ {_tv:,.2f}</div>
    <div style="font-size:.70rem;color:rgba(148,163,184,.45);margin-top:.25rem">costo total del inventario</div>
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
        st.markdown("<div style='margin-bottom:.6rem'></div>", unsafe_allow_html=True)
        for _oi in _overreserved:
            _mat  = _oi.material.name  if _oi.material  else f"Material {_oi.material_id}"
            _unit = _oi.material.unit  if _oi.material  else ""
            _wh   = _oi.warehouse.name if _oi.warehouse else f"Almacén {_oi.warehouse_id}"
            _diff = _oi.reserved - _oi.stock
            st.warning(
                f"**Alerta — {_mat}** en **{_wh}**:  \n"
                f"Reservado ({_oi.reserved} {_unit}) supera el stock actual "
                f"({_oi.stock} {_unit}). "
                f"Se necesitan al menos **{_diff} {_unit}** adicionales.",
                icon=None,
            )

    def _stat_block(label: str, value: str, color: str) -> str:
        return (
            f'<div class="inv-stat"><span class="inv-stat-lbl">{label}</span>'
            f'<span class="inv-stat-val" style="color:{color}">{value}</span></div>'
        )

    def _render_inv_card(inv):
        wh_name  = inv.warehouse.name if inv.warehouse else f"Almacén {inv.warehouse_id}"
        wh_type  = inv.warehouse.type if inv.warehouse else "principal"
        mat_name = inv.material.name  if inv.material  else f"Material {inv.material_id}"
        mat_unit = str(inv.material.unit).strip() if inv.material and inv.material.unit else "uds"
        is_obra  = wh_type == "obra"
        border_c = "rgba(13,148,136,.16)" if is_obra else "rgba(37,99,235,.16)"
        bg_c     = "rgba(13,148,136,.05)" if is_obra else "rgba(37,99,235,.05)"
        proj_name = inv.budget_name if getattr(inv, "budget_name", None) else None

        unit_price = float(inv.material.unit_price or 0.0) if inv.material else 0.0
        total_val  = inv.stock * unit_price

        if is_obra:
            available   = inv.stock
            avail_color = "#34d399" if available > 0 else "#f87171"
            stats_html = (
                _stat_block("Stock", str(inv.stock), "#60a5fa")
                + _stat_block("Disponible", str(available), avail_color)
            )
        else:
            available   = inv.stock - inv.reserved
            avail_color = "#34d399" if available > 0 else ("#fbbf24" if inv.stock > 0 else "#f87171")
            stats_html = (
                _stat_block("Stock", str(inv.stock), "#60a5fa")
                + _stat_block("Reservado", str(inv.reserved), "#fbbf24")
                + _stat_block("Disponible", str(available), avail_color)
            )
            if unit_price > 0:
                stats_html += _stat_block(
                    "Precio", f"S/ {unit_price:,.2f}/{mat_unit}", "#a78bfa"
                )
                stats_html += _stat_block(
                    "Valor total", f"S/ {total_val:,.2f}", "#c4b5fd"
                )

        proj_badge = (
            '<span class="inv-proj-chip">&#128196; ' + proj_name + '</span>'
        ) if proj_name else (
            '<span class="inv-noproj-chip">Sin proyecto</span>' if not is_obra else ""
        )
        unit_span = (
            f'<span class="inv-unit">{mat_unit}</span>' if mat_unit else ""
        )

        confirming  = st.session_state.get("confirm_del_inv")    == inv.id
        assigning   = st.session_state.get("assign_proj_inv")    == inv.id

        if not confirming:
            # Botón "Asignar/Editar proyecto" solo aplica al inventario PRINCIPAL
            show_proj_btn = (not is_obra)
            if show_proj_btn:
                col_card, col_assign, col_del = st.columns([8, 1.4, 0.9], gap="small")
            else:
                col_card, col_del = st.columns([9, 1], gap="small")
                col_assign = None

            with col_card:
                card_html = (
                    f'<div class="inv-card" style="border:1px solid {border_c};background:{bg_c}">'
                      '<div class="inv-card-head">'
                        f'<span class="inv-wh">{wh_name}</span>'
                        '<span class="inv-sep">·</span>'
                        f'<span class="inv-mat">{mat_name}</span>'
                        f'{unit_span}'
                        f'{proj_badge}'
                      '</div>'
                      f'<div class="inv-stats">{stats_html}</div>'
                    '</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)

            if col_assign is not None:
                with col_assign:
                    st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)
                    _btn_label = "✏ Editar proy." if proj_name else "📂 Asignar"
                    _btn_help  = (
                        f"Cambiar proyecto (actualmente: {proj_name})"
                        if proj_name else "Vincular este stock a un proyecto"
                    )
                    if st.button(
                        _btn_label,
                        key=f"assign_inv_{inv.id}",
                        use_container_width=True,
                        help=_btn_help,
                    ):
                        st.session_state["assign_proj_inv"] = inv.id
                        st.rerun()
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
                delete_inventory_record(db, inv.id, owner_id=owner_id)
                del st.session_state["confirm_del_inv"]
                st.session_state.pop("inv_page", None)
                st.rerun()
            if c_no.button("Cancelar", key=f"no_inv_{inv.id}",
                           use_container_width=True):
                del st.session_state["confirm_del_inv"]
                st.rerun()

        # Panel de asignación / edición de proyecto
        if assigning:
            _live_buds = [b for b in get_budgets(db) if b.is_active]
            if not _live_buds and not proj_name:
                st.warning(
                    "No hay proyectos activos. Crea uno en **Presupuestos** para poder asignarlo."
                )
                if st.button("Cerrar", key=f"close_assign_{inv.id}"):
                    st.session_state.pop("assign_proj_inv", None)
                    st.rerun()
            else:
                _opts = {b.name: b.id for b in _live_buds if b.name != proj_name}
                if proj_name:
                    _opts["— Sin proyecto —"] = None
                _c1, _c2, _c3 = st.columns([4, 1.2, 1.2], gap="small")
                _sel = _c1.selectbox(
                    ("Cambiar proyecto a..." if proj_name else "Proyecto destino"),
                    list(_opts.keys()),
                    key=f"assign_proj_sel_{inv.id}",
                    label_visibility="collapsed",
                )
                _btn_lbl = "Cambiar" if proj_name else "Asignar"
                if _c2.button(_btn_lbl, type="primary",
                              key=f"do_assign_{inv.id}", use_container_width=True):
                    _target_id = _opts[_sel]
                    if assign_project_to_inventory(db, inv.id, _target_id):
                        st.session_state.pop("assign_proj_inv", None)
                        if _target_id is None:
                            _msg = f"Stock de **{mat_name}** desvinculado de su proyecto."
                        else:
                            _msg = f"Stock de **{mat_name}** asignado al proyecto **{_sel}**."
                        st.session_state["inv_add_msgs"] = [_msg]
                        st.rerun()
                    else:
                        st.error("No se pudo asignar el proyecto.")
                if _c3.button("Cancelar", key=f"cancel_assign_{inv.id}",
                              use_container_width=True):
                    st.session_state.pop("assign_proj_inv", None)
                    st.rerun()

        st.markdown("<div style='margin-bottom:.25rem'></div>", unsafe_allow_html=True)

    # ── Filtro de inventario ──────────────────────────────────────────────────
    _fc1, _fc2 = st.columns([3, 5], gap="small")
    with _fc1:
        _inv_search = st.text_input(
            "Buscar material",
            placeholder="Filtrar por nombre de material...",
            key="inv_search_text",
            label_visibility="collapsed",
        )
    with _fc2:
        st.markdown(
            "<div style='padding-top:.45rem;font-size:.78rem;"
            "color:rgba(148,163,184,.45)'>🔍 Filtrar inventario actual</div>",
            unsafe_allow_html=True,
        )

    if _inv_search:
        _s = _inv_search.lower()
        _filtered_inv = [
            inv for inv in own_inventory
            if _s in (inv.material.name  if inv.material  else "").lower()
            or _s in (inv.warehouse.name if inv.warehouse else "").lower()
        ]
        if not _filtered_inv:
            st.info(f"No se encontraron materiales que coincidan con «{_inv_search}».")
    else:
        _filtered_inv = own_inventory

    # ── Paginación ────────────────────────────────────────────────────────────
    ITEMS_PER_PAGE = 10
    total_pages    = max(1, (len(_filtered_inv) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
    current_page   = int(st.session_state.get("inv_page", 0))
    current_page   = min(current_page, total_pages - 1)
    page_items     = _filtered_inv[current_page * ITEMS_PER_PAGE:(current_page + 1) * ITEMS_PER_PAGE]

    for _inv in page_items:
        _render_inv_card(_inv)

    if total_pages > 1:
        _pcol_prev, _pcol_info, _pcol_next = st.columns([1, 3, 1])
        _pcol_info.markdown(
            f"<div class='pag-info'>Página {current_page + 1} de {total_pages} "
            f"— {len(_filtered_inv)} registros</div>",
            unsafe_allow_html=True,
        )
        if _pcol_prev.button("← Anterior", key="inv_prev", disabled=(current_page == 0), use_container_width=True):
            st.session_state["inv_page"] = current_page - 1
            st.rerun()
        if _pcol_next.button("Siguiente →", key="inv_next", disabled=(current_page == total_pages - 1), use_container_width=True):
            st.session_state["inv_page"] = current_page + 1
            st.rerun()

# ── Inventario Congelado (proyecto eliminado) ─────────────────────────────────
frozen_items = get_frozen_inventory_for_owner(db, owner_id)

if frozen_items:
    st.markdown('<div class="sec-title-frozen">&#10052; Stock Congelado — Proyecto Eliminado</div>', unsafe_allow_html=True)
    st.caption(
        "Estos registros pertenecían a un proyecto que fue eliminado. "
        "Redirígelos a otro proyecto para reactivarlos, o libéralos sin proyecto."
    )

    _active_buds_frz = [b for b in get_budgets(db) if b.is_active]
    _frz_bud_map     = {b.name: b.id for b in _active_buds_frz}

    for _frec in frozen_items:
        _frz_mat  = _frec.material.name  if _frec.material  else f"Material {_frec.material_id}"
        _frz_unit = _frec.material.unit  if _frec.material  else "uds"
        _frz_wh   = _frec.warehouse.name if _frec.warehouse else f"Almacén {_frec.warehouse_id}"
        _old_proj = _frec.budget_name or "proyecto eliminado"
        _frz_price = float(_frec.material.unit_price or 0.0) if _frec.material else 0.0
        _frz_val   = _frec.stock * _frz_price

        _val_block = (
            f'<div class="inv-stat"><span class="inv-stat-lbl">Valor</span>'
            f'<span class="inv-stat-val" style="color:#94a3b8;font-size:.88rem">S/ {_frz_val:,.2f}</span></div>'
            if _frz_price > 0 else ""
        )
        st.markdown(
            f'<div class="frozen-card">'
              f'<div style="flex:1;min-width:180px">'
                f'<div class="inv-card-head" style="margin-bottom:.38rem">'
                  f'<span class="inv-wh">{_frz_wh}</span>'
                  f'<span class="inv-sep">·</span>'
                  f'<span class="inv-mat" style="color:#94a3b8">{_frz_mat}</span>'
                  f'<span class="frozen-badge">&#10052; Congelado · {_old_proj}</span>'
                f'</div>'
                f'<div class="inv-stats">'
                  f'<div class="inv-stat"><span class="inv-stat-lbl">Stock</span>'
                  f'<span class="inv-stat-val" style="color:#94a3b8">{_frec.stock}</span></div>'
                  f'{_val_block}'
                f'</div>'
              f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        _frz_action_key = f"frz_action_{_frec.id}"
        _frz_action     = st.session_state.get(_frz_action_key)

        if _frz_action is None:
            _fc1, _fc2, _fc3 = st.columns([2, 2, 4], gap="small")
            if _fc1.button("Redirigir a proyecto", key=f"frz_redir_{_frec.id}", use_container_width=True, type="primary"):
                st.session_state[_frz_action_key] = "redirect"
                st.rerun()
            if _fc2.button("Liberar sin proyecto", key=f"frz_free_{_frec.id}", use_container_width=True):
                st.session_state[_frz_action_key] = "free"
                st.rerun()

        elif _frz_action == "redirect":
            if _frz_bud_map:
                _sel_proj = st.selectbox(
                    "Selecciona el proyecto de destino",
                    list(_frz_bud_map.keys()),
                    key=f"frz_proj_sel_{_frec.id}",
                )
                _ok_col, _cancel_col = st.columns(2, gap="small")
                if _ok_col.button("Confirmar redirección", key=f"frz_ok_{_frec.id}", type="primary", use_container_width=True):
                    redirect_frozen_inventory(db, _frec.id, _frz_bud_map[_sel_proj])
                    st.session_state.pop(_frz_action_key, None)
                    st.success(f"**{_frz_mat}** redirigido al proyecto **{_sel_proj}** y reactivado.")
                    st.rerun()
                if _cancel_col.button("Cancelar", key=f"frz_cancel_{_frec.id}", use_container_width=True):
                    st.session_state.pop(_frz_action_key, None)
                    st.rerun()
            else:
                st.warning("No hay proyectos activos disponibles. Crea uno en la sección Presupuestos.")
                if st.button("Cancelar", key=f"frz_cancel_nop_{_frec.id}", use_container_width=True):
                    st.session_state.pop(_frz_action_key, None)
                    st.rerun()

        elif _frz_action == "free":
            st.markdown(
                f"<div style='padding:.55rem 1rem;border-radius:10px;"
                f"border:1px solid rgba(100,116,139,.30);background:rgba(100,116,139,.08);"
                f"margin-bottom:.4rem'>"
                f"<span style='color:#94a3b8;font-size:.82rem;font-weight:600'>"
                f"El stock de <strong>{_frz_mat}</strong> quedará activo sin proyecto asignado.</span></div>",
                unsafe_allow_html=True,
            )
            _ok2, _cancel2 = st.columns(2, gap="small")
            if _ok2.button("Confirmar", key=f"frz_free_ok_{_frec.id}", type="primary", use_container_width=True):
                unfreeze_inventory(db, _frec.id)
                st.session_state.pop(_frz_action_key, None)
                st.success(f"**{_frz_mat}** reactivado sin proyecto asignado.")
                st.rerun()
            if _cancel2.button("Cancelar", key=f"frz_free_cancel_{_frec.id}", use_container_width=True):
                st.session_state.pop(_frz_action_key, None)
                st.rerun()

        st.markdown("<div style='margin-bottom:.25rem'></div>", unsafe_allow_html=True)

# ── Inventario Eliminado ──────────────────────────────────────────────────────
deleted_items = get_deleted_inventory(db, owner_id=owner_id)

if deleted_items:
    st.markdown('<div class="sec-title-danger">Inventario Eliminado</div>', unsafe_allow_html=True)
    st.caption("Registros eliminados del inventario. Indica si el material se perdió o fue devuelto.")

    _del_active_buds = [b for b in get_budgets(db) if b.is_active]
    _del_bud_map     = {b.name: b.id for b in _del_active_buds}

    for _drec in deleted_items:
        _state_key_action = f"del_action_{_drec.id}"
        _action = st.session_state.get(_state_key_action)

        _val_str = f"S/ {_drec.total_value:,.2f}" if _drec.total_value else "sin precio"
        _price_str = (
            f"Precio unitario: S/ {_drec.unit_price:,.2f}/{_drec.material_unit}"
            if _drec.unit_price else "sin precio registrado"
        )

        st.markdown(f"""
<div class="del-inv-card">
  <div style="display:flex;align-items:center;gap:.6rem;flex-wrap:wrap;margin-bottom:.5rem">
    <span style="font-weight:800;color:#fca5a5;font-size:.88rem">{_drec.warehouse_name}</span>
    <span style="color:rgba(148,163,184,.35)">·</span>
    <span style="font-weight:700;color:#f1f5f9;font-size:.84rem">{_drec.material_name}</span>
    <span style="color:rgba(148,163,184,.45);font-size:.76rem">{_drec.material_unit}</span>
  </div>
  <div style="display:flex;gap:2rem;flex-wrap:wrap">
    <div>
      <span style="font-size:.63rem;font-weight:700;color:rgba(148,163,184,.55);
                   text-transform:uppercase;letter-spacing:.05em">Cantidad</span>
      <span style="font-weight:900;color:#f87171;font-size:1rem;margin-left:.4rem">{_drec.stock}</span>
    </div>
    <div>
      <span style="font-size:.63rem;font-weight:700;color:rgba(148,163,184,.55);
                   text-transform:uppercase;letter-spacing:.05em">Valor</span>
      <span style="font-weight:900;color:#fca5a5;font-size:1rem;margin-left:.4rem">{_val_str}</span>
    </div>
    <div style="font-size:.73rem;color:rgba(148,163,184,.5);align-self:center">{_price_str}</div>
  </div>
</div>
""", unsafe_allow_html=True)

        if _action is None:
            _btn_col_lost, _btn_col_ret, _btn_col_space = st.columns([1.5, 1.5, 5])
            if _btn_col_lost.button(
                "Se perdió el material", key=f"lost_{_drec.id}", use_container_width=True
            ):
                st.session_state[_state_key_action] = "lost"
                st.rerun()
            if _btn_col_ret.button(
                "Se devolvió material", key=f"ret_{_drec.id}", use_container_width=True
            ):
                st.session_state[_state_key_action] = "return_select"
                st.rerun()

        elif _action == "lost":
            st.markdown(
                f"<div style='padding:.55rem 1rem;border-radius:10px;"
                f"border:1px solid rgba(239,68,68,.3);background:rgba(239,68,68,.07);"
                f"margin-bottom:.4rem'>"
                f"<span style='color:#fca5a5;font-size:.82rem;font-weight:600'>"
                f"Confirmar: material perdido. "
                f"{'Costo no recuperado: ' + _val_str + '.' if _drec.total_value else ''} "
                f"No se modificará el presupuesto.</span></div>",
                unsafe_allow_html=True,
            )
            _c_ok, _c_cancel = st.columns(2)
            if _c_ok.button("Confirmar pérdida", key=f"lost_ok_{_drec.id}", type="primary", use_container_width=True):
                resolve_deleted_inventory(db, _drec.id, "lost")
                del st.session_state[_state_key_action]
                st.success(
                    f"Material **{_drec.material_name}** marcado como perdido."
                    + (f" Costo no recuperado: {_val_str}." if _drec.total_value else "")
                )
                st.rerun()
            if _c_cancel.button("Cancelar", key=f"lost_cancel_{_drec.id}", use_container_width=True):
                del st.session_state[_state_key_action]
                st.rerun()

        elif _action == "return_select":
            if _del_bud_map:
                _ret_bud_label = st.selectbox(
                    "Acreditar devolución al presupuesto",
                    list(_del_bud_map.keys()),
                    key=f"ret_bud_{_drec.id}",
                )
                _ret_bud_id = _del_bud_map[_ret_bud_label]
            else:
                st.caption("No hay presupuestos activos. Se marcará como devuelto sin acreditar presupuesto.")
                _ret_bud_id = None

            _c_ok2, _c_cancel2 = st.columns(2)
            if _c_ok2.button("Confirmar devolución", key=f"ret_ok_{_drec.id}", type="primary", use_container_width=True):
                resolve_deleted_inventory(db, _drec.id, "returned")
                if _ret_bud_id is not None and _drec.total_value:
                    credit_budget(db, _ret_bud_id, _drec.total_value, _drec.unit_price_dol * _drec.stock)
                    _msg = (
                        f"Material **{_drec.material_name}** devuelto. "
                        f"Se acreditaron **{_val_str}** al presupuesto **{_ret_bud_label}**."
                    )
                else:
                    _msg = f"Material **{_drec.material_name}** marcado como devuelto."
                del st.session_state[_state_key_action]
                st.success(_msg)
                st.rerun()
            if _c_cancel2.button("Cancelar", key=f"ret_cancel_{_drec.id}", use_container_width=True):
                del st.session_state[_state_key_action]
                st.rerun()

        st.markdown("<div style='margin-bottom:.3rem'></div>", unsafe_allow_html=True)

db.close()
