import streamlit as st
import pandas as pd
import os
from datetime import date

NOMBRE_HOSTAL = "Hostal Familiar Tarija - Control de Egresos y Balance"
MONEDA = "Bs."
ARCHIVO_BASE_DATOS = "finanzas_hostal_tarija.csv"
ARCHIVO_CATEGORIAS = "categorias_hostal_tarija.csv"
AUTOR_MODULO = "Sebastian Espana"

METODOS_PAGO = ["Efectivo", "QR / Transferencia", "Tarjeta"]

CATEGORIAS_INGRESOS_BASE = [
    "Alquiler de Habitaciones",
    "Desayunos / Servicios Adicionales"
]

CATEGORIAS_EGRESOS_BASE = [
    "Servicios Basicos (Luz, Agua, Gas, Wi-Fi)",
    "Limpieza y Lavanderia",
    "Insumos de Cocina y Desayunos",
    "Mantenimiento y Reparaciones",
    "Articulos de Higiene (Amenidades)",
    "Impuestos y Tramites Municipales",
    "Otros Gastos Operativos"
]

def cargar_categorias():
    if os.path.exists(ARCHIVO_CATEGORIAS):
        df_categorias = pd.read_csv(ARCHIVO_CATEGORIAS)
        ingresos = df_categorias[df_categorias["Tipo"] == "Ingreso"]["Categoria"].tolist()
        egresos = df_categorias[df_categorias["Tipo"] == "Egreso"]["Categoria"].tolist()
        return ingresos, egresos

    filas_iniciales = (
        [{"Tipo": "Ingreso", "Categoria": cat} for cat in CATEGORIAS_INGRESOS_BASE]
        + [{"Tipo": "Egreso", "Categoria": cat} for cat in CATEGORIAS_EGRESOS_BASE]
    )
    pd.DataFrame(filas_iniciales).to_csv(ARCHIVO_CATEGORIAS, index=False)
    return CATEGORIAS_INGRESOS_BASE.copy(), CATEGORIAS_EGRESOS_BASE.copy()

def agregar_nueva_categoria(tipo_categoria, nombre_categoria):
    nombre_limpio = str(nombre_categoria).strip()
    if not nombre_limpio:
        return False, "Escribe un nombre para la nueva categoria."

    ingresos, egresos = cargar_categorias()
    lista_actual = ingresos if tipo_categoria == "Ingreso" else egresos

    if nombre_limpio.lower() in [cat.lower() for cat in lista_actual]:
        return False, "Esa categoria ya existe en la lista."

    df_categorias = pd.read_csv(ARCHIVO_CATEGORIAS)
    nueva_fila = pd.DataFrame([{"Tipo": tipo_categoria, "Categoria": nombre_limpio}])
    pd.concat([df_categorias, nueva_fila], ignore_index=True).to_csv(ARCHIVO_CATEGORIAS, index=False)
    return True, f"Categoria '{nombre_limpio}' agregada correctamente."

def obtener_datos_iniciales():
    return [
        {"Fecha": "2026-11-10", "Tipo": "Ingreso", "Categoria": "Alquiler de Habitaciones", "Detalle": "Habitacion Matrimonial #1 (2 noches)", "Metodo": "QR / Transferencia", "Monto": 320.0},
        {"Fecha": "2026-11-10", "Tipo": "Egreso", "Categoria": "Limpieza y Lavanderia", "Detalle": "Detergente, lavandina y suavizante", "Metodo": "Efectivo", "Monto": 85.0},
        {"Fecha": "2026-11-11", "Tipo": "Ingreso", "Categoria": "Alquiler de Habitaciones", "Detalle": "Habitacion Doble #3 (1 noche)", "Metodo": "Efectivo", "Monto": 180.0},
        {"Fecha": "2026-11-11", "Tipo": "Egreso", "Categoria": "Insumos de Cocina y Desayunos", "Detalle": "Pan, cafe, leche, huevos y frutas", "Metodo": "Efectivo", "Monto": 65.0},
        {"Fecha": "2026-11-12", "Tipo": "Egreso", "Categoria": "Servicios Basicos (Luz, Agua, Gas, Wi-Fi)", "Detalle": "Factura mensual de energia electrica", "Metodo": "QR / Transferencia", "Monto": 290.0},
        {"Fecha": "2026-11-12", "Tipo": "Egreso", "Categoria": "Mantenimiento y Reparaciones", "Detalle": "Cambio de grifo de ducha Habitacion #2", "Metodo": "Efectivo", "Monto": 110.0},
        {"Fecha": "2026-11-13", "Tipo": "Ingreso", "Categoria": "Alquiler de Habitaciones", "Detalle": "Habitacion Triple #4 (2 noches)", "Metodo": "QR / Transferencia", "Monto": 420.0},
        {"Fecha": "2026-11-13", "Tipo": "Egreso", "Categoria": "Articulos de Higiene (Amenidades)", "Detalle": "Papel higienico, jaboncillos y shampoo", "Metodo": "Efectivo", "Monto": 75.0}
    ]

