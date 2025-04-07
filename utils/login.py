import streamlit as st
import extra_streamlit_components as stx
from datetime import datetime, timedelta
import os
import pandas as pd

# Inicializar CookieManager
cookie_manager = stx.CookieManager()

def cargar_usuarios():
    # Ruta relativa al archivo usuarios.xlsx
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'usuarios.xlsx')
    
    # Verificar si el archivo existe
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"El archivo de usuarios no se encontró en: {file_path}")
    
    # Cargar el archivo Excel
    df_usuarios = pd.read_excel(file_path)
    return df_usuarios

def validarUsuario(login, password):
    # Cargar los usuarios
    usuarios = cargar_usuarios()
    
    # Filtrar los usuarios por el nombre de usuario y la contraseña
    usuario_data = usuarios[
        (usuarios['usuario'].str.strip() == login.strip()) &
        (usuarios['contraseña'].str.strip() == password.strip())
    ]
    
    # Si se encuentra al menos un usuario, devolvemos True (es válido)
    return not usuario_data.empty

def check_authentication():
    # Verifica si el usuario está autenticado con cookies
    if cookie_manager.get(cookie='authenticated') == 'true':
        st.session_state['authenticated'] = True
        st.session_state['usuario'] = cookie_manager.get(cookie='usuario')
    else:
        st.session_state['authenticated'] = False
        st.session_state['usuario'] = None

def generarLogin():
    check_authentication()
    
    if not st.session_state.get('authenticated', False):
        # Crear layout centrado para el login
        col1, col2, col3 = st.columns([1, 2, 1])  # Columnas para centrar
        
        with col2:
            st.title("Tarea Modulo 8 Máster Python SDC")

            with st.form('frmLogin', border=True):
                parLogin = st.text_input('Usuario')
                parPassword = st.text_input('Contraseña', type='password')
                remember_me = st.checkbox('Recuérdame')
                btnLogin = st.form_submit_button('Ingresar')

                if btnLogin:
                    if validarUsuario(parLogin, parPassword):
                        # Guardar en session_state para mantener la sesión
                        st.session_state['usuario'] = parLogin
                        st.session_state['authenticated'] = True
                        st.session_state['logged_in'] = True
                        
                        # Guardar cookies para recordar la sesión
                        expiry = datetime.now() + timedelta(days=30 if remember_me else 1)
                        cookie_manager.set('authenticated', 'true', key='auth_cookie', expires_at=expiry)
                        cookie_manager.set('usuario', parLogin, key='user_cookie', expires_at=expiry)

                        st.success("Inicio de sesión exitoso")
                        
                        # Usar st.stop() para detener la ejecución y evitar que el formulario se siga mostrando
                        st.session_state['logged_in'] = True
                        st.stop()  # Detener la ejecución para que la página no se vuelva a cargar innecesariamente
                    else:
                        st.error("Usuario o contraseña incorrectos")
    else:
        st.write(f"Usuario autenticado: {st.session_state['usuario']}")

def logout():
    # Eliminar las cookies y limpiar el estado de sesión
    cookie_manager.delete('authenticated', key='delete_auth')
    cookie_manager.delete('usuario', key='delete_user')

    # Limpiar completamente las claves de session_state
    st.session_state.clear()  # Limpiar todos los valores guardados en la sesión

    # Detener y permitir la recarga de la página
    st.stop()