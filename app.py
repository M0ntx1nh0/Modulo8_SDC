import streamlit as st
from utils.login import generarLogin

# Mostrar login y detener si no está autenticado
generarLogin()

# ✅ Solo si el usuario está logueado
if st.session_state.get("authenticated", False):

    # --- SIDEBAR personalizado --- Solo aparece si el usuario está logueado
    with st.sidebar:
        st.markdown("## ⚽ App-Fútbol")
        st.markdown("---")
        st.markdown("**Diseñado por:** Ramón Codesido")
        st.markdown("*Alumno de SDC del Máster de Python Avanzado*")
        st.markdown("© 2025")
        st.markdown("---")

        # Menú de navegación para las páginas
        page = st.radio("Selecciona una sección:", ["Estadísticas Jugadores", "Info Equipos API"])

        # Opción para cerrar sesión
        st.markdown("---")
        if st.button("🔓 Cerrar sesión"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state["authenticated"] = False
            st.session_state["usuario"] = None
            st.experimental_rerun()  # Esto forzará una recarga de la página

    # --- Carga de páginas según la selección ---
    if page == "Estadísticas Jugadores":
        from pages import Estadisticas_Jugadores
        Estadisticas_Jugadores.app()
    elif page == "Info Equipos API":
        from pages import Info_Equipos_API
        Info_Equipos_API.app()

else:
    # Solo el formulario de login y sin Sidebar
    st.sidebar.empty()  # Vaciamos el sidebar completamente hasta que el usuario se loguee