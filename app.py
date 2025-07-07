
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calculadora de Venta de Viajes Expeditados", layout="centered")

st.image("https://trayecto.app/wp-content/uploads/2023/09/trayecto-header-1024x576.jpg", use_container_width=True)

st.title("Calculadora de Venta de Viajes Expeditados")

# Cargar datos
@st.cache_data
def cargar_datos():
    xls = pd.ExcelFile("CAT_TAB.xlsx")
    ala = xls.parse("ALA_TAB")
    peak = xls.parse("PEAK_TAB")
    venta_ext = xls.parse("VENTAEXT_TAB")
    return ala, peak, venta_ext

ala_tab, peak_tab, venta_ext = cargar_datos()

# Limpiar columnas de VENTAEXT_TAB
venta_ext.columns = venta_ext.columns.str.strip()
venta_ext['KM'] = venta_ext['KM'].astype(float)

# Sección de kilómetros
st.subheader("Ingresa los kilómetros del viaje")
km = st.number_input(" ", min_value=1.0, step=1.0)

if st.button("Calcular"):
    st.success(f"Resultado para {km:.2f} KM")

    # Tarifa extendida
    venta_ext['DIF'] = (venta_ext['KM'] - km).abs()
    fila_extendida = venta_ext.loc[venta_ext['DIF'].idxmin()]
    venta_mxn_ext = fila_extendida['Venta MXN']
    venta_usd_ext = fila_extendida['Venta USD']

    with st.container():
        with st.expander("📈 Venta por Km (Extendida)", expanded=True):
            st.markdown(f"- **MXN:** ${venta_mxn_ext:,.2f}")
            st.markdown(f"- **USD:** ${venta_usd_ext:,.2f}")

    # ALA_TAB
    ala_tab['DIF'] = (ala_tab['KMs'] - km).abs()
    fila_ala = ala_tab.loc[ala_tab['DIF'].idxmin()]
    venta_mxn_ala = fila_ala['Venta total']
    venta_usd_ala = fila_ala['BID (USD)']

    with st.container():
        with st.expander("📊 Tabulador ALA (Comparativa)", expanded=True):
            st.markdown(f"- **MXN:** ${venta_mxn_ala:,.2f}")
            st.markdown(f"- **USD:** ${venta_usd_ala:,.2f}")

# Selector de ruta desde PEAK_TAB
st.markdown("---")
st.subheader("🧭 Selector de Ruta (Peak Tab)")

peak_tab.columns = peak_tab.columns.str.strip()
if "Ruta" in peak_tab.columns:
    rutas_disponibles = peak_tab["Ruta"].dropna().unique()
    ruta_seleccionada = st.selectbox("Selecciona una ruta:", rutas_disponibles)

    if ruta_seleccionada:
        fila_ruta = peak_tab[peak_tab["Ruta"] == ruta_seleccionada].iloc[0]
        venta_mxn = fila_ruta.get("Venta MXN", "N/A")
        venta_usd = fila_ruta.get("Venta USD", "N/A")

        st.write(f"**Venta MXN:** ${venta_mxn:,.2f}" if pd.notna(venta_mxn) else "Venta MXN no disponible")
        st.write(f"**Venta USD:** ${venta_usd:,.2f}" if pd.notna(venta_usd) else "Venta USD no disponible")
else:
    st.warning("No se encontró una columna llamada 'Ruta' en PEAK_TAB.")
