
import streamlit as st
import pandas as pd
from datetime import datetime
import base64

# Configuración de página
st.set_page_config(page_title="Calculadora de Venta de Viajes Expeditados", layout="centered")

# Estilos personalizados
st.markdown(
    """
    <style>
        .main {
            background-color: #0B2341;
            color: white;
        }
        .title {
            color: #FB6500;
            font-size: 48px;
            font-weight: bold;
        }
        .subtitle {
            color: #FB6500;
            font-size: 36px;
            font-weight: bold;
        }
        .stButton>button {
            background-color: #FB6500;
            color: white;
        }
        .stDownloadButton>button {
            background-color: #FB6500;
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Banner
st.image("https://trayecto.mx/wp-content/uploads/2023/07/WhatsApp-Image-2023-07-07-at-11.50.03-AM.jpeg", use_column_width=True)

st.markdown("<h1 class='title'> Calculadora de Venta de Viajes Expeditados</h1>", unsafe_allow_html=True)

# Cargar archivos
try:
    ala_tab = pd.read_excel("CAT_TAB.xlsx", sheet_name="ALA_TAB")
    peak_tab = pd.read_excel("CAT_TAB.xlsx", sheet_name="PEAK_TAB")
    venta_tab = pd.read_excel("CAT_TAB.xlsx", sheet_name="VENTA_TAB")
except Exception as e:
    st.error(f"Error al cargar archivos: {e}")
    st.stop()

# Input de kilómetros
km = st.number_input("Ingresa los kilómetros del viaje", min_value=1.0, value=60.0)

# Botón para calcular
if st.button("Calcular"):
    try:
        # ALA
        ala_row = ala_tab[ala_tab["KM"] >= km].iloc[0]
        ala_mxn = ala_row["MXN"]
        ala_usd = ala_row["USD"]

        # PEAK
        peak_row = peak_tab[peak_tab["KM"] >= km].iloc[0]
        peak_mxn = peak_row["MXN"]
        peak_usd = peak_row["USD"]

        # VENTA
        venta_row = venta_tab[venta_tab["KM"] >= km].iloc[0]
        venta_mxn = venta_row["MXN"]
        venta_usd = venta_row["USD"]

        # Mostrar resultados
        with st.expander("► Tabulador ALA"):
            st.markdown(f"- MXN: **${ala_mxn:,.2f}**")
            st.markdown(f"- USD: **${ala_usd:,.2f}**")

        with st.expander("► Tabulador Peak"):
            st.markdown(f"- MXN: **${peak_mxn:,.2f}**")
            st.markdown(f"- USD: **${peak_usd:,.2f}**")

        with st.expander("► Tabulador por Rango de KM"):
            st.markdown(f"- MXN: **${venta_mxn:,.2f}**")
            st.markdown(f"- USD: **${venta_usd:,.2f}**")

        # Guardar resultados en Excel
        resultados_df = pd.DataFrame({
            "Tipo": ["ALA", "PEAK", "Por KM"],
            "MXN": [ala_mxn, peak_mxn, venta_mxn],
            "USD": [ala_usd, peak_usd, venta_usd],
            "KM": [km, km, km],
            "Fecha": [datetime.now()] * 3
        })

        resultados_df.to_csv("historial_consultas.csv", mode='a', header=not Path("historial_consultas.csv").exists(), index=False)

        # Descargar Excel
        st.markdown("### 📥 Descargar comparativa")
        csv = resultados_df.to_csv(index=False).encode("utf-8")
        st.download_button("Descargar CSV", csv, "tarifas_calculadas.csv", "text/csv")
    except Exception as e:
        st.error(f"Error al calcular tarifas: {e}")

# Mostrar historial
st.markdown("## 📊 Historial de consultas por día")
try:
    hist = pd.read_csv("historial_consultas.csv")
    hist["Fecha"] = pd.to_datetime(hist["Fecha"])
    hist = hist.sort_values("Fecha", ascending=False)
    st.dataframe(hist, use_container_width=True)
except Exception as e:
    st.warning(f"No se pudo mostrar el historial: {e}")
