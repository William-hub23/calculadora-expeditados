import streamlit as st
import pandas as pd
from io import BytesIO
from pathlib import Path

# =========================
# CONFIGURACIÓN
# =========================
st.set_page_config(page_title="Calculadora de Viajes Expeditados", layout="centered")

# =========================
# ESTILOS PERSONALIZADOS
# =========================
st.markdown("""
    <style>
        body { background-color: #0B2341; color: #FB6500; }
        .stTextInput > div > div > input { color: #000000; }
        .title { text-align: center; font-size: 28px; font-weight: 800; margin: 8px 0 4px; }
        .box { background: #e8f6ef; border-left: 6px solid #16a085; padding: 12px 14px; border-radius: 10px; }
        .muted { color: #ced4da; font-size: 13px; }
        .header { text-align:center; margin-top: 6px; }
    </style>
""", unsafe_allow_html=True)

# =========================
# UTILIDADES
# =========================
def safe_div(n, d):
    try:
        d = float(d)
        return (float(n) / d) if d else 0.0
    except Exception:
        return 0.0

def moneda(v):
    try:
        return f"${float(v):,.2f}"
    except Exception:
        return "-"

def _find_first(df, candidates):
    """Devuelve el primer nombre de columna existente en df.columns que coincida con la lista candidates."""
    for c in candidates:
        for col in df.columns:
            if col.strip().lower() == c.lower():
                return col
    return None

def _infer_columns(df):
    """
    Intenta inferir columnas de rangos y precio por km (MXN y USD).
    Retorna un dict con keys: km_min, km_max, mxn, usd.
    """
    km_min = _find_first(df, ["km_min", "min_km", "desde_km", "desde", "from_km", "inicio_km"])
    km_max = _find_first(df, ["km_max", "max_km", "hasta_km", "hasta", "to_km", "fin_km"])
    mxn    = _find_first(df, ["precio_mxn", "mxn", "mxn_km", "precio_km_mxn", "tarifa_mxn", "costo_mxn"])
    usd    = _find_first(df, ["precio_usd", "usd", "usd_km", "precio_km_usd", "tarifa_usd", "costo_usd"])
    return {"km_min": km_min, "km_max": km_max, "mxn": mxn, "usd": usd}

def _precio_por_km(df, km, sheet_name):
    """
    Dado un DataFrame con columnas inferidas, regresa (precio_mxn, precio_usd) por KM para el rango en el que cae `km`.
    Si no encuentra el rango, hace match aproximado por el rango con km_min más cercano <= km.
    """
    cols = _infer_columns(df)
    for required in ["km_min", "km_max"]:
        if not cols[required]:
            raise ValueError(f"En la hoja '{sheet_name}' no se encontraron columnas de rango ('km_min'/'km_max', 'desde'/'hasta', etc.).")

    # Asegurar tipos numéricos
    df_work = df.copy()
    df_work[cols["km_min"]] = pd.to_numeric(df_work[cols["km_min"]], errors="coerce")
    df_work[cols["km_max"]] = pd.to_numeric(df_work[cols["km_max"]], errors="coerce")

    # Intentar match exacto de rango
    mask = (df_work[cols["km_min"]] <= km) & (km <= df_work[cols["km_max"]])
    if mask.any():
        row = df_work.loc[mask].iloc[0]
    else:
        # Aproximación: rango cuyo km_min sea el más grande <= km
        df_le = df_work[df_work[cols["km_min"]] <= km]
        if df_le.empty:
            row = df_work.sort_values(by=cols["km_min"]).iloc[0]
        else:
            row = df_le.sort_values(by=cols["km_min"]).iloc[-1]

    # Extraer precio por km en MXN/USD si existen columnas; si no, usar 0
    precio_mxn = 0.0
    precio_usd = 0.0
    if cols["mxn"] and cols["mxn"] in row:
        precio_mxn = pd.to_numeric(row[cols["mxn"]], errors="coerce") or 0.0
    if cols["usd"] and cols["usd"] in row:
        precio_usd = pd.to_numeric(row[cols["usd"]], errors="coerce") or 0.0

    return float(precio_mxn), float(precio_usd)

