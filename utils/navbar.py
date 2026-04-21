import streamlit as st
from datetime import datetime

# Mapeo página → clave de menú
_PAGE_KEYS = {
    "pages/dashboard.py":     "menu_dashboard",
    "pages/warehouses.py":    "menu_warehouses",
    "pages/materials.py":     "menu_materials",
    "pages/requirements.py":  "menu_requirements",
    "pages/receipts.py":      "menu_receipts",
    "pages/dispatches.py":    "menu_dispatches",
    "pages/inventory.py":     "menu_inventory",
    "pages/access_logs.py":   "menu_access_logs",
}

# Importación diferida para evitar ciclos
def _apply_theme():
    try:
        from utils.theme import apply_theme
        apply_theme()
    except Exception:
        pass

def _current_page() -> str:
    try:
        path = st.context.headers.get("Referer", "")
        for k in _PAGE_KEYS:
            slug = k.replace("pages/", "").replace(".py", "").replace("_", "-")
            if slug in path.lower():
                return k
    except Exception:
        pass
    return st.session_state.get("_current_page", "")

def render_navbar():
    """Oculta la nav nativa de Streamlit."""
    st.markdown(
        "<style>[data-testid='stSidebarNav']{display:none!important}</style>",
        unsafe_allow_html=True,
    )

