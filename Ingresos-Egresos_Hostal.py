import streamlit as st
import pandas as pd
import os
from datetime import date

NOMBRE_HOSTAL = "Hostal Familiar Tarija - Control de Egresos y Balance"
MONEDA = "Bs."
ARCHIVO_BASE_DATOS = "finanzas_hostal_tarija.csv"
ARCHIVO_CATEGORIAS = "categorias_hostal_tarija.csv"
AUTOR_MODULO = "Sebastian Espana"

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
        df_cat = pd.read_csv(ARCHIVO_CATEGORIAS)
        ing = df_cat[df_cat["Tipo"] == "Ingreso"]["Categoria"].tolist()
        egr = df_cat[df_cat["Tipo"] == "Egreso"]["Categoria"].tolist()
        return ing, egr
    
    filas = [{"Tipo": "Ingreso", "Categoria": c} for c in CATEGORIAS_INGRESOS_BASE] + \
            [{"Tipo": "Egreso", "Categoria": c} for c in CATEGORIAS_EGRESOS_BASE]
    df_inicial = pd.DataFrame(filas)
    df_inicial.to_csv(ARCHIVO_CATEGORIAS, index=False)
    return CATEGORIAS_INGRESOS_BASE.copy(), CATEGORIAS_EGRESOS_BASE.copy()

def agregar_nueva_categoria(tipo_cat, nombre_cat):
    nombre_limpio = str(nombre_cat).strip()
    if not nombre_limpio:
        return False, "Escribe un nombre para la nueva categoria."
    
    ing, egr = cargar_categorias()
    lista_actual = ing if tipo_cat == "Ingreso" else egr
    
    if nombre_limpio.lower() in [c.lower() for c in lista_actual]:
        return False, "Esa categoria ya existe en la lista."
    
    df_cat = pd.read_csv(ARCHIVO_CATEGORIAS)
    nueva_fila = pd.DataFrame([{"Tipo": tipo_cat, "Categoria": nombre_limpio}])
    df_cat = pd.concat([df_cat, nueva_fila], ignore_index=True)
    df_cat.to_csv(ARCHIVO_CATEGORIAS, index=False)
    return True, f"Categoria '{nombre_limpio}' agregada correctamente."

def inicializar_o_cargar_datos():
    if os.path.exists(ARCHIVO_BASE_DATOS):
        return pd.read_csv(ARCHIVO_BASE_DATOS)
    
    datos_iniciales = [
        {"Fecha": "2026-11-10", "Tipo": "Ingreso", "Categoria": "Alquiler de Habitaciones", "Detalle": "Habitacion Matrimonial #1 (2 noches)", "Metodo": "QR / Transferencia", "Monto": 320.0},
        {"Fecha": "2026-11-10", "Tipo": "Egreso", "Categoria": "Limpieza y Lavanderia", "Detalle": "Detergente, lavandina y suavizante", "Metodo": "Efectivo", "Monto": 85.0},
        {"Fecha": "2026-11-11", "Tipo": "Ingreso", "Categoria": "Alquiler de Habitaciones", "Detalle": "Habitacion Doble #3 (1 noche)", "Metodo": "Efectivo", "Monto": 180.0},
        {"Fecha": "2026-11-11", "Tipo": "Egreso", "Categoria": "Insumos de Cocina y Desayunos", "Detalle": "Pan, cafe, leche, huevos y frutas", "Metodo": "Efectivo", "Monto": 65.0},
        {"Fecha": "2026-11-12", "Tipo": "Egreso", "Categoria": "Servicios Basicos (Luz, Agua, Gas, Wi-Fi)", "Detalle": "Factura mensual de energia electrica", "Metodo": "QR / Transferencia", "Monto": 290.0},
        {"Fecha": "2026-11-12", "Tipo": "Egreso", "Categoria": "Mantenimiento y Reparaciones", "Detalle": "Cambio de grifo de ducha Habitacion #2", "Metodo": "Efectivo", "Monto": 110.0},
        {"Fecha": "2026-11-13", "Tipo": "Ingreso", "Categoria": "Alquiler de Habitaciones", "Detalle": "Habitacion Triple #4 (2 noches)", "Metodo": "QR / Transferencia", "Monto": 420.0},
        {"Fecha": "2026-11-13", "Tipo": "Egreso", "Categoria": "Articulos de Higiene (Amenidades)", "Detalle": "Papel higienico, jaboncillos y shampoo", "Metodo": "Efectivo", "Monto": 75.0}
    ]
    df_inicial = pd.DataFrame(datos_iniciales)
    df_inicial.to_csv(ARCHIVO_BASE_DATOS, index=False)
    return df_inicial

