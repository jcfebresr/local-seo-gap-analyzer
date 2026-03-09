import streamlit as st
import advertools as adv
import pandas as pd
import re
from unidecode import unidecode

EXCLUSION_DICT = {
    "cerrajero": ["fontanero", "electricista", "pintor", "reformas", "mudanzas"],
    "fontanero": ["cerrajero", "electricista", "pintor", "reformas"],
    "electricista": ["cerrajero", "fontanero", "pintor", "reformas"]
}

def extraer_zona(url, servicio):
    slug = url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]
    slug_limpio = unidecode(slug).lower()
    exclusiones = EXCLUSION_DICT.get(servicio, [])
    for palabra in exclusiones:
        if palabra in slug_limpio: return None
    partes = re.split(r'[-_]', slug_limpio)
    zona = [p for p in partes if p != servicio and len(p) > 3]
    return "-".join(zona) if zona else None

st.set_page_config(page_title="Geo-Gap Analyzer", layout="wide")
st.title("🎯 Local SEO Geo-Gap Analyzer")

with st.sidebar:
    st.header("Configuración")
    servicio = st.selectbox("Servicio", ["cerrajero", "fontanero", "electricista"])
    tu_web = st.text_input("Tu dominio (ej: misitio.com)")
    sitemap_rival = st.text_input("Sitemap Rival (URL)")

if st.button("🚀 Analizar Gaps"):
    if not sitemap_rival or not tu_web:
        st.error("Rellena los campos de la izquierda.")
    else:
        with st.spinner("Escaneando..."):
            try:
                df_sitemap = adv.sitemap_to_df(sitemap_rival)
                urls_rival = df_sitemap['loc'].tolist()
                resultados = []
                for url in urls_rival:
                    zona = extraer_zona(url, servicio)
                    if zona:
                        resultados.append({"Zona": zona.capitalize(), "Slug": f"/{servicio}-{zona}/", "Rival": url})
                if resultados:
                    st.success(f"¡Gaps encontrados!")
                    st.table(pd.DataFrame(resultados).drop_duplicates('Zona'))
                else:
                    st.warning("No se detectaron zonas.")
            except Exception as e:
                st.error("Error al leer el sitemap.")
