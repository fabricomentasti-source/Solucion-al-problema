from datetime import datetime
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Gestión Artesanal Pro", page_icon="🌿", layout="wide"
)

# 1. Inicializar variables en la sesión
if "nombre_negocio" not in st.session_state:
  st.session_state.nombre_negocio = "Mi Emprendimiento Artesanal"
if "meta_ventas" not in st.session_state:
  st.session_state.meta_ventas = 2000.0
if "historial_ventas" not in st.session_state:
  st.session_state.historial_ventas = []

if "inventario" not in st.session_state:
  datos_iniciales = [
      {
          "Producto": "Tisana Frutos del Bosque",
          "Categoría": "Tisanas",
          "Costo (Bs)": 12.0,
          "Precio (Bs)": 25.0,
          "Stock": 30,
          "Ventas": 12,
      },
      {
          "Producto": "Tisana Manzanilla y Menta",
          "Categoría": "Tisanas",
          "Costo (Bs)": 9.0,
          "Precio (Bs)": 20.0,
          "Stock": 25,
          "Ventas": 18,
      },
      {
          "Producto": "Manzana Deshidratada (100g)",
          "Categoría": "Deshidratados",
          "Costo (Bs)": 7.0,
          "Precio (Bs)": 15.0,
          "Stock": 40,
          "Ventas": 25,
      },
      {
          "Producto": "Naranja Deshidratada para Coctel",
          "Categoría": "Deshidratados",
          "Costo (Bs)": 8.5,
          "Precio (Bs)": 18.0,
          "Stock": 20,
          "Ventas": 10,
      },
      {
          "Producto": "Miel Artesanal Pura (500g)",
          "Categoría": "Artesanal",
          "Costo (Bs)": 25.0,
          "Precio (Bs)": 45.0,
          "Stock": 15,
          "Ventas": 8,
      },
      {
          "Producto": "Mermelada Casera de Higo",
          "Categoría": "Artesanal",
          "Costo (Bs)": 10.0,
          "Precio (Bs)": 22.0,
          "Stock": 4,
          "Ventas": 14,
      },
  ]
  st.session_state.inventario = pd.DataFrame(datos_iniciales)

# 2. Barra lateral: Configuración del emprendimiento y Carga rápida
with st.sidebar:
  st.header("⚙️ Configura tu Negocio")
  st.session_state.nombre_negocio = st.text_input(
      "Nombre del Emprendimiento", st.session_state.nombre_negocio
  )
  st.session_state.meta_ventas = st.number_input(
      "Meta de Ingresos (Bs)",
      min_value=100.0,
      value=st.session_state.meta_ventas,
      step=100.0,
  )

  st.divider()
  st.subheader("➕ Registrar Nuevo Producto")
  with st.form("nuevo_producto_form", clear_on_submit=True):
    nombre_nuevo = st.text_input(
        "Nombre del producto", placeholder="Ej. Té de Cedrón"
    )
    cat_nueva = st.selectbox(
        "Categoría",
        ["Tisanas", "Deshidratados", "Artesanal", "Cosmética Natural", "Otros"],
    )
    col_c, col_p = st.columns(2)
    costo_nuevo = col_c.number_input(
        "Costo Prod. (Bs)", min_value=0.5, value=10.0, step=0.5
    )
    precio_nuevo = col_p.number_input(
        "Precio Venta (Bs)", min_value=1.0, value=20.0, step=0.5
    )
    stock_nuevo = st.number_input(
        "Stock inicial", min_value=1, value=10, step=1
    )

    submit_nuevo = st.form_submit_button("Guardar en Inventario")

    if submit_nuevo:
      if nombre_nuevo.strip() == "":
        st.error("Por favor ingresa un nombre para el producto.")
      elif precio_nuevo <= costo_nuevo:
        st.warning(
            "⚠️ El precio de venta es menor o igual al costo. No tendrás"
            " ganancia."
        )
      else:
        nuevo_item = pd.DataFrame([{
            "Producto": nombre_nuevo,
            "Categoría": cat_nueva,
            "Costo (Bs)": costo_nuevo,
            "Precio (Bs)": precio_nuevo,
            "Stock": stock_nuevo,
            "Ventas": 0,
        }])
        st.session_state.inventario = pd.concat(
            [st.session_state.inventario, nuevo_item], ignore_index=True
        )
        st.success(f"¡{nombre_nuevo} agregado con éxito!")
        st.rerun()

