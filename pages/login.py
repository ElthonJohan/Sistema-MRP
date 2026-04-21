# -*- coding: utf-8 -*-
import re
import streamlit as st
from database import SessionLocal
from services.auth_service import (
    register_user,
    login_user,
    validate_username,
    validate_email,
    validate_password,
)
from services.login_log_service import log_login
from services.session_service import create_session
from utils.session_manager import login_redirect
from utils.theme import apply_theme, render_theme_fab

st.set_page_config(
    page_title="Login — Sistema MRP",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Dark mode ─────────────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
apply_theme()

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>

/* ── Ocultar nav nativa y sidebar ── */
[data-testid="collapsedControl"],
section[data-testid="stSidebar"],
[data-testid="stSidebarNav"] { display: none !important; }

/* ── Sin scrollbar ── */
html { scrollbar-width: none !important; }
::-webkit-scrollbar { display: none !important; }

/* ── Bloque central ── */
.block-container {
    max-width: 460px !important;
    padding: 2rem 1.2rem 1.2rem !important;
}

/* ══════════════════
   HERO
══════════════════ */
@keyframes fadeUp {
    from { opacity:0; transform:translateY(12px); }
    to   { opacity:1; transform:translateY(0); }
}
@keyframes drawLine {
    from { width: 0; }
    to   { width: 40px; }
}

.login-hero {
    text-align: center;
    padding: .8rem 0 1.4rem;
    animation: fadeUp .5s ease both;
}

/* Logo geométrico: 4 cuadrados en 2×2 */
.hero-mark {
    display: inline-grid;
    grid-template-columns: 1fr 1fr;
    gap: 4px;
    margin-bottom: 1.1rem;
}
.hero-mark span {
    display: block;
    width: 14px; height: 14px;
    border-radius: 3px;
}
.hm-1 { background: #2563eb; }
.hm-2 { background: #3b82f6; opacity: .7; }
.hm-3 { background: #1d4ed8; opacity: .7; }
.hm-4 { background: #2563eb; }

.hero-eyebrow {
    display: flex; align-items: center; justify-content: center;
    gap: .5rem; margin-bottom: .55rem;
}
.hero-line {
    width: 0; height: 1px; background: #2563eb;
    animation: drawLine .8s .3s ease forwards;
}
.hero-eyebrow-text {
    font-size: .68rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: .14em;
    color: #2563eb;
}

.hero-title {
    font-size: 1.70rem; font-weight: 800;
    color: var(--text-color, #0f172a);
    letter-spacing: -.3px; margin: 0 0 .35rem;
    line-height: 1.2;
}
.hero-sub {
    font-size: .80rem;
    color: var(--text-color, #64748b);
    opacity: .5; margin: 0;
    letter-spacing: .01em;
}

/* ══════════════════
   TAB SWITCHER CUSTOM
══════════════════ */
/* Contenedor de tabs: pill segmentado */
[data-baseweb="tab-list"] {
    background: color-mix(in srgb, var(--text-color,#0f172a) 7%, transparent) !important;
    border-radius: 14px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid color-mix(in srgb, var(--text-color,#0f172a) 10%, transparent) !important;
}
[data-baseweb="tab"] {
    border-radius: 11px !important;
    font-size: .875rem !important;
    font-weight: 600 !important;
    letter-spacing: .01em !important;
    padding: .5rem 1.1rem !important;
    color: color-mix(in srgb, var(--text-color,#0f172a) 60%, transparent) !important;
    background: transparent !important;
    transition: all .2s ease !important;
    flex: 1 !important;
    text-align: center !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    background: #2563eb !important;
    color: #fff !important;
    box-shadow: 0 2px 8px rgba(37,99,235,.30) !important;
}
[data-baseweb="tab"]:hover:not([aria-selected="true"]) {
    background: color-mix(in srgb, var(--text-color,#0f172a) 5%, transparent) !important;
    color: var(--text-color, #0f172a) !important;
}
/* Ocultar barra inferior de los tabs */
[data-baseweb="tab-highlight"],
[data-baseweb="tab-border"]  { display: none !important; }

/* ══════════════════
   SEPARADOR DE SECCIÓN
══════════════════ */
.form-section {
    display: flex; align-items: center; gap: .65rem;
    margin: 1.1rem 0 .75rem;
}
.form-section-line {
    flex: 1; height: 1px;
    background: color-mix(in srgb, var(--text-color,#0f172a) 10%, transparent);
}
.form-section-label {
    font-size: .68rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: .12em;
    color: color-mix(in srgb, var(--text-color,#0f172a) 38%, transparent);
}

/* ══════════════════
   LABELS
══════════════════ */
label[data-testid="stWidgetLabel"] p {
    font-size: .80rem !important;
    font-weight: 600 !important;
    letter-spacing: .02em !important;
    color: var(--text-color, #334155) !important;
    margin-bottom: .18rem !important;
}

/* ══════════════════
   INPUTS
══════════════════ */
[data-baseweb="input"] > div {
    border-radius: 11px !important;
    transition: border-color .2s, box-shadow .2s !important;
}
[data-baseweb="input"] > div:focus-within {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,.13) !important;
}
/* Botón ojo — sin fondo, sin borde lateral blanco */
[data-baseweb="input"] [data-testid="stBaseButton-minimal"],
[data-baseweb="input"] button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 4px !important;
    margin: 0 !important;
    color: inherit !important;
    width: auto !important;
    min-width: 0 !important;
}
/* Wrapper del botón ojo: mismo fondo que el input */
[data-baseweb="input"] > div > div:last-child:not(input),
[data-baseweb="input"] [data-baseweb="input-suffix"] {
    background: inherit !important;
    border-left: none !important;
    padding-right: 4px !important;
}

/* ══════════════════
   BOTONES SUBMIT
══════════════════ */
[data-testid="stFormSubmitButton"] button {
    background: #2563eb !important;
    color: #fff !important;
    border: none !important;
    border-radius: 11px !important;
    font-size: .90rem !important;
    font-weight: 700 !important;
    letter-spacing: .03em !important;
    width: 100% !important;
    padding: .65rem !important;
    box-shadow: 0 2px 10px rgba(37,99,235,.28) !important;
    transition: background .2s, transform .15s, box-shadow .2s !important;
    margin-top: .2rem !important;
}
[data-testid="stFormSubmitButton"] button:hover {
    background: #1d4ed8 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 5px 18px rgba(37,99,235,.38) !important;
}
[data-testid="stFormSubmitButton"] button:focus-visible {
    outline: 3px solid #2563eb !important;
    outline-offset: 2px !important;
}

/* ══════════════════
   EXPANDER
══════════════════ */
[data-testid="stExpander"] {
    border-radius: 11px !important;
    border: 1px solid color-mix(in srgb, var(--text-color,#0f172a) 9%, transparent) !important;
    background: transparent !important;
}
/* Área de contenido del expander — fondo transparente, texto visible */
[data-testid="stExpander"] > div[data-testid="stExpanderDetails"],
[data-testid="stExpander"] > div > div {
    background: transparent !important;
}
[data-testid="stExpander"] p,
[data-testid="stExpander"] li,
[data-testid="stExpander"] [data-testid="stMarkdownContainer"] * {
    color: var(--text-color, #0f172a) !important;
}
[data-testid="stExpander"] [data-testid="stAlert"] {
    background: rgba(37,99,235,.09) !important;
    color: var(--text-color, #0f172a) !important;
    border-color: rgba(37,99,235,.25) !important;
}
[data-testid="stExpander"] [data-testid="stAlert"] p,
[data-testid="stExpander"] [data-testid="stAlert"] div {
    color: var(--text-color, #0f172a) !important;
}
[data-testid="stExpander"] summary {
    font-size: .80rem !important;
    font-weight: 600 !important;
    letter-spacing: .01em !important;
}
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span {
    color: var(--text-color, #0f172a) !important;
}
[data-testid="stExpander"] code {
    background: color-mix(in srgb, var(--text-color,#0f172a) 9%, transparent) !important;
    color: var(--text-color, #0f172a) !important;
    border-radius: 4px !important;
    padding: 1px 5px !important;
}

/* ══════════════════
   MISC
══════════════════ */
[data-testid="stAlert"]           { border-radius: 10px !important; }
[data-testid="InputInstructions"] { display: none !important; }

.auth-footer {
    text-align: center;
    opacity: .28;
    font-size: .70rem;
    margin-top: 1rem;
    letter-spacing: .04em;
}

/* ── FAB tema — círculo fijo abajo derecha ── */
.theme-fab {
    position: fixed !important;
    bottom: 1.4rem !important;
    right: 1.4rem !important;
    z-index: 9999 !important;
}
.theme-fab [data-testid="stBaseButton-secondary"] {
    width: 38px !important; height: 38px !important;
    min-width: 38px !important; padding: 0 !important;
    border-radius: 50% !important;
    font-size: 1.05rem !important;
    border: 1.5px solid color-mix(in srgb, var(--text-color,#0f172a) 14%, transparent) !important;
    background: var(--secondary-background-color, #fff) !important;
    box-shadow: 0 2px 10px rgba(0,0,0,.12) !important;
    transition: transform .2s, box-shadow .2s !important;
    display: flex !important; align-items: center !important; justify-content: center !important;
}
.theme-fab [data-testid="stBaseButton-secondary"]:hover {
    transform: scale(1.10) !important;
    box-shadow: 0 5px 18px rgba(37,99,235,.22) !important;
    border-color: #2563eb !important;
}
</style>
""", unsafe_allow_html=True)

# ── Estado de sesión ──────────────────────────────────────────────────────────
for key, val in [("logged_in", False), ("user_id", None), ("username", None), ("session_token", None)]:
    if key not in st.session_state:
        st.session_state[key] = val

db = SessionLocal()

if st.session_state.logged_in:
    st.switch_page("pages/dashboard.py")

# ── FAB tema ──────────────────────────────────────────────────────────────────
st.markdown('<div class="theme-fab">', unsafe_allow_html=True)
render_theme_fab(key="login_theme_fab")
st.markdown('</div>', unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="login-hero">
  <div class="hero-mark">
    <span class="hm-1"></span><span class="hm-2"></span>
    <span class="hm-3"></span><span class="hm-4"></span>
  </div>
  <div class="hero-eyebrow">
    <span class="hero-line"></span>
    <span class="hero-eyebrow-text">Sistema MRP</span>
    <span class="hero-line"></span>
  </div>
  <h1 class="hero-title">Bienvenido de nuevo</h1>
  <p class="hero-sub">Gestión de recursos y planificación de materiales</p>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["  Iniciar sesión  ", "  Crear cuenta  "])

# ── LOGIN ─────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown("""
    <div class="form-section">
      <span class="form-section-line"></span>
      <span class="form-section-label">Credenciales</span>
      <span class="form-section-line"></span>
    </div>""", unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Usuario", placeholder="Nombre de usuario")
        password = st.text_input("Contraseña", type="password", placeholder="Contraseña")
        submit_login = st.form_submit_button("Continuar", use_container_width=True)

    if submit_login:
        if not username or not password:
            st.error("Completa todos los campos.")
        else:
            success, user, msg = login_user(db, username, password)
            if success:
                log_login(db, user.id, user.username)
                token = create_session(db, user.id, user.username)
                st.session_state.logged_in     = True
                st.session_state.user_id       = user.id
                st.session_state.username      = user.username
                st.session_state.session_token = token
                login_redirect(token)
            else:
                st.error(msg)

    with st.expander("Información de seguridad", expanded=False):
        st.info("La cuenta se bloqueará temporalmente después de **8 intentos fallidos**.")

# ── REGISTRO ──────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("""
    <div class="form-section">
      <span class="form-section-line"></span>
      <span class="form-section-label">Datos de la cuenta</span>
      <span class="form-section-line"></span>
    </div>""", unsafe_allow_html=True)

    with st.form("register_form", clear_on_submit=False):
        new_username = st.text_input("Usuario", placeholder="3–20 caracteres")
        new_email    = st.text_input("Correo electrónico", placeholder="ejemplo@empresa.com")

        st.markdown("""
        <div class="form-section" style="margin-top:.9rem">
          <span class="form-section-line"></span>
          <span class="form-section-label">Contraseña</span>
          <span class="form-section-line"></span>
        </div>""", unsafe_allow_html=True)

        new_password         = st.text_input("Nueva contraseña", type="password",
                                             placeholder="Mín. 8 caracteres")
        new_password_confirm = st.text_input("Confirmar contraseña", type="password",
                                             placeholder="Repite la contraseña")
        submit_register = st.form_submit_button("Crear cuenta", use_container_width=True)

    if submit_register:
        if not new_username or not new_email or not new_password or not new_password_confirm:
            st.error("Completa todos los campos.")
        else:
            valid_user, user_msg = validate_username(new_username)
            if not valid_user:
                st.error(user_msg)
            else:
                valid_email, email_msg = validate_email(new_email)
                if not valid_email:
                    st.error(email_msg)
                else:
                    valid_pass, pass_msg = validate_password(new_password)
                    if not valid_pass:
                        if "debe contener" in pass_msg:
                            missing = []
                            if not re.search(r'[A-Z]', new_password):
                                missing.append("mayúscula (A-Z)")
                            if not re.search(r'[a-z]', new_password):
                                missing.append("minúscula (a-z)")
                            if not re.search(r'[0-9]', new_password):
                                missing.append("número (0-9)")
                            if not re.search(r'[@$!%*?&]', new_password):
                                missing.append("símbolo (@$!%*?&)")
                            st.error("Contraseña insegura — falta: " + " · ".join(missing))
                        else:
                            st.error(pass_msg)
                    elif new_password != new_password_confirm:
                        st.error("Las contraseñas no coinciden. Revisa que ambas sean iguales.")
                    else:
                        success, msg = register_user(
                            db, new_username, new_email,
                            new_password, new_password_confirm
                        )
                        if success:
                            st.success(msg)
                            st.info("Ahora puedes iniciar sesión.")
                        else:
                            st.error(msg)

    with st.expander("Requisitos de contraseña", expanded=False):
        st.markdown("""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:.35rem .8rem;padding:.1rem 0">
          <span>8 + caracteres</span>
          <span>Mayúscula <code>A–Z</code></span>
          <span>Minúscula <code>a–z</code></span>
          <span>Número <code>0–9</code></span>
          <span style="grid-column:span 2">Símbolo <code>@ $ ! % * ? &amp;</code></span>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<p class="auth-footer">SISTEMA MRP &nbsp;·&nbsp; 2025</p>', unsafe_allow_html=True)

