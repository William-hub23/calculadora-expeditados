
import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import plotly.express as px
import os

# Configuración inicial
st.set_page_config(page_title="Calculadora Expeditados", layout="centered")

# Banner y estilos
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

st.image("banner.png", use_container_width=True)

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

st.markdown("<h1 style='color: #FB6500;'>🚚 Calculadora de Venta de Viajes Expeditados</h1>", unsafe_allow_html=True)

# Cargar archivo Excel
excel_path = "CAT_TAB.xlsx"
df_ala = pd.read_excel(excel_path, sheet_name='ALA_TAB')
df_peak = pd.read_excel(excel_path, sheet_name='PEAK_TAB')
df_rango = pd.read_excel(excel_path, sheet_name='VENTA_TAB')

# Entrada de KM
km = st.number_input("Ingresa los kilómetros del viaje", min_value=1.0, step=1.0)

if st.button("Calcular"):
    try:
        # ALA_TAB
        ala_result = df_ala[df_ala["KM"] >= km].sort_values(by="KM").head(1)
        venta_ala_mxn = ala_result["MXN"].values[0]
        venta_ala_usd = ala_result["USD"].values[0]

        # PEAK_TAB
        peak_result = df_peak[df_peak["KM"] >= km].sort_values(by="KM").head(1)
        venta_peak_mxn = peak_result["MXN"].values[0]
        venta_peak_usd = peak_result["USD"].values[0]

        # VENTA_TAB (por rango)
        rango_result = df_rango[
            (df_rango["KM_INICIAL"] <= km) & (df_rango["KM_FINAL"] >= km)
        ]
        if not rango_result.empty:
            venta_rango_mxn = rango_result["MXN"].values[0] * km
            venta_rango_usd = rango_result["USD"].values[0] * km
        else:
            venta_rango_mxn = 0
            venta_rango_usd = 0

        # Mostrar resultados
        st.success(f"Resultado para {km:.2f} KM")
        st.markdown(f"- **ALA (MXN):** ${venta_ala_mxn:,.2f}")
        st.markdown(f"- **ALA (USD):** ${venta_ala_usd:,.2f}")
        st.markdown(f"- **PEAK (MXN):** ${venta_peak_mxn:,.2f}")
        st.markdown(f"- **PEAK (USD):** ${venta_peak_usd:,.2f}")
        st.markdown(f"- **Por KM (MXN):** ${venta_rango_mxn:,.2f}")
        st.markdown(f"- **Por KM (USD):** ${venta_rango_usd:,.2f}")

        # Exportar a Excel
        df_result = pd.DataFrame({
            "KM": [km],
            "ALA_MXN": [venta_ala_mxn],
            "ALA_USD": [venta_ala_usd],
            "PEAK_MXN": [venta_peak_mxn],
            "PEAK_USD": [venta_peak_usd],
            "RANGO_MXN": [venta_rango_mxn],
            "RANGO_USD": [venta_rango_usd],
        })

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_result.to_excel(writer, index=False, sheet_name='Tarifas')
        output.seek(0)

        st.download_button(
            label="📥 Descargar tarifas en Excel",
            data=output,
            file_name=f"tarifas_{int(km)}km.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Guardar en historial
        now = datetime.now()
        hoy = now.strftime("%Y-%m-%d")
        hora = now.strftime("%H:%M:%S")
        historial_path = "historial_consultas.csv"

        if os.path.exists(historial_path):
            df_hist = pd.read_csv(historial_path)
        else:
            df_hist = pd.DataFrame(columns=["fecha", "hora", "KM", "ALA_MXN", "ALA_USD", "PEAK_MXN", "PEAK_USD", "RANGO_MXN", "RANGO_USD"])

        nueva_fila = {
            "fecha": hoy, "hora": hora, "KM": km,
            "ALA_MXN": venta_ala_mxn, "ALA_USD": venta_ala_usd,
            "PEAK_MXN": venta_peak_mxn, "PEAK_USD": venta_peak_usd,
            "RANGO_MXN": venta_rango_mxn, "RANGO_USD": venta_rango_usd
        }
        df_hist = pd.concat([df_hist, pd.DataFrame([nueva_fila])], ignore_index=True)
        df_hist.to_csv(historial_path, index=False)

    except Exception as e:
        st.error(f"Error al calcular tarifas: {e}")

# Mostrar gráficas diarias si existe historial
if os.path.exists("historial_consultas.csv"):
    st.markdown("### 📊 Historial de consultas (hoy)")
    df_hist = pd.read_csv("historial_consultas.csv")
    hoy = datetime.now().strftime("%Y-%m-%d")
    df_hoy = df_hist[df_hist["fecha"] == hoy]

    if not df_hoy.empty:
        for tab in ["ALA", "PEAK", "RANGO"]:
            df_plot = df_hoy[["hora", f"{tab}_MXN", f"{tab}_USD"]].copy()
            df_plot = df_plot.melt(id_vars="hora", var_name="Moneda", value_name="Valor")
            fig = px.bar(df_plot, x="hora", y="Valor", color="Moneda", barmode="group",
                         title=f"{tab} - Tarifas consultadas hoy")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aún no hay consultas registradas para hoy.")