def registrar_movimiento(fecha_mov, tipo_mov, categoria, detalle, metodo_pago, monto):
    detalle_limpio = str(detalle).strip()
    if not detalle_limpio:
        return False, "El detalle del movimiento no puede quedar vacio."
    if monto <= 0:
        return False, "El monto debe ser mayor a 0 Bs."

    nuevo_registro = pd.DataFrame([{
        "Fecha": str(fecha_mov),
        "Tipo": tipo_mov,
        "Categoria": categoria,
        "Detalle": detalle_limpio,
        "Metodo": metodo_pago,
        "Monto": round(float(monto), 2)
    }])

    df_actual = inicializar_o_cargar_datos()
    df_actualizado = pd.concat([df_actual, nuevo_registro], ignore_index=True)
    df_actualizado.to_csv(ARCHIVO_BASE_DATOS, index=False)
    return True, "Registro guardado correctamente en la base de datos."

def calcular_balance_y_egresos(df):
    if df.empty:
        return 0.0, 0.0, 0.0, pd.DataFrame()
    
    total_ingresos = df[df["Tipo"] == "Ingreso"]["Monto"].sum()
    total_egresos = df[df["Tipo"] == "Egreso"]["Monto"].sum()
    balance_neto = total_ingresos - total_egresos

    df_egresos = df[df["Tipo"] == "Egreso"]
    if not df_egresos.empty:
        resumen_egresos = df_egresos.groupby("Categoria", as_index=False)["Monto"].sum()
        resumen_egresos = resumen_egresos.sort_values(by="Monto", ascending=False)
        resumen_egresos["Porcentaje (%)"] = round((resumen_egresos["Monto"] / total_egresos) * 100, 1)
    else:
        resumen_egresos = pd.DataFrame(columns=["Categoria", "Monto", "Porcentaje (%)"])

    return total_ingresos, total_egresos, balance_neto, resumen_egresos

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

categorias_ingresos, categorias_egresos = cargar_categorias()
df_finanzas = inicializar_o_cargar_datos()

tab_registro, tab_egresos, tab_balance = st.tabs([
    "Registrar Egreso o Ingreso",
    "Analisis Detallado de Egresos",
    "Balance General y Libro Diario"
])

