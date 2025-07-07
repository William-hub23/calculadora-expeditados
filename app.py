
import streamlit as st
import pandas as pd

# Configuración inicial
st.set_page_config(page_title="Calculadora de Viajes Expeditados", layout="centered")

# Autenticación básica
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
st.markdown("<h1 style='text-align: center;'>Calculadora de Venta de Viajes Expeditados</h1>", unsafe_allow_html=True)

# Input de kilómetros
km = st.number_input("Ingresa los kilómetros del viaje", min_value=1, step=1)

# Cargar Excel con tres pestañas: ALA_TAB, VENTA_TAB, VENTAEXT_TAB
archivo_excel = 'CAT_TAB.xlsx'
ala_tab = pd.read_excel(archivo_excel, sheet_name='ALA_TAB')
venta_tab = pd.read_excel(archivo_excel, sheet_name='VENTA_TAB')
venta_ext_tab = pd.read_excel(archivo_excel, sheet_name='VENTAEXT_TAB')

if st.button("Calcular"):
    try:
        # --- TABULADOR POR RANGO DE KM ---
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
        st.markdown(f"""<div style='background-color:#16794D;padding:20px;border-radius:10px;'>
        <h4 style='color:white;'>▶ Tabulador por Rango de KM</h4>
        <ul>
            <li><strong>MXN:</strong> ${venta_rango_mxn:,.2f}</li>
            <li><strong>USD:</strong> ${venta_rango_usd:,.2f}</li>
        </ul>
        </div>""", unsafe_allow_html=True)

        # --- TABULADOR ALA ---
        if km in ala_tab['KMs'].values:
            fila_ala = ala_tab[ala_tab['KMs'] == km].iloc[0]
        else:
            fila_ala = ala_tab.iloc[(ala_tab['KMs'] - km).abs().argsort()[:1]].iloc[0]
        venta_ala_mxn = fila_ala['Venta total']
        venta_ala_usd = fila_ala['BID (USD)']

        st.markdown(f"""### ▶ Tabulador ALA
        - MXN: **${venta_ala_mxn:,.2f}**
        - USD: **${venta_ala_usd:,.2f}**""")

        # --- TABULADOR VENTAEXT_TAB ---
        venta_ext_tab["KM"] = pd.to_numeric(venta_ext_tab["KM"], errors="coerce")
        fila_ext = venta_ext_tab.iloc[(venta_ext_tab["KM"] - km).abs().argsort()[:1]].iloc[0]
        venta_ext_mxn = fila_ext['Venta MXN']
        venta_ext_usd = fila_ext['Venta USD']

        st.markdown(f"""### ▶ Venta por Km (Extendida)
        - MXN: **{venta_ext_mxn}**
        - USD: **{venta_ext_usd}**""")

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
