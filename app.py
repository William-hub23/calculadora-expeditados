import streamlit as st
import pandas as pd
import math

# =========================
# CONFIG & ESTILOS
# =========================
st.set_page_config(
    page_title="Trayecto | Calculadora de Viajes Expeditados",
    page_icon="favicon.png",
    layout="centered"
)

st.markdown("""
    <style>
        header[data-testid="stHeader"] {display: none;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        body, .stApp { background-color: #ffffff; color: #0B2341; }
        h1, h2, h3, h4, h5, label { color: #0B2341 !important; font-weight: 600; }

        .stTextInput input {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 1px solid #cfd8e3 !important;
            border-radius: 6px !important;
        }
        ::placeholder { color: #0B2341 !important; opacity: 0.7 !important; }

        div.stButton > button {
            background-color: #0B2341 !important;
            color: #ffffff !important;
            border-radius: 6px !important;
        }
        div.stButton > button:hover { background-color: #13315c !important; }

        .resaltado { background-color: #107144; padding: 1em; border-radius: 10px; }
        .resaltado h3, .resaltado li { color: #ffffff !important; }

        .resultado-box {
            background-color: #0B2341;
            padding: 0.7em; border-radius: 6px; margin-bottom: 1em;
            color: #ffffff; font-weight: bold;
        }

        .info-blue {
            background-color: #0B2341; color: #ffffff;
            padding: 0.6em 0.8em; border-radius: 8px; margin-top:.6em;
        }

        .ala-box {
            background-color: #0B2341; color: #ffffff;
            padding: 0.9em 1.1em; border-radius: 8px; margin-top: 0.6em;
        }
        .ala-box h3, .ala-box li { color: #ffffff !important; }
    </style>
""", unsafe_allow_html=True)

# =========================
# LOGIN
# =========================
def login():
    st.image("banner.png", use_container_width=True)
    st.subheader("🔒 Acceso restringido")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if username == "admin" and password == "admin":
            st.session_state['authenticated'] = True
        else:
            st.error("Credenciales incorrectas")

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if not st.session_state['authenticated']:
    login()
    st.stop()

# =========================
# BANNER + TÍTULO
# =========================
st.image("banner.png", use_container_width=True)
st.markdown("<h1 style='text-align: center;'>Calculadora de Venta de Viajes Expeditados</h1>", unsafe_allow_html=True)

# =========================
# CARGA DE DATOS
# =========================
archivo_excel = 'CAT_TAB.xlsx'
ala_tab = pd.read_excel(archivo_excel, sheet_name='ALA_TAB', engine="openpyxl")
ventaext_tab = pd.read_excel(archivo_excel, sheet_name='VENTAEXT_TAB', engine="openpyxl")

# Columnas numéricas
for c in ["KMs","Venta total","BID (USD)"]:
    ala_tab[c] = pd.to_numeric(ala_tab[c], errors="coerce")
ala_tab = ala_tab.dropna(subset=["KMs","Venta total","BID (USD)"])

for c in ["KM","Millas","Venta Por Km","Venta Por Km USD","Venta MXN","Venta USD"]:
    ventaext_tab[c] = pd.to_numeric(ventaext_tab[c], errors="coerce")

# --- NUEVO: convertir "% Ganancia" como UAFIR ---
if "% Ganancia" in ventaext_tab.columns:
    ventaext_tab["UAFIR"] = ventaext_tab["% Ganancia"].astype(str).str.replace("%", "", regex=False)
    ventaext_tab["UAFIR"] = pd.to_numeric(ventaext_tab["UAFIR"], errors="coerce")

ventaext_tab = ventaext_tab.dropna(subset=["KM","Millas","Venta Por Km","Venta Por Km USD","Venta MXN","Venta USD"])

# =========================
# FUNCIONES
# =========================
def fila_mas_cercana(df, col, objetivo):
    exactos = df[df[col] == objetivo]
    if not exactos.empty:
        return exactos.iloc[0], 0.0
    idx = (df[col] - objetivo).abs().argsort().iloc[0]
    fila = df.iloc[idx]
    return fila, float(abs(fila[col] - objetivo))

def parse_float(s):
    if s is None: return None
    s = s.strip().replace(",", "")
    if s == "": return None
    try:
        x = float(s)
        if math.isfinite(x) and x >= 0: return x
    except: pass
    return None

# =========================
# FORMULARIO
# =========================
st.markdown("### Ingresar Parámetros Del Viaje")
with st.form("form_params", clear_on_submit=False):
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Ingresa los kilómetros del viaje", value=st.session_state.get("km_field",""), placeholder="Ej. 600", key="km_field")
    with c2:
        st.text_input("Ingresa las millas del viaje", value=st.session_state.get("mi_field",""), placeholder="Ej. 373", key="mi_field")
    submitted = st.form_submit_button("Calcular")

if st.button("Resetear"):
    for k in ("km_field","mi_field"):
        if k in st.session_state: del st.session_state[k]
    st.rerun()

