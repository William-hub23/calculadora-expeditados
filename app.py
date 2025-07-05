
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import requests
from datetime import datetime
import pytz

# Configuración inicial
st.set_page_config(page_title="Calculadora de Venta de Viajes Expeditados", layout="centered")

# Estilos
st.markdown(
    '''
    <style>
    .main {
        background-color: #0B2341;
        color: white;
    }
    .stTextInput > div > div > input {
        color: white !important;
    }
    </style>
    ''',
    unsafe_allow_html=True
)

# Banner
st.image("banner.png", use_column_width=True)

# Autenticación simple
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Acceso restringido")
    user = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if user == "admin" and pwd == "admin":
            st.session_state.authenticated = True
        else:
            st.error("Credenciales incorrectas")
    st.stop()

# Título principal
st.markdown("<h1 style='color: #FB6500;'>🚚 Calculadora de Venta de Viajes Expeditados</h1>", unsafe_allow_html=True)

# Cargar archivo Excel desde el repositorio
url_excel = "https://raw.githubusercontent.com/William-hub23/calculadora-expeditados/main/CAT_TAB.xlsx"
response = requests.get(url_excel)
excel_data = BytesIO(response.content)

try:
    df_ala = pd.read_excel(excel_data, sheet_name='ALA_TAB')
    df_peak = pd.read_excel(excel_data, sheet_name='PEAK_TAB')
    df_rango = pd.read_excel(excel_data, sheet_name='VENTA_TAB')

    km = st.number_input("Ingresa los kilómetros del viaje", min_value=1.0, step=1.0)

    if st.button("Calcular"):
        # Cálculo por ALA
        df_ala_filtrado = df_ala[df_ala['KM'] >= km].sort_values(by='KM').head(1)
        venta_ala_mxn = df_ala_filtrado['MXN'].values[0]
        venta_ala_usd = df_ala_filtrado['USD'].values[0]

        # Cálculo por PEAK
        df_peak_filtrado = df_peak[df_peak['KM'] >= km].sort_values(by='KM').head(1)
        venta_peak_mxn = df_peak_filtrado['MXN'].values[0]
        venta_peak_usd = df_peak_filtrado['USD'].values[0]

        # Cálculo por RANGO
        df_rango_filtrado = df_rango[
            (df_rango['KM_MIN'] <= km) & (df_rango['KM_MAX'] >= km)
        ]
        if not df_rango_filtrado.empty:
            venta_rango_mxn = df_rango_filtrado['MXN'].values[0] * km
            venta_rango_usd = df_rango_filtrado['USD'].values[0] * km
        else:
            venta_rango_mxn = 0
            venta_rango_usd = 0

        # Mostrar resultados
        st.success(f"Resultado para {km:.2f} KM")
        with st.expander("► Tabulador ALA"):
            st.markdown(f"- **MXN:** ${venta_ala_mxn:,.2f}")
            st.markdown(f"- **USD:** ${venta_ala_usd:,.2f}")
        with st.expander("► Tabulador Peak"):
            st.markdown(f"- **MXN:** ${venta_peak_mxn:,.2f}")
            st.markdown(f"- **USD:** ${venta_peak_usd:,.2f}")
        with st.expander("► Tabulador por Rango de KM"):
            st.markdown(f"- **MXN:** ${venta_rango_mxn:,.2f}")
            st.markdown(f"- **USD:** ${venta_rango_usd:,.2f}")

        # Botón para exportar a Excel
        datos = {
            'Kilómetros': [km],
            'ALA_MXN': [venta_ala_mxn],
            'ALA_USD': [venta_ala_usd],
            'PEAK_MXN': [venta_peak_mxn],
            'PEAK_USD': [venta_peak_usd],
            'RANGO_MXN': [venta_rango_mxn],
            'RANGO_USD': [venta_rango_usd],
        }
        df_resultado = pd.DataFrame(datos)

        st.download_button(
            label="📥 Descargar tarifas en Excel",
            data=df_resultado.to_csv(index=False).encode('utf-8'),
            file_name=f"tarifas_{int(km)}km.csv",
            mime="text/csv"
        )

except Exception as e:
    st.error(f"Ocurrió un error: {e}")
