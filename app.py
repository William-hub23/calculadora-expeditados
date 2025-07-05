
import streamlit as st
import pandas as pd
from PIL import Image
import streamlit as st

# Personalizar favicon
st.set_page_config(
    page_title="Calculadora de Viajes Expeditados",
    page_icon="banner_trayecto.png"
)
# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Calculadora Expeditados", layout="centered")

# --- ESTILOS PERSONALIZADOS ---
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
            background-color: #FB6500;
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
            background-color: #ffffff10;
        }
    </style>
""", unsafe_allow_html=True)

# --- AUTENTICACIÓN ---
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

# --- BANNER ---
st.image("banner.png", use_container_width=True)

# --- TÍTULO ---
st.markdown("<h1 style='text-align: center;'>Calculadora de Venta de Viajes Expeditados</h1>", unsafe_allow_html=True)

# --- CARGA DE DATOS ---
archivo_excel = 'CAT_TAB.xlsx'
ala_tab = pd.read_excel(archivo_excel, sheet_name='ALA_TAB')
peak_tab = pd.read_excel(archivo_excel, sheet_name='PEAK_TAB')
venta_tab = pd.read_excel(archivo_excel, sheet_name='VENTA_TAB')

# --- CALCULADORA ---
km = st.number_input("Ingresa los kilómetros del viaje", min_value=1, step=1)

if st.button("Calcular"):
    try:
        # ALA_TAB
        if km in ala_tab['KMs'].values:
            fila_ala = ala_tab[ala_tab['KMs'] == km].iloc[0]
        else:
            fila_ala = ala_tab.iloc[(ala_tab['KMs'] - km).abs().argsort()[:1]].iloc[0]
        venta_ala_mxn = fila_ala['Venta total']
        venta_ala_usd = fila_ala['BID (USD)']

        # PEAK_TAB
        peak_tab_valid = peak_tab[pd.to_numeric(peak_tab['Promedio KM'], errors='coerce').notna()]
        peak_tab_valid['Promedio KM'] = peak_tab_valid['Promedio KM'].astype(float)
        fila_peak = peak_tab_valid.iloc[(peak_tab_valid['Promedio KM'] - km).abs().argsort()[:1]].iloc[0]
        venta_peak_mxn = fila_peak['MXN']
        venta_peak_usd = fila_peak['USD']

        # VENTA_TAB
        fila_venta = venta_tab[venta_tab['Rangos KM'] >= km].sort_values(by='Rangos KM').head(1)
        if not fila_venta.empty:
            precio_mxn = fila_venta.iloc[0]['$/Km MXN']
            precio_usd = fila_venta.iloc[0]['$/Km USD']
        else:
            precio_mxn = venta_tab.iloc[-1]['$/Km MXN']
            precio_usd = venta_tab.iloc[-1]['$/Km USD']
        venta_rango_mxn = km * precio_mxn
        venta_rango_usd = km * precio_usd

        st.success(f"Resultado para {km:.2f} KM")
        st.markdown(f"""
        ### ▶ Tabulador ALA  
        - MXN: **${venta_ala_mxn:,.2f}**  
        - USD: **${venta_ala_usd:,.2f}**  

        ### ▶ Tabulador Peak  
        - MXN: **${venta_peak_mxn:,.2f}**  
        - USD: **${venta_peak_usd:,.2f}**  

        ### ▶ Tabulador por Rango de KM  
        - MXN: **${venta_rango_mxn:,.2f}**  
        - USD: **${venta_rango_usd:,.2f}**
        """)

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
