
import streamlit as st
import pandas as pd
from PIL import Image

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Calculadora Expeditados", layout="centered")

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
        body {
            background-color: #0B2341;
            color: white;
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
        .highlight-box {
            background-color: #10733f;
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
peak_tab = pd.read_excel(archivo_excel, sheet_name='PEAK_TAB')

# --- INPUT DEL USUARIO ---
km = st.number_input("Ingresa los kilómetros del viaje", min_value=1, step=1)

if st.button("Calcular"):
    try:
        st.success(f"Resultado para {km:.2f} KM")

        # --- VENTAEXT_TAB (Primero y resaltado) ---
        fila_ext = ventaext_tab.iloc[(ventaext_tab['KM'] - km).abs().argsort()[:1]].iloc[0]
        venta_ext_mxn = fila_ext['Venta MXN']
        venta_ext_usd = fila_ext['Venta USD']

        st.markdown(f"""
        <div class="highlight-box">
        <h4>▶ Venta por Km (Extendida)</h4>
        • MXN: <b>${venta_ext_mxn:,.2f}</b><br>
        • USD: <b>${venta_ext_usd:,.2f}</b>
        </div>
        """, unsafe_allow_html=True)

        # --- TABULADOR ALA ---
        if km in ala_tab['KMs'].values:
            fila_ala = ala_tab[ala_tab['KMs'] == km].iloc[0]
        else:
            fila_ala = ala_tab.iloc[(ala_tab['KMs'] - km).abs().argsort()[:1]].iloc[0]
        venta_ala_mxn = fila_ala['Venta total']
        venta_ala_usd = fila_ala['BID (USD)']

        st.markdown(f"""
        ### ▶ Tabulador ALA (Comparativa)
        • MXN: ${venta_ala_mxn:,.2f}  
        • USD: ${venta_ala_usd:,.2f}
        """)

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")

# --- SELECTOR DE RUTA DESDE PEAK_TAB ---
st.markdown("## 🧭 Selector de Ruta (Peak Tab)")

if 'Ruta' in peak_tab.columns:
    rutas = sorted(peak_tab['Ruta'].dropna().unique())
    ruta_seleccionada = st.selectbox("Selecciona una ruta", rutas)

    fila_ruta = peak_tab[peak_tab['Ruta'] == ruta_seleccionada].iloc[0]
    venta_mxn_ruta = fila_ruta['MXN']
    venta_usd_ruta = fila_ruta['USD']

    st.success(f"""### Resultado para **{ruta_seleccionada}**
- **MXN:** ${venta_mxn_ruta:,.2f}
- **USD:** ${venta_usd_ruta:,.2f}
""")
else:
    st.warning("No se encontró una columna llamada 'Ruta' en PEAK_TAB.")
