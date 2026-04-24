# -*- coding: utf-8 -*-
"""
session_manager.py

PROBLEMA RAÍZ: st.switch_page() interrumpe el script antes de que cualquier
componente JS (iframe) termine de ejecutarse, por lo que las cookies nunca
se escriben en el browser antes de la navegación.

SOLUCIÓN DEFINITIVA:
- ESCRIBIR + NAVEGAR: Un único bloque JS inyectado vía st.components.v1.html
  que (1) escribe la cookie en window.parent y (2) navega al dashboard.
  Todo en el MISMO JavaScript → sin race condition.
- LEER en cada recarga: st.context.cookies (HTTP request header, 100% confiable).
- Timeout 30 min: verificado en base de datos.
"""
import streamlit as st
import streamlit.components.v1 as components
from database import SessionLocal
from services.session_service import (
    get_valid_session,
    update_activity,
    delete_session,
)

COOKIE_NAME = "mrp_session_token"
_DASHBOARD_PATH = "/pages/dashboard"
_LOGIN_PATH = "/pages/login"


def login_redirect(token: str) -> None:
    """
    Escribe la cookie de sesión Y navega al dashboard en una sola operación JS.
    El JS corre dentro del iframe de components.html (mismo origen → acceso a
    window.parent), primero escribe el cookie, luego navega. Así cuando el
    browser hace el request al dashboard el cookie YA está presente en los headers.
    Llama st.stop() para que Python no continúe ejecutando.
    """
    expires = _js_expires(days=1)
    components.html(
        f"""
        <script>
        (function() {{
            // 1. Escribir cookie en la ventana principal (mismo origen)
            var exp = "{expires}";
            try {{
                window.parent.document.cookie =
                    "{COOKIE_NAME}={token}; path=/; expires=" + exp + "; SameSite=Lax";
            }} catch(e) {{
                document.cookie =
                    "{COOKIE_NAME}={token}; path=/; expires=" + exp + "; SameSite=Lax";
            }}
            // 2. Navegar al dashboard (full page load → cookie en HTTP header)
            window.parent.location.href = window.parent.location.origin + "{_DASHBOARD_PATH}";
        }})();
        </script>
        """,
        height=0,
    )
    st.stop()


def logout_redirect() -> None:
    """
    Borra la cookie Y navega al login en una sola operación JS.
    """
    components.html(
        f"""
        <script>
        (function() {{
            // Borrar cookie poniendo fecha de expiración en el pasado
            try {{
                window.parent.document.cookie =
                    "{COOKIE_NAME}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax";
            }} catch(e) {{
                document.cookie =
                    "{COOKIE_NAME}=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax";
            }}
            window.parent.location.href = window.parent.location.origin + "{_LOGIN_PATH}";
        }})();
        </script>
        """,
        height=0,
    )
    st.stop()


def init_session() -> bool:
    """
    Verifica y restaura la sesión en cada carga de página.
    Retorna True si sesión válida, False si debe redirigir al login.

    Caso 1: session_state tiene logged_in=True  → navegación normal (sin F5).
    Caso 2: session_state vacío (F5/nueva pestaña) → lee st.context.cookies
            que viene del HTTP request header — siempre confiable.
    """
    st.session_state.setdefault("logged_in", False)
    st.session_state.setdefault("username", None)
    st.session_state.setdefault("user_id", None)
    st.session_state.setdefault("session_token", None)

    # Caso 1: sesión activa en memory (navegación entre páginas sin recarga)
    if st.session_state.logged_in and st.session_state.session_token:
        db = SessionLocal()
        try:
            valid = get_valid_session(db, st.session_state.session_token)
            if valid:
                update_activity(db, st.session_state.session_token)
                return True
            else:
                # Expiró por inactividad (30 min)
                _clear_state()
                return False
        finally:
            db.close()

    # Caso 2: F5 / nueva pestaña → leer cookie del HTTP request header
    token = st.context.cookies.get(COOKIE_NAME)
    if not token:
        return False

    db = SessionLocal()
    try:
        valid = get_valid_session(db, token)
        if valid:
            st.session_state.logged_in = True
            st.session_state.user_id = valid.user_id
            st.session_state.username = valid.username
            st.session_state.session_token = token
            update_activity(db, token)
            return True
        else:
            # Token expirado → limpiar y denegar
            _clear_state()
            return False
    finally:
        db.close()


def logout_session() -> None:
    """Elimina la sesión de la DB, limpia session_state y redirige al login vía JS."""
    token = st.session_state.get("session_token")
    if token:
        db = SessionLocal()
        try:
            delete_session(db, token)
        finally:
            db.close()
    _clear_state()
    logout_redirect()


def _clear_state() -> None:
    """Limpia el session_state de autenticación."""
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.session_token = None


def _js_expires(days: int = 1) -> str:
    """Genera fecha de expiración de cookie en formato GMT string para JS."""
    from datetime import datetime, timedelta, timezone
    dt = datetime.now(timezone.utc) + timedelta(days=days)
    return dt.strftime("%a, %d %b %Y %H:%M:%S GMT")