# 3. Encabezado y Cálculos Financieros
st.title(f"🌿 {st.session_state.nombre_negocio}")
st.caption(
    "Sistema interactivo de control de inventario, punto de venta y resultados"
    " financieros."
)

df = st.session_state.inventario.copy()
df["Ingresos Brutos (Bs)"] = df["Precio (Bs)"] * df["Ventas"]
df["Costo Total (Bs)"] = df["Costo (Bs)"] * df["Ventas"]
df["Ganancia Neta (Bs)"] = df["Ingresos Brutos (Bs)"] - df["Costo Total (Bs)"]

# 4. Pestañas interactivas paso a paso
tab1, tab2, tab3 = st.tabs([
    "🛒 1. Punto de Venta",
    "📦 2. Inventario Editable",
    "📊 3. Resultados Finales",
])

# --- PESTAÑA 1: PUNTO DE VENTA ---
with tab1:
  col_venta, col_historial = st.columns([1, 1])

  with col_venta:
    st.subheader("Registrar una Venta")
    with st.container(border=True):
      cliente = st.text_input(
          "Nombre del Cliente (opcional)", placeholder="Ej. Ana Pérez"
      )
      producto_venta = st.selectbox(
          "Selecciona el Producto", df["Producto"].tolist()
      )

      # Mostrar datos en vivo del producto elegido
      datos_prod = df[df["Producto"] == producto_venta].iloc[0]
      st.info(
          f"**Precio:** {datos_prod['Precio (Bs)']} Bs | **Stock disponible:**"
          f" {datos_prod['Stock']} uds | **Ganancia por unidad:**"
          f" {datos_prod['Precio (Bs)'] - datos_prod['Costo (Bs)']} Bs"
      )

      col_cant, col_desc = st.columns(2)
      cantidad_venta = col_cant.number_input(
          "Cantidad a vender", min_value=1, step=1
      )
      descuento = col_desc.number_input(
          "Descuento total (Bs)", min_value=0.0, step=1.0
      )

      metodo_pago = st.radio(
          "Método de Pago", ["Efectivo", "QR / Transferencia"], horizontal=True
      )

      subtotal = (datos_prod["Precio (Bs)"] * cantidad_venta) - descuento
      st.markdown(f"### Total a cobrar: **{max(subtotal, 0.0):,.2f} Bs**")

      if st.button(
          "✅ Confirmar y Registrar Venta",
          type="primary",
          use_container_width=True,
      ):
        idx = df[df["Producto"] == producto_venta].index[0]
        if datos_prod["Stock"] >= cantidad_venta:
          st.session_state.inventario.loc[idx, "Stock"] -= cantidad_venta
          st.session_state.inventario.loc[idx, "Ventas"] += cantidad_venta

          # Guardar en el recibo/historial
          st.session_state.historial_ventas.insert(
              0,
              {
                  "Hora": datetime.now().strftime("%H:%M:%S"),
                  "Cliente": cliente if cliente else "Cliente General",
                  "Producto": producto_venta,
                  "Cant.": cantidad_venta,
                  "Total (Bs)": max(subtotal, 0.0),
                  "Pago": metodo_pago,
              },
          )
          st.balloons()
          st.success(f"Venta exitosa de {cantidad_venta}x {producto_venta}")
          st.rerun()
        else:
          st.error(
              "❌ No hay suficiente stock. Solo quedan"
              f" {datos_prod['Stock']} unidades."
          )

  with col_historial:
    st.subheader("🧾 Últimas Ventas Registradas")
    if st.session_state.historial_ventas:
      df_hist = pd.DataFrame(st.session_state.historial_ventas)
      st.dataframe(df_hist, use_container_width=True, hide_index=True)
    else:
      st.info(
          "Aún no has registrado ventas en esta sesión. ¡Usa el formulario de"
          " la izquierda para empezar!"
      )

