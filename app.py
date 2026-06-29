import sqlite3

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

def agregar_producto(nombre, cantidad, precio):
    conn = conectar()
    conn.execute("INSERT INTO productos (nombre, cantidad, precio) VALUES (?, ?, ?)", 
                 (nombre, cantidad, precio))
    conn.commit()
    conn.close()
    print(f"Producto '{nombre}' añadido con éxito.")

def listar_productos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    print("\n--- INVENTARIO ACTUAL ---")
    for p in productos:
        print(f"ID: {p[0]} | Producto: {p[1]} | Cantidad: {p[2]} | Precio: ${p[3]:.2f}")
    conn.close()

# Ejemplo de uso
if __name__ == "__main__":
    #agregar_producto("Laptop", 10, 850.00)
    listar_productos()

