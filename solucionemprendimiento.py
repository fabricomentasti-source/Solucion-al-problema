import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Gestión Artesanal", page_icon="🌿", layout="wide"
)

st.title("🌿 Inventario y Ventas: Deshidratados & Tisanas")

# 1. Inicializar datos en la sesión para que no se borren al recargar
if "inventario" not in st.session_state:
  datos_iniciales = [
      {
          "Producto": "Tisana Frutos del Bosque",
          "Categoría": "Tisanas",
          "Precio (Bs)": 25.0,
          "Stock": 30,
          "Ventas": 12,
      },
      {
          "Producto": "Tisana Manzanilla y Menta",
          "Categoría": "Tisanas",
          "Precio (Bs)": 20.0,
          "Stock": 25,
          "Ventas": 18,
      },
      {
          "Producto": "Manzana Deshidratada (100g)",
          "Categoría": "Deshidratados",
          "Precio (Bs)": 15.0,
          "Stock": 40,
          "Ventas": 25,
      },
      {
          "Producto": "Naranja Deshidratada para Coctel",
          "Categoría": "Deshidratados",
          "Precio (Bs)": 18.0,
          "Stock": 20,
          "Ventas": 10,
      },
      {
          "Producto": "Miel Artesanal Pura (500g)",
          "Categoría": "Artesanal",
          "Precio (Bs)": 45.0,
          "Stock": 15,
          "Ventas": 8,
      },
      {
          "Producto": "Mermelada Casera de Higo",
          "Categoría": "Artesanal",
          "Precio (Bs)": 22.0,
          "Stock": 12,
          "Ventas": 14,
      },
  ]
  st.session_state.inventario = pd.DataFrame(datos_iniciales)

df = st.session_state.inventario

# Calcular columna de dinero ganado por producto
df["Dinero Ganado (Bs)"] = df["Precio (Bs)"] * df["Ventas"]

# 2. Panel de Métricas Principales
total_ganado = df["Dinero Ganado (Bs)"].sum()
total_ventas = df["Ventas"].sum()
total_stock = df["Stock"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Dinero Ganado", f"{total_ganado:,.2f} Bs")
col2.metric("🛍️ Unidades Vendidas", f"{total_ventas} uds")
col3.metric("📦 Stock Disponible", f"{total_stock} uds")

# 3. Barra lateral para acciones (Registrar venta y Agregar producto)
st.sidebar.header("⚙️ Panel de Control")

# Sección: Registrar Venta
st.sidebar.subheader("🛒 Registrar Venta")
producto_venta = st.sidebar.selectbox(
    "Selecciona el producto", df["Producto"].tolist()
)
cantidad_venta = st.sidebar.number_input("Cantidad vendida", min_value=1, step=1)

if st.sidebar.button("Confirmar Venta"):
  idx = df[df["Producto"] == producto_venta].index[0]
  stock_actual = df.loc[idx, "Stock"]

  if stock_actual >= cantidad_venta:
    st.session_state.inventario.loc[idx, "Stock"] -= cantidad_venta
    st.session_state.inventario.loc[idx, "Ventas"] += cantidad_venta
    st.sidebar.success(
        f"Venta registrada: {cantidad_venta}x {producto_venta}"
    )
    st.rerun()
  else:
    st.sidebar.error(f"Stock insuficiente. Solo quedan {stock_actual} unidades.")

# Sección: Agregar Nuevo Producto
st.sidebar.subheader("➕ Nuevo Producto")
with st.sidebar.form("nuevo_producto_form", clear_on_submit=True):
  nombre_nuevo = st.text_input("Nombre del producto")
  cat_nueva = st.selectbox(
      "Categoría", ["Tisanas", "Deshidratados", "Artesanal", "Otros"]
  )
  precio_nuevo = st.number_input(
      "Precio unitario (Bs)", min_value=0.5, step=0.5
  )
  stock_nuevo = st.number_input("Stock inicial", min_value=1, step=1)
  submit_nuevo = st.form_submit_button("Guardar Producto")

  if submit_nuevo and nombre_nuevo:
    nuevo_item = pd.DataFrame([{
        "Producto": nombre_nuevo,
        "Categoría": cat_nueva,
        "Precio (Bs)": precio_nuevo,
        "Stock": stock_nuevo,
        "Ventas": 0,
    }])
    st.session_state.inventario = pd.concat(
        [st.session_state.inventario, nuevo_item], ignore_index=True
    )
    st.sidebar.success(f"Agregado: {nombre_nuevo}")
    st.rerun()

# 4. Vista Principal: Tabla y Gráficos
col_tabla, col_grafico = st.columns([3, 2])

with col_tabla:
  st.subheader("📋 Lista de Productos")
  st.dataframe(df, use_container_width=True, hide_index=True)

with col_grafico:
  st.subheader("📊 Ingresos por Producto (Bs)")
  st.bar_chart(df.set_index("Producto")["Dinero Ganado (Bs)"])