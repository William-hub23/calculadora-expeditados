
import streamlit as st
import pandas as pd
import datetime

# Configuración de la página
st.set_page_config(
    page_title="Calculadora de Venta de Viajes Expeditados",
    page_icon="🚛",
    layout="centered",
    initial_sidebar_state="auto",
)

# Encabezado de la app
st.image("trayecto.png", use_container_width=True)
st.markdown("# 🚛 Calculadora de Venta de Viajes Expeditados")

# Entrada del usuario
km = st.number_input("Ingresa los kilómetros del viaje", min_value=1.0, value=60.0, step=1.0)

# Botón de cálculo
if st.button("Calcular"):
    try:
        # Tabulador ALA
        if km <= 100:
            venta_usd_ala = 175
        elif km <= 200:
            venta_usd_ala = 275
        elif km <= 300:
            venta_usd_ala = 375
        elif km <= 400:
            venta_usd_ala = 475
        elif km <= 500:
            venta_usd_ala = 575
        elif km <= 600:
            venta_usd_ala = 675
        elif km <= 700:
            venta_usd_ala = 775
        elif km <= 800:
            venta_usd_ala = 875
        elif km <= 900:
            venta_usd_ala = 975
        elif km <= 1000:
            venta_usd_ala = 1075
        else:
            venta_usd_ala = 1175 + ((km - 1000) / 100) * 100

        # Tabulador Peak
        if km <= 100:
            venta_usd_peak = 200
        elif km <= 200:
            venta_usd_peak = 300
        elif km <= 300:
            venta_usd_peak = 400
        elif km <= 400:
            venta_usd_peak = 500
        elif km <= 500:
            venta_usd_peak = 600
        elif km <= 600:
            venta_usd_peak = 700
        elif km <= 700:
            venta_usd_peak = 800
        elif km <= 800:
            venta_usd_peak = 900
        elif km <= 900:
            venta_usd_peak = 1000
        elif km <= 1000:
            venta_usd_peak = 1100
        else:
            venta_usd_peak = 1200 + ((km - 1000) / 100) * 100

        # Tabulador por KM
        if km <= 100:
            venta_usd_km = km * 2.5
        elif km <= 300:
            venta_usd_km = km * 2.2
        elif km <= 600:
            venta_usd_km = km * 2.0
        else:
            venta_usd_km = km * 1.8

        tipo_cambio = 18.0
        resultado = pd.DataFrame({
            "Tabulador": ["ALA", "PEAK", "POR_KM"],
            "USD": [round(venta_usd_ala, 2), round(venta_usd_peak, 2), round(venta_usd_km, 2)],
            "MXN": [round(venta_usd_ala * tipo_cambio, 2),
                    round(venta_usd_peak * tipo_cambio, 2),
                    round(venta_usd_km * tipo_cambio, 2)]
        })

        st.success("Tarifas calculadas correctamente")
        st.dataframe(resultado, use_container_width=True)

        # Guardar en CSV y botón de descarga
        archivo_csv = "tarifas_resultado.csv"
        resultado.to_csv(archivo_csv, index=False)
        with open(archivo_csv, "rb") as file:
            st.download_button(
                label="📥 Descargar tarifas en Excel",
                data=file,
                file_name=archivo_csv,
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"Error al calcular tarifas: {e}")

# Historial por día (estructura base)
st.markdown("## 📊 Historial de consultas por día")
try:
    historial = pd.read_csv("historial_consultas.csv")
    st.dataframe(historial, use_container_width=True)
except Exception as e:
    st.warning(f"No se pudo mostrar el historial: {e}")
