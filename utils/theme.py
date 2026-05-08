# -*- coding: utf-8 -*-
"""
Utilidades de tema (dark / light mode).
Todas las páginas autenticadas obtienen el CSS via render_sidebar_menu().
La página de login lo aplica llamando apply_theme() directamente.
"""
import streamlit as st

_DARK_CSS = """
<style>
/* ════════════════════════ DARK MODE ════════════════════════ */
:root {
    --background-color:           #0f172a !important;
    --secondary-background-color: #1e293b !important;
    --text-color:                 #e2e8f0 !important;
    --primary-color:              #3b82f6 !important;
}

/* Fondo principal */
.stApp,
[data-testid="stAppViewContainer"] { background-color: #0f172a !important; }
[data-testid="stHeader"]            { background-color: #0f172a !important; }
[data-testid="stMain"]              { background-color: #0f172a !important; }
.block-container                    { background-color: transparent !important; }

/* ── Texto ── */
p, span, li, h1, h2, h3, h4, h5, h6, label {
    color: #e2e8f0 !important;
}
[data-testid="stMarkdownContainer"] * { color: #e2e8f0 !important; }
label[data-testid="stWidgetLabel"] p  { color: #cbd5e1 !important; }

/* ── Inputs ── */
[data-baseweb="input"] > div,
[data-baseweb="textarea"] > div {
    background-color: #1e293b !important;
    border-color: #334155 !important;
}
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
    color: #e2e8f0 !important;
    background-color: #1e293b !important;
}
[data-baseweb="input"] input::placeholder,
[data-baseweb="textarea"] textarea::placeholder {
    color: rgba(226,232,240,.35) !important;
}

/* ── Select / dropdown ── */
[data-baseweb="select"] > div {
    background-color: #1e293b !important;
    border-color: #334155 !important;
    color: #e2e8f0 !important;
}
[data-baseweb="popover"] ul {
    background-color: #1e293b !important;
}
[data-baseweb="option"] {
    background-color: #1e293b !important;
    color: #e2e8f0 !important;
}

/* ── Tabs ── */
[data-baseweb="tab-list"]                            { background-color: #1e293b !important; }
button[data-baseweb="tab"]                           { color: #94a3b8 !important; }
button[aria-selected="true"][data-baseweb="tab"]     { background: #2563eb !important; color:#fff!important; }

/* ── Expander ── */
[data-testid="stExpander"],
[data-testid="stExpanderDetails"]   { background-color: #1e293b !important; border-color: #334155 !important; }
[data-testid="stExpander"] summary  { color: #e2e8f0 !important; }

/* ── Alerts ── */
[data-testid="stAlert"]             { background-color: #1e293b !important; border-color: #334155 !important; }
[data-testid="stAlert"] p           { color: #e2e8f0 !important; }

/* ── Metrics ── */
[data-testid="stMetric"]            { background-color: #1e293b !important; }
[data-testid="stMetricValue"],
[data-testid="stMetricLabel"]       { color: #e2e8f0 !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] iframe  { filter: invert(88%) hue-rotate(180deg); }

/* ── Login card ── */
.login-card {
    background: #1e293b !important;
    border-color: #334155 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar-track { background: #0f172a; }
::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #475569; }
</style>
"""


def apply_theme() -> None:
    """Inyecta CSS de dark mode cuando está habilitado."""
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False
    if st.session_state.dark_mode:
        st.markdown(_DARK_CSS, unsafe_allow_html=True)


def render_theme_toggle(key: str = "theme_toggle") -> None:
    """Botón toggle de tema con texto. Úsalo en la barra lateral."""
    is_dark = st.session_state.get("dark_mode", False)
    label = "Sol" if is_dark else "Noche"
    if st.button(label, use_container_width=True, key=key):
        st.session_state.dark_mode = not is_dark
        st.rerun()


def render_theme_fab(key: str = "theme_fab") -> None:
    """Botón FAB solo-ícono para el login (sin texto). Renderiza 🌙 / ☀️."""
    is_dark = st.session_state.get("dark_mode", False)
    icon = "☀️" if is_dark else "🌙"
    if st.button(icon, key=key):
        st.session_state.dark_mode = not is_dark
        st.rerun()
