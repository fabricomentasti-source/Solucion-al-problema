import streamlit as st
import pandas as pd
import os
from datetime import date, datetime

NOMBRE_HOSTAL = "Hostal Familiar Tarija - Control de Egresos y Balance"
MONEDA = "Bs."
ARCHIVO_BASE_DATOS = "finanzas_hostal_tarija.csv"
ARCHIVO_CATEGORIAS = "categorias_hostal_tarija.csv"
ARCHIVO_HUESPEDES = "huespedes_hostal_tarija.csv"
AUTOR_MODULO = "Sebastian Espana"

HORA_MINIMA = 8
HORA_MAXIMA = 22

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

COLUMNAS_HUESPED = [
    "Nombre",
    "Fecha de llegada",
    "Hora de llegada",
    "Fecha de salida",
    "Hora de salida",
    "Número de habitación",
    "Número de personas",
    "Garantia"
]


def CargarHuespedes():
    if os.path.exists(ARCHIVO_HUESPEDES):
        return pd.read_csv(ARCHIVO_HUESPEDES, dtype=str).fillna("").to_dict("records")
    return []


REGISTRO = CargarHuespedes()


def ValidarHoraSalida(hora_salida):
    try:
        partes = str(hora_salida).split(":")
        hora = int(partes[0])
        minutos = int(partes[1]) if len(partes) > 1 else 0
    except ValueError:
        return False, "Ingrese una hora válida (hh:mm)."

    if hora < HORA_MINIMA or hora > HORA_MAXIMA or (hora == HORA_MAXIMA and minutos > 0):
        return False, "La hora de salida no puede ser mayor que las 10:00 P.M. ni menor a las 8:00 A.M. Por favor, ingrese una hora válida."
    return True, "Hora de salida válida."


def CrearHuesped(garantia, nombre_huesped, fecha_llegada, hora_llegada, fecha_salida, hora_salida, numero_habitacion, numero_personas):
    huesped = {
        "Nombre": nombre_huesped,
        "Fecha de llegada": fecha_llegada,
        "Hora de llegada": hora_llegada,
        "Fecha de salida": fecha_salida,
        "Hora de salida": hora_salida,
        "Número de habitación": numero_habitacion,
        "Número de personas": numero_personas,
        "Garantia": garantia
    }
    return huesped


def RegistrarHuesped(huesped):
    REGISTRO.append(huesped)
    pd.DataFrame(REGISTRO, columns=COLUMNAS_HUESPED).to_csv(ARCHIVO_HUESPEDES, index=False)
    return huesped


def PedirDatos():
    with st.form("form_huesped", clear_on_submit=True):
        garantia = st.text_input("Tipo de garantía:", placeholder="Ej. Efectivo")
        nombre_huesped = st.text_input("Nombre del huésped:")
        col_h1, col_h2 = st.columns(2)
        with col_h1:
            fecha_llegada = st.date_input("Fecha de llegada:", value=date.today(), key="fecha_llegada")
            hora_llegada = st.time_input("Hora de llegada:", key="hora_llegada")
        with col_h2:
            fecha_salida = st.date_input("Fecha de salida:", value=date.today(), key="fecha_salida")
            hora_salida_ingresada = st.time_input("Hora de salida:", key="hora_salida")
        col_h3, col_h4 = st.columns(2)
        with col_h3:
            numero_habitacion = st.text_input("Número de habitación (C-X):", placeholder="Ej. C-1")
        with col_h4:
            numero_personas = st.number_input("Número de personas:", min_value=1, max_value=20, value=1, step=1)

        if st.form_submit_button("Guardar Huésped", use_container_width=True):
            hora_salida_texto = hora_salida_ingresada.strftime("%H:%M")
            valida, mensaje = ValidarHoraSalida(hora_salida_texto)

            if not nombre_huesped.strip():
                st.error("El nombre del huésped no puede quedar vacío.")
            elif not numero_habitacion.strip():
                st.error("Ingrese el número de habitación.")
            elif fecha_salida < fecha_llegada:
                st.error("La fecha de salida no puede ser anterior a la fecha de llegada.")
            elif not valida:
                st.error(mensaje)
            else:
                nuevo_huesped = CrearHuesped(
                    garantia.strip(),
                    nombre_huesped.strip(),
                    fecha_llegada.strftime("%d/%m/%Y"),
                    hora_llegada.strftime("%H:%M"),
                    fecha_salida.strftime("%d/%m/%Y"),
                    hora_salida_texto,
                    numero_habitacion.strip(),
                    str(numero_personas)
                )
                RegistrarHuesped(nuevo_huesped)
                st.success("Huésped registrado correctamente.")


def RenderizarSeccionHuespedes():
    st.subheader("Registro de Huéspedes")
    st.caption("Horario de atención: de 8:00 A.M. hasta 10:00 P.M.")
    PedirDatos()

    st.divider()
    st.subheader("Huéspedes Registrados")
    if not REGISTRO:
        st.info("Aun no existen huéspedes registrados.")
        return
    st.dataframe(pd.DataFrame(REGISTRO, columns=COLUMNAS_HUESPED), use_container_width=True, hide_index=True)


def CargarCategorias():
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