with tab_registro:
    col_egr, col_ing = st.columns(2)

    with col_egr:
        st.subheader("Registrar Nuevo Egreso (Gasto)")
        with st.form("form_egreso", clear_on_submit=True):
            cat_egr = st.selectbox("Categoria del Gasto:", categorias_egresos)
            det_egr = st.text_input("Descripcion del Gasto:", placeholder="Ej. Compra de focos LED o pago factura agua")
            c1, c2 = st.columns(2)
            with c1:
                fecha_egr = st.date_input("Fecha del Gasto:", value=date.today(), key="f_egr")
                metodo_egr = st.selectbox("Metodo de Pago:", ["Efectivo", "QR / Transferencia", "Tarjeta"], key="m_egr")
            with c2:
                monto_egr = st.number_input(f"Monto Gastado ({MONEDA}):", min_value=1.0, max_value=50000.0, value=50.0, step=5.0, key="v_egr")

            btn_egr = st.form_submit_button("Guardar Egreso", use_container_width=True)
            if btn_egr:
                ok, msg = registrar_movimiento(fecha_egr, "Egreso", cat_egr, det_egr, metodo_egr, monto_egr)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        with st.expander("Aumentar nueva categoria de Egreso"):
            with st.form("form_nueva_cat_egr", clear_on_submit=True):
                nueva_cat_egr = st.text_input("Nombre de la nueva categoria de gasto:", placeholder="Ej. Publicidad y Redes Sociales")
                if st.form_submit_button("Agregar Categoria de Egreso"):
                    ok_cat, msg_cat = agregar_nueva_categoria("Egreso", nueva_cat_egr)
                    if ok_cat:
                        st.success(msg_cat)
                        st.rerun()
                    else:
                        st.error(msg_cat)

    with col_ing:
        st.subheader("Registrar Ingreso por Habitacion")
        with st.form("form_ingreso", clear_on_submit=True):
            cat_ing = st.selectbox("Concepto de Ingreso:", categorias_ingresos)
            det_ing = st.text_input("Detalle (Cuarto / Noches):", placeholder="Ej. Habitacion #2 - 2 noches")
            c3, c4 = st.columns(2)
            with c3:
                fecha_ing = st.date_input("Fecha de Cobro:", value=date.today(), key="f_ing")
                metodo_ing = st.selectbox("Metodo de Cobro:", ["Efectivo", "QR / Transferencia", "Tarjeta"], key="m_ing")
            with c4:
                monto_ing = st.number_input(f"Monto Cobrado ({MONEDA}):", min_value=1.0, max_value=50000.0, value=150.0, step=10.0, key="v_ing")

            btn_ing = st.form_submit_button("Guardar Ingreso", use_container_width=True)
            if btn_ing:
                ok, msg = registrar_movimiento(fecha_ing, "Ingreso", cat_ing, det_ing, metodo_ing, monto_ing)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        with st.expander("Aumentar nueva categoria de Ingreso"):
            with st.form("form_nueva_cat_ing", clear_on_submit=True):
                nueva_cat_ing = st.text_input("Nombre de la nueva categoria de ingreso:", placeholder="Ej. Alquiler de Salon o Lavanderia")
                if st.form_submit_button("Agregar Categoria de Ingreso"):
                    ok_cat, msg_cat = agregar_nueva_categoria("Ingreso", nueva_cat_ing)
                    if ok_cat:
                        st.success(msg_cat)
                        st.rerun()
                    else:
                        st.error(msg_cat)

with tab_egresos:
    st.subheader("Desglose de Egresos por Categoria")
    _, total_egr, _, df_resumen_egr = calcular_balance_y_egresos(df_finanzas)

    if not df_resumen_egr.empty:
        col_tabla, col_grafico = st.columns([1, 1])
        with col_tabla:
            st.write("**Tabla de Gastos Agrupados (Mayor a Menor)**")
            st.dataframe(df_resumen_egr, use_container_width=True, hide_index=True)
            st.metric("Total Egresos Acumulados", f"{MONEDA} {total_egr:,.2f}")
        with col_grafico:
            st.write("**Distribucion Visual de Gastos (Bs.)**")
            st.bar_chart(df_resumen_egr.set_index("Categoria")["Monto"])
    else:
        st.info("Aun no existen egresos registrados.")

with tab_balance:
    st.subheader("Balance General del Hostal")
    total_ing, total_egr, balance_neto, _ = calcular_balance_y_egresos(df_finanzas)

    m1, m2, m3 = st.columns(3)
    m1.metric("Ingresos Totales", f"{MONEDA} {total_ing:,.2f}")
    m2.metric("Egresos Totales (Gastos Categorizados)", f"{MONEDA} {total_egr:,.2f}", delta="-Salidas", delta_color="inverse")
    m3.metric(
        "Balance Final (Ganancia Neta)",
        f"{MONEDA} {balance_neto:,.2f}",
        delta="Superavit" if balance_neto >= 0 else "Deficit"
    )

    st.divider()
    st.subheader("Historial Completo de Movimientos")

    f1, f2 = st.columns(2)
    with f1:
        filtro_tipo = st.selectbox("Filtrar por Tipo:", ["Todos", "Egreso", "Ingreso"])
    with f2:
        todas_cats = ["Todas"] + categorias_egresos + categorias_ingresos
        filtro_cat = st.selectbox("Filtrar por Categoria:", todas_cats)

    df_vista = df_finanzas.copy()
    if filtro_tipo != "Todos":
        df_vista = df_vista[df_vista["Tipo"] == filtro_tipo]
    if filtro_cat != "Todas":
        df_vista = df_vista[df_vista["Categoria"] == filtro_cat]

    st.dataframe(df_vista, use_container_width=True, hide_index=True)

    csv_bytes = df_vista.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Descargar Balance y Egresos en Excel / CSV",
        data=csv_bytes,
        file_name="balance_egresos_hostal_tarija.csv",
        mime="text/csv"
    )
