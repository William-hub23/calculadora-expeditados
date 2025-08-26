import streamlit as st
import pandas as pd

# =========================
# CONFIG & ESTILOS (igual que antes)
# =========================
st.set_page_config(page_title="Calculadora de Viajes Expeditados", layout="centered")
st.markdown("""
    <style>
        body { background-color: #0B2341; color: #FB6500; }
        .stApp { background-color: #0B2341; }
        .stTextInput > div > div > input,
        .stNumberInput > div > input {
            background-color: white; color: black;
        }
        .stButton button { background-color: #0B2341; color: white; }
        h1, h2, h3, h4, h5 { color: white; }
        .resaltado {
            background-color: #107144; padding: 1em; border-radius: 10px; color: white;
        }
        .resultado-box {
            background-color: #0F2D3F; padding: 0.7em; border-radius: 6px; margin-bottom: 1em; color: white; font-weight: bold;
        }
        .warn-box {
            background-color: #5a2e0e; padding: 0.6em; border-radius: 6px; color: #ffd7b3; margin-top:.5em;
        }
    </style>
""", unsafe_allow_html=True)

# =========================
# BANNER + TÍTULO (igual)
# =========================
try:
    st.image("banner.png", use_container_width=True)
except Exception:
    pass

st.markdown("<h1 style='text-align: center;'>Calculadora de Venta de Viajes Expeditados</h1>", unsafe_allow_html=True)

# =========================
# CARGA DE DATOS (simple, igual)
# =========================
archivo_excel = 'CAT_TAB.xlsx'
ala_tab = pd.read_excel(archivo_excel, sheet_name='ALA_TAB', engine="openpyxl")
ventaext_tab = pd.read_excel(archivo_excel, sheet_name='VENTAEXT_TAB', engine="openpyxl")

# Validaciones mínimas
def num(s): return pd.to_numeric(s, errors="coerce")
for c in ["KMs","Venta total","BID (USD)"]:
    ala_tab[c] = num(ala_tab[c])
ala_tab = ala_tab.dropna(subset=["KMs","Venta total","BID (USD)"])

for c in ["KM","Millas","Venta Por Km","Venta Por Km USD","Venta MXN","Venta USD"]:
    ventaext_tab[c] = num(ventaext_tab[c])
ventaext_tab = ventaext_tab.dropna(subset=["KM","Millas","Venta Por Km","Venta Por Km USD","Venta MXN","Venta USD"])

def fila_mas_cercana(df, col, objetivo):
    exactos = df[df[col] == objetivo]
    if not exactos.empty:
        return exactos.iloc[0], 0.0
    idx = (df[col] - objetivo).abs().argsort().iloc[0]
    fila = df.iloc[idx]
    return fila, float(abs(fila[col] - objetivo))

# =========================
# ENTRADAS (dos columnas pero mismo estilo visual)
# =========================
c1, c2 = st.columns(2)
with c1:
    km = st.number_input("Ingresa los kilómetros del viaje", min_value=0.0, step=1.0, value=0.0)
with c2:
    mi = st.number_input("Ingresa las millas del viaje", min_value=0.0, step=1.0, value=0.0)

# Conversión automática (sin cambiar lo que sí escribas)
if km > 0 and mi == 0:
    mi = km / 1.60934
elif mi > 0 and km == 0:
    km = mi * 1.60934

margen = st.number_input("Margen de aviso para 'valor más cercano' (km/millas)", min_value=0, value=10, step=1)

