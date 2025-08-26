import streamlit as st
import pandas as pd
import math

# =========================
# CONFIG & ESTILOS
# =========================
st.set_page_config(page_title="Calculadora de Viajes Expeditados", layout="centered")
st.markdown("""
    <style>
        /* Ocultar barra superior de Streamlit */
        header[data-testid="stHeader"] {display: none;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        body, .stApp { background-color: #ffffff; color: #0B2341; }
        h1, h2, h3, h4, h5, label { color: #0B2341 !important; font-weight: 600; }

        .stTextInput input, input[type="text"], input[type="number"] {
            background-color: #ffffff !important;
            color: #000000 !important;
            caret-color: #000000 !important;
            border: 1px solid #cfd8e3 !important;
            border-radius: 6px !important;
        }
        ::placeholder { color: #0B2341 !important; opacity: 0.7 !important; }
        ::selection { background: #e6f0ff; color: #000; }
        input::selection, textarea::selection { background: #e6f0ff; color: #000; }

        div.stButton > button,
        div.stFormSubmitButton > button,
        .stButton button,
        .stForm button {
            background-color: #0B2341 !important;
            color: #ffffff !important;
            border: 1px solid #0B2341 !important;
            border-radius: 6px !important;
            opacity: 1 !important;
            box-shadow: none !important;
        }
        div.stButton > button:hover,
        div.stFormSubmitButton > button:hover { background-color: #13315c !important; }

        .resaltado {
            background-color: #107144;
            padding: 1em; border-radius: 10px;
        }
        .resaltado h3 { color: #ffffff !important; }
        .resaltado li { color: #ffffff !important; }

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
        .ala-box h3, .ala-box li, .ala-box p { color: #ffffff !important; }

        .block-container { padding-top: 1rem; }
        .banner-space { margin-bottom: 12px; }
    </style>
""", unsafe_allow_html=True)

# =========================
# LOGIN
# =========================
def login():
    st.image("banner.png", use_container_width=True)  # Banner completo también en login
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
st.image("banner.png", use_container_width=True)  # Banner completo en la app principal
st.markdown("<h1 style='text-align: center;'>Calculadora de Venta de Viajes Expeditados</h1>", unsafe_allow_html=True)

# =========================
# CARGA DE DATOS
# =========================
archivo_excel = 'CAT_TAB.xlsx'
ala_tab = pd.read_excel(archivo_excel, sheet_name='ALA_TAB', engine="openpyxl")
ventaext_tab = pd.read_excel(archivo_excel, sheet_name='VENTAEXT_TAB', engine="openpyxl")

def to_num(s): return pd.to_numeric(s, errors="coerce")
for c in ["KMs","Venta total","BID (USD)"]:
    ala_tab[c] = to_num(ala_tab[c])
ala_tab = ala_tab.dropna(subset=["KMs","Venta total","BID (USD)"])

for c in ["KM","Millas","Venta Por Km","Venta Por Km USD","Venta MXN","Venta USD"]:
    ventaext_tab[c] = to_num(ventaext_tab[c])
ventaext_tab = ventaext_tab.dropna(subset=["KM","Millas","Venta Por Km","Venta Por Km USD","Venta MXN","Venta USD"])

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
# ESTADO INICIAL
# =========================
st.session_state.setdefault("km_field", "")
st.session_state.setdefault("mi_field", "")

# =========================
# FORMULARIO
# =========================
st.markdown("### Ingresar Parámetros Del Viaje")

with st.form("form_params", clear_on_submit=False):
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Ingresa los kilómetros del viaje",
                      value=st.session_state.km_field, placeholder="Ej. 600", key="km_field")
    with c2:
        st.text_input("Ingresa las millas del viaje",
                      value=st.session_state.mi_field, placeholder="Ej. 373", key="mi_field")
    submitted = st.form_submit_button("Calcular")

if st.button("Resetear", key="reset_btn"):
    for k in ("km_field", "mi_field"):
        if k in st.session_state: del st.session_state[k]
    st.rerun()

# =========================
# CÁLCULO
# =========================
if submitted:
    try:
        km = parse_float(st.session_state.get("km_field", ""))
        mi = parse_float(st.session_state.get("mi_field", ""))

        if km is not None and mi is None:
            mi = km / 1.60934
        elif mi is not None and km is None:
            km = mi * 1.60934

        if km is None and mi is None:
            st.warning("Ingresa **KM** o **Millas** para calcular.")
            st.stop()

        st.markdown(f"<div class='resultado-box'>Resultado</div>", unsafe_allow_html=True)

        km_block = mi_block = None
        if km is not None and km > 0:
            fila_ext_km, diff_km = fila_mas_cercana(ventaext_tab, "KM", km)
            km_block = dict(
                km_ref=float(fila_ext_km["KM"]),
                ing_km_mxn=float(fila_ext_km["Venta Por Km"]),
                ing_km_usd=float(fila_ext_km["Venta Por Km USD"]),
                venta_mxn=float(fila_ext_km["Venta MXN"]),
                venta_usd=float(fila_ext_km["Venta USD"]),
                diff=diff_km
            )
        if mi is not None and mi > 0:
            fila_ext_mi, diff_mi = fila_mas_cercana(ventaext_tab, "Millas", mi)
            mi_block = dict(
                mi_ref=float(fila_ext_mi["Millas"]),
                ing_km_mxn=float(fila_ext_mi["Venta Por Km"]),
                ing_km_usd=float(fila_ext_mi["Venta Por Km USD"]),
                venta_mxn=float(fila_ext_mi["Venta MXN"]),
                venta_usd=float(fila_ext_mi["Venta USD"]),
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
            ]
        parts += ["</ul>"]
        st.markdown(f"<div class='resaltado'>{''.join(parts)}</div>", unsafe_allow_html=True)

        # Avisos azules
        if km_block and km_block["diff"] > 0:
            st.markdown(f"<div class='info-blue'>Se usó el KM más cercano: {km_block['km_ref']:,.0f}.</div>", unsafe_allow_html=True)
        if mi_block and mi_block["diff"] > 0:
            st.markdown(f"<div class='info-blue'>Se usó la milla más cercana: {mi_block['mi_ref']:,.0f}.</div>", unsafe_allow_html=True)

        # Tabulador ALA
        if km is not None and km > 0:
            fila_ala, diff_ala = fila_mas_cercana(ala_tab, "KMs", km)
            venta_ala_mxn = float(fila_ala['Venta total'])
            venta_ala_usd = float(fila_ala['BID (USD)'])
            km_ref_ala    = float(fila_ala['KMs'])

            ala_html = f"""
            <div class="ala-box">
                <h3>▶ Tabulador ALA (Comparativa)</h3>
                <ul style="margin:0 0 0.2em 1em;">
                    <li><b>MXN:</b> ${venta_ala_mxn:,.2f}</li>
                    <li><b>USD:</b> ${venta_ala_usd:,.2f}</li>
                </ul>
            </div>
            """
            st.markdown(ala_html, unsafe_allow_html=True)

            if diff_ala > 0:
                st.markdown(f"<div class='info-blue'>Se usó el KM más cercano en ALA: {km_ref_ala:,.0f}.</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")


