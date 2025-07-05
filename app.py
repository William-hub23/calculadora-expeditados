
import streamlit as st
import pandas as pd
from datetime import datetime
import base64
from io import BytesIO
import plotly.express as px

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Calculadora de Viajes Expeditados", layout="centered")

# --- BANNER CON LOGO Y FONDO PERSONALIZADO ---
st.markdown(
    f"""
    <div style="background-color:#0B2341;padding:10px;border-radius:10px">
        <img src="https://raw.githubusercontent.com/William-hub23/calculadora-expeditados/main/banner.png" style="width:100%">
    </div>
    """,
    unsafe_allow_html=True
)

# --- ENCABEZADO ---
st.markdown("<h1 style='color:#FB6500;'>ALA Calculadora de Venta Viajes Expeditados</h1>", unsafe_allow_html=True)

# --- ACCESO CON CONTRASEÑA BÁSICA ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.subheader("🔒 Acceso restringido")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if username == "admin" and password == "trayecto2025":
            st.session_state.authenticated = True
        else:
            st.error("Usuario o contraseña incorrectos")
    st.stop()

# --- CARGA DE DATOS ---
@st.cache_data
def cargar_datos():
    return pd.read_excel("CAT_TAB.xlsx", sheet_name=None)

datos_tab = cargar_datos()

# --- ENTRADA DE KILÓMETROS ---
km = st.number_input("Ingresa los kilómetros del viaje", min_value=1, value=50, step=10, format="%d")

if st.button("Calcular", use_container_width=True):
    try:
        df_ala = datos_tab["ALA"]
        df_peak = datos_tab["PEAK"]
        df_rango = datos_tab["Venta_por_km"]

        # Cálculos por tabulador
        venta_ala_mxn = float(df_ala.loc[df_ala["KM"] == km, "MXN"].values[0])
        venta_ala_usd = float(df_ala.loc[df_ala["KM"] == km, "USD"].values[0])

        venta_peak_mxn = float(df_peak.loc[df_peak["KM"] == km, "MXN"].values[0])
        venta_peak_usd = float(df_peak.loc[df_peak["KM"] == km, "USD"].values[0])

        row_rango = df_rango[(df_rango["KM_MIN"] <= km) & (df_rango["KM_MAX"] >= km)].iloc[0]
        venta_rango_mxn = km * float(row_rango["MXN_KM"])
        venta_rango_usd = km * float(row_rango["USD_KM"])

        st.success(f"Resultado para {km:.2f} KM")

        with st.expander("► Tabulador ALA", expanded=True):
            st.markdown(f"- MXN: **${venta_ala_mxn:,.2f}**")
            st.markdown(f"- USD: **${venta_ala_usd:,.2f}**")

        with st.expander("► Tabulador Peak", expanded=True):
            st.markdown(f"- MXN: **${venta_peak_mxn:,.2f}**")
            st.markdown(f"- USD: **${venta_peak_usd:,.2f}**")

        with st.expander("► Tabulador por Rango de KM", expanded=True):
            st.markdown(f"- MXN: **${venta_rango_mxn:,.2f}**")
            st.markdown(f"- USD: **${venta_rango_usd:,.2f}**")

        # --- GUARDAR CONSULTA EN CSV ---
        fecha_hora = datetime.now().astimezone().strftime("%Y-%m-%d,%H:%M:%S")
        fila = f"{fecha_hora},{km},{venta_ala_mxn},{venta_ala_usd},{venta_peak_mxn},{venta_peak_usd},{venta_rango_mxn},{venta_rango_usd}\n"
        with open("historial.csv", "a") as file:
            file.write(fila)

        # --- BOTÓN DE DESCARGA EXCEL ---
        datos = {
            "Kilómetros": [km],
            "ALA_MXN": [venta_ala_mxn],
            "ALA_USD": [venta_ala_usd],
            "PEAK_MXN": [venta_peak_mxn],
            "PEAK_USD": [venta_peak_usd],
            "RANGO_MXN": [venta_rango_mxn],
            "RANGO_USD": [venta_rango_usd],
        }
        df_resultado = pd.DataFrame(datos)
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df_resultado.to_excel(writer, index=False, sheet_name="Tarifas")

        st.download_button(
            label="📥 Descargar tarifas en Excel",
            data=output.getvalue(),
            file_name=f"tarifas_{int(km)}km.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")

# --- HISTOGRAMA DE CONSULTAS ---
st.markdown("---")
st.markdown("### 📊 Historial de consultas por día")
try:
    df_hist = pd.read_csv("historial.csv", names=[
        "fecha", "hora", "km", "ALA_MXN", "ALA_USD", "PEAK_MXN", "PEAK_USD", "RANGO_MXN", "RANGO_USD"
    ])
    hoy = datetime.now().astimezone().strftime("%Y-%m-%d")
    df_hoy = df_hist[df_hist["fecha"] == hoy]

    for tab in ["ALA", "PEAK", "RANGO"]:
        fig = px.bar(
            df_hoy,
            x="km",
            y=[f"{tab}_MXN", f"{tab}_USD"],
            barmode="group",
            labels={"value": "Venta", "km": "Kilómetros"},
            title=f"Historial de {tab} - {hoy}"
        )
        st.plotly_chart(fig, use_container_width=True)

except FileNotFoundError:
    st.warning("El historial de consultas aún no ha sido creado.")
