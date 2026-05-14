# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from database import SessionLocal
from services.dashboard_service import (
    get_kpis,
    get_recent_movements,
    get_stock_by_warehouse,
    get_movements_last_7_days,
    get_top_materials_by_movement,
)
from utils.auth import require_cliente, get_current_user_id
from utils.navbar import render_navbar, render_sidebar_menu

st.set_page_config(
    page_title="Dashboard — Sistema MRP",
    layout="wide",
    initial_sidebar_state="expanded",
)

render_navbar()        # primero — inyecta CSS anti-flash
require_cliente()      # redirige al superadmin hacia /admin

# ── Tema (sincronizado con session_state) ─────────────────────────────────────
_dark  = st.session_state.get("dark_mode", False)

_tpl        = "plotly_dark" if _dark else "plotly_white"
_font       = "#e2e8f0"     if _dark else "#1e293b"
_grid       = "rgba(255,255,255,0.07)" if _dark else "rgba(0,0,0,0.06)"
_bg         = "rgba(0,0,0,0)"
_surface    = "rgba(255,255,255,0.04)" if _dark else "rgba(255,255,255,0.85)"

# ── Estilos globales ──────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Reset header ── */
[data-testid="stHeader"]        { background: transparent !important; }
[data-testid="stSidebarNav"]    { display: none !important; }
[data-testid="stAppViewBlockContainer"] { padding-top: 1.2rem !important; }

