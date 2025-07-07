import streamlit as st
import pandas as pd
from PIL import Image

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Calculadora de Viajes Expeditados",
    page_icon="banner_trayecto.png",
    layout="centered"
)

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
        .resaltado {
            background-color: #157347;
            padding: 1em;
            border-radius: 10px;
            color: white;
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
venta_tab = pd.read_excel(archivo_excel, sheet_name='VENTA_TAB')
ventaext_tab = pd.read_excel(archivo_excel, sheet_name='VENTAEXT_TAB')

# --- CALCULADORA ---
km = st.number_input("Ingresa los kilómetros del viaje", min_value=1, step=1)

if st.button("Calcular"):
    try:
        st.success(f"Resultado para {km:.2f} KM")

        # --- VENTA POR RANGO ---
        fila_venta = venta_tab[venta_tab['Rangos KM'] >= km].sort_values(by='Rangos KM').head(1)
        if not fila_venta.empty:
            precio_mxn = fila_venta.iloc[0]['$/Km MXN']
            precio_usd = fila_venta.iloc[0]['$/Km USD']
        else:
            precio_mxn = venta_tab.iloc[-1]['$/Km MXN']
            precio_usd = venta_tab.iloc[-1]['$/Km USD']
        venta_rango_mxn = km * precio_mxn
        venta_rango_usd = km * precio_usd

        # --- TABULADOR ALA ---
        if km in ala_tab['KMs'].values:
            fila_ala = ala_tab[ala_tab['KMs'] == km].iloc[0]
        else:
            fila_ala = ala_tab.iloc[(ala_tab['KMs'] - km).abs().argsort()[:1]].iloc[0]
        venta_ala_mxn = fila_ala['Venta total']
        venta_ala_usd = fila_ala['BID (USD)']

        # --- VENTA POR KM (NUEVO MÓDULO) ---
        fila_ext = ventaext_tab.iloc[(ventaext_tab['KM'] - km).abs().argsort()[:1]].iloc[0]
        venta_por_km_mxn = fila_ext['Venta Por Km']
        venta_por_km_usd = fila_ext['Venta Por Km USD']

        # --- RESULTADOS ---
        st.markdown(f"""
        <div class='resaltado'>
        <h4>▶ Tabulador por Rango de KM</h4>
        • MXN: <strong>${venta_rango_mxn:,.2f}</strong><br>
        • USD: <strong>${venta_rango_usd:,.2f}</strong>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <h4>▶ Tabulador ALA</h4>
        • MXN: <strong>${venta_ala_mxn:,.2f}</strong><br>
        • USD: <strong>${venta_ala_usd:,.2f}</strong>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <h4>▶ Venta por Km (Tarifa Extendida)</h4>
        • MXN por km: <strong>${venta_por_km_mxn:,.2f}</strong><br>
        • USD por km: <strong>${venta_por_km_usd:,.2f}</strong>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