# =========================
# CÁLCULO
# =========================
if submitted:
    km = parse_float(st.session_state.get("km_field", ""))
    mi = parse_float(st.session_state.get("mi_field", ""))
    if km is not None and mi is None: mi = km / 1.60934
    elif mi is not None and km is None: km = mi * 1.60934

    if km is None and mi is None:
        st.warning("Ingresa **KM** o **Millas** para calcular.")
        st.stop()

    st.markdown("<div class='resultado-box'>Resultado</div>", unsafe_allow_html=True)

    # ------- Tabulador por Rango (VENTAEXT) -------
    km_block = mi_block = None
    if km is not None and km > 0:
        fila_ext_km, diff_km = fila_mas_cercana(ventaext_tab, "KM", km)
        km_block = dict(
            km_ref=fila_ext_km["KM"],
            ing_km_mxn=fila_ext_km["Venta Por Km"],
            ing_km_usd=fila_ext_km["Venta Por Km USD"],
            venta_mxn=fila_ext_km["Venta MXN"],
            venta_usd=fila_ext_km["Venta USD"],
            uafir=fila_ext_km.get("UAFIR", None),
            diff=diff_km
        )
    if mi is not None and mi > 0:
        fila_ext_mi, diff_mi = fila_mas_cercana(ventaext_tab, "Millas", mi)
        mi_block = dict(
            mi_ref=fila_ext_mi["Millas"],
            ing_km_mxn=fila_ext_mi["Venta Por Km"],
            ing_km_usd=fila_ext_mi["Venta Por Km USD"],
            venta_mxn=fila_ext_mi["Venta MXN"],
            venta_usd=fila_ext_mi["Venta USD"],
            uafir=fila_ext_mi.get("UAFIR", None),
            diff=diff_mi
        )

    # Caja verde
    parts = ["<h3>▶ Tabulador Por Rango de Km</h3><ul>"]
    if km_block:
        parts += [
            f"<li><b>KM de referencia:</b> {km_block['km_ref']:,.0f}</li>",
            f"<li><b>Ing/Km MXN:</b> ${km_block['ing_km_mxn']:,.2f}</li>",
            f"<li><b>Ing/Km USD:</b> ${km_block['ing_km_usd']:,.2f}</li>",
            f"<li><b>MXN:</b> ${km_block['venta_mxn']:,.2f}</li>",
            f"<li><b>USD:</b> ${km_block['venta_usd']:,.2f}</li>",
            (f"<li><b>UAFIR:</b> {km_block['uafir']:,.0f}%</li>" if km_block['uafir'] is not None else "")
        ]
    if km_block and mi_block:
        parts += ["<hr style='border:0;border-top:1px solid rgba(255,255,255,.35);margin:.6em 0;'>"]
    if mi_block:
        parts += [
            f"<li><b>Millas de referencia:</b> {mi_block['mi_ref']:,.0f}</li>",
            f"<li><b>Ing/Km MXN:</b> ${mi_block['ing_km_mxn']:,.2f}</li>",
            f"<li><b>Ing/Km USD:</b> ${mi_block['ing_km_usd']:,.2f}</li>",
            f"<li><b>MXN:</b> ${mi_block['venta_mxn']:,.2f}</li>",
            f"<li><b>USD:</b> ${mi_block['venta_usd']:,.2f}</li>",
            (f"<li><b>UAFIR:</b> {mi_block['uafir']:,.0f}%</li>" if mi_block['uafir'] is not None else "")
        ]
    parts += ["</ul>"]
    st.markdown(f"<div class='resaltado'>{''.join(parts)}</div>", unsafe_allow_html=True)

    # Avisos azules
    if km_block and km_block["diff"] > 0:
        st.markdown(f"<div class='info-blue'>Se usó el KM más cercano: {km_block['km_ref']:,.0f}.</div>", unsafe_allow_html=True)
    if mi_block and mi_block["diff"] > 0:
        st.markdown(f"<div class='info-blue'>Se usó la milla más cercana: {mi_block['mi_ref']:,.0f}.</div>", unsafe_allow_html=True)

    # ------- Tabulador ALA -------
    if km is not None and km > 0:
        fila_ala, diff_ala = fila_mas_cercana(ala_tab, "KMs", km)
        venta_ala_mxn = fila_ala['Venta total']
        venta_ala_usd = fila_ala['BID (USD)']
        km_ref_ala    = fila_ala['KMs']

        ala_html = f"""
        <div class="ala-box">
            <h3>▶ Tabulador ALA (Comparativa)</h3>
            <ul>
                <li><b>MXN:</b> ${venta_ala_mxn:,.2f}</li>
                <li><b>USD:</b> ${venta_ala_usd:,.2f}</li>
            </ul>
        </div>
        """
        st.markdown(ala_html, unsafe_allow_html=True)
        if diff_ala > 0:
            st.markdown(f"<div class='info-blue'>Se usó el KM más cercano en ALA: {km_ref_ala:,.0f}.</div>", unsafe_allow_html=True)
