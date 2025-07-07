
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calculadora de Venta de Viajes Expeditados", layout="centered")

st.image("https://trayecto.mx/img/banner.jpeg", use_column_width=True)

st.title("Calculadora de Venta de Viajes Expeditados")

# Cargar archivo Excel
excel_path = "CAT_TAB.xlsx"
venta_extendida = pd.read_excel(excel_path, sheet_name="VENTAEXT_TAB")
ala_tab = pd.read_excel(excel_path, sheet_name="ALA_TAB")
peak_tab = pd.read_excel(excel_path, sheet_name="PEAK_TAB")

# Limpiar nombres de columnas para evitar errores por espacios
peak_tab.columns = peak_tab.columns.str.strip()

# Ingreso de kilómetros
km = st.number_input("Ingresa los kilómetros del viaje", min_value=1.0, max_value=4000.0, step=1.0)

if st.button("Calcular"):
    st.success(f"Resultado para {km:.2f} KM")

    # --- Venta por KM Extendida ---
    closest_row_ext = venta_extendida.iloc[(venta_extendida["KM"] - km).abs().argsort()[:1]]
    mxn_ext = closest_row_ext["Venta MXN"].values[0]
    usd_ext = closest_row_ext["Venta USD"].values[0]

    with st.expander("🟩 Venta por Km (Extendida)", expanded=True):
        st.markdown(f"**• MXN:** ${mxn_ext:,.2f}")
        st.markdown(f"**• USD:** ${usd_ext:,.2f}")

    # --- Tabulador ALA ---
    closest_row_ala = ala_tab.iloc[(ala_tab["KMs"] - km).abs().argsort()[:1]]
    mxn_ala = closest_row_ala["Venta total"].values[0]
    usd_ala = closest_row_ala["BID (USD)"].values[0]

    with st.expander("▶️ Tabulador ALA (Comparativa)"):
        st.markdown(f"**• MXN:** ${mxn_ala:,.2f}")
        st.markdown(f"**• USD:** ${usd_ala:,.2f}")

# --- Selector de Rutas desde PEAK_TAB ---
st.markdown("---")
st.subheader("🧭 Selector de Ruta (Peak Tab)")

if "Ruta" in peak_tab.columns:
    rutas_disponibles = peak_tab["Ruta"].dropna().unique()
    ruta_seleccionada = st.selectbox("Selecciona una ruta:", rutas_disponibles)

    if ruta_seleccionada:
        fila_ruta = peak_tab[peak_tab["Ruta"] == ruta_seleccionada].iloc[0]
        venta_mxn = fila_ruta["Venta MXN"]
        venta_usd = fila_ruta["Venta USD"]

        st.success(f"Resultado para la ruta seleccionada: **{ruta_seleccionada}**")
        st.markdown(f"**• MXN:** ${venta_mxn:,.2f}")
        st.markdown(f"**• USD:** ${venta_usd:,.2f}")
else:
    st.warning("No se encontró una columna llamada 'Ruta' en PEAK_TAB.")