/* ══════════════ HERO ══════════════ */
.dash-hero {
    display: flex; align-items: center; justify-content: space-between;
    flex-wrap: wrap; gap: .5rem;
    padding: 1.1rem 1.6rem 1.3rem;
    border-radius: 22px;
    background: linear-gradient(135deg, #0a1628 0%, #1a3470 45%, #2563eb 100%);
    margin-bottom: 1.6rem;
    box-shadow: 0 8px 40px rgba(37,99,235,.30), 0 1px 0 rgba(255,255,255,.08) inset;
    border: 1px solid rgba(255,255,255,.07);
    position: relative; overflow: hidden;
}
/* Glow sutil en la esquina derecha del hero */
.dash-hero::after {
    content: "";
    position: absolute; right: -40px; top: -40px;
    width: 180px; height: 180px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(96,165,250,.18) 0%, transparent 70%);
    pointer-events: none;
}
.dash-hero-left { display: flex; align-items: center; gap: 1rem; position: relative; z-index: 1; }
.dash-hero-icon {
    width: 52px; height: 52px; border-radius: 14px;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,.18);
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.hero-mark-sm {
    display: inline-grid; grid-template-columns: 1fr 1fr; gap: 4px;
}
.hero-mark-sm span { display:block; width:13px; height:13px; border-radius:3px; }
.hms-1{background:#fff;opacity:.95} .hms-2{background:#fff;opacity:.45}
.hms-3{background:#fff;opacity:.45} .hms-4{background:#fff;opacity:.95}
.dash-hero h1  { font-size: 1.5rem; font-weight: 900; color: #fff; margin: 0; letter-spacing: -.02em; }
.dash-hero p   { font-size: .80rem; color: rgba(255,255,255,.62); margin: 3px 0 0; }
.dash-hero-right { display: flex; align-items: center; gap: .65rem; position: relative; z-index: 1; }
.dash-hero-badge {
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,.20);
    border-radius: 30px; padding: .38rem 1rem;
    font-size: .77rem; font-weight: 700; color: #fff;
    white-space: nowrap; display: flex; align-items: center; gap: .35rem;
    backdrop-filter: blur(8px);
}
.dash-hero-kpi-chip {
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,.15);
    border-radius: 24px; padding: .32rem .8rem;
    font-size: .72rem; font-weight: 600; color: rgba(255,255,255,.85);
    white-space: nowrap;
}

/* ══════════════ KPI CARDS ══════════════ */
.kpi-wrap {
    border-radius: 18px; padding: 1.25rem 1.4rem;
    position: relative; overflow: hidden;
    transition: transform .22s ease, box-shadow .22s ease;
    cursor: default;
    border: 1px solid rgba(255,255,255,.06);
}
/* Accent bar on top */
.kpi-wrap::before {
    content: "";
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: rgba(255,255,255,.25);
    border-radius: 18px 18px 0 0;
}
.kpi-wrap:hover { transform: translateY(-5px); }
.k-blue:hover  { box-shadow: 0 18px 48px rgba(37,99,235,.40) !important; }
.k-amber:hover { box-shadow: 0 18px 48px rgba(217,119,6,.40) !important; }
.k-violet:hover{ box-shadow: 0 18px 48px rgba(124,58,237,.40) !important; }
.k-teal:hover  { box-shadow: 0 18px 48px rgba(13,148,136,.40) !important; }

.kpi-icon-bg {
    position: absolute; right: 1rem; top: 50%; transform: translateY(-50%);
    opacity: 0.12; pointer-events: none;
}
.kpi-icon-bg svg { width: 58px; height: 58px; stroke: white; fill: none; stroke-width: 1.5; stroke-linecap: round; stroke-linejoin: round; }
.kpi-label { font-size: .70rem; font-weight: 700; text-transform: uppercase;
             letter-spacing: .12em; opacity: .75; margin-bottom: .35rem; }
.kpi-val   { font-size: 2.5rem; font-weight: 900; line-height: 1; margin-bottom: .2rem; }
.kpi-sub   { font-size: .73rem; opacity: .60; }
.kpi-badge { display:inline-block; padding:.15rem .55rem; border-radius:20px;
             font-size:.68rem; font-weight:700; margin-top:.4rem; }

.k-blue   { background: linear-gradient(145deg,#1a3270,#2563eb); color:#fff;
            box-shadow: 0 8px 28px rgba(37,99,235,.25); }
.k-amber  { background: linear-gradient(145deg,#6b2d0f,#d97706); color:#fff;
            box-shadow: 0 8px 28px rgba(217,119,6,.25); }
.k-violet { background: linear-gradient(145deg,#3b176e,#7c3aed); color:#fff;
            box-shadow: 0 8px 28px rgba(124,58,237,.25); }
.k-teal   { background: linear-gradient(145deg,#0f4040,#0d9488); color:#fff;
            box-shadow: 0 8px 28px rgba(13,148,136,.25); }

/* ══════════════ SECTION TITLES ══════════════ */
.sec-title {
    font-size: .95rem; font-weight: 800;
    display: flex; align-items: center; gap: .55rem;
    padding: .55rem .9rem;
    border-radius: 10px;
    background: color-mix(in srgb, var(--text-color,#0f172a) 5%, transparent);
    border-left: 3px solid #2563eb;
    margin: 1.8rem 0 .85rem;
    letter-spacing: .005em;
}
.sec-title svg { width: 15px; height: 15px; stroke: #2563eb; fill: none; stroke-width: 2.2; stroke-linecap: round; stroke-linejoin: round; flex-shrink: 0; }
.sec-num {
    font-size: .65rem; font-weight: 700; color: #2563eb;
    background: rgba(37,99,235,.12); border-radius: 6px;
    padding: .15rem .38rem; letter-spacing: .04em; margin-left: auto;
}

/* ══════════════ CHART CARDS ══════════════ */
[data-testid="stPlotlyChart"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    box-shadow: none !important;
}

/* ── Tabla de movimientos ── */
[data-testid="stDataFrame"] {
    border-radius: 14px !important;
    overflow: hidden;
    border: 1px solid color-mix(in srgb, var(--text-color,#0f172a) 7%, transparent) !important;
}

/* ══════════════ ACTIVITY FEED ══════════════ */
.feed-item {
    display: flex; align-items: flex-start; gap: .75rem;
    padding: .6rem .8rem;
    border-radius: 10px; margin-bottom: .4rem;
    border: 1px solid transparent;
    transition: background .15s, border-color .15s;
}
.feed-item:hover {
    background: rgba(37,99,235,.06);
    border-color: rgba(37,99,235,.12);
}
.feed-dot {
    width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0;
    margin-top: 6px;
}
.feed-in  { background: #10b981; box-shadow: 0 0 0 3px rgba(16,185,129,.20); }
.feed-out { background: #f59e0b; box-shadow: 0 0 0 3px rgba(245,158,11,.20); }
.feed-body { flex: 1; min-width: 0; }
.feed-body strong { font-size: .84rem; display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.feed-body span   { font-size: .72rem; opacity: .55; }
.feed-ts { font-size: .68rem; opacity: .45; flex-shrink: 0; margin-top: 6px; }

</style>
""", unsafe_allow_html=True)

# ── Navbar + Sidebar ──────────────────────────────────────────────────────────
render_navbar()
with st.sidebar:
    render_sidebar_menu()

# ── Datos (filtrados por el cliente actual) ───────────────────────────────────
db       = SessionLocal()
owner_id = get_current_user_id()
kpis     = get_kpis(db, owner_id=owner_id)

# ── Hero ──────────────────────────────────────────────────────────────────────
now  = datetime.now()
user = st.session_state.get("username", "—")

hour = now.hour
greeting = "Buenos días" if hour < 12 else ("Buenas tardes" if hour < 19 else "Buenas noches")

st.markdown(f"""
<div class="dash-hero">
  <div class="dash-hero-left">
    <div class="dash-hero-icon">
      <div class="hero-mark-sm">
        <span class="hms-1"></span><span class="hms-2"></span>
        <span class="hms-3"></span><span class="hms-4"></span>
      </div>
    </div>
    <div>
      <h1>{greeting}, {user} 👋</h1>
      <p>Dashboard Logístico &nbsp;·&nbsp; {now.strftime("%A %d de %B, %Y")}</p>
    </div>
  </div>
  <div class="dash-hero-right">
    <div class="dash-hero-kpi-chip">
      <svg viewBox="0 0 24 24" width="11" height="11" style="stroke:rgba(255,255,255,.7);fill:none;stroke-width:2;vertical-align:middle;margin-right:3px"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8"/></svg>
      {kpis['total_stock']:,} uds en stock
    </div>
    <div class="dash-hero-badge">
      <svg viewBox="0 0 24 24" width="11" height="11" style="stroke:#fff;fill:none;stroke-width:2;"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
      {now.strftime("%H:%M")}
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4, gap="medium")

_SVG_BOX    = '<svg viewBox="0 0 24 24"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>'
_SVG_WARN   = '<svg viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'
_SVG_CLIP   = '<svg viewBox="0 0 24 24"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/><line x1="9" y1="12" x2="15" y2="12"/><line x1="9" y1="16" x2="15" y2="16"/></svg>'
_SVG_TRUCK  = '<svg viewBox="0 0 24 24"><rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>'

k1.markdown(f"""
<div class="kpi-wrap k-blue">
  <div class="kpi-label">Stock Total</div>
  <div class="kpi-val">{kpis['total_stock']:,}</div>
  <div class="kpi-sub">Unidades en todos los almacenes</div>
  <div class="kpi-icon-bg">{_SVG_BOX}</div>
</div>""", unsafe_allow_html=True)

_alert_color = "rgba(255,80,80,.28)" if kpis["critical"] > 0 else "rgba(255,255,255,.18)"
_alert_text  = "&#9679; Atención" if kpis["critical"] > 0 else "&#10003; Sin alertas"
alert_badge = f'<span class="kpi-badge" style="background:{_alert_color}">{_alert_text}</span>'
k2.markdown(f"""
<div class="kpi-wrap k-amber">
  <div class="kpi-label">Materiales Críticos</div>
  <div class="kpi-val">{kpis['critical']}</div>
  <div class="kpi-sub">Stock ≤ 5 en almacén principal</div>
  {alert_badge}
  <div class="kpi-icon-bg">{_SVG_WARN}</div>
</div>""", unsafe_allow_html=True)

k3.markdown(f"""
<div class="kpi-wrap k-violet">
  <div class="kpi-label">Pendientes</div>
  <div class="kpi-val">{kpis['pending_req']}</div>
  <div class="kpi-sub">Requerimientos sin completar</div>
  <div class="kpi-icon-bg">{_SVG_CLIP}</div>
</div>""", unsafe_allow_html=True)

k4.markdown(f"""
<div class="kpi-wrap k-teal">
  <div class="kpi-label">Despachos</div>
  <div class="kpi-val">{kpis['dispatch_today']}</div>
  <div class="kpi-sub">Salidas registradas (total)</div>
  <div class="kpi-icon-bg">{_SVG_TRUCK}</div>
</div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:1.5rem'></div>", unsafe_allow_html=True)

# ── Fila 2: Tendencia 7 days + Donut stock ────────────────────────────────────
st.markdown('<div class="sec-title"><svg viewBox="0 0 24 24"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>Tendencia de Movimientos — Últimos 7 días</div>', unsafe_allow_html=True)

col_trend, col_donut = st.columns([3, 2], gap="large")

with col_trend:
    trend_data = get_movements_last_7_days(db, owner_id=owner_id)
    if trend_data:
        df_trend = pd.DataFrame(trend_data)
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=df_trend["Día"], y=df_trend["Entradas"],
            mode="lines+markers", name="Entradas",
            line=dict(color="#10b981", width=3),
            marker=dict(size=8, color="#10b981"),
            fill="tozeroy", fillcolor="rgba(16,185,129,0.10)",
        ))
        fig_line.add_trace(go.Scatter(
            x=df_trend["Día"], y=df_trend["Salidas"],
            mode="lines+markers", name="Salidas",
            line=dict(color="#f59e0b", width=3),
            marker=dict(size=8, color="#f59e0b"),
            fill="tozeroy", fillcolor="rgba(245,158,11,0.08)",
        ))
        fig_line.update_layout(
            template=_tpl, paper_bgcolor=_bg, plot_bgcolor=_bg,
            margin=dict(t=10, b=10, l=0, r=0), height=280,
            font=dict(color=_font, size=12),
            xaxis=dict(gridcolor=_grid, showline=False),
            yaxis=dict(gridcolor=_grid, showline=False),
            legend=dict(orientation="h", y=1.12, x=0),
            hovermode="x unified",
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Sin movimientos en los últimos 7 días.")

with col_donut:
    stock_data = get_stock_by_warehouse(db, owner_id=owner_id)
    if stock_data:
        df_stock = pd.DataFrame(list(stock_data.items()), columns=["Almacén", "Stock"])
        palette = ["#2563eb","#7c3aed","#0d9488","#d97706","#dc2626","#0ea5e9"]
        fig_donut = px.pie(
            df_stock, names="Almacén", values="Stock",
            hole=0.55,
            color_discrete_sequence=palette,
            template=_tpl,
        )
        fig_donut.update_traces(
            textinfo="percent", textfont_color="#fff",
            marker=dict(line=dict(color=_bg, width=2)),
        )
        fig_donut.update_layout(
            paper_bgcolor=_bg, margin=dict(t=10, b=0, l=0, r=0),
            font=dict(color=_font, size=12), height=280,
            legend=dict(orientation="v", y=0.5, x=1.02),
            annotations=[dict(
                text=f"<b>{sum(stock_data.values()):,}</b><br><span style='font-size:11px'>unidades</span>",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=18, color=_font),
            )],
        )
        st.plotly_chart(fig_donut, use_container_width=True)
    else:
        st.info("Sin datos de stock.")

# ── Fila 3: Barras por almacén + Top materiales ───────────────────────────────
col_bar, col_top = st.columns([3, 2], gap="large")

with col_bar:
    st.markdown('<div class="sec-title"><svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2"/><polyline points="3 9 21 9"/><polyline points="9 21 9 9"/></svg>Stock por Almacén</div>', unsafe_allow_html=True)
    if stock_data:
        fig_bar = px.bar(
            df_stock.sort_values("Stock", ascending=False),
            x="Almacén", y="Stock",
            color="Almacén",
            color_discrete_sequence=palette,
            template=_tpl, text_auto=True,
        )
        fig_bar.update_layout(
            paper_bgcolor=_bg, plot_bgcolor=_bg,
            margin=dict(t=10, b=10, l=0, r=0), height=280,
            font=dict(color=_font, size=12),
            xaxis=dict(gridcolor=_grid),
            yaxis=dict(gridcolor=_grid),
            showlegend=False,
        )
        fig_bar.update_traces(marker_line_width=0, textfont_color="#fff")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Sin datos de stock.")

with col_top:
    st.markdown('<div class="sec-title"><svg viewBox="0 0 24 24"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>Top 5 Materiales Activos</div>', unsafe_allow_html=True)
    top_mats = get_top_materials_by_movement(db, owner_id=owner_id)
    if top_mats:
        df_top = pd.DataFrame(top_mats)
        max_val = df_top["Movimientos"].max() or 1
        fig_h = px.bar(
            df_top, y="Material", x="Movimientos",
            orientation="h",
            color="Movimientos",
            color_continuous_scale=["#1e3a8a","#2563eb","#60a5fa"],
            template=_tpl, text_auto=True,
        )
        fig_h.update_layout(
            paper_bgcolor=_bg, plot_bgcolor=_bg,
            margin=dict(t=10, b=10, l=0, r=0), height=280,
            font=dict(color=_font, size=12),
            xaxis=dict(gridcolor=_grid),
            yaxis=dict(gridcolor=_grid, categoryorder="total ascending"),
            coloraxis_showscale=False, showlegend=False,
        )
        fig_h.update_traces(textfont_color="#fff", marker_line_width=0)
        st.plotly_chart(fig_h, use_container_width=True)
    else:
        st.info("Sin datos de movimientos.")

# ── Fila 4: Actividad reciente ────────────────────────────────────────────────
movs = get_recent_movements(db, owner_id=owner_id)

st.markdown(
    f'<div class="sec-title"><svg viewBox="0 0 24 24"><polyline points="17 1 21 5 17 9"/>'
    f'<path d="M3 11V9a4 4 0 0 1 4-4h14"/><polyline points="7 23 3 19 7 15"/>'
    f'<path d="M21 13v2a4 4 0 0 1-4 4H3"/></svg>Actividad Reciente'
    f'<span class="sec-num">{len(movs)} mov.</span></div>',
    unsafe_allow_html=True,
)

if not movs:
    st.info("No hay movimientos registrados aún.")
else:
    col_l, col_r = st.columns(2, gap="medium")
    mid = (len(movs) + 1) // 2

    for col, batch in ((col_l, movs[:mid]), (col_r, movs[mid:])):
        with col:
            for m in batch:
                tipo  = m.movement_type or "?"
                mat   = m.material.name  if m.material  else "—"
                wh    = m.warehouse.name if m.warehouse else "—"
                ts    = m.timestamp.strftime("%d/%m %H:%M") if m.timestamp else "—"
                dot   = "feed-in" if tipo == "IN" else "feed-out"
                label = "Entrada" if tipo == "IN" else "Salida"
                qty   = f"+{m.qty_change}" if tipo == "IN" else f"-{m.qty_change}"
                qcol  = "#10b981" if tipo == "IN" else "#f59e0b"
                arrow = "&#8593;" if tipo == "IN" else "&#8595;"
                st.markdown(f"""
<div class="feed-item">
  <div class="feed-dot {dot}"></div>
  <div class="feed-body">
    <strong>{label} &nbsp;<span style='color:{qcol}'>{arrow} {qty} uds</span></strong>
    <span>{mat} &nbsp;·&nbsp; {wh}</span>
    <span style='display:block;font-size:.66rem;opacity:.40;margin-top:.1rem'>{ts}</span>
  </div>
</div>""", unsafe_allow_html=True)

db.close()

