
import streamlit as st
import pandas as pd

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Calculadora de Viajes Expeditados", layout="centered")
st.markdown("""
<style>
  .stApp { background:#0B2341; }
  .block-container, h1,h2,h3,h4,h5,h6 { color:#fff; }
  .stTextInput input, .stNumberInput input { background:#fff !important; color:#000 !important; }
  .stButton button { background:#0B2341 !important; color:#fff !important; border:1px solid #FB6500; }
  .resaltado { background:#107144; padding:1em; border-radius:10px; color:#fff; }
  .resultado-box { background:#0F2D3F; padding:.7em; border-radius:6px; margin:.6em 0; color:#fff; font-weight:700;}
  .warn-box { background:#5a2e0e; padding:.6em; border-radius:6px; color:#ffd7b3; }
</style>
""", unsafe_allow_html=True)

# =========================
# BANNER
# =========================
try:
    st.image("banner.png", use_container_width=True)
except Exception:
    pass

st.markdown("<h1 style='text-align:center;'>Calculadora de Venta de Viajes Expeditados</h1>", unsafe_allow_html=True)

# =========================
# DATOS
# =========================
archivo_excel = "CAT_TAB.xlsx"

@st.cache_data(show_spinner=False)
def leer_hoja(_file, sheet):
    return pd.read_excel(_file, sheet_name=sheet, engine="openpyxl")

def to_num(s):
    return pd.to_numeric(s, errors="coerce")

try:
    ala_tab = leer_hoja(archivo_excel, "ALA_TAB")
    ventaext_tab = leer_hoja(archivo_excel, "VENTAEXT_TAB")
except Exception as e:
    st.error(f"No se pudo leer el archivo/hojas: {e}")
    st.stop()

req_ala = ["KMs", "Venta total", "BID (USD)"]
req_ext = ["KM", "Millas", "Venta Por Km", "Venta Por Km USD", "Venta MXN", "Venta USD"]

# Validación de columnas
for c in req_ala:
    if c not in ala_tab.columns:
        st.error(f"Falta columna '{c}' en ALA_TAB"); st.stop()
for c in req_ext:
    if c not in ventaext_tab.columns:
        st.error(f"Falta columna '{c}' en VENTAEXT_TAB"); st.stop()

# Tipos numéricos
for c in req_ala:
    ala_tab[c] = to_num(ala_tab[c])
for c in req_ext:
    ventaext_tab[c] = to_num(ventaext_tab[c])

ala_tab = ala_tab.dropna(subset=req_ala).copy()
ventaext_tab = ventaext_tab.dropna(subset=req_ext).copy()

# =========================
# ENTRADAS
# =========================
st.markdown("#### 🚚 Parámetros del viaje")
col1, col2 = st.columns(2)
with col1:
    km_input = st.number_input("Ingresa los **kilómetros**", min_value=0.0, step=1.0, value=0.0)
with col2:
    mi_input = st.number_input("Ingresa las **millas**", min_value=0.0, step=1.0, value=0.0)

# Conversión automática
if km_input > 0 and mi_input == 0:
    mi_input = km_input / 1.60934
elif mi_input > 0 and km_input == 0:
    km_input = mi_input * 1.60934

aprox_threshold = st.number_input(
    "Margen de aviso para 'valor más cercano' (km/millas)",
    min_value=0, value=10, step=1
)

# =========================
# HELPERS
# =========================
def fila_mas_cercana(df, col, objetivo):
    exact = df[df[col] == objetivo]
    if not exact.empty:
        return exact.iloc[0], 0.0
    idx = (df[col] - objetivo).abs().argsort().iloc[0]
    fila = df.iloc[idx]
    return fila, float(abs(fila[col] - objetivo))

# =========================
# CÁLCULO
# =========================
if st.button("Calcular"):
    try:
        resumen = []
        st.markdown(f"<div class='resultado-box'>Resultados</div>", unsafe_allow_html=True)

        # ---- Por KM ----
        if km_input > 0:
            fila_km, diff_km = fila_mas_cercana(ventaext_tab, "KM", km_input)
            resumen.append({
                "Modo": "VENTAEXT - KM",
                "Referencia": fila_km["KM"],
                "Ing/Km MXN": fila_km["Venta Por Km"],
                "Ing/Km USD": fila_km["Venta Por Km USD"],
                "Venta MXN": fila_km["Venta MXN"],
                "Venta USD": fila_km["Venta USD"]
            })
            if diff_km > aprox_threshold:
                st.markdown(
                    f"<div class='warn-box'>⚠️ KM {km_input:,.0f} no existe; se usó {fila_km['KM']:,.0f} (diff {diff_km:,.0f}).</div>",
                    unsafe_allow_html=True
                )

        # ---- Por Millas ----
        if mi_input > 0:
            fila_mi, diff_mi = fila_mas_cercana(ventaext_tab, "Millas", mi_input)
            resumen.append({
                "Modo": "VENTAEXT - Millas",
                "Referencia": fila_mi["Millas"],
                "Ing/Km MXN": fila_mi["Venta Por Km"],
                "Ing/Km USD": fila_mi["Venta Por Km USD"],
                "Venta MXN": fila_mi["Venta MXN"],
                "Venta USD": fila_mi["Venta USD"]
            })
            if diff_mi > aprox_threshold:
                st.markdown(
                    f"<div class='warn-box'>⚠️ Millas {mi_input:,.0f} no existen; se usó {fila_mi['Millas']:,.0f} (diff {diff_mi:,.0f}).</div>",
                    unsafe_allow_html=True
                )

        # ---- Comparativa ALA (solo km) ----
        if km_input > 0:
            fila_ala, diff_ala = fila_mas_cercana(ala_tab, "KMs", km_input)
            resumen.append({
                "Modo": "ALA_TAB",
                "Referencia": fila_ala["KMs"],
                "Ing/Km MXN": None,
                "Ing/Km USD": None,
                "Venta MXN": fila_ala["Venta total"],
                "Venta USD": fila_ala["BID (USD)"]
            })
            if diff_ala > aprox_threshold:
                st.markdown(
                    f"<div class='warn-box'>⚠️ KM {km_input:,.0f} no existe en ALA; se usó {fila_ala['KMs']:,.0f} (diff {diff_ala:,.0f}).</div>",
                    unsafe_allow_html=True
                )

        # ---- TABLA RESUMEN FINAL ----
        if resumen:
            df_resumen = pd.DataFrame(resumen)
            st.markdown("### 📊 Resumen Final")
            st.dataframe(
                df_resumen.style.format({
                    "Referencia": "{:,.0f}",
                    "Ing/Km MXN": (lambda x: f"${x:,.2f}" if pd.notnull(x) else "-"),
                    "Ing/Km USD": (lambda x: f"${x:,.2f}" if pd.notnull(x) else "-"),
                    "Venta MXN": "${:,.2f}",
                    "Venta USD": "${:,.2f}",
                }),
                use_container_width=True
            )

            # Descargas
            st.download_button(
                "⬇️ Descargar resumen (CSV)",
                data=df_resumen.to_csv(index=False).encode("utf-8"),
                file_name="resumen_calculadora.csv",
                mime="text/csv"
            )

            try:
                import io
                import xlsxwriter  # noqa: F401

                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    df_resumen.to_excel(writer, index=False, sheet_name="Resumen")
                st.download_button(
                    "⬇️ Descargar resumen (Excel)",
                    data=output.getvalue(),
                    file_name="resumen_calculadora.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception:
                st.caption("Para exportar a Excel, instala 'xlsxwriter'. CSV disponible.")
    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