def render_sidebar_menu():
    """Renderiza el sidebar personalizado."""

    # Aplica dark mode CSS si está habilitado
    _apply_theme()

    st.markdown("""
    <style>
    /* ═══════════════════════════════════════════════════════════════════
       SIDEBAR — SaaS profesional
       Técnica: position:absolute en el hijo directo de stSidebarContent
       → ignora por completo el padding-top inyectado por Streamlit.
       → sin margin negativos, sin hacks.
    ═══════════════════════════════════════════════════════════════════ */
    [data-testid="stSidebarNav"] { display: none !important; }

    /* 1 ─ Contenedor raíz: fondo + sin scroll */
    section[data-testid="stSidebar"] {
        background:   #0d1117 !important;
        border-right: 1px solid rgba(255,255,255,.07) !important;
        overflow:     hidden !important;
    }
    section[data-testid="stSidebar"]::-webkit-scrollbar { display: none !important; }
    section[data-testid="stSidebar"]                    { scrollbar-width: none !important; }

    /* 2 ─ stSidebarContent: posición de referencia, altura completa.
           Streamlit inyecta padding-top aquí; el hijo absoluto lo anula. */
    section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        position:   relative    !important;
        height:     100dvh      !important;
        overflow:   hidden      !important;
        padding:    0           !important;
        background: transparent !important;
    }

    /* 3 ─ Primer div hijo: position:absolute inset:0
           → ocupa el área exacta del sidebar ignorando el padding del padre */
    section[data-testid="stSidebar"] [data-testid="stSidebarContent"] > div {
        position: absolute !important;
        inset:    0        !important;
        padding:  0        !important;
        margin:   0        !important;
        overflow: hidden   !important;
        height:   100%     !important;
    }
    /* 3b ─ Divs intermedios entre > div y stVerticalBlock:
            propagar altura para que height:100% funcione */
    section[data-testid="stSidebar"] [data-testid="stSidebarContent"] > div > div:not([data-testid="stVerticalBlock"]) {
        height:  100% !important;
        padding: 0    !important;
        margin:  0    !important;
    }

    /* 4 ─ ROOT stVerticalBlock: columna flex de altura completa.
           Selector de doble profundidad cubre estructura plana Y con wrapper. */
    section[data-testid="stSidebar"] [data-testid="stSidebarContent"] > div > [data-testid="stVerticalBlock"],
    section[data-testid="stSidebar"] [data-testid="stSidebarContent"] > div > div > [data-testid="stVerticalBlock"] {
        display:        flex    !important;
        flex-direction: column  !important;
        align-items:    stretch !important;
        height:         100dvh  !important;
        padding:        0       !important;
        margin:         0       !important;
        gap:            0       !important;
        overflow:       hidden  !important;
    }
    /* stVerticalBlocks anidados: reset para no heredar height */
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] [data-testid="stVerticalBlock"] {
        height:     auto    !important;
        min-height: 0       !important;
        display:    block   !important;
        overflow:   visible !important;
    }

    /* 5 ─ Cada stElementContainer: sin relleno interno de Streamlit */
    section[data-testid="stSidebar"] [data-testid="stElementContainer"] {
        padding:     0 !important;
        margin:      0 !important;
        flex-shrink: 0 !important;
    }

    /* ═══════════════════════════════════════════════════════════════════
       HEADER — logo + usuario (sin margin negativo)
    ═══════════════════════════════════════════════════════════════════ */
    .sb-header {
        padding:       .9rem 1rem .75rem;
        border-bottom: 1px solid rgba(255,255,255,.07);
        background:    #0d1117;
        flex-shrink:   0;
    }

    .sb-brand-row {
        display: flex; align-items: center; gap: .65rem;
        margin-bottom: .6rem;
    }
    .sb-logo {
        width: 32px; height: 32px; flex-shrink: 0;
        background: linear-gradient(135deg, #1d4ed8, #6366f1);
        border-radius: 9px;
        display: flex; align-items: center; justify-content: center;
        box-shadow: 0 0 0 1px rgba(99,102,241,.4), 0 4px 12px rgba(29,78,216,.35);
    }
    .sb-logo-mark {
        display: grid; grid-template-columns: 1fr 1fr; gap: 3px;
    }
    .sb-logo-mark span { display: block; width: 9px; height: 9px; border-radius: 2px; }
    .slm-1 { background: rgba(255,255,255,1); }
    .slm-2 { background: rgba(255,255,255,.4); }
    .slm-3 { background: rgba(255,255,255,.4); }
    .slm-4 { background: rgba(255,255,255,1); }
    .sb-brand-text { min-width: 0; }
    .sb-brand-name {
        font-size: .92rem; font-weight: 700;
        color: #f0f6fc; margin: 0; line-height: 1.2; letter-spacing: -.01em;
    }
    .sb-brand-sub {
        font-size: .67rem; color: rgba(240,246,252,.38);
        margin: 1px 0 0; letter-spacing: .02em;
        text-transform: uppercase;
    }

    .sb-user-row {
        display: flex; align-items: center; gap: .6rem;
    }
    .sb-avatar {
        width: 30px; height: 30px; flex-shrink: 0;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: .78rem; font-weight: 800; color: #fff;
        box-shadow: 0 0 0 2px rgba(59,130,246,.30);
    }
    .sb-user-info { flex: 1; min-width: 0; }
    .sb-user-name {
        font-size: .80rem; font-weight: 600; color: #e6edf3;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        line-height: 1.3;
    }
    .sb-user-role {
        font-size: .65rem; color: rgba(240,246,252,.35);
        letter-spacing: .02em;
    }
    .sb-status-dot {
        width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0;
        background: #22c55e;
        box-shadow: 0 0 0 2px rgba(34,197,94,.20), 0 0 6px rgba(34,197,94,.35);
    }

    /* ═══════════════════════════════════════════════════════════════════
       SECCIONES DE NAVEGACIÓN
    ═══════════════════════════════════════════════════════════════════ */
    .sb-section {
        font-size: .60rem; font-weight: 700;
        text-transform: uppercase; letter-spacing: .13em;
        color: rgba(240,246,252,.38) !important;
        padding: 1.2rem 1rem .4rem; margin: 0;
    }

    /* Botones secundarios (inactivos) */
    [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {
        border-radius: 7px !important;
        border: none !important;
        font-size: .84rem !important;
        font-weight: 500 !important;
        padding: .58rem .85rem !important;
        text-align: left !important;
        margin-bottom: 3px !important;
        width: 100% !important;
        letter-spacing: .005em !important;
        color: rgba(240,246,252,.68) !important;
        background: transparent !important;
        transition: background .12s ease, color .12s ease !important;
    }
    [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover {
        background: rgba(255,255,255,.06) !important;
        color: #e6edf3 !important;
    }
    [data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:focus-visible {
        outline: 2px solid rgba(59,130,246,.6) !important;
        outline-offset: 1px !important;
    }

    /* Botón activo (primary) */
    [data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {
        border-radius: 7px !important;
        border: none !important;
        font-size: .84rem !important;
        font-weight: 600 !important;
        padding: .58rem .85rem !important;
        text-align: left !important;
        margin-bottom: 3px !important;
        width: 100% !important;
        letter-spacing: .005em !important;
        background: rgba(59,130,246,.14) !important;
        color: #93c5fd !important;
        box-shadow: inset 2px 0 0 #3b82f6 !important;
    }



    /* ═══════════════════════════════════════════════════════════════════
       FOOTER ANCLADO AL FONDO
       .sb-divider → spacer invisible (height:0) con margin-top:auto.
       border-top visual se aplica sobre el container del botón logout.
    ═══════════════════════════════════════════════════════════════════ */

    /* Spacer: flex-grow:1 absorbe el espacio libre → logout+footer quedan pegados al fondo */
    section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.sb-divider) {
        flex-grow:   1      !important;
        flex-shrink: 1      !important;
        min-height:  0      !important;
        height:      0      !important;
        padding:     0      !important;
        margin:      0      !important;
        overflow:    hidden !important;
    }

    /* Todos los containers que vienen después del spacer: fondo oscuro unificado */
    section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.sb-divider)
    ~ [data-testid="stElementContainer"] {
        background: rgba(255,255,255,.025) !important;
    }

    /* Container del botón Cerrar sesión: borde superior + padding */
    section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.sb-divider)
    + [data-testid="stElementContainer"] {
        border-top: 1px solid rgba(255,255,255,.08) !important;
        padding:    .45rem .5rem .2rem            !important;
    }

    /* Botón Cerrar sesión: rojo suave */
    section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.sb-divider)
    + [data-testid="stElementContainer"] [data-testid="stBaseButton-secondary"] {
        color:       rgba(248,113,113,.82) !important;
        font-weight: 500                  !important;
        background:  transparent          !important;
        border:      none                 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.sb-divider)
    + [data-testid="stElementContainer"] [data-testid="stBaseButton-secondary"]:hover {
        background: rgba(239,68,68,.12) !important;
        color:      #fca5a5             !important;
    }

    /* Container del texto de versión: padding visible */
    section[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.sb-footer) {
        padding: .1rem .75rem .55rem !important;
    }

    /* Texto de versión: legible pero sutil */
    .sb-footer {
        font-size:      .68rem;
        color:          rgba(240,246,252,.42) !important;
        text-align:     center;
        letter-spacing: .05em;
        text-transform: uppercase;
        line-height:    1;
        padding:        0;
        margin:         0;
    }

    /* ══════════════════════════════════════════════════════
       ICONOS SVG via data-nav (JS)
    ══════════════════════════════════════════════════════ */
    [data-testid="stSidebar"] button[data-nav] {
        display: flex !important; align-items: center !important;
    }
    [data-testid="stSidebar"] button[data-nav]::before {
        content: ""; flex-shrink: 0; display: inline-block;
        width: 15px; height: 15px; margin-right: 9px;
        background: center / contain no-repeat; opacity: .70;
        transition: opacity .12s;
    }
    [data-testid="stSidebar"] button[data-nav]:hover::before,
    [data-testid="stSidebar"] [data-testid="stBaseButton-primary"][data-nav]::before {
        opacity: 1;
    }
    [data-testid="stSidebar"] button[data-nav="dashboard"]::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2393c5fd' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='3' width='7' height='7'/%3E%3Crect x='14' y='3' width='7' height='7'/%3E%3Crect x='14' y='14' width='7' height='7'/%3E%3Crect x='3' y='14' width='7' height='7'/%3E%3C/svg%3E");
    }
    [data-testid="stSidebar"] button[data-nav="warehouses"]::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23e6edf3' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z'/%3E%3Cpolyline points='9 22 9 12 15 12 15 22'/%3E%3C/svg%3E");
    }
    [data-testid="stSidebar"] button[data-nav="materials"]::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23e6edf3' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z'/%3E%3Cpolyline points='3.27 6.96 12 12.01 20.73 6.96'/%3E%3Cline x1='12' y1='22.08' x2='12' y2='12'/%3E%3C/svg%3E");
    }
    [data-testid="stSidebar"] button[data-nav="requirements"]::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23e6edf3' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2'/%3E%3Crect x='8' y='2' width='8' height='4' rx='1'/%3E%3Cline x1='9' y1='12' x2='15' y2='12'/%3E%3Cline x1='9' y1='16' x2='13' y2='16'/%3E%3C/svg%3E");
    }
    [data-testid="stSidebar"] button[data-nav="receipts"]::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23e6edf3' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/%3E%3Cpolyline points='14 2 14 8 20 8'/%3E%3Cline x1='12' y1='18' x2='12' y2='12'/%3E%3Cpolyline points='15 15 12 18 9 15'/%3E%3C/svg%3E");
    }
    [data-testid="stSidebar"] button[data-nav="dispatches"]::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23e6edf3' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='1' y='3' width='15' height='13'/%3E%3Cpolygon points='16 8 20 8 23 11 23 16 16 16 16 8'/%3E%3Ccircle cx='5.5' cy='18.5' r='2.5'/%3E%3Ccircle cx='18.5' cy='18.5' r='2.5'/%3E%3C/svg%3E");
    }
    [data-testid="stSidebar"] button[data-nav="inventory"]::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23e6edf3' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cline x1='18' y1='20' x2='18' y2='10'/%3E%3Cline x1='12' y1='20' x2='12' y2='4'/%3E%3Cline x1='6' y1='20' x2='6' y2='14'/%3E%3C/svg%3E");
    }
    [data-testid="stSidebar"] button[data-nav="access_logs"]::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23e6edf3' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='11' width='18' height='11' rx='2' ry='2'/%3E%3Cpath d='M7 11V7a5 5 0 0 1 10 0v4'/%3E%3C/svg%3E");
    }
    [data-testid="stSidebar"] button[data-nav="logout"]::before {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23f87171' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4'/%3E%3Cpolyline points='16 17 21 12 16 7'/%3E%3Cline x1='21' y1='12' x2='9' y2='12'/%3E%3C/svg%3E");
        opacity: .80;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── JS: etiqueta botones para iconos CSS via data-nav ───────────────────────
    st.markdown("""
    <script>
    (function(){
      var N={
        'Dashboard':'dashboard','Almacenes':'warehouses','Materiales':'materials',
        'Requerimientos':'requirements','Recibos':'receipts','Despachos':'dispatches',
        'Inventario':'inventory','Logs de Acceso':'access_logs','Cerrar sesión':'logout'
      };
      function tag(){
        document.querySelectorAll('[data-testid="stSidebar"] button').forEach(function(b){
          var t=b.textContent.trim(); if(N[t]) b.dataset.nav=N[t];
        });
      }
      tag(); setTimeout(tag,300); setTimeout(tag,800); setTimeout(tag,2000);
    })();
    </script>
    """, unsafe_allow_html=True)

    logged_in = st.session_state.get("logged_in", False)
    if not logged_in:
        return

    username = st.session_state.get("username", "Usuario")
    initials = username[0].upper() if username else "U"
    active   = _current_page()

    # ── Header marca + usuario ────────────────────────────────────────────────
    st.markdown(f"""
    <div class="sb-header">
      <div class="sb-brand-row">
        <div class="sb-logo">
          <div class="sb-logo-mark">
            <span class="slm-1"></span><span class="slm-2"></span>
            <span class="slm-3"></span><span class="slm-4"></span>
          </div>
        </div>
        <div class="sb-brand-text">
          <p class="sb-brand-name">Sistema MRP</p>
          <p class="sb-brand-sub">Gestión de Recursos</p>
        </div>
      </div>
      <div class="sb-user-row">
        <div class="sb-avatar">{initials}</div>
        <div class="sb-user-info">
          <div class="sb-user-name">{username}</div>
          <div class="sb-user-role">Operador</div>
        </div>
        <div class="sb-status-dot"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Helper para botón con resaltado activo
    def _btn(label: str, page: str, key: str):
        is_active = (active == page)
        _type = "primary" if is_active else "secondary"
        if st.button(label, use_container_width=True, key=key, type=_type):
            st.session_state["_current_page"] = page
            st.switch_page(page)

    # ── Principal ────────────────────────────────────────────────────────────
    st.markdown('<p class="sb-section">Principal</p>', unsafe_allow_html=True)
    _btn("Dashboard",        "pages/dashboard.py",    "menu_dashboard")

    # ── Operaciones ──────────────────────────────────────────────────────────
    st.markdown('<p class="sb-section">Operaciones</p>', unsafe_allow_html=True)
    _btn("Almacenes",        "pages/warehouses.py",   "menu_warehouses")
    _btn("Materiales",       "pages/materials.py",    "menu_materials")
    _btn("Requerimientos",   "pages/requirements.py", "menu_requirements")
    _btn("Recibos",          "pages/receipts.py",     "menu_receipts")
    _btn("Despachos",        "pages/dispatches.py",   "menu_dispatches")
    _btn("Inventario",       "pages/inventory.py",    "menu_inventory")

    # ── Administración ───────────────────────────────────────────────────────
    st.markdown('<p class="sb-section">Administración</p>', unsafe_allow_html=True)
    _btn("Logs de Acceso",   "pages/access_logs.py",  "menu_access_logs")

    # ── Separador: margin-top:auto empuja logout+footer al fondo ───────────────
    st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

    # ── Logout ───────────────────────────────────────────────────────────────
    if st.button("Cerrar sesión", use_container_width=True, key="sidebar_logout_btn"):
        st.session_state.logged_in = False
        st.session_state.user_id   = None
        st.session_state.username  = None
        st.switch_page("pages/login.py")

    # ── Footer ───────────────────────────────────────────────────────────────
    st.markdown(
        f'<div class="sb-footer">Sistema MRP · v1.0 · {datetime.now().strftime("%Y")}</div>',
        unsafe_allow_html=True,
    )
