
import pandas as pd
import streamlit as st
from PIL import Image

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Calculadora de Viajes Expeditados", page_icon="banner_trayecto.png", layout="centered")

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
venta_ext = pd.read_excel(archivo_excel, sheet_name='VENTAEXT_TAB')

# Normalizar nombres de columnas (quita espacios)
peak_tab.columns = peak_tab.columns.str.strip()

# --- CALCULADORA ---
km = st.number_input("Ingresa los kilómetros del viaje", min_value=1.0, step=1.0)

if st.button("Calcular"):
    try:
        st.success(f"Resultado para {km:.2f} KM")

        # --- VENTAEXT_TAB (Extendida)
        venta_ext['KM'] = venta_ext['KM'].astype(float)
        fila_ext = venta_ext.iloc[(venta_ext['KM'] - km).abs().argsort()[:1]].iloc[0]
        venta_ext_mxn = fila_ext['Venta MXN']
        venta_ext_usd = fila_ext['Venta USD']

        with st.expander("📗 Venta por Km (Extendida)", expanded=True):
            st.markdown(f"- **MXN:** ${venta_ext_mxn:,.2f}")
            st.markdown(f"- **USD:** ${venta_ext_usd:,.2f}")

        # --- ALA_TAB
        if km in ala_tab['KMs'].values:
            fila_ala = ala_tab[ala_tab['KMs'] == km].iloc[0]
        else:
            fila_ala = ala_tab.iloc[(ala_tab['KMs'] - km).abs().argsort()[:1]].iloc[0]
        venta_ala_mxn = fila_ala['Venta total']
        venta_ala_usd = fila_ala['BID (USD)']

        with st.expander("📘 Tabulador ALA (Comparativa)"):
            st.markdown(f"- **MXN:** ${venta_ala_mxn:,.2f}")
            st.markdown(f"- **USD:** ${venta_ala_usd:,.2f}")

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")

# --- SELECTOR DE RUTA DESDE PEAK_TAB ---
st.markdown("---")
st.markdown("### 🧭 Selector de Ruta (Peak Tab)")

if 'Ruta' in peak_tab.columns:
    ruta_seleccionada = st.selectbox("Selecciona una ruta:", peak_tab['Ruta'].dropna().unique())

    if ruta_seleccionada:
        fila_ruta = peak_tab[peak_tab['Ruta'] == ruta_seleccionada].iloc[0]

        try:
            venta_mxn = fila_ruta["MXN"]
            venta_usd = fila_ruta["USD"]
            st.success(f"Tarifa para la ruta seleccionada:")
            st.markdown(f"- **MXN:** ${venta_mxn:,.2f}")
            st.markdown(f"- **USD:** ${venta_usd:,.2f}")
        except KeyError as e:
            st.error(f"No se encontró alguna de las columnas necesarias: {e}")
else:
    st.warning("No se encontró una columna llamada 'Ruta' en PEAK_TAB.")