if st.button("Calcular"):
    try:
        st.markdown(f"<div class='resultado-box'>Resultado</div>", unsafe_allow_html=True)

        # =========================
        # TABULADOR POR RANGO (VENTAEXT) — MANTENIENDO LA CAJA VERDE
        # =========================
        # — Por KM (si hay km calculado)
        if km > 0:
            fila_ext_km, diff_km = fila_mas_cercana(ventaext_tab, "KM", km)
            venta_ext_mxn = float(fila_ext_km["Venta MXN"])
            venta_ext_usd = float(fila_ext_km["Venta USD"])
            ing_km_mxn   = float(fila_ext_km["Venta Por Km"])
            ing_km_usd   = float(fila_ext_km["Venta Por Km USD"])
            km_ref       = float(fila_ext_km["KM"])

        # — Por Millas (si hay millas calculadas)
        if mi > 0:
            fila_ext_mi, diff_mi = fila_mas_cercana(ventaext_tab, "Millas", mi)
            venta_ext_mxn_mi = float(fila_ext_mi["Venta MXN"])
            venta_ext_usd_mi = float(fila_ext_mi["Venta USD"])
            ing_mi_mxn       = float(fila_ext_mi["Venta Por Km"])
            ing_mi_usd       = float(fila_ext_mi["Venta Por Km USD"])
            mi_ref           = float(fila_ext_mi["Millas"])

        # Caja verde única (como antes), mostrando ambos bloques internos
        st.markdown(f"""<div class='resaltado'>
            <h3>▶ Tabulador Por Rango de Km</h3>
            <ul>
                {"<li><b>KM de referencia:</b> {:,.0f}</li><li><b>Ing/Km MXN:</b> ${:,.2f}</li><li><b>Ing/Km USD:</b> ${:,.2f}</li><li><b>MXN:</b> ${:,.2f}</li><li><b>USD:</b> ${:,.2f}</li>".format(km_ref, ing_km_mxn, ing_km_usd, venta_ext_mxn, venta_ext_usd) if km > 0 else ""}
                {"<hr style='border:0;border-top:1px solid rgba(255,255,255,.35);margin:.6em 0;'>" if (km>0 and mi>0) else ""}
                {"<li><b>Millas de referencia:</b> {:,.0f}</li><li><b>Ing/Km MXN:</b> ${:,.2f}</li><li><b>Ing/Km USD:</b> ${:,.2f}</li><li><b>MXN:</b> ${:,.2f}</li><li><b>USD:</b> ${:,.2f}</li>".format(mi_ref, ing_mi_mxn, ing_mi_usd, venta_ext_mxn_mi, venta_ext_usd_mi) if mi > 0 else ""}
            </ul>
        </div>""", unsafe_allow_html=True)

        if km > 0 and diff_km > margen:
            st.markdown(f"<div class='warn-box'>⚠️ No existe {km:,.0f} km exacto en VENTAEXT; se usó {km_ref:,.0f} (dif {diff_km:,.0f}).</div>", unsafe_allow_html=True)
        if mi > 0 and diff_mi > margen:
            st.markdown(f"<div class='warn-box'>⚠️ No existen {mi:,.0f} millas exactas en VENTAEXT; se usó {mi_ref:,.0f} (dif {diff_mi:,.0f}).</div>", unsafe_allow_html=True)

        # =========================
        # TABULADOR ALA (Comparativa) — MANTENIDO
        # =========================
        if km > 0:
            if km in ala_tab['KMs'].values:
                fila_ala = ala_tab[ala_tab['KMs'] == km].iloc[0]
                diff_ala = 0.0
            else:
                fila_ala, diff_ala = fila_mas_cercana(ala_tab, "KMs", km)

            venta_ala_mxn = float(fila_ala['Venta total'])
            venta_ala_usd = float(fila_ala['BID (USD)'])
            km_ref_ala    = float(fila_ala['KMs'])

            st.markdown(f"""### ▶ Tabulador ALA (Comparativa)
- MXN: ${venta_ala_mxn:,.2f}
- USD: ${venta_ala_usd:,.2f}
""")
            if diff_ala > margen:
                st.markdown(f"<div class='warn-box'>⚠️ No existe {km:,.0f} km exacto en ALA_TAB; se usó {km_ref_ala:,.0f} (dif {diff_ala:,.0f}).</div>", unsafe_allow_html=True)

        # =========================
        # (Opcional) Tabla resumen final (apagada por defecto para no cambiar el diseño)
        # =========================
        mostrar_tabla = st.checkbox("Mostrar resumen final (tabla)", value=False)
        if mostrar_tabla:
            filas = []
            if km > 0:
                filas.append({
                    "Modo": "VENTAEXT - KM",
                    "Referencia": km_ref,
                    "Ing/Km MXN": ing_km_mxn,
                    "Ing/Km USD": ing_km_usd,
                    "Venta MXN": venta_ext_mxn,
                    "Venta USD": venta_ext_usd
                })
            if mi > 0:
                filas.append({
                    "Modo": "VENTAEXT - Millas",
                    "Referencia": mi_ref,
                    "Ing/Km MXN": ing_mi_mxn,
                    "Ing/Km USD": ing_mi_usd,
                    "Venta MXN": venta_ext_mxn_mi,
                    "Venta USD": venta_ext_usd_mi
                })
            if km > 0:
                filas.append({
                    "Modo": "ALA_TAB",
                    "Referencia": km_ref_ala,
                    "Ing/Km MXN": None,
                    "Ing/Km USD": None,
                    "Venta MXN": venta_ala_mxn,
                    "Venta USD": venta_ala_usd
                })
            df = pd.DataFrame(filas)
            st.dataframe(df.style.format({
                "Referencia": "{:,.0f}",
                "Ing/Km MXN": (lambda x: f"${x:,.2f}" if pd.notnull(x) else "-"),
                "Ing/Km USD": (lambda x: f"${x:,.2f}" if pd.notnull(x) else "-"),
                "Venta MXN": "${:,.2f}",
                "Venta USD": "${:,.2f}",
            }), use_container_width=True)

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
