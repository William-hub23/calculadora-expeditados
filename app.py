
import streamlit as st
import pandas as pd
from PIL import Image

# Configuración de la página
st.set_page_config(
    page_title="Calculadora de Viajes Expeditados",
    page_icon="banner_trayecto.png",
    layout="centered"
)

# Estilos personalizados
st.markdown("""
    <style>
        body {
            background-color: #0B2341;
            color: #FB6500;
        }
        .stTextInput > div > div > input {
            background-color: #ffffff10;
            color: white;
        }
        .stButton button {
            background-color: #0B2341;
            color: white;
        }
        .stNumberInput > div {
            background-color: white;
            color: white;
        }
        h1, h2, h3, h4, h5 {
            color: white;
        }
        .stAlert {
            background-color: #0B2341;
        }
    </style>
""", unsafe_allow_html=True)

# Autenticación
def login():
    with st.form("login"):
        st.image("banner.png", use_container_width=True)
        st.subheader("🔒 Acceso restringido")
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Entrar")
        if submit:
            if username == "admin" and password == "viajes123":
                st.session_state['authenticated'] = True
            else:
                st.error("Credenciales incorrectas")

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    login()
    st.stop()

# Banner
st.image("banner.png", use_container_width=True)

# Título
st.markdown("<h1 style='text-align: center;'>Calculadora de Venta de Viajes Expeditados</h1>", unsafe_allow_html=True)

# Carga de datos
archivo_excel = 'CAT_TAB.xlsx'
ala_tab = pd.read_excel(archivo_excel, sheet_name='ALA_TAB')
venta_tab = pd.read_excel(archivo_excel, sheet_name='VENTA_TAB')
ventaext_tab = pd.read_excel(archivo_excel, sheet_name='VENTAEXT_TAB')

# Entrada de kilómetros
km = st.number_input("Ingresa los kilómetros del viaje", min_value=1, step=1)

if st.button("Calcular"):
    try:
        st.success(f"Resultado para {km:.2f} KM")

        # Tabulador por Rango de KM
        fila_venta = venta_tab[venta_tab['Rangos KM'] >= km].sort_values(by='Rangos KM').head(1)
        if not fila_venta.empty:
            precio_mxn = fila_venta.iloc[0]['$/Km MXN']
            precio_usd = fila_venta.iloc[0]['$/Km USD']
        else:
            precio_mxn = venta_tab.iloc[-1]['$/Km MXN']
            precio_usd = venta_tab.iloc[-1]['$/Km USD']
        venta_rango_mxn = km * precio_mxn
        venta_rango_usd = km * precio_usd

        with st.container():
            st.markdown("""<div style='background-color:#107849;padding:15px;border-radius:10px'>
            <h4 style='color:white;'>▶ Tabulador por Rango de KM</h4>
            <ul>
            <li><strong>MXN:</strong> ${:,.2f}</li>
            <li><strong>USD:</strong> ${:,.2f}</li>
            </ul>
            </div>""".format(venta_rango_mxn, venta_rango_usd), unsafe_allow_html=True)

        # Venta por KM Extendida
        ventaext_tab['KM'] = pd.to_numeric(ventaext_tab['KM'], errors='coerce')
        fila_ext = ventaext_tab.iloc[(ventaext_tab['KM'] - km).abs().argsort()[:1]].iloc[0]
        venta_ext_mxn = fila_ext['Venta MXN']
        venta_ext_usd = fila_ext['Venta USD']

        st.markdown("### ▶ Venta por Km (Extendida)")
        st.markdown(f"- MXN: ${venta_ext_mxn:,.2f}", unsafe_allow_html=True)
        st.markdown(f"- USD: ${venta_ext_usd:,.2f}", unsafe_allow_html=True)

        # Tabulador ALA
        if km in ala_tab['KMs'].values:
            fila_ala = ala_tab[ala_tab['KMs'] == km].iloc[0]
        else:
            fila_ala = ala_tab.iloc[(ala_tab['KMs'] - km).abs().argsort()[:1]].iloc[0]
        venta_ala_mxn = fila_ala['Venta total']
        venta_ala_usd = fila_ala['BID (USD)']

        st.markdown("### ▶ Tabulador ALA (Comparativa)")
        st.markdown(f"- MXN: ${venta_ala_mxn:,.2f}", unsafe_allow_html=True)
        st.markdown(f"- USD: ${venta_ala_usd:,.2f}", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
