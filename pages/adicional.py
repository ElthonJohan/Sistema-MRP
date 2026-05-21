# -*- coding: utf-8 -*-
import streamlit as st
from datetime import datetime, date

from database import SessionLocal
from services.budget_service import get_budgets
from services.additional_service import (
    create_additional, get_additionals, update_additional, delete_additional,
)
from utils.auth import require_superadmin
from utils.navbar import render_navbar, render_sidebar_menu


st.set_page_config(
    page_title="Adicional — Sistema MRP",
    layout="wide",
    initial_sidebar_state="expanded",
)

require_superadmin()

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stHeader"]     { background: transparent !important; }
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stAppViewBlockContainer"] { padding-top: 1.2rem !important; }

.add-hero {
    display: flex; align-items: center; justify-content: space-between;
    flex-wrap: wrap; gap: .5rem;
    padding: 1rem 1.5rem 1.2rem;
    border-radius: 20px;
    background: linear-gradient(135deg, #78350f 0%, #b45309 55%, #f59e0b 100%);
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(245,158,11,.30);
}
.add-hero-left { display: flex; align-items: center; gap: 1rem; }
.add-hero-icon {
    width: 60px; height: 60px; border-radius: 16px;
    background: rgba(255,255,255,0.15);
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; font-size: 1.8rem;
}
.add-hero h1 { font-size: 1.55rem; font-weight: 900; color: #fff; margin: 0; }
.add-hero p  { font-size: .82rem; color: rgba(255,255,255,.78); margin: 2px 0 0; }
.add-badge {
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,.25);
    border-radius: 30px; padding: .35rem 1rem;
    font-size: .78rem; font-weight: 700; color: #fef3c7;
    white-space: nowrap;
}

.sec-title {
    font-size: 1rem; font-weight: 800;
    display: flex; align-items: center; gap: .55rem;
    padding-left: .8rem;
    border-left: 4px solid #f59e0b;
    margin: 1.8rem 0 .9rem;
}

.add-card {
    display: flex; gap: 1rem; align-items: stretch;
    padding: .85rem 1.15rem;
    border-radius: 14px;
    border: 1px solid rgba(245,158,11,.22);
    background: linear-gradient(135deg, rgba(245,158,11,.08) 0%, rgba(217,119,6,.04) 100%);
    margin-bottom: .55rem;
    position: relative; overflow: hidden;
}
.add-card::before {
    content: ""; position: absolute; left: 0; top: 0; bottom: 0;
    width: 4px; background: linear-gradient(180deg, #f59e0b, #d97706);
}
.add-card-icon {
    width: 42px; height: 42px; border-radius: 12px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    background: linear-gradient(135deg, #f59e0b, #d97706); color: #fff;
}
.add-card-body { flex: 1; min-width: 0; }
.add-card-head {
    display: flex; align-items: center; gap: .6rem; flex-wrap: wrap;
    margin-bottom: .35rem;
}
.add-proj-chip {
    display: inline-flex; align-items: center;
    padding: .15rem .55rem; border-radius: 20px;
    font-size: .65rem; font-weight: 700;
    background: rgba(5,150,105,.18); color: #6ee7b7;
    border: 1px solid rgba(5,150,105,.30);
    white-space: nowrap;
}
.add-date-chip {
    display: inline-flex; align-items: center;
    padding: .15rem .55rem; border-radius: 20px;
    font-size: .65rem; font-weight: 700;
    background: rgba(99,102,241,.16); color: #a5b4fc;
    border: 1px solid rgba(99,102,241,.28);
    white-space: nowrap;
}
.add-card-concept {
    font-size: .96rem; font-weight: 700; color: #f1f5f9;
    line-height: 1.3; word-break: break-word;
}
.add-card-notes {
    font-size: .80rem; color: rgba(203,213,225,.78);
    line-height: 1.42; margin-top: .35rem; white-space: pre-wrap;
}
.add-empty {
    padding: 1.2rem; text-align: center;
    border: 1px dashed rgba(245,158,11,.32);
    border-radius: 14px; color: rgba(245,158,11,.80);
    background: rgba(245,158,11,.04);
}

[data-testid="stExpander"] {
    border-radius: 14px !important;
    border: 1px solid rgba(245,158,11,.22) !important;
    background: rgba(245,158,11,.04) !important;
    overflow: hidden !important;
    margin-bottom: .55rem !important;
}
[data-testid="stExpander"]:hover { border-color: rgba(245,158,11,.38) !important; }
details[data-testid="stExpander"] > summary {
    padding: .82rem 1.1rem !important;
    font-size: .86rem !important; font-weight: 700 !important;
    color: #fde68a !important;
}
[data-testid="stBaseButton-primary"],
[data-testid="stFormSubmitButton"] button {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
    color: #fff !important; border: none !important;
    border-radius: 10px !important; font-weight: 700 !important;
    box-shadow: 0 2px 14px rgba(245,158,11,.32) !important;
}
[data-testid="stBaseButton-primary"]:hover,
[data-testid="stFormSubmitButton"] button:hover {
    background: linear-gradient(135deg, #d97706 0%, #b45309 100%) !important;
    transform: translateY(-1px) !important;
}
[data-testid="stBaseButton-secondary"] {
    background: rgba(239,68,68,.10) !important;
    color: #fca5a5 !important;
    border: 1px solid rgba(239,68,68,.32) !important;
    border-radius: 10px !important; font-weight: 700 !important;
}
[data-testid="stBaseButton-secondary"]:hover {
    background: rgba(239,68,68,.22) !important;
    color: #fee2e2 !important;
}
[data-testid="stAlert"] { border-radius: 10px !important; }
label[data-testid="stWidgetLabel"] p { font-size: .80rem !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

render_navbar()
with st.sidebar:
    render_sidebar_menu()

# ── Hero ─────────────────────────────────────────────────────────────────────
now  = datetime.now()
user = st.session_state.get("username", "Superadmin")
st.markdown(f"""
<div class="add-hero">
  <div class="add-hero-left">
    <div class="add-hero-icon">&#10133;</div>
    <div>
      <h1>Adicionales del Proyecto</h1>
      <p>Solicitudes que no son parte original del alcance &nbsp;·&nbsp; {now.strftime("%A %d de %B, %Y")}</p>
    </div>
  </div>
  <div class="add-badge">&#9733; {user}</div>
</div>
""", unsafe_allow_html=True)

db = SessionLocal()
budgets    = get_budgets(db)
buds_by_id = {b.id: b for b in budgets}

# ── Crear adicional ───────────────────────────────────────────────────────────
st.markdown('<div class="sec-title">&#43; Registrar Adicional</div>', unsafe_allow_html=True)

if not budgets:
    st.warning("No hay proyectos registrados. Crea un proyecto primero en Presupuestos.")
else:
    with st.expander("Nueva solicitud", expanded=False):
        with st.form("form_new_additional", clear_on_submit=True):
            _cn1, _cn2 = st.columns([3, 2], gap="medium")
            with _cn1:
                _bud_labels  = {f"{b.name} (#{b.id})": b.id for b in budgets}
                _bud_label   = st.selectbox(
                    "Proyecto *", list(_bud_labels.keys()),
                    help="Proyecto al que pertenece esta solicitud adicional.",
                )
                f_concept = st.text_input(
                    "Concepto *",
                    placeholder="Ej. Más fierro corrugado · Más área construida",
                    max_chars=200,
                )
            with _cn2:
                f_req_date = st.date_input("Fecha de la solicitud *", value=date.today())
            f_notes = st.text_area(
                "Notas",
                placeholder="Detalles, justificación, presupuestado, autorizado por...",
                height=80,
            )
            _s1, _s2 = st.columns([1, 2])
            with _s1:
                _submit = st.form_submit_button("Registrar adicional", use_container_width=True, type="primary")

            if _submit:
                if not f_concept.strip():
                    st.error("El concepto es obligatorio.")
                else:
                    create_additional(
                        db,
                        budget_id    = _bud_labels[_bud_label],
                        request_date = datetime.combine(f_req_date, datetime.min.time()),
                        concept      = f_concept.strip(),
                        notes        = f_notes.strip() or None,
                    )
                    st.success(f"Adicional registrado para **{_bud_label}**.")
                    st.rerun()

# ── Lista de adicionales ──────────────────────────────────────────────────────
st.markdown('<div class="sec-title">&#128203; Adicionales Registrados</div>', unsafe_allow_html=True)

_fc1, _fc2 = st.columns([3, 3], gap="small")
with _fc1:
    _search = st.text_input(
        "Buscar concepto",
        placeholder="Filtrar por concepto o notas...",
        key="add_search_text",
        label_visibility="collapsed",
    )
with _fc2:
    _proj_filter_opts = ["Todos los proyectos"] + [b.name for b in budgets]
    _proj_filter = st.selectbox(
        "Filtrar por proyecto", _proj_filter_opts,
        key="add_proj_filter",
        label_visibility="collapsed",
    )

if _proj_filter == "Todos los proyectos":
    additionals = get_additionals(db)
else:
    _sel_bud = next((b for b in budgets if b.name == _proj_filter), None)
    additionals = get_additionals(db, budget_id=_sel_bud.id) if _sel_bud else []

if _search:
    _q = _search.lower()
    additionals = [
        a for a in additionals
        if _q in (a.concept or "").lower()
        or _q in (a.notes or "").lower()
    ]

if not additionals:
    st.markdown(
        '<div class="add-empty">Sin solicitudes adicionales registradas '
        'para los filtros aplicados.</div>',
        unsafe_allow_html=True,
    )
else:
    import html as _html
    for a in additionals:
        _editing = st.session_state.get("edit_add_id") == a.id
        bud      = buds_by_id.get(a.budget_id)
        _proj_lbl = bud.name if bud else f"Proyecto #{a.budget_id}"
        _date_lbl = a.request_date.strftime("%d/%m/%Y") if a.request_date else "—"
        _concept  = _html.escape(a.concept or "—")
        _notes    = _html.escape(a.notes or "")
        _notes_html = (
            f'<div class="add-card-notes">{_notes}</div>' if _notes else ""
        )

        col_card, col_edit, col_del = st.columns([8.5, 1, 1], gap="small", vertical_alignment="center")
        with col_card:
            st.markdown(
                f'<div class="add-card">'
                f'<div class="add-card-icon">&#10133;</div>'
                f'<div class="add-card-body">'
                f'<div class="add-card-head">'
                f'<span class="add-proj-chip">📂 {_html.escape(_proj_lbl)}</span>'
                f'<span class="add-date-chip">📅 Solicitado: {_date_lbl}</span>'
                f'</div>'
                f'<div class="add-card-concept">{_concept}</div>'
                f'{_notes_html}'
                f'</div></div>',
                unsafe_allow_html=True,
            )
        with col_edit:
            _lbl_e = "Cerrar ✕" if _editing else "Editar"
            if st.button(_lbl_e, key=f"edit_add_{a.id}", use_container_width=True, type="primary"):
                if _editing:
                    st.session_state.pop("edit_add_id", None)
                else:
                    st.session_state["edit_add_id"] = a.id
                st.rerun()
        with col_del:
            if st.button("🗑", key=f"del_add_{a.id}", use_container_width=True,
                         help="Eliminar este adicional"):
                st.session_state["confirm_del_add"] = a.id
                st.session_state.pop("edit_add_id", None)
                st.rerun()

        # ── Confirmación de borrado ───────────────────────────────────────────
        if st.session_state.get("confirm_del_add") == a.id:
            c_msg, c_yes, c_no = st.columns([5, 1, 1], gap="small")
            c_msg.error(f"¿Eliminar el adicional «{a.concept}»? Esta acción no se puede deshacer.")
            if c_yes.button("Sí, eliminar", key=f"yes_del_add_{a.id}", type="primary", use_container_width=True):
                delete_additional(db, a.id)
                st.session_state.pop("confirm_del_add", None)
                st.success("Adicional eliminado.")
                st.rerun()
            if c_no.button("Cancelar", key=f"no_del_add_{a.id}", use_container_width=True):
                st.session_state.pop("confirm_del_add", None)
                st.rerun()

        # ── Edición inline ────────────────────────────────────────────────────
        if _editing:
            with st.form(key=f"form_edit_add_{a.id}"):
                ec1, ec2 = st.columns([3, 2], gap="medium")
                with ec1:
                    e_concept = st.text_input("Concepto *", value=a.concept or "")
                with ec2:
                    e_date = st.date_input(
                        "Fecha de la solicitud *",
                        value=a.request_date.date() if a.request_date else date.today(),
                    )
                e_notes = st.text_area("Notas", value=a.notes or "", height=80)
                _es, _ec = st.columns(2, gap="small")
                with _es:
                    _save = st.form_submit_button("Guardar cambios", use_container_width=True, type="primary")
                with _ec:
                    _cancel = st.form_submit_button("Cancelar", use_container_width=True)
                if _save:
                    if not e_concept.strip():
                        st.error("El concepto es obligatorio.")
                    else:
                        update_additional(
                            db, a.id,
                            request_date = datetime.combine(e_date, datetime.min.time()),
                            concept      = e_concept.strip(),
                            notes        = e_notes,
                        )
                        st.session_state.pop("edit_add_id", None)
                        st.success("Adicional actualizado.")
                        st.rerun()
                if _cancel:
                    st.session_state.pop("edit_add_id", None)
                    st.rerun()

db.close()