def cargar_movimientos():
    if os.path.exists(ARCHIVO_BASE_DATOS):
        return pd.read_csv(ARCHIVO_BASE_DATOS)

    df_inicial = pd.DataFrame(obtener_datos_iniciales())
    df_inicial.to_csv(ARCHIVO_BASE_DATOS, index=False)
    return df_inicial

def registrar_movimiento(fecha_movimiento, tipo_movimiento, categoria, detalle, metodo_pago, monto):
    detalle_limpio = str(detalle).strip()
    if not detalle_limpio:
        return False, "El detalle del movimiento no puede quedar vacio."
    if monto <= 0:
        return False, "El monto debe ser mayor a 0 Bs."

    nuevo_registro = pd.DataFrame([{
        "Fecha": str(fecha_movimiento),
        "Tipo": tipo_movimiento,
        "Categoria": categoria,
        "Detalle": detalle_limpio,
        "Metodo": metodo_pago,
        "Monto": round(float(monto), 2)
    }])

    df_actual = cargar_movimientos()
    pd.concat([df_actual, nuevo_registro], ignore_index=True).to_csv(ARCHIVO_BASE_DATOS, index=False)
    return True, "Registro guardado correctamente en la base de datos."

def calcular_resumen_financiero(df_movimientos):
    if df_movimientos.empty:
        return 0.0, 0.0, 0.0, pd.DataFrame(columns=["Categoria", "Monto", "Porcentaje (%)"])

    total_ingresos = df_movimientos[df_movimientos["Tipo"] == "Ingreso"]["Monto"].sum()
    total_egresos = df_movimientos[df_movimientos["Tipo"] == "Egreso"]["Monto"].sum()
    balance_neto = total_ingresos - total_egresos

    df_egresos = df_movimientos[df_movimientos["Tipo"] == "Egreso"]
    if df_egresos.empty:
        resumen_egresos = pd.DataFrame(columns=["Categoria", "Monto", "Porcentaje (%)"])
    else:
        resumen_egresos = df_egresos.groupby("Categoria", as_index=False)["Monto"].sum()
        resumen_egresos = resumen_egresos.sort_values(by="Monto", ascending=False)
        resumen_egresos["Porcentaje (%)"] = round((resumen_egresos["Monto"] / total_egresos) * 100, 1)

    return total_ingresos, total_egresos, balance_neto, resumen_egresos

def filtrar_movimientos(df_movimientos, tipo_filtro, categoria_filtro):
    df_filtrado = df_movimientos.copy()
    if tipo_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Tipo"] == tipo_filtro]
    if categoria_filtro != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Categoria"] == categoria_filtro]
    return df_filtrado

def configurar_interfaz():
    st.set_page_config(page_title=NOMBRE_HOSTAL, layout="wide")
    st.markdown("""
        <style>
        .stMetric {
            background-color: #1E2129;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #C84B31;
        }
        </style>
    """, unsafe_allow_html=True)
    st.title(NOMBRE_HOSTAL)
    st.caption(f"Control categorizado de gastos operativos y balance del hostal | Desarrollado por: {AUTOR_MODULO}")
    st.divider()

def renderizar_formulario_categoria(tipo_categoria, clave_form, etiqueta_expander, placeholder_texto):
    with st.expander(etiqueta_expander):
        with st.form(clave_form, clear_on_submit=True):
            nueva_categoria = st.text_input("Nombre de la nueva categoria:", placeholder=placeholder_texto)
            if st.form_submit_button(f"Agregar Categoria de {tipo_categoria}"):
                exito, mensaje = agregar_nueva_categoria(tipo_categoria, nueva_categoria)
                if exito:
                    st.success(mensaje)
                    st.rerun()
                else:
                    st.error(mensaje)