def AgregarNuevaCategoria(tipo_categoria, nombre_categoria):
    nombre_limpio = str(nombre_categoria).strip()
    if not nombre_limpio:
        return False, "Escribe un nombre para la nueva categoria."

    ingresos, egresos = CargarCategorias()
    lista_actual = ingresos if tipo_categoria == "Ingreso" else egresos

    if nombre_limpio.lower() in [cat.lower() for cat in lista_actual]:
        return False, "Esa categoria ya existe en la lista."

    df_categorias = pd.read_csv(ARCHIVO_CATEGORIAS)
    nueva_fila = pd.DataFrame([{"Tipo": tipo_categoria, "Categoria": nombre_limpio}])
    pd.concat([df_categorias, nueva_fila], ignore_index=True).to_csv(ARCHIVO_CATEGORIAS, index=False)
    return True, f"Categoria '{nombre_limpio}' agregada correctamente."


def ObtenerDatosIniciales():
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


def CargarMovimientos():
    if os.path.exists(ARCHIVO_BASE_DATOS):
        return pd.read_csv(ARCHIVO_BASE_DATOS)

    df_inicial = pd.DataFrame(ObtenerDatosIniciales())
    df_inicial.to_csv(ARCHIVO_BASE_DATOS, index=False)
    return df_inicial


def RegistrarMovimiento(fecha_movimiento, tipo_movimiento, categoria, detalle, metodo_pago, monto):
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

    df_actual = CargarMovimientos()
    pd.concat([df_actual, nuevo_registro], ignore_index=True).to_csv(ARCHIVO_BASE_DATOS, index=False)
    return True, "Registro guardado correctamente en la base de datos."


def CalcularResumenFinanciero(df_movimientos):
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


def FiltrarMovimientos(df_movimientos, tipo_filtro, categoria_filtro):
    df_filtrado = df_movimientos.copy()
    if tipo_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Tipo"] == tipo_filtro]
    if categoria_filtro != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Categoria"] == categoria_filtro]
    return df_filtrado


def ConfigurarInterfaz():
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


def RenderizarFormularioCategoria(tipo_categoria, clave_form, etiqueta_expander, placeholder_texto):
    with st.expander(etiqueta_expander):
        with st.form(clave_form, clear_on_submit=True):
            nueva_categoria = st.text_input("Nombre de la nueva categoria:", placeholder=placeholder_texto)
            if st.form_submit_button(f"Agregar Categoria de {tipo_categoria}"):
                exito, mensaje = AgregarNuevaCategoria(tipo_categoria, nueva_categoria)
                if exito:
                    st.success(mensaje)
                    st.rerun()
                else:
                    st.error(mensaje)


def RenderizarSeccionRegistro(categorias_ingresos, categorias_egresos):
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
                exito, mensaje = RegistrarMovimiento(fecha_egr, "Egreso", categoria_egr, detalle_egr, metodo_egr, monto_egr)
                if exito:
                    st.success(mensaje)
                    st.rerun()
                else:
                    st.error(mensaje)

        RenderizarFormularioCategoria("Egreso", "form_nueva_cat_egr", "Aumentar nueva categoria de Egreso", "Ej. Publicidad y Redes Sociales")

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
                exito, mensaje = RegistrarMovimiento(fecha_ing, "Ingreso", categoria_ing, detalle_ing, metodo_ing, monto_ing)
                if exito:
                    st.success(mensaje)
                    st.rerun()
                else:
                    st.error(mensaje)

        RenderizarFormularioCategoria("Ingreso", "form_nueva_cat_ing", "Aumentar nueva categoria de Ingreso", "Ej. Alquiler de Salon o Lavanderia")


def RenderizarSeccionEgresos(total_egresos, df_resumen_egresos):
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


def RenderizarSeccionBalance(df_movimientos, total_ingresos, total_egresos, balance_neto, categorias_egresos, categorias_ingresos):
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

    df_vista = FiltrarMovimientos(df_movimientos, filtro_tipo, filtro_categoria)
    st.dataframe(df_vista, use_container_width=True, hide_index=True)

    csv_bytes = df_vista.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Descargar Balance y Egresos en Excel / CSV",
        data=csv_bytes,
        file_name="balance_egresos_hostal_tarija.csv",
        mime="text/csv"
    )


def IniciarAplicacion():
    ConfigurarInterfaz()
    categorias_ingresos, categorias_egresos = CargarCategorias()
    df_movimientos = CargarMovimientos()
    total_ingresos, total_egresos, balance_neto, df_resumen_egresos = CalcularResumenFinanciero(df_movimientos)

    tab_huespedes, tab_registro, tab_egresos, tab_balance = st.tabs([
        "Registro de Huéspedes",
        "Registrar Egreso o Ingreso",
        "Analisis Detallado de Egresos",
        "Balance General y Libro Diario"
    ])

    with tab_huespedes:
        RenderizarSeccionHuespedes()
    with tab_registro:
        RenderizarSeccionRegistro(categorias_ingresos, categorias_egresos)
    with tab_egresos:
        RenderizarSeccionEgresos(total_egresos, df_resumen_egresos)
    with tab_balance:
        RenderizarSeccionBalance(df_movimientos, total_ingresos, total_egresos, balance_neto, categorias_egresos, categorias_ingresos)


IniciarAplicacion()