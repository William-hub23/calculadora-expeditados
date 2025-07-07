
import streamlit as st
import pandas as pd
from PIL import Image

# Cargar el banner
banner = Image.open("banner.png")
st.image(banner, use_column_width=True)

st.title("Calculadora de Venta de Viajes Expeditados")

# Cargar los datos desde el archivo Excel
archivo = "CAT_TAB.xlsx"
ala_df = pd.read_excel(archivo, sheet_name="ALA_TAB")
peak_df = pd.read_excel(archivo, sheet_name="PEAK_TAB")
venta_ext_df = pd.read_excel(archivo, sheet_name="VENTAEXT_TAB")

# Convertir KM a número en venta_ext_df
venta_ext_df["KM"] = pd.to_numeric(venta_ext_df["KM"], errors="coerce")

# Entrada del usuario
km = st.number_input("Ingresa los kilómetros del viaje", min_value=1.0, value=1.0, step=1.0)

# Selector de Ruta desde PEAK_TAB
st.markdown("### 🧭 Selector de Ruta (Peak Tab)")
if "Ruta" in peak_df.columns:
    rutas_disponibles = peak_df["Ruta"].dropna().unique().tolist()
    ruta_seleccionada = st.selectbox("Selecciona una ruta:", rutas_disponibles)

    # Buscar la fila correspondiente
    fila_ruta = peak_df[peak_df["Ruta"] == ruta_seleccionada].squeeze()

    if not fila_ruta.empty:
        venta_mxn = fila_ruta.get("Venta MXN", None)
        venta_usd = fila_ruta.get("Venta USD", None)

        st.subheader("🔍 Resultado por Ruta Seleccionada")
        st.write(f"**Ruta:** {ruta_seleccionada}")
        if pd.notna(venta_mxn):
            st.write(f"**Venta MXN:** ${venta_mxn:,.2f}")
        else:
            st.write("**Venta MXN:** No disponible")

        if pd.notna(venta_usd):
            st.write(f"**Venta USD:** ${venta_usd:,.2f}")
        else:
            st.write("**Venta USD:** No disponible")
    else:
        st.warning("No se encontraron datos para la ruta seleccionada.")
else:
    st.warning("No se encontró una columna llamada 'Ruta' en PEAK_TAB.")

# Lógica de búsqueda por KM
fila_km = venta_ext_df.iloc[(venta_ext_df["KM"] - km).abs().argsort()[:1]].squeeze()

venta_ext_mxn = fila_km.get("Venta MXN", None)
venta_ext_usd = fila_km.get("Venta USD", None)

with st.expander("📊 Venta por Km (Extendida)", expanded=True):
    if pd.notna(venta_ext_mxn):
        st.write(f"**MXN:** ${venta_ext_mxn:,.2f}")
    else:
        st.write("**MXN:** No disponible")
    if pd.notna(venta_ext_usd):
        st.write(f"**USD:** ${venta_ext_usd:,.2f}")
    else:
        st.write("**USD:** No disponible")

# Tabulador ALA
fila_ala = ala_df.iloc[(ala_df["KM"] - km).abs().argsort()[:1]].squeeze()
ala_mxn = fila_ala.get("Venta MXN", None)
ala_usd = fila_ala.get("Venta USD", None)

with st.expander("📉 Tabulador ALA (Comparativa)"):
    if pd.notna(ala_mxn):
        st.write(f"**MXN:** ${ala_mxn:,.2f}")
    else:
        st.write("**MXN:** No disponible")
    if pd.notna(ala_usd):
        st.write(f"**USD:** ${ala_usd:,.2f}")
    else:
        st.write("**USD:** No disponible")