# --- PESTAÑA 2: INVENTARIO EDITABLE ---
with tab2:
  st.subheader("📋 Control de Stock y Precios")
  st.write(
      "💡 **Modo didáctico:** Haz doble clic sobre cualquier celda de"
      " **Costo**, **Precio** o **Stock** en la tabla para modificarla"
      " directamente."
  )

  # Alertas de stock bajo
  stock_bajo = df[df["Stock"] <= 5]
  if not stock_bajo.empty:
    st.warning(
        "⚠️ **Alerta de Reposición:** Tienes productos con 5 o menos unidades:"
        f" {', '.join(stock_bajo['Producto'].tolist())}"
    )

  # Editor de datos interactivo
  df_editado = st.data_editor(
      st.session_state.inventario,
      column_config={
          "Producto": st.column_config.TextColumn("Producto", disabled=True),
          "Categoría": st.column_config.SelectboxColumn(
              "Categoría",
              options=[
                  "Tisanas",
                  "Deshidratados",
                  "Artesanal",
                  "Cosmética Natural",
                  "Otros",
              ],
          ),
          "Costo (Bs)": st.column_config.NumberColumn(
              "Costo Prod. (Bs)", format="%.2f Bs", min_value=0.0
          ),
          "Precio (Bs)": st.column_config.NumberColumn(
              "Precio Venta (Bs)", format="%.2f Bs", min_value=0.5
          ),
          "Stock": st.column_config.NumberColumn(
              "Stock Actual", min_value=0, step=1
          ),
          "Ventas": st.column_config.NumberColumn(
              "Unidades Vendidas", min_value=0, step=1
          ),
      },
      use_container_width=True,
      hide_index=True,
      num_rows="dynamic",
  )

  if not df_editado.equals(st.session_state.inventario):
    st.session_state.inventario = df_editado
    st.rerun()

# --- PESTAÑA 3: RESULTADOS FINALES ---
with tab3:
  st.subheader("🏆 Balance Final del Emprendimiento")

  total_ingresos = df["Ingresos Brutos (Bs)"].sum()
  total_costos = df["Costo Total (Bs)"].sum()
  ganancia_neta = df["Ganancia Neta (Bs)"].sum()
  unidades_totales = df["Ventas"].sum()

  # Progreso de la meta
  progreso = min(total_ingresos / st.session_state.meta_ventas, 1.0)
  st.write(
      f"**Progreso hacia tu meta de ingresos ({st.session_state.meta_ventas:,.2f}"
      f" Bs):** {progreso * 100:.1f}%"
  )
  st.progress(progreso)

  # Tarjetas de resumen
  c1, c2, c3, c4 = st.columns(4)
  c1.metric("💰 Ingresos Brutos", f"{total_ingresos:,.2f} Bs")
  c2.metric("🛠️ Costo de lo Vendido", f"{total_costos:,.2f} Bs")
  c3.metric(
      "✨ Ganancia Neta Real",
      f"{ganancia_neta:,.2f} Bs",
      delta=f"{(ganancia_neta/total_ingresos*100) if total_ingresos>0 else 0:.1f}% margen",
  )
  c4.metric("🛍️ Productos Vendidos", f"{unidades_totales} uds")

  st.divider()

  # Gráficos y Tabla Final
  col_g1, col_g2 = st.columns(2)
  with col_g1:
    st.markdown("##### 📊 Comparativa: Ingresos vs. Ganancia Neta por Producto")
    st.bar_chart(
        df.set_index("Producto")[["Ingresos Brutos (Bs)", "Ganancia Neta (Bs)"]]
    )

  with col_g2:
    st.markdown("##### 📦 Ingresos por Categoría")
    df_cat = df.groupby("Categoría")["Ingresos Brutos (Bs)"].sum()
    st.bar_chart(df_cat)

  st.markdown("##### 📄 Tabla Detallada de Resultados")
  st.dataframe(df, use_container_width=True, hide_index=True)

  # Botón de descarga
  csv = df.to_csv(index=False).encode("utf-8")
  st.download_button(
      label="📥 Descargar Reporte Final en CSV (Excel)",
      data=csv,
      file_name="reporte_emprendimiento.csv",
      mime="text/csv",
  )