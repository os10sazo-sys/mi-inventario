
import streamlit as st
import sqlite3
import pandas as pd
import hashlib

# Función para encriptar contraseñas
def encriptar_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# Conexión y creación de tablas
def inicializar_db():
    conn = sqlite3.connect("inventario_comercial.db")
    cursor = conn.cursor()
    # Tabla de usuarios (empresas)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            empresa TEXT NOT NULL
        )
    """)
    # Tabla de productos (enlazada al usuario por usuario_id)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL,
            usuario_id INTEGER NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
        )
    """)
    # Crear un usuario de prueba si la base de datos está vacía
    cursor.execute("SELECT * FROM usuarios WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios (username, password, empresa) VALUES (?, ?, ?)",
                       ("admin", encriptar_password("admin123"), "Mi Empresa Demo"))
    conn.commit()
    return conn

# Funciones de autenticación
def verificar_usuario(username, password):
    conn = sqlite3.connect("inventario_comercial.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, empresa FROM usuarios WHERE username = ? AND password = ?", 
                   (username, encriptar_password(password)))
    resultado = cursor.fetchone()
    conn.close()
    return resultado

def registrar_usuario(username, password, empresa):
    conn = sqlite3.connect("inventario_comercial.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO usuarios (username, password, empresa) VALUES (?, ?, ?)", 
                       (username, encriptar_password(password), empresa))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

# Inicializar base de datos al arrancar
inicializar_db()

# Estado de la sesión en Streamlit
if "logeado" not in st.session_state:
    st.session_state["logeado"] = False
    st.session_state["usuario_id"] = None
    st.session_state["nombre_empresa"] = ""

# --- INTERFAZ DE USUARIO ---
st.set_page_config(page_title="Inventario Pro", page_icon="📦")

if not st.session_state["logeado"]:
    st.title("🔑 Acceso al Sistema de Inventario")
    
    pestana = st.tabs(["Iniciar Sesión", "Registrar Nueva Empresa"])
    
    with pestana[0]:
        usuario_input = st.text_input("Usuario (Email)", key="login_user")
        clave_input = st.text_input("Contraseña", type="password", key="login_pass")
        if st.button("Entrar", type="primary"):
            datos_user = verificar_usuario(usuario_input, clave_input)
            if datos_user:
                st.session_state["logeado"] = True
                st.session_state["usuario_id"] = datos_user[0]
                st.session_state["nombre_empresa"] = datos_user[1]
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")
                
    with pestana[1]:
        nuevo_user = st.text_input("Usuario para la empresa (Email)", key="reg_user")
        nueva_clave = st.text_input("Contraseña segura", type="password", key="reg_pass")
        nombre_empresa = st.text_input("Nombre de la Empresa", key="reg_empresa")
        if st.button("Crear Cuenta"):
            if nuevo_user and nueva_clave and nombre_empresa:
                if registrar_usuario(nuevo_user, nueva_clave, nombre_empresa):
                    st.success("¡Empresa registrada con éxito! Ya puedes iniciar sesión.")
                else:
                    st.error("El nombre de usuario ya está en uso.")
            else:
                st.warning("Por favor, llena todos los campos.")

else:
    # SISTEMA LOGEADO
    st.sidebar.title(f"🏢 {st.session_state['nombre_empresa']}")
    menu = st.sidebar.selectbox("Menú", ["Ver Inventario", "Agregar Producto"])
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state["logeado"] = False
        st.session_state["usuario_id"] = None
        st.session_state["nombre_empresa"] = ""
        st.rerun()

    conn = sqlite3.connect("inventario_comercial.db")
    
    if menu == "Ver Inventario":
        st.title("📦 Inventario Actual")
        # Filtrar productos SOLO del usuario activo
        query = "SELECT id, nombre, cantidad, precio FROM productos WHERE usuario_id = ?"
        df = pd.read_sql_query(query, conn, params=(st.session_state["usuario_id"],))
        
        if df.empty:
            st.info("Aún no tienes productos registrados. Ve a 'Agregar Producto' en el menú.")
        else:
            st.dataframe(df, use_container_width=True)
            
    elif menu == "Agregar Producto":
        st.title("➕ Registrar Producto")
        nombre = st.text_input("Nombre del artículo")
        cantidad = st.number_input("Cantidad en Stock", min_value=0, step=1)
        precio = st.number_input("Precio por unidad", min_value=0.0, step=0.01)
        
        if st.button("Guardar en Inventario", type="primary"):
            if nombre:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO productos (nombre, cantidad, precio, usuario_id) VALUES (?, ?, ?, ?)",
                    (nombre, cantidad, precio, st.session_state["usuario_id"])
                )
                conn.commit()
                st.success(f"¡{nombre} ha sido agregado al inventario de tu empresa!")
            else:
                st.warning("El nombre del producto no puede estar vacío.")
                
    conn.close()
