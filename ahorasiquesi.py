from datetime import datetime
import pandas as pd
import streamlit as st


# ==========================================
# 1. FUNCIONES DE INICIALIZACIÓN Y ESTADO
# ==========================================
def configurar_pagina():
  """Configura los parámetros visuales de la página en Streamlit."""
  st.set_page_config(
      page_title="Gestión Artesanal Pro", page_icon="🌿", layout="wide"
  )


def inicializar_estado():
  """Inicializa todas las variables en session_state si no existen."""
  if "nombre_negocio" not in st.session_state:
    st.session_state.nombre_negocio = "EcoArtesanal: Tisanas & Deshidratados"
  if "meta_ventas" not in st.session_state:
    st.session_state.meta_ventas = 2500.0
  if "historial_ventas" not in st.session_state:
    st.session_state.historial_ventas = []
  if "gastos_fijos" not in st.session_state:
    st.session_state.gastos_fijos = [
        {"Concepto": "Empaques ecológicos y bolsas kraft", "Monto (Bs)": 80.0},
        {"Concepto": "Alquiler de stand en feria", "Monto (Bs)": 150.0},
    ]
  if "inventario" not in st.session_state:
    st.session_state.inventario = obtener_datos_iniciales()


def obtener_datos_iniciales():
  """Retorna el DataFrame base con los productos iniciales."""
  datos = [
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
  return pd.DataFrame(datos)


# ==========================================
# 2. FUNCIONES DE LÓGICA DE NEGOCIO Y CÁLCULO
# ==========================================
def calcular_finanzas_df(df):
  """Añade columnas financieras calculadas al DataFrame de inventario."""
  df_calc = df.copy()
  df_calc["Margen Unitario (Bs)"] = (
      df_calc["Precio (Bs)"] - df_calc["Costo (Bs)"]
  )
  df_calc["Ingresos Brutos (Bs)"] = df_calc["Precio (Bs)"] * df_calc["Ventas"]
  df_calc["Costo de Ventas (Bs)"] = df_calc["Costo (Bs)"] * df_calc["Ventas"]
  df_calc["Ganancia Bruta (Bs)"] = (
      df_calc["Ingresos Brutos (Bs)"] - df_calc["Costo de Ventas (Bs)"]
  )
  return df_calc


def registrar_venta_individual(
    producto, cantidad, descuento, cliente, metodo_pago
):
  """Valida el stock, descuenta inventario y guarda la venta en el historial."""
  df = st.session_state.inventario
  idx = df[df["Producto"] == producto].index[0]
  stock_actual = df.loc[idx, "Stock"]
  precio_unit = df.loc[idx, "Precio (Bs)"]

  if stock_actual < cantidad:
    return False, f"❌ Stock insuficiente. Solo quedan {stock_actual} unidades."

  st.session_state.inventario.loc[idx, "Stock"] -= cantidad
  st.session_state.inventario.loc[idx, "Ventas"] += cantidad

  total_cobrado = max((precio_unit * cantidad) - descuento, 0.0)
  nuevo_registro = {
      "Fecha/Hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
      "Cliente": cliente if cliente.strip() else "Cliente General",
      "Detalle": f"{cantidad}x {producto}",
      "Total (Bs)": round(total_cobrado, 2),
      "Método": metodo_pago,
  }
  st.session_state.historial_ventas.insert(0, nuevo_registro)
  return (
      True,
      (
          f"✅ Venta registrada: {cantidad}x {producto} por"
          f" {total_cobrado:.2f} Bs."
      ),
  )


def agregar_nuevo_producto(nombre, categoria, costo, precio, stock):
  """Inserta un producto nuevo en el DataFrame de inventario."""
  if not nombre.strip():
    return False, "⚠️ Debes escribir un nombre para el producto."
  if precio <= costo:
    return (
        False,
        "⚠️ El precio de venta debe ser mayor al costo para generar ganancia.",
    )

  nuevo_df = pd.DataFrame([{
      "Producto": nombre.strip(),
      "Categoría": categoria,
      "Costo (Bs)": costo,
      "Precio (Bs)": precio,
      "Stock": stock,
      "Ventas": 0,
  }])
  st.session_state.inventario = pd.concat(
      [st.session_state.inventario, nuevo_df], ignore_index=True
  )
  return True, f"✅ Producto '{nombre}' añadido al catálogo."


def vender_combo_artesanal(
    lista_productos, pct_descuento, cliente, metodo_pago
):
  """Descuenta 1 unidad de cada producto del combo y registra la venta."""
  df = st.session_state.inventario
  for prod in lista_productos:
    idx = df[df["Producto"] == prod].index[0]
    if df.loc[idx, "Stock"] < 1:
      return False, f"❌ El producto '{prod}' no tiene stock para el combo."

  precio_normal = 0.0
  for prod in lista_productos:
    idx = df[df["Producto"] == prod].index[0]
    st.session_state.inventario.loc[idx, "Stock"] -= 1
    st.session_state.inventario.loc[idx, "Ventas"] += 1
    precio_normal += df.loc[idx, "Precio (Bs)"]

  total_combo = precio_normal * (1 - (pct_descuento / 100.0))
  st.session_state.historial_ventas.insert(
      0,
      {
          "Fecha/Hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
          "Cliente": cliente if cliente.strip() else "Cliente General",
          "Detalle": (
              f"Combo ({', '.join(lista_productos)}) [-{pct_descuento}%]"
          ),
          "Total (Bs)": round(total_combo, 2),
          "Método": metodo_pago,
      },
  )
  return (
      True,
      (
          "✅ ¡Combo vendido exitosamente por"
          f" {total_combo:.2f} Bs!{chr(10)}(Ahorro:"
          f" {precio_normal - total_combo:.2f} Bs)"
      ),
  )


def generar_texto_recibo(venta):
  """Genera un comprobante en formato texto listo para copiar o descargar."""
  return f"""========================================
🌿 {st.session_state.nombre_negocio.upper()}
COMPROBANTE DE VENTA
========================================
Fecha:   {venta['Fecha/Hora']}
Cliente: {venta['Cliente']}
Detalle: {venta['Detalle']}
Método:  {venta['Método']}
----------------------------------------
TOTAL PAGADO: {venta['Total (Bs)']} Bs
========================================
¡Gracias por apoyar el trabajo artesanal!"""


# ==========================================
# 3. FUNCIONES DE INTERFAZ DE USUARIO (UI)
# ==========================================
def renderizar_sidebar():
  """Dibuja la barra lateral con configuración y alta rápida de productos."""
  with st.sidebar:
    st.header("⚙️ Panel de Control")
    st.session_state.nombre_negocio = st.text_input(
        "Nombre del Negocio", st.session_state.nombre_negocio
    )
    st.session_state.meta_ventas = st.number_input(
        "Meta Mensual (Bs)",
        min_value=100.0,
        value=st.session_state.meta_ventas,
        step=100.0,
    )

    st.divider()
    st.subheader("➕ Añadir Producto al Catálogo")
    with st.form("form_alta_producto", clear_on_submit=True):
      nombre = st.text_input("Nombre", placeholder="Ej. Piña Deshidratada")
      categoria = st.selectbox(
          "Categoría",
          [
              "Tisanas",
              "Deshidratados",
              "Artesanal",
              "Cosmética Natural",
              "Otros",
          ],
      )
      c1, c2 = st.columns(2)
      costo = c1.number_input(
          "Costo (Bs)", min_value=0.5, value=8.0, step=0.5
      )
      precio = c2.number_input(
          "Precio (Bs)", min_value=1.0, value=18.0, step=0.5
      )
      stock = st.number_input("Stock Inicial", min_value=1, value=15, step=1)

      if st.form_submit_button("Guardar Producto", use_container_width=True):
        exito, msg = agregar_nuevo_producto(
            nombre, categoria, costo, precio, stock
        )
        if exito:
          st.success(msg)
          st.rerun()
        else:
          st.error(msg)


def renderizar_metricas_superiores(df_calc):
  """Muestra las tarjetas de resumen financiero y la barra de progreso."""
  ingresos = df_calc["Ingresos Brutos (Bs)"].sum()
  ganancia_bruta = df_calc["Ganancia Bruta (Bs)"].sum()
  gastos_fijos = sum(item["Monto (Bs)"] for item in st.session_state.gastos_fijos)
  ganancia_neta_real = ganancia_bruta - gastos_fijos
  unidades_vendidas = df_calc["Ventas"].sum()

  progreso = min(ingresos / st.session_state.meta_ventas, 1.0)
  st.write(
      f"🎯 **Progreso de Meta de Ventas ({st.session_state.meta_ventas:,.2f}"
      f" Bs):** {progreso*100:.1f}%"
  )
  st.progress(progreso)

  c1, c2, c3, c4 = st.columns(4)
  c1.metric("💰 Ingresos Brutos", f"{ingresos:,.2f} Bs")
  c2.metric("📈 Ganancia de Productos", f"{ganancia_bruta:,.2f} Bs")
  c3.metric(
      "🏆 Utilidad Neta (Tras Gastos)",
      f"{ganancia_neta_real:,.2f} Bs",
      delta=f"-{gastos_fijos} Bs gastos fijos",
  )
  c4.metric("🛍️ Unidades Vendidas", f"{unidades_vendidas} uds")


def renderizar_tab_caja(df_calc):
  """Pestaña 1: Punto de venta individual y generador de recibos."""
  col_izq, col_der = st.columns([1, 1])

  with col_izq:
    st.subheader("🛒 Registrar Venta")
    with st.container(border=True):
      cliente = st.text_input(
          "Nombre del Cliente", placeholder="Ej. Carlos Mendoza"
      )
      prod_sel = st.selectbox(
          "Selecciona el Producto", df_calc["Producto"].tolist()
      )

      fila = df_calc[df_calc["Producto"] == prod_sel].iloc[0]
      st.info(
          f"**Precio:** {fila['Precio (Bs)']} Bs | **Stock:**"
          f" {fila['Stock']} uds | **Ganancia unitaria:**"
          f" {fila['Margen Unitario (Bs)']} Bs"
      )

      c1, c2 = st.columns(2)
      cantidad = c1.number_input("Cantidad", min_value=1, step=1)
      descuento = c2.number_input(
          "Descuento (Bs)", min_value=0.0, step=1.0
      )
      metodo = st.radio(
          "Método de Pago", ["Efectivo", "QR / Transferencia"], horizontal=True
      )

      total = max((fila["Precio (Bs)"] * cantidad) - descuento, 0.0)
      st.markdown(f"#### Total a Cobrar: **{total:,.2f} Bs**")

      if st.button(
          "✅ Confirmar Venta", type="primary", use_container_width=True
      ):
        exito, msg = registrar_venta_individual(
            prod_sel, cantidad, descuento, cliente, metodo
        )
        if exito:
          st.balloons()
          st.success(msg)
          st.rerun()
        else:
          st.error(msg)

  with col_der:
    st.subheader("🧾 Historial y Recibos")
    if st.session_state.historial_ventas:
      df_hist = pd.DataFrame(st.session_state.historial_ventas)
      st.dataframe(df_hist, use_container_width=True, hide_index=True)

      with st.expander("🖨️ Ver / Descargar Recibo de la Última Venta"):
        ultima_venta = st.session_state.historial_ventas[0]
        texto_recibo = generar_texto_recibo(ultima_venta)
        st.code(texto_recibo, language="text")
        st.download_button(
            "📥 Descargar Recibo (.txt)",
            texto_recibo,
            file_name="recibo_venta.txt",
        )
    else:
      st.info("Aún no se registraron ventas en esta sesión.")


def renderizar_tab_combos(df_calc):
  """Pestaña 2: Armador de packs y cajas regalo con descuento."""
  st.subheader("🎁 Armador de Combos y Cajas Regalo")
  st.write(
      "Selecciona 2 o más productos para armar un pack promocional (ej. *Tisana"
      " + Miel + Deshidratado*) y aplica un descuento automático."
  )

  with st.container(border=True):
    seleccionados = st.multiselect(
        "Productos incluidos en el Combo (1 unidad de cada uno)",
        df_calc["Producto"].tolist(),
    )
    c1, c2, c3 = st.columns(3)
    pct_desc = c1.slider("Porcentaje de Descuento (%)", 0, 40, 10)
    cliente_combo = c2.text_input("Cliente del Combo", placeholder="Opcional")
    metodo_combo = c3.selectbox("Pago", ["QR / Transferencia", "Efectivo"])

    if len(seleccionados) >= 2:
      df_sel = df_calc[df_calc["Producto"].isin(seleccionados)]
      suma_normal = df_sel["Precio (Bs)"].sum()
      suma_costo = df_sel["Costo (Bs)"].sum()
      precio_final = suma_normal * (1 - pct_desc / 100.0)
      ganancia_combo = precio_final - suma_costo

      st.markdown(
          f"**Precio Normal:** ~~{suma_normal:.2f} Bs~~ ➡️ **Precio Combo:**"
          f" `{precio_final:.2f} Bs` *(Tu ganancia neta: {ganancia_combo:.2f}"
          " Bs)*"
      )

      if st.button("🎉 Vender Combo Promocional", type="primary"):
        exito, msg = vender_combo_artesanal(
            seleccionados, pct_desc, cliente_combo, metodo_combo
        )
        if exito:
          st.balloons()
          st.success(msg)
          st.rerun()
        else:
          st.error(msg)
    else:
      st.warning("👆 Selecciona al menos 2 productos para habilitar el combo.")


def renderizar_tab_inventario(df_calc):
  """Pestaña 3: Editor interactivo de inventario y reabastecimiento."""
  st.subheader("📦 Gestión Interactiva de Inventario")

  bajos = df_calc[df_calc["Stock"] <= 5]
  if not bajos.empty:
    st.warning(
        "⚠️ **Productos por agotarse (5 o menos):** "
        + ", ".join(bajos["Producto"].tolist())
    )

  c_filtro, c_lote = st.columns([2, 1])
  categorias = ["Todas"] + list(df_calc["Categoría"].unique())
  cat_filtro = c_filtro.selectbox("Filtrar por Categoría", categorias)

  if c_lote.button(
      "➕ Sumar +10 uds de Stock a TODOS los productos",
      use_container_width=True,
  ):
    st.session_state.inventario["Stock"] += 10
    st.success("¡Se sumaron 10 unidades a todo el inventario!")
    st.rerun()

  df_mostrar = st.session_state.inventario
  if cat_filtro != "Todas":
    df_mostrar = df_mostrar[df_mostrar["Categoría"] == cat_filtro]

  st.caption(
      "💡 Haz doble clic en cualquier celda para editar costos, precios o"
      " stock."
  )
  df_editado = st.data_editor(
      df_mostrar, use_container_width=True, hide_index=True, num_rows="dynamic"
  )

  if cat_filtro == "Todas" and not df_editado.equals(
      st.session_state.inventario
  ):
    st.session_state.inventario = df_editado
    st.rerun()


def renderizar_tab_simulador():
  """Pestaña 4: Simulador didáctico de costos para nuevos productos."""
  st.subheader("🧮 Simulador Didáctico de Precios y Punto de Equilibrio")
  st.write(
      "Usa esta calculadora antes de lanzar una nueva tisana o deshidratado"
      " para saber a cuánto venderlo."
  )

  c1, c2 = st.columns(2)
  with c1:
    with st.container(border=True):
      st.markdown("##### 1. Costos por Unidad")
      insumos = st.number_input(
          "Materia Prima (Fruta/Hierbas, miel, etc.) [Bs]",
          min_value=0.0,
          value=5.0,
          step=0.5,
      )
      empaque = st.number_input(
          "Empaque, bolsa hermética y etiqueta [Bs]",
          min_value=0.0,
          value=2.5,
          step=0.5,
      )
      energia = st.number_input(
          "Energía (Uso de deshidratador / gas) [Bs]",
          min_value=0.0,
          value=1.5,
          step=0.5,
      )
      margen_deseado = st.slider("Margen de Ganancia Deseado (%)", 10, 200, 60)
      inversion_fija = st.number_input(
          "Inversión en Equipos/Feria a recuperar (Bs)",
          min_value=0.0,
          value=300.0,
          step=50.0,
      )

  with c2:
    costo_unitario_total = insumos + empaque + energia
    precio_sugerido = costo_unitario_total * (1 + (margen_deseado / 100.0))
    ganancia_por_unidad = precio_sugerido - costo_unitario_total
    punto_equilibrio = (
        inversion_fija / ganancia_por_unidad if ganancia_por_unidad > 0 else 0
    )

    with st.container(border=True):
      st.markdown("##### 2. Resultados Sugeridos")
      st.metric("🛠️ Costo Total de Producción", f"{costo_unitario_total:.2f} Bs")
      st.metric("🏷️ Precio de Venta Sugerido", f"{precio_sugerido:.2f} Bs")
      st.metric("✨ Ganancia por cada Bolsa/Frasco", f"{ganancia_por_unidad:.2f} Bs")
      st.info(
          "⚖️ **Punto de Equilibrio:** Necesitas vender"
          f" **{int(punto_equilibrio) + 1} unidades** para recuperar tu"
          f" inversión de {inversion_fija:.2f} Bs."
      )


def renderizar_tab_reportes(df_calc):
  """Pestaña 5: Registro de gastos fijos, gráficos y exportación CSV."""
  st.subheader("📊 Balance Financiero y Gastos Operativos")

  col_gastos, col_graficos = st.columns([1, 2])
  with col_gastos:
    st.markdown("##### 💸 Registrar Gasto Operativo")
    with st.form("form_gasto", clear_on_submit=True):
      concepto = st.text_input("Concepto (Ej. Transporte, Publicidad)")
      monto = st.number_input("Monto (Bs)", min_value=1.0, step=5.0)
      if st.form_submit_button("Añadir Gasto") and concepto:
        st.session_state.gastos_fijos.append(
            {"Concepto": concepto, "Monto (Bs)": monto}
        )
        st.rerun()

    st.dataframe(
        pd.DataFrame(st.session_state.gastos_fijos),
        use_container_width=True,
        hide_index=True,
    )

  with col_graficos:
    st.markdown("##### 📈 Ingresos Brutos vs. Ganancia por Producto")
    st.bar_chart(
        df_calc.set_index("Producto")[
            ["Ingresos Brutos (Bs)", "Ganancia Bruta (Bs)"]
        ]
    )

  st.divider()
  st.markdown("##### 📋 Tabla Financiera Completa")
  st.dataframe(df_calc, use_container_width=True, hide_index=True)

  csv = df_calc.to_csv(index=False).encode("utf-8")
  st.download_button(
      "📥 Descargar Balance Completo en CSV (Excel)",
      data=csv,
      file_name="balance_artesanal.csv",
      mime="text/csv",
  )


# ==========================================
# 4. FUNCIÓN PRINCIPAL (MAIN)
# ==========================================
def main():
  """Función orquestadora que ejecuta toda la aplicación."""
  configurar_pagina()
  inicializar_estado()
  renderizar_sidebar()

  st.title(f"🌿 {st.session_state.nombre_negocio}")
  st.caption(
      "Sistema modular de gestión de inventario, ventas, combos y finanzas"
      " para emprendimientos."
  )

  df_calculado = calcular_finanzas_df(st.session_state.inventario)
  renderizar_metricas_superiores(df_calculado)

  tab1, tab2, tab3, tab4, tab5 = st.tabs([
      "🛒 1. Caja y Recibos",
      "🎁 2. Armar Combos",
      "📦 3. Inventario",
      "🧮 4. Simulador de Costos",
      "📊 5. Balance y Gastos",
  ])

  with tab1:
    renderizar_tab_caja(df_calculado)
  with tab2:
    renderizar_tab_combos(df_calculado)
  with tab3:
    renderizar_tab_inventario(df_calculado)
  with tab4:
    renderizar_tab_simulador()
  with tab5:
    renderizar_tab_reportes(df_calculado)


if __name__ == "__main__":
  main()