def calcular_ventas(km, book_path: Path):
    """
    Carga el libro y calcula ventas totales por tabulador (ALA, PEAK, VENTA por km).
    Asume que los precios en cada hoja son por KM.
    Retorna un dict con totales MXN/USD y también ingresos por km.
    """
    xls = pd.ExcelFile(book_path)
    # Cargar hojas si existen
    def _load_sheet(name):
        if name in xls.sheet_names:
            return pd.read_excel(xls, sheet_name=name)
        return None

    ala_tab   = _load_sheet("ALA_TAB")
    peak_tab  = _load_sheet("PEAK_TAB")
    venta_tab = _load_sheet("VENTA_TAB")

    resultados = {}

    # ALA
    if ala_tab is not None:
        p_mxn, p_usd = _precio_por_km(ala_tab, km, "ALA_TAB")
        resultados["venta_ala_mxn"] = km * p_mxn
        resultados["venta_ala_usd"] = km * p_usd
    else:
        resultados["venta_ala_mxn"] = 0.0
        resultados["venta_ala_usd"] = 0.0

    # PEAK
    if peak_tab is not None:
        p_mxn, p_usd = _precio_por_km(peak_tab, km, "PEAK_TAB")
        resultados["venta_peak_mxn"] = km * p_mxn
        resultados["venta_peak_usd"] = km * p_usd
    else:
        resultados["venta_peak_mxn"] = 0.0
        resultados["venta_peak_usd"] = 0.0

    # VENTA por KM
    if venta_tab is not None:
        p_mxn, p_usd = _precio_por_km(venta_tab, km, "VENTA_TAB")
        resultados["venta_rango_mxn"] = km * p_mxn
        resultados["venta_rango_usd"] = km * p_usd
    else:
        resultados["venta_rango_mxn"] = 0.0
        resultados["venta_rango_usd"] = 0.0

    # Ingreso/km
    resultados["ingreso_km_ala_mxn"]   = safe_div(resultados["venta_ala_mxn"], km)
    resultados["ingreso_km_ala_usd"]   = safe_div(resultados["venta_ala_usd"], km)
    resultados["ingreso_km_peak_mxn"]  = safe_div(resultados["venta_peak_mxn"], km)
    resultados["ingreso_km_peak_usd"]  = safe_div(resultados["venta_peak_usd"], km)
    resultados["ingreso_km_rango_mxn"] = safe_div(resultados["venta_rango_mxn"], km)
    resultados["ingreso_km_rango_usd"] = safe_div(resultados["venta_rango_usd"], km)

    return resultados

def excel_bytes_con_hojas(dfs_por_hoja: dict) -> bytes:
    """Crea un Excel en memoria con varias hojas."""
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        for nombre_hoja, df in dfs_por_hoja.items():
            df.to_excel(writer, sheet_name=nombre_hoja, index=False)
            wb = writer.book
            ws = writer.sheets[nombre_hoja]
            fmt_moneda = wb.add_format({"num_format": "$#,##0.00"})
            fmt_text   = wb.add_format({"num_format": "@"})
            for col_idx, col in enumerate(df.columns):
                try:
                    maxlen = max(12, int(df[col].astype(str).str.len().max()) + 2)
                except Exception:
                    maxlen = 18
                if df[col].dtype.kind in "if":
                    ws.set_column(col_idx, col_idx, maxlen, fmt_moneda if ("MXN" in col or "USD" in col) else None)
                else:
                    ws.set_column(col_idx, col_idx, maxlen, fmt_text)
    buffer.seek(0)
    return buffer.getvalue()

# =========================
# BANNER (si existe) + TÍTULO
# =========================
banner_path = Path("banner.png")
if banner_path.exists():
    st.image(str(banner_path), use_container_width=True)

st.markdown("<h1 class='header'>Calculadora de Venta de Viajes Expeditados</h1>", unsafe_allow_html=True)

# =========================
# ENTRADAS
# =========================
col_a, col_b = st.columns([2,1])
with col_a:
    archivo = st.text_input("Ruta del archivo Excel (CAT_TAB.xlsx)", value="CAT_TAB.xlsx")
with col_b:
    km = st.number_input("KM a cotizar", min_value=1.0, step=1.0, value=500.0, help="Kilómetros recorridos para la cotización.")

book_path = Path(archivo)

