
import streamlit as st
import pandas as pd
from PIL import Image

# Configuración de página
st.set_page_config(page_title="Calculadora de Viajes Expeditados", layout="centered")

# Estilos personalizados
st.markdown("""
    <style>
        body {
            background-color: #0B2341;
            color: #FB6500;
        }
        .stTextInput > div > div > input {
            background-color: white;
            color: black;
        }
        .stButton button {
            background-color: #0B2341;
            color: white;
        }
        .stNumberInput > div {
            background-color: white;
            color: black;
        }
        h1, h2, h3, h4, h5 {
            color: white;
        }
        .stAlert {
            background-color: #0B2341;
        }
        .resaltado {
            background-color: #107144;
            padding: 1em;
            border-radius: 10px;
            color: white;
        }
        .resultado-box {
            background-color: #0F2D3F;
            padding: 0.7em;
            border-radius: 6px;
            margin-bottom: 1em;
            color: white;
            font-weight: bold;
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
ventaext_tab = pd.read_excel(archivo_excel, sheet_name='VENTAEXT_TAB')

# Entrada de KM
km = st.number_input("Ingresa los kilómetros del viaje", min_value=1, step=1)

if st.button("Calcular"):
    try:
        st.markdown(f"<div class='resultado-box'>Resultado para {km:.2f} KM</div>", unsafe_allow_html=True)

        # VENTA POR KM (EXTENDIDA)
        ventaext_tab['KM'] = ventaext_tab['KM'].astype(float)
        fila_ext = ventaext_tab.iloc[(ventaext_tab['KM'] - km).abs().argsort()[:1]].iloc[0]
        venta_ext_mxn = fila_ext['Venta MXN']
        venta_ext_usd = fila_ext['Venta USD']

        st.markdown(f"""<div class='resaltado'>
        <h3>▶ Venta por Km (Extendida)</h3>
        <ul>
            <li><b>MXN:</b> ${venta_ext_mxn:,.2f}</li>
            <li><b>USD:</b> ${venta_ext_usd:,.2f}</li>
        </ul>
        </div>""", unsafe_allow_html=True)

        # TABULADOR ALA
        if km in ala_tab['KMs'].values:
            fila_ala = ala_tab[ala_tab['KMs'] == km].iloc[0]
        else:
            fila_ala = ala_tab.iloc[(ala_tab['KMs'] - km).abs().argsort()[:1]].iloc[0]
        venta_ala_mxn = fila_ala['Venta total']
        venta_ala_usd = fila_ala['BID (USD)']

        st.markdown(f"""### ▶ Tabulador ALA (Comparativa)
        - MXN: ${venta_ala_mxn:,.2f}
        - USD: ${venta_ala_usd:,.2f}
        """)

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
