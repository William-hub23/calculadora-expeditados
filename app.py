
import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")

# Título
st.image("https://i.imgur.com/kA0jF9N.png", use_column_width=True)
st.title("Calculadora de Venta de Viajes Expeditados")

# Cargar archivo Excel
archivo = "CAT_TAB.xlsx"
if not os.path.exists(archivo):
    st.error(f"No se encontró el archivo {archivo} en el directorio actual.")
    st.stop()

xls = pd.ExcelFile(archivo)

# Venta por KM Extendida
venta_ext = pd.read_excel(xls, sheet_name="Venta_por_km")
venta_ext["KM"] = venta_ext["KM"].astype(float)

# PEAK_TAB para el selector
try:
    peak_tab = pd.read_excel(xls, sheet_name="PEAK_TAB")
    if "Ruta" not in peak_tab.columns:
        st.warning("No se encontró una columna llamada 'Ruta' en PEAK_TAB.")
        peak_tab = None
except:
    st.warning("No se pudo leer la hoja PEAK_TAB.")
    peak_tab = None

# Sección de entrada de kilómetros
km = st.number_input("Ingresa los kilómetros del viaje", min_value=1.0, step=1.0)

if st.button("Calcular"):
    st.success(f"Resultado para {km:.2f} KM")

    # Cálculo por Venta Extendida
    closest_row = venta_ext.iloc[(venta_ext["KM"] - km).abs().argsort()[:1]]
    venta_mxn_ext = closest_row["Venta MXN"].values[0]
    venta_usd_ext = closest_row["Venta USD"].values[0]

    with st.expander("📊 Venta por Km (Extendida)", expanded=True):
        st.write(f"**MXN:** ${venta_mxn_ext:,.2f}")
        st.write(f"**USD:** ${venta_usd_ext:,.2f}")

    # Tabulador ALA
    costo_fijo_usd = 300
    costo_variable_usd = km * 3.75
    total_usd = costo_fijo_usd + costo_variable_usd
    total_mxn = total_usd * 19

    with st.expander("📉 Tabulador ALA (Comparativa)", expanded=True):
        st.write(f"**MXN:** ${total_mxn:,.2f}")
        st.write(f"**USD:** ${total_usd:,.2f}")

st.markdown("---")

# Selector de Ruta PEAK_TAB
if peak_tab is not None:
    st.subheader("🧭 Selector de Ruta (Peak Tab)")
    ruta_sel = st.selectbox("Selecciona una ruta:", options=peak_tab["Ruta"].dropna().unique())

    fila_ruta = peak_tab[peak_tab["Ruta"] == ruta_sel]

    if not fila_ruta.empty:
        venta_mxn = fila_ruta["MXN"].values[0]
        venta_usd = fila_ruta["USD"].values[0]
        st.success("Resultado por ruta seleccionada:")
        st.write(f"**Venta MXN:** ${venta_mxn:,.2f}")
        st.write(f"**Venta USD:** ${venta_usd:,.2f}")
    else:
        st.error("No se encontró información para la ruta seleccionada.")
