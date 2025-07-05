
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from io import BytesIO

# Configuración de la página
st.set_page_config(
    page_title="Calculadora de Venta de Viajes Expeditados",
    page_icon="🚚",
    layout="centered"
)

# Banner de inicio
st.markdown(
    "<h1 style='color:#FB6500; background-color:#0B2341; padding:20px;'>"
    "🚛 Calculadora de Venta de Viajes Expeditados</h1>",
    unsafe_allow_html=True
)
st.image("banner.png", use_container_width=True)

# Cargar archivo Excel
df_cat = pd.read_excel("CAT_TAB.xlsx", sheet_name=None)
ALA_TAB = df_cat['ALA_TAB']
PEAK_TAB = df_cat['PEAK_TAB']
VENTA_TAB = df_cat['VENTA_TAB']

# Formato de moneda
def formato_moneda(valor, moneda):
    simbolo = "$"
    if moneda == "USD":
        return f"{simbolo}{valor:,.2f}"
    else:
        return f"{simbolo}{valor:,.2f}"

# Sidebar de input
km = st.number_input("Ingresa los kilómetros del viaje", min_value=1, step=1)

# Botón para calcular
if st.button("Calcular"):
    try:
        # Tabulador ALA
        venta_ala_mxn = ALA_TAB[ALA_TAB["KM"] <= km].iloc[-1]["MXN"]
        venta_ala_usd = ALA_TAB[ALA_TAB["KM"] <= km].iloc[-1]["USD"]

        # Tabulador PEAK
        venta_peak_mxn = PEAK_TAB[PEAK_TAB["KM"] <= km].iloc[-1]["MXN"]
        venta_peak_usd = PEAK_TAB[PEAK_TAB["KM"] <= km].iloc[-1]["USD"]

        # Tabulador por Rango
        rango_tab = VENTA_TAB[
            (VENTA_TAB["KM_INICIAL"] <= km) & (VENTA_TAB["KM_FINAL"] >= km)
        ]
        if rango_tab.empty:
            raise ValueError("El kilometraje ingresado no está dentro de ningún rango.")
        venta_rango_mxn = rango_tab["MXN"].values[0]
        venta_rango_usd = rango_tab["USD"].values[0]

        # Mostrar resultados
        st.success(f"Resultado para {km:.2f} KM")

        with st.expander("► Tabulador ALA"):
            st.write("• MXN:", f"**{formato_moneda(venta_ala_mxn, 'MXN')}**")
            st.write("• USD:", f"**{formato_moneda(venta_ala_usd, 'USD')}**")

        with st.expander("► Tabulador Peak"):
            st.write("• MXN:", f"**{formato_moneda(venta_peak_mxn, 'MXN')}**")
            st.write("• USD:", f"**{formato_moneda(venta_peak_usd, 'USD')}**")

        with st.expander("► Tabulador por Rango de KM"):
            st.write("• MXN:", f"**{formato_moneda(venta_rango_mxn, 'MXN')}**")
            st.write("• USD:", f"**{formato_moneda(venta_rango_usd, 'USD')}**")

        # Descargar archivo Excel
        datos = {
            "Kilómetros": [km],
            "ALA_MXN": [venta_ala_mxn],
            "ALA_USD": [venta_ala_usd],
            "PEAK_MXN": [venta_peak_mxn],
            "PEAK_USD": [venta_peak_usd],
            "RANGO_MXN": [venta_rango_mxn],
            "RANGO_USD": [venta_rango_usd],
        }

        df_resultado = pd.DataFrame(datos)
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df_resultado.to_excel(writer, index=False, sheet_name="Tarifas")
        st.download_button(
            label="📥 Descargar tarifas en Excel",
            data=buffer.getvalue(),
            file_name=f"tarifas_{int(km)}km.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Historial de consultas por día
        hoy = datetime.now().strftime('%Y-%m-%d')
        csv_path = "historial_consultas.csv"
        if Path(csv_path).exists():
            df_hist = pd.read_csv(csv_path)
        else:
            df_hist = pd.DataFrame(columns=["fecha", "km", "ALA_MXN", "PEAK_MXN", "RANGO_MXN", "ALA_USD", "PEAK_USD", "RANGO_USD"])

        df_hist = pd.concat([df_hist, pd.DataFrame([{
            "fecha": hoy,
            "km": km,
            "ALA_MXN": venta_ala_mxn,
            "PEAK_MXN": venta_peak_mxn,
            "RANGO_MXN": venta_rango_mxn,
            "ALA_USD": venta_ala_usd,
            "PEAK_USD": venta_peak_usd,
            "RANGO_USD": venta_rango_usd
        }])], ignore_index=True)

        df_hist.to_csv(csv_path, index=False)

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")

# Gráfica diaria de historial
st.markdown("### 📊 Historial de consultas por día")
try:
    df_hist = pd.read_csv("historial_consultas.csv")
    hoy = datetime.now().strftime('%Y-%m-%d')
    df_hoy = df_hist[df_hist["fecha"] == hoy]

    if not df_hoy.empty:
        df_melted = df_hoy.melt(id_vars=["fecha", "km"], value_vars=["ALA_MXN", "PEAK_MXN", "RANGO_MXN", "ALA_USD", "PEAK_USD", "RANGO_USD"],
                                var_name="Tipo", value_name="Tarifa")
        fig = px.bar(df_melted, x="Tipo", y="Tarifa", color="Tipo", barmode="group",
                     title=f"Consultas del {hoy} (Horario centro de México)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("El historial de consultas aún no ha sido creado.")

except Exception as e:
    st.error(f"No se pudo mostrar el historial: {e}")