def renderizar_seccion_registro(categorias_ingresos, categorias_egresos):
    col_egresos, col_ingresos = st.columns(2)

    with col_egresos:
        st.subheader("Registrar Nuevo Egreso (Gasto)")
        with st.form("form_egreso", clear_on_submit=True):
            categoria_egr = st.selectbox("Categoria del Gasto:", categorias_egresos)
            detalle_egr = st.text_input("Descripcion del Gasto:", placeholder="Ej. Compra de focos LED o pago factura agua")
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                fecha_egr = st.date_input("Fecha del Gasto:", value=date.today(), key="fecha_egr")
                metodo_egr = st.selectbox("Metodo de Pago:", METODOS_PAGO, key="metodo_egr")
            with col_f2:
                monto_egr = st.number_input(f"Monto Gastado ({MONEDA}):", min_value=1.0, max_value=50000.0, value=50.0, step=5.0, key="monto_egr")

            if st.form_submit_button("Guardar Egreso", use_container_width=True):
                exito, mensaje = registrar_movimiento(fecha_egr, "Egreso", categoria_egr, detalle_egr, metodo_egr, monto_egr)
                if exito:
                    st.success(mensaje)
                    st.rerun()
                else:
                    st.error(mensaje)

        renderizar_formulario_categoria("Egreso", "form_nueva_cat_egr", "Aumentar nueva categoria de Egreso", "Ej. Publicidad y Redes Sociales")

    with col_ingresos:
        st.subheader("Registrar Ingreso por Habitacion")
        with st.form("form_ingreso", clear_on_submit=True):
            categoria_ing = st.selectbox("Concepto de Ingreso:", categorias_ingresos)
            detalle_ing = st.text_input("Detalle (Cuarto / Noches):", placeholder="Ej. Habitacion #2 - 2 noches")
            col_f3, col_f4 = st.columns(2)
            with col_f3:
                fecha_ing = st.date_input("Fecha de Cobro:", value=date.today(), key="fecha_ing")
                metodo_ing = st.selectbox("Metodo de Cobro:", METODOS_PAGO, key="metodo_ing")
            with col_f4:
                monto_ing = st.number_input(f"Monto Cobrado ({MONEDA}):", min_value=1.0, max_value=50000.0, value=150.0, step=10.0, key="monto_ing")

            if st.form_submit_button("Guardar Ingreso", use_container_width=True):
                exito, mensaje = registrar_movimiento(fecha_ing, "Ingreso", categoria_ing, detalle_ing, metodo_ing, monto_ing)
                if exito:
                    st.success(mensaje)
                    st.rerun()
                else:
                    st.error(mensaje)

        renderizar_formulario_categoria("Ingreso", "form_nueva_cat_ing", "Aumentar nueva categoria de Ingreso", "Ej. Alquiler de Salon o Lavanderia")

def renderizar_seccion_egresos(total_egresos, df_resumen_egresos):
    st.subheader("Desglose de Egresos por Categoria")
    if df_resumen_egresos.empty:
        st.info("Aun no existen egresos registrados.")
        return

    col_tabla, col_grafico = st.columns([1, 1])
    with col_tabla:
        st.write("**Tabla de Gastos Agrupados (Mayor a Menor)**")
        st.dataframe(df_resumen_egresos, use_container_width=True, hide_index=True)
        st.metric("Total Egresos Acumulados", f"{MONEDA} {total_egresos:,.2f}")
    with col_grafico:
        st.write("**Distribucion Visual de Gastos (Bs.)**")
        st.bar_chart(df_resumen_egresos.set_index("Categoria")["Monto"])

def renderizar_seccion_balance(df_movimientos, total_ingresos, total_egresos, balance_neto, categorias_egresos, categorias_ingresos):
    st.subheader("Balance General del Hostal")
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Ingresos Totales", f"{MONEDA} {total_ingresos:,.2f}")
    col_m2.metric("Egresos Totales (Gastos Categorizados)", f"{MONEDA} {total_egresos:,.2f}", delta="-Salidas", delta_color="inverse")
    col_m3.metric(
        "Balance Final (Ganancia Neta)",
        f"{MONEDA} {balance_neto:,.2f}",
        delta="Superavit" if balance_neto >= 0 else "Deficit"
    )

    st.divider()
    st.subheader("Historial Completo de Movimientos")

    col_filtro1, col_filtro2 = st.columns(2)
    with col_filtro1:
        filtro_tipo = st.selectbox("Filtrar por Tipo:", ["Todos", "Egreso", "Ingreso"])
    with col_filtro2:
        todas_categorias = ["Todas"] + categorias_egresos + categorias_ingresos
        filtro_categoria = st.selectbox("Filtrar por Categoria:", todas_categorias)

    df_vista = filtrar_movimientos(df_movimientos, filtro_tipo, filtro_categoria)
    st.dataframe(df_vista, use_container_width=True, hide_index=True)

    csv_bytes = df_vista.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Descargar Balance y Egresos en Excel / CSV",
        data=csv_bytes,
        file_name="balance_egresos_hostal_tarija.csv",
        mime="text/csv"
    )

def iniciar_aplicacion():
    configurar_interfaz()
    categorias_ingresos, categorias_egresos = cargar_categorias()
    df_movimientos = cargar_movimientos()
    total_ingresos, total_egresos, balance_neto, df_resumen_egresos = calcular_resumen_financiero(df_movimientos)

    tab_registro, tab_egresos, tab_balance = st.tabs([
        "Registrar Egreso o Ingreso",
        "Analisis Detallado de Egresos",
        "Balance General y Libro Diario"
    ])

    with tab_registro:
        renderizar_seccion_registro(categorias_ingresos, categorias_egresos)
    with tab_egresos:
        renderizar_seccion_egresos(total_egresos, df_resumen_egresos)
    with tab_balance:
        renderizar_seccion_balance(df_movimientos, total_ingresos, total_egresos, balance_neto, categorias_egresos, categorias_ingresos)

if __name__ == "__main__":
    iniciar_aplicacion()
