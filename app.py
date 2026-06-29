import streamlit as st
import sqlite3
import pandas as pd

# Conexión a la base de datos
def conectar():
    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL
        )
    """)
    conn.commit()
    return conn

st.title("📦 Sistema de Inventario Empresarial")

menu = st.sidebar.selectbox("Menú", ["Ver Inventario", "Agregar Producto"])

if menu == "Ver Inventario":
    st.subheader("Productos en Stock")
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM productos", conn)
    st.table(df)
    conn.close()

elif menu == "Agregar Producto":
    st.subheader("Registrar nuevo producto")
    nombre = st.text_input("Nombre del producto")
    cantidad = st.number_input("Cantidad", min_value=0, step=1)
    precio = st.number_input("Precio", min_value=0.0, step=0.01)
    
    if st.button("Guardar"):
        conn = conectar()
        conn.execute("INSERT INTO productos (nombre, cantidad, precio) VALUES (?, ?, ?)", 
                     (nombre, cantidad, precio))
        conn.commit()
        conn.close()
        st.success(f"Producto '{nombre}' guardado exitosamente!")