if not book_path.exists():
    st.warning("No se encontró el archivo especificado. Carga el Excel o ajusta la ruta.")
    excel_file = st.file_uploader("Sube tu CAT_TAB.xlsx", type=["xlsx"])
    if excel_file:
        tmp_path = Path("CAT_TAB.xlsx")
        with open(tmp_path, "wb") as f:
            f.write(excel_file.getbuffer())
        book_path = tmp_path

# =========================
# CÁLCULO
# =========================
if st.button("Calcular"):
    try:
        if not book_path.exists():
            st.error("No se encontró el archivo Excel. Verifica la ruta o sube el archivo.")
            st.stop()

        resultados = calcular_ventas(km, book_path)

        # Bloque de resultados detallados
        st.markdown("<div class='box'>", unsafe_allow_html=True)
        st.markdown(f"**Resultado para {km:.0f} km**", unsafe_allow_html=True)
        st.markdown(
            f"""
            ### ▶ Tabulador ALA  
            - MXN: **{moneda(resultados['venta_ala_mxn'])}**  
            - USD: **{moneda(resultados['venta_ala_usd'])}**  
            - Ingreso/km: **{moneda(resultados['ingreso_km_ala_mxn'])}** | **{moneda(resultados['ingreso_km_ala_usd'])}**

            ### ▶ Tabulador Peak  
            - MXN: **{moneda(resultados['venta_peak_mxn'])}**  
            - USD: **{moneda(resultados['venta_peak_usd'])}**  
            - Ingreso/km: **{moneda(resultados['ingreso_km_peak_mxn'])}** | **{moneda(resultados['ingreso_km_peak_usd'])}**

            ### ▶ Tabulador por Rango de KM  
            - MXN: **{moneda(resultados['venta_rango_mxn'])}**  
            - USD: **{moneda(resultados['venta_rango_usd'])}**  
            - Ingreso/km: **{moneda(resultados['ingreso_km_rango_mxn'])}** | **{moneda(resultados['ingreso_km_rango_usd'])}**
            """,
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # Tabla comparativa
        comparativa = pd.DataFrame(
            [
                {"Tabulador": "ALA",    "Venta MXN": resultados["venta_ala_mxn"],   "Venta USD": resultados["venta_ala_usd"],
                 "Ingreso/km MXN": resultados["ingreso_km_ala_mxn"], "Ingreso/km USD": resultados["ingreso_km_ala_usd"]},
                {"Tabulador": "Peak",   "Venta MXN": resultados["venta_peak_mxn"],  "Venta USD": resultados["venta_peak_usd"],
                 "Ingreso/km MXN": resultados["ingreso_km_peak_mxn"], "Ingreso/km USD": resultados["ingreso_km_peak_usd"]},
                {"Tabulador": "Por KM", "Venta MXN": resultados["venta_rango_mxn"], "Venta USD": resultados["venta_rango_usd"],
                 "Ingreso/km MXN": resultados["ingreso_km_rango_mxn"], "Ingreso/km USD": resultados["ingreso_km_rango_usd"]},
            ]
        )
        comparativa_fmt = comparativa.copy()
        for col in ["Venta MXN", "Venta USD", "Ingreso/km MXN", "Ingreso/km USD"]:
            comparativa_fmt[col] = comparativa_fmt[col].map(moneda)

        st.subheader("Comparativa")
        st.dataframe(comparativa_fmt, use_container_width=True)

        # Descargas
        csv_bytes = comparativa.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="⬇️ Descargar CSV (Comparativa)",
            data=csv_bytes,
            file_name=f"comparativa_{int(km)}km.csv",
            mime="text/csv",
            use_container_width=True
        )

        excel_bytes = excel_bytes_con_hojas({"Datos": comparativa, "Vista": comparativa_fmt})
        st.download_button(
            label="⬇️ Descargar Excel (Comparativa)",
            data=excel_bytes,
            file_name=f"comparativa_{int(km)}km.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        st.caption("Los valores de ALA, Peak y Por KM asumen precios por kilómetro en cada hoja. Si tus tablas usan otro esquema, ajusta los nombres de columnas o el cálculo.")

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
        st.exception(e)
else:
    st.markdown("<span class='muted'>Ingresa los KM y verifica la ruta del Excel para comenzar.</span>", unsafe_allow_html=True)
