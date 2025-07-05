
import streamlit as st
import pandas as pd

# Cargar archivo
archivo_excel = 'CAT_TAB.xlsx'
ala_tab = pd.read_excel(archivo_excel, sheet_name='ALA_TAB')
peak_tab = pd.read_excel(archivo_excel, sheet_name='PEAK_TAB')
venta_tab = pd.read_excel(archivo_excel, sheet_name='VENTA_TAB')

st.title("🚚 Calculadora de Venta de Viajes Expeditados")

km = st.number_input("Ingresa los kilómetros del viaje", min_value=1, step=1)

if st.button("Calcular"):
    try:
        # ALA_TAB
        if km in ala_tab['KMs'].values:
            fila_ala = ala_tab[ala_tab['KMs'] == km].iloc[0]
        else:
            fila_ala = ala_tab.iloc[(ala_tab['KMs'] - km).abs().argsort()[:1]].iloc[0]
        venta_ala_mxn = fila_ala['Venta total']
        venta_ala_usd = fila_ala['BID (USD)']

        # PEAK_TAB
        peak_tab_valid = peak_tab[pd.to_numeric(peak_tab['Promedio KM'], errors='coerce').notna()]
        peak_tab_valid['Promedio KM'] = peak_tab_valid['Promedio KM'].astype(float)
        fila_peak = peak_tab_valid.iloc[(peak_tab_valid['Promedio KM'] - km).abs().argsort()[:1]].iloc[0]
        venta_peak_mxn = fila_peak['MXN']
        venta_peak_usd = fila_peak['USD']

        # VENTA_TAB
        fila_venta = venta_tab[venta_tab['Rangos KM'] >= km].sort_values(by='Rangos KM').head(1)
        if not fila_venta.empty:
            precio_mxn = fila_venta.iloc[0]['$/Km MXN']
            precio_usd = fila_venta.iloc[0]['$/Km USD']
        else:
            precio_mxn = venta_tab.iloc[-1]['$/Km MXN']
            precio_usd = venta_tab.iloc[-1]['$/Km USD']
        venta_rango_mxn = km * precio_mxn
        venta_rango_usd = km * precio_usd

        st.success(f"Resultado para {km:.2f} KM")
        st.markdown(f"""
        ### ▶ Tabulador ALA  
        - MXN: **${venta_ala_mxn:,.2f}**  
        - USD: **${venta_ala_usd:,.2f}**  

        ### ▶ Tabulador Peak  
        - MXN: **${venta_peak_mxn:,.2f}**  
        - USD: **${venta_peak_usd:,.2f}**  

        ### ▶ Tabulador por Rango de KM  
        - MXN: **${venta_rango_mxn:,.2f}**  
        - USD: **${venta_rango_usd:,.2f}**
        """)

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
