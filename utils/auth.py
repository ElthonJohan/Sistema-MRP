import streamlit as st


def require_login():
    """
    Utility function to require login on any page.
    Intenta restaurar la sesión desde cookie antes de redirigir al login.
    """
    from utils.session_manager import init_session

    session_valid = init_session()

    if not session_valid:
        st.error("❌ Debes iniciar sesión para acceder a esta página")
        st.switch_page("pages/login.py")

def get_current_user_id():
    """Get the ID of the currently logged-in user"""
    if "user_id" not in st.session_state:
        return None
    return st.session_state.user_id

def get_current_username():
    """Get the username of the currently logged-in user"""
    if "username" not in st.session_state:
        return None
    return st.session_state.username

def logout():
    """Logout: elimina sesión en DB, borra cookie y navega al login vía JS."""
    from utils.session_manager import logout_session
    logout_session()  # logout_session ya llama logout_redirect() con st.stop()
