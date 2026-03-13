"""
Local SEO Geo-Gap Analyzer v2.6
Sprint 4.4 - Competidores Ilimitados + Error Handling
- 3 competidores obligatorios
- Hasta 7 competidores adicionales (opcionales)
- UI colapsable para competidores extra
- Validación defensiva contra None/NaN en URLs
"""

import streamlit as st
import pandas as pd
import advertools as adv
import re
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode
from urllib.parse import urlparse, urljoin
from rapidfuzz import fuzz
import time
import io
import hashlib

# ============================================
# CONFIGURACIÓN MULTIIDIOMA
# ============================================

TRANSLATIONS = {
    "es": {
        "title": "🎯 Local SEO Geo-Gap Analyzer",
        "language": "Idioma / Language",
        "service": "Servicio",
        "your_domain": "Tu dominio",
        "competitor": "Competidor",
        "domain_placeholder": "ejemplo.com (sin https://)",
        "analyze_button": "🚀 Analizar Gaps",
        "min_competitors": "❌ Debes ingresar exactamente 3 competidores",
        "invalid_domain": "❌ Dominio inválido",
        "select_saved_domain": "Seleccionar dominio guardado",
        "new_domain": "✏️ Escribir dominio nuevo...",
        "clear_history": "🗑️ Limpiar historial",
        "history_cleared": "Historial borrado",
        "no_saved_domains": "No hay dominios guardados aún",
        "home_zone_detected": "🏠 Zona base detectada",
        "is_correct": "¿Es correcto?",
        "yes": "✓ Sí",
        "no": "✗ No, cambiar",
        "select_city": "Selecciona tu ciudad principal",
        "sitemap_found": "✅ Sitemap detectado",
        "sitemap_robots": "✅ Sitemap en robots.txt",
        "no_sitemap": "⚠️ Sin sitemap (crawling fallback)",
        "domain_error": "❌ No accesible, verifica dominio",
        "analyzing": "Analizando",
        "extracting_urls": "Extrayendo URLs",
        "processing": "Procesando",
        "gaps_found": "Gaps Detectados",
        "strengths_found": "Tus Fortalezas",
        "ties_found": "Empates",
        "low_confidence": "Baja Confianza - Revisar",
        "zone": "Zona",
        "slug": "Slug Sugerido",
        "competitor_urls": "URLs Competidores",
        "competitors_count": "Nº Comps",
        "confidence": "Confianza",
        "search_volume": "Volumen",
        "keyword_difficulty": "KD",
        "traffic": "Tráfico",
        "keywords_ranking": "Keywords",
        "score": "Score",
        "advantage": "Ventaja",
        "strategy": "Estrategia",
        "priority": "Prioridad",
        "confirm": "Confirmar",
        "required_field": "Campo obligatorio",
        "duplicate_domains": "Los dominios deben ser diferentes entre sí",
        "urls_filtered": "URLs filtradas por servicio diferente",
        "critical_priority": "CRÍTICA",
        "high_priority": "ALTA",
        "medium_priority": "MEDIA",
        "low_priority": "BAJA",
        "max_advantage": "MÁXIMA (zona única)",
        "medium_advantage": "MEDIA (baja competencia)",
        "maintain_dominance": "Mantener dominancia. Reforzar contenido y backlinks.",
        "early_advantage": "Ventaja temprana. Invertir en diferenciación.",
        "competitive_market": "Mercado competitivo. Mantener posición con contenido de calidad.",
        "validated_opportunity": "Oportunidad Validada - todos los competidores están ahí",
        "emerging_niche": "Nicho Emergente - mayoría presente",
        "long_tail": "Larga Cola / Experimental - solo uno lo tiene",
        "filter_by_priority": "Filtrar por prioridad",
        "filter_by_competitors": "Filtrar por Nº competidores",
        "search_zone": "Buscar zona",
        "all": "Todas",
        "show_results": "Mostrando",
        "of": "de",
        "results": "resultados",
        "no_gaps_filter": "No hay gaps que coincidan con los filtros",
        "export_csv": "📥 Exportar CSV",
        "api_optional": "📊 API Keywords (Opcional)",
        "enable_api": "Habilitar API",
        "api_provider": "Proveedor",
        "api_key": "API Key",
        "api_key_placeholder": "Pega tu API key aquí",
        "country_code": "País",
        "fetching_metrics": "Obteniendo métricas de API...",
        "using_cache": "✅ Usando datos en caché",
        "add_competitors": "➕ Agregar más competidores (opcional)",
        "competitors_required": "Competidores Obligatorios",
        "competitors_optional": "Competidores Adicionales (Opcional)",
        "total_competitors": "Total competidores",
        "generate_pages": "📄 Generar Páginas",
        "select_gaps": "Seleccionar gaps para crear páginas",
        "preview_template": "👁️ Preview Plantilla",
        "template_selector": "Seleccionar plantilla",
        "base_template": "Plantilla Base",
        "premium_template": "Plantilla Premium",
        "minimal_template": "Plantilla Minimalista",
    },
    "en": {
        "title": "🎯 Local SEO Geo-Gap Analyzer",
        "language": "Idioma / Language",
        "service": "Service",
        "your_domain": "Your domain",
        "competitor": "Competitor",
        "domain_placeholder": "example.com (without https://)",
        "analyze_button": "🚀 Analyze Gaps",
        "min_competitors": "❌ You must enter exactly 3 competitors",
        "invalid_domain": "❌ Invalid domain",
        "select_saved_domain": "Select saved domain",
        "new_domain": "✏️ Enter new domain...",
        "clear_history": "🗑️ Clear history",
        "history_cleared": "History cleared",
        "no_saved_domains": "No saved domains yet",
        "home_zone_detected": "🏠 Home zone detected",
        "is_correct": "Is this correct?",
        "yes": "✓ Yes",
        "no": "✗ No, change",
        "select_city": "Select your main city",
        "sitemap_found": "✅ Sitemap detected",
        "sitemap_robots": "✅ Sitemap in robots.txt",
        "no_sitemap": "⚠️ No sitemap (crawling fallback)",
        "domain_error": "❌ Not accessible, verify domain",
        "analyzing": "Analyzing",
        "extracting_urls": "Extracting URLs",
        "processing": "Processing",
        "gaps_found": "Gaps Detected",
        "strengths_found": "Your Strengths",
        "ties_found": "Ties",
        "low_confidence": "Low Confidence - Review",
        "zone": "Zone",
        "slug": "Suggested Slug",
        "competitor_urls": "Competitor URLs",
        "competitors_count": "# Comps",
        "confidence": "Confidence",
        "search_volume": "Volume",
        "keyword_difficulty": "KD",
        "traffic": "Traffic",
        "keywords_ranking": "Keywords",
        "score": "Score",
        "advantage": "Advantage",
        "strategy": "Strategy",
        "priority": "Priority",
        "confirm": "Confirm",
        "required_field": "Required field",
        "duplicate_domains": "Domains must be different from each other",
        "urls_filtered": "URLs filtered by different service",
        "critical_priority": "CRITICAL",
        "high_priority": "HIGH",
        "medium_priority": "MEDIUM",
        "low_priority": "LOW",
        "max_advantage": "MAXIMUM (unique zone)",
        "medium_advantage": "MEDIUM (low competition)",
        "maintain_dominance": "Maintain dominance. Reinforce content and backlinks.",
        "early_advantage": "Early advantage. Invest in differentiation.",
        "competitive_market": "Competitive market. Maintain position with quality content.",
        "validated_opportunity": "Validated Opportunity - all competitors are there",
        "emerging_niche": "Emerging Niche - majority present",
        "long_tail": "Long Tail / Experimental - only one has it",
        "filter_by_priority": "Filter by priority",
        "filter_by_competitors": "Filter by # competitors",
        "search_zone": "Search zone",
        "all": "All",
        "show_results": "Showing",
        "of": "of",
        "results": "results",
        "no_gaps_filter": "No gaps match the filters",
        "export_csv": "📥 Export CSV",
        "api_optional": "📊 Keywords API (Optional)",
        "enable_api": "Enable API",
        "api_provider": "Provider",
        "api_key": "API Key",
        "api_key_placeholder": "Paste your API key here",
        "country_code": "Country",
        "fetching_metrics": "Fetching API metrics...",
        "using_cache": "✅ Using cached data",
        "add_competitors": "➕ Add more competitors (optional)",
        "competitors_required": "Required Competitors",
        "competitors_optional": "Additional Competitors (Optional)",
        "total_competitors": "Total competitors",
        "generate_pages": "📄 Generate Pages",
        "select_gaps": "Select gaps to create pages",
        "preview_template": "👁️ Preview Template",
        "template_selector": "Select template",
        "base_template": "Base Template",
        "premium_template": "Premium Template",
        "minimal_template": "Minimal Template",
    }
}

SERVICES = {
    "es": {
        "cerrajero": "Cerrajero",
        "fontanero": "Fontanero",
        "electricista": "Electricista",
        "pintor": "Pintor",
        "carpintero": "Carpintero",
        "cristalero": "Cristalero",
        "reformas": "Reformas",
        "mudanzas": "Mudanzas",
        "limpieza": "Limpieza",
        "jardinero": "Jardinero",
        "aire-acondicionado": "Aire Acondicionado",
        "albañil": "Albañil",
        "tecnico-climatizacion": "Técnico Climatización",
        "instalador-gas": "Instalador Gas",
        "tapicero": "Tapicero",
    },
    "en": {
        "locksmith": "Locksmith",
        "plumber": "Plumber",
        "electrician": "Electrician",
        "painter": "Painter",
        "carpenter": "Carpenter",
        "glazier": "Glazier",
        "remodeling": "Remodeling",
        "moving": "Moving",
        "cleaning": "Cleaning",
        "gardener": "Gardener",
        "hvac": "HVAC",
        "handyman": "Handyman",
        "roofer": "Roofer",
        "mason": "Mason",
        "pest-control": "Pest Control",
    }
}

EXCLUSION_DICTIONARY = {
    "es": {
        "cerrajero": ["fontanero", "fontaneria", "electricista", "electrico", "pintor", "pintura", "reformas", "obra", "limpieza", "mudanzas", "carpintero", "carpinteria", "cristalero", "jardinero", "jardineria", "aire", "climatizacion", "albañil", "albanileria", "gas", "tapicero"],
        "fontanero": ["cerrajero", "cerrajeria", "electricista", "electrico", "pintor", "pintura", "reformas", "obra", "limpieza", "mudanzas", "carpintero", "cristalero", "jardinero", "aire", "climatizacion", "albañil", "tapicero"],
        "electricista": ["cerrajero", "cerrajeria", "fontanero", "fontaneria", "pintor", "pintura", "reformas", "obra", "limpieza", "mudanzas", "carpintero", "cristalero", "jardinero", "aire", "climatizacion", "albañil", "tapicero"],
        "pintor": ["cerrajero", "cerrajeria", "fontanero", "fontaneria", "electricista", "electrico", "reformas", "limpieza", "mudanzas", "carpintero", "cristalero", "jardinero", "aire", "climatizacion", "albañil", "tapicero"],
        "carpintero": ["cerrajero", "cerrajeria", "fontanero", "fontaneria", "electricista", "electrico", "pintor", "pintura", "reformas", "limpieza", "mudanzas", "cristalero", "jardinero", "aire", "climatizacion", "albañil", "tapicero"],
        "cristalero": ["cerrajero", "cerrajeria", "fontanero", "fontaneria", "electricista", "electrico", "pintor", "pintura", "reformas", "limpieza", "mudanzas", "carpintero", "jardinero", "aire", "climatizacion", "albañil", "tapicero"],
        "reformas": ["cerrajero", "fontanero", "electricista", "pintor", "limpieza", "mudanzas", "cristalero", "jardinero", "aire", "tapicero"],
        "mudanzas": ["cerrajero", "cerrajeria", "fontanero", "fontaneria", "electricista", "electrico", "pintor", "pintura", "reformas", "limpieza", "carpintero", "cristalero", "jardinero", "aire", "climatizacion", "albañil", "tapicero"],
        "limpieza": ["cerrajero", "cerrajeria", "fontanero", "fontaneria", "electricista", "electrico", "pintor", "pintura", "reformas", "mudanzas", "carpintero", "cristalero", "jardinero", "aire", "climatizacion", "albañil", "tapicero"],
        "jardinero": ["cerrajero", "cerrajeria", "fontanero", "fontaneria", "electricista", "electrico", "pintor", "pintura", "reformas", "mudanzas", "carpintero", "cristalero", "limpieza", "aire", "climatizacion", "albañil", "tapicero"],
        "aire-acondicionado": ["cerrajero", "cerrajeria", "fontanero", "fontaneria", "pintor", "pintura", "reformas", "mudanzas", "carpintero", "cristalero", "limpieza", "jardinero", "albañil", "tapicero"],
        "albañil": ["cerrajero", "cerrajeria", "fontanero", "fontaneria", "electricista", "electrico", "pintor", "pintura", "mudanzas", "carpintero", "cristalero", "limpieza", "jardinero", "aire", "tapicero"],
        "tecnico-climatizacion": ["cerrajero", "cerrajeria", "fontanero", "fontaneria", "pintor", "pintura", "reformas", "mudanzas", "carpintero", "cristalero", "limpieza", "jardinero", "albañil", "tapicero"],
        "instalador-gas": ["cerrajero", "cerrajeria", "electricista", "electrico", "pintor", "pintura", "reformas", "mudanzas", "carpintero", "cristalero", "limpieza", "jardinero", "aire", "albañil", "tapicero"],
        "tapicero": ["cerrajero", "cerrajeria", "fontanero", "fontaneria", "electricista", "electrico", "reformas", "mudanzas", "cristalero", "limpieza", "jardinero", "aire", "climatizacion", "albañil"],
    },
    "en": {
        "locksmith": ["plumber", "plumbing", "electrician", "electrical", "painter", "painting", "remodeling", "renovation", "cleaning", "moving", "carpenter", "glazier", "gardener", "hvac", "handyman", "mason", "pest"],
        "plumber": ["locksmith", "locks", "electrician", "electrical", "painter", "painting", "remodeling", "renovation", "cleaning", "moving", "carpenter", "glazier", "gardener", "hvac", "handyman", "mason", "pest"],
        "electrician": ["locksmith", "locks", "plumber", "plumbing", "painter", "painting", "remodeling", "renovation", "cleaning", "moving", "carpenter", "glazier", "gardener", "hvac", "handyman", "mason", "pest"],
        "painter": ["locksmith", "locks", "plumber", "plumbing", "electrician", "electrical", "remodeling", "cleaning", "moving", "carpenter", "glazier", "gardener", "hvac", "handyman", "mason", "pest"],
        "carpenter": ["locksmith", "locks", "plumber", "plumbing", "electrician", "electrical", "painter", "painting", "remodeling", "cleaning", "moving", "glazier", "gardener", "hvac", "handyman", "mason", "pest"],
        "glazier": ["locksmith", "locks", "plumber", "plumbing", "electrician", "electrical", "painter", "painting", "remodeling", "cleaning", "moving", "carpenter", "gardener", "hvac", "handyman", "mason", "pest"],
        "remodeling": ["locksmith", "plumber", "electrician", "painter", "cleaning", "moving", "glazier", "gardener", "hvac", "pest"],
        "moving": ["locksmith", "locks", "plumber", "plumbing", "electrician", "electrical", "painter", "painting", "remodeling", "cleaning", "carpenter", "glazier", "gardener", "hvac", "handyman", "mason", "pest"],
        "cleaning": ["locksmith", "locks", "plumber", "plumbing", "electrician", "electrical", "painter", "painting", "remodeling", "moving", "carpenter", "glazier", "gardener", "hvac", "handyman", "mason", "pest"],
        "gardener": ["locksmith", "locks", "plumber", "plumbing", "electrician", "electrical", "painter", "painting", "remodeling", "moving", "carpenter", "glazier", "cleaning", "hvac", "handyman", "mason", "pest"],
        "hvac": ["locksmith", "locks", "plumber", "plumbing", "painter", "painting", "remodeling", "moving", "carpenter", "glazier", "cleaning", "gardener", "handyman", "mason", "pest"],
        "handyman": ["locksmith", "locks", "plumber", "plumbing", "electrician", "electrical", "painter", "painting", "moving", "carpenter", "glazier", "cleaning", "gardener", "hvac", "mason", "pest"],
        "roofer": ["locksmith", "locks", "plumber", "plumbing", "electrician", "electrical", "painter", "painting", "remodeling", "moving", "carpenter", "glazier", "cleaning", "gardener", "hvac", "pest"],
        "mason": ["locksmith", "locks", "plumber", "plumbing", "electrician", "electrical", "painter", "painting", "moving", "carpenter", "glazier", "cleaning", "gardener", "hvac", "pest"],
        "pest-control": ["locksmith", "locks", "plumber", "plumbing", "electrician", "electrical", "painter", "painting", "remodeling", "moving", "carpenter", "glazier", "gardener", "hvac", "handyman", "mason"],
    }
}

TOP_CITIES = {
    "es": [
        "madrid", "barcelona", "valencia", "sevilla", "zaragoza", "malaga", 
        "murcia", "palma", "bilbao", "alicante", "cordoba", "valladolid",
        "vigo", "gijon", "hospitalet", "vitoria", "coruña", "granada", 
        "elche", "oviedo", "terrassa", "badalona", "cartagena", "sabadell",
        "jerez", "mostoles", "santa-cruz", "pamplona", "almeria", "fuenlabrada",
        "leganes", "san-sebastian", "santander", "burgos", "castellon", "albacete",
        "alcorcon", "getafe", "salamanca", "logroño", "huelva", "tarragona",
        "leon", "cadiz", "marbella", "badajoz", "lleida", "torrevieja",
        "chamberi", "retiro", "tetuan", "fuencarral", "moncloa", "carabanchel",
        "usera", "puente-vallecas", "moratalaz", "ciudad-lineal", "hortaleza",
        "villaverde", "villa-vallecas", "vicalvaro", "san-blas", "barajas",
    ],
    "en": [
        "new-york", "los-angeles", "chicago", "houston", "phoenix", "philadelphia",
        "san-antonio", "san-diego", "dallas", "san-jose", "austin", "jacksonville",
        "fort-worth", "columbus", "charlotte", "san-francisco", "indianapolis", "seattle",
        "denver", "washington", "boston", "el-paso", "nashville", "detroit",
        "oklahoma-city", "portland", "las-vegas", "memphis", "louisville", "baltimore",
        "milwaukee", "albuquerque", "tucson", "fresno", "mesa", "sacramento",
        "atlanta", "kansas-city", "colorado-springs", "omaha", "raleigh", "miami",
        "long-beach", "virginia-beach", "oakland", "minneapolis", "tulsa", "tampa",
        "brooklyn", "manhattan", "queens", "bronx", "staten-island",
    ]
}

STOP_WORDS = {
    "es": [
        "en", "a", "de", "la", "el", "los", "las", "para", "con", "por", "sin",
        "del", "al", "y", "o", "un", "una", "unos", "unas",
        "urgente", "urgentes", "barato", "baratos", "barata", "baratas",
        "economico", "economicos", "economica", "economicas",
        "mejor", "mejores", "rapido", "rapidos", "rapida", "rapidas",
        "profesional", "profesionales", "calidad", "confianza",
        "garantizado", "garantizada", "certificado", "certificada",
        "24h", "24-horas", "24horas", "24-h", "24hs",
        "servicio", "servicios", "precio", "precios", "presupuesto",
        "gratis", "gratuito", "oferta", "ofertas", "descuento",
        "cerca", "cercano", "cercana", "zona", "zonas",
    ],
    "en": [
        "in", "at", "on", "of", "the", "a", "an", "for", "with", "by", "to",
        "and", "or", "near", "around",
        "urgent", "cheap", "affordable", "economical", "economy",
        "best", "top", "fast", "quick", "rapid", "professional",
        "quality", "trusted", "certified", "guaranteed",
        "24h", "24-hour", "24-hours", "24hr", "24hrs",
        "emergency", "same-day", "sameday",
        "service", "services", "price", "prices", "quote", "free",
        "discount", "offer", "deals",
        "near", "nearby", "local", "area", "areas",
    ]
}

def get_text(key, lang="es"):
    return TRANSLATIONS.get(lang, TRANSLATIONS["es"]).get(key, key)

def get_services(lang="es"):
    return SERVICES.get(lang, SERVICES["es"])

def get_cities(lang="es"):
    return TOP_CITIES.get(lang, TOP_CITIES["es"])

def get_stop_words(lang="es"):
    return STOP_WORDS.get(lang, STOP_WORDS["es"])

def get_exclusion_list(service_key, lang="es"):
    return EXCLUSION_DICTIONARY.get(lang, {}).get(service_key, [])

def get_service_variations(service_key, lang="es"):
    variations = {service_key}
    
    if lang == "es":
        if service_key.endswith('o'):
            variations.add(service_key + 's')
        elif service_key.endswith('a'):
            variations.add(service_key + 's')
        
        if service_key.endswith('ero'):
            base = service_key[:-3]
            variations.add(base + 'eria')
            variations.add(base + 'erias')
        
        special_variations = {
            "pintor": ["pintura", "pinturas"],
            "limpieza": ["limpiezas"],
            "reformas": ["reforma"],
            "mudanzas": ["mudanza"],
            "electricista": ["electrico", "electricos", "electricidad"],
            "fontanero": ["fontaneria", "fontanerias"],
            "carpintero": ["carpinteria", "carpinterias"],
            "cristalero": ["cristaleria", "cristalerias"],
            "jardinero": ["jardineria", "jardinerias"],
            "aire-acondicionado": ["aire", "climatizacion", "clima"],
            "albañil": ["albanileria", "albaniles"],
            "tecnico-climatizacion": ["climatizacion", "clima", "aire"],
            "instalador-gas": ["gas", "instalacion-gas"],
            "tapicero": ["tapiceria", "tapicerias"],
        }
        
        if service_key in special_variations:
            variations.update(special_variations[service_key])
    
    elif lang == "en":
        variations.add(service_key + 's')
        
        special_variations = {
            "locksmith": ["locks", "locksmithing"],
            "plumber": ["plumbing"],
            "electrician": ["electrical", "electric"],
            "painter": ["painting"],
            "carpenter": ["carpentry"],
            "glazier": ["glazing", "glass"],
            "remodeling": ["renovation", "renovations", "remodel"],
            "moving": ["movers", "relocation"],
            "cleaning": ["cleaners", "clean"],
            "gardener": ["gardening", "landscaping"],
            "hvac": ["heating", "cooling", "air-conditioning"],
            "handyman": ["handymen", "repair", "repairs"],
            "roofer": ["roofing"],
            "mason": ["masonry", "bricklayer"],
            "pest-control": ["pest", "exterminator"],
        }
        
        if service_key in special_variations:
            variations.update(special_variations[service_key])
    
    return list(variations)

# ============================================
# CACHING SYSTEM
# ============================================

@st.cache_data(ttl=3600, show_spinner=False)
def extract_urls_from_sitemap_cached(sitemap_url, max_urls=5000):
    try:
        df = adv.sitemap_to_df(sitemap_url)
        # FILTRAR None/NaN antes de convertir a lista
        urls = df['loc'].dropna().astype(str).tolist()
        
        if len(urls) > max_urls:
            import random
            urls = random.sample(urls, max_urls)
        
        return urls, len(df)
    except Exception as e:
        return [], 0

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_api_data_cached(keyword, api_provider, api_key_hash, country_code):
    if api_provider == "SE Ranking":
        return fetch_seranking_keyword_data_uncached(keyword, api_key_hash, country_code)
    elif api_provider == "Semrush":
        return fetch_semrush_keyword_data_uncached(keyword, api_key_hash, country_code)
    elif api_provider == "Ahrefs":
        return fetch_ahrefs_keyword_data_uncached(keyword, api_key_hash, country_code)
    return None

def hash_api_key(api_key):
    return hashlib.sha256(api_key.encode()).hexdigest()[:16]

# ============================================
# API INTEGRATIONS
# ============================================

def build_keyword_from_gap(service, zone, lang="es"):
    if lang == "es":
        return f"{service} {zone}"
    else:
        return f"{zone} {service}"

def fetch_seranking_keyword_data_uncached(keyword, api_key, country_code="es"):
    try:
        url = "https://api4.seranking.com/research/keywords"
        headers = {
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "keywords": [keyword],
            "location_id": country_code,
            "language_code": "es" if country_code == "es" else "en"
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                kw_data = data[0]
                return {
                    'volume': kw_data.get('search_volume', 0),
                    'kd': kw_data.get('difficulty', 0)
                }
        
        return None
    except Exception as e:
        return None

def fetch_semrush_keyword_data_uncached(keyword, api_key, database="es"):
    try:
        url = f"https://api.semrush.com/"
        params = {
            'type': 'phrase_this',
            'key': api_key,
            'phrase': keyword,
            'database': database,
            'export_columns': 'Ph,Nq,Kd'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            lines = response.text.strip().split('\n')
            if len(lines) > 1:
                data = lines[1].split(';')
                return {
                    'volume': int(data[1]) if len(data) > 1 else 0,
                    'kd': int(data[2]) if len(data) > 2 else 0
                }
        
        return None
    except Exception as e:
        return None

def fetch_ahrefs_keyword_data_uncached(keyword, api_key, country="es"):
    try:
        url = "https://api.ahrefs.com/v3/keywords-explorer/overview"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "country": country,
            "keywords": [keyword]
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'keywords' in data and len(data['keywords']) > 0:
                kw_data = data['keywords'][0]
                return {
                    'volume': kw_data.get('volume', 0),
                    'kd': kw_data.get('difficulty', 0)
                }
        
        return None
    except Exception as e:
        return None

def fetch_api_data(keyword, api_provider, api_key, country_code):
    api_key_hash = hash_api_key(api_key)
    return fetch_api_data_cached(keyword, api_provider, api_key_hash, country_code)

@st.cache_data(ttl=86400, show_spinner=False)
def fetch_url_keywords_cached(url, api_provider, api_key_hash, country_code):
    if api_provider == "SE Ranking":
        return fetch_seranking_url_keywords_uncached(url, api_key_hash, country_code)
    return None

def fetch_seranking_url_keywords_uncached(url, api_key, country_code="es"):
    try:
        api_url = "https://api4.seranking.com/research/competitors"
        headers = {
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "url": url,
            "location_id": country_code,
            "limit": 50
        }
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            keywords_list = data.get('keywords', [])
            
            total_traffic = sum([kw.get('traffic', 0) for kw in keywords_list])
            keywords_str = ", ".join([kw.get('keyword', '') for kw in keywords_list[:10]])
            
            return {
                'traffic': total_traffic,
                'keywords': keywords_str,
                'keywords_count': len(keywords_list)
            }
        
        return None
    except Exception as e:
        return None

def fetch_url_keywords_api(url, api_provider, api_key, country_code):
    api_key_hash = hash_api_key(api_key)
    return fetch_url_keywords_cached(url, api_provider, api_key_hash, country_code)

# ============================================
# SCORING SYSTEM
# ============================================

def calculate_gap_score(comp_count, volume=0, has_api=False):
    if not has_api or volume == 0:
        comp_score_map = {
            3: 100,
            2: 70,
            1: 40
        }
        return comp_score_map.get(min(comp_count, 3), min(comp_count * 10, 100))
    
    # Normalizar competidores (escala hasta 10)
    comp_normalized = min((comp_count / 10) * 100, 100)
    
    # Normalizar volumen
    import math
    if volume <= 0:
        vol_normalized = 0
    elif volume < 100:
        vol_normalized = (volume / 100) * 30
    elif volume < 1000:
        vol_normalized = 30 + ((math.log10(volume) - 2) / 1) * 40
    else:
        vol_normalized = 70 + min(((math.log10(volume) - 3) / 2) * 30, 30)
    
    score = (comp_normalized * 0.4) + (vol_normalized * 0.6)
    
    return int(min(score, 100))

def get_priority_from_score(score, lang="es"):
    if score >= 90:
        return {
            'label': get_text('critical_priority', lang),
            'badge': "🔴🔴",
            'color': "#8B0000"
        }
    elif score >= 70:
        return {
            'label': get_text('high_priority', lang),
            'badge': "🔴",
            'color': "#DC143C"
        }
    elif score >= 40:
        return {
            'label': get_text('medium_priority', lang),
            'badge': "🟡",
            'color': "#FFD700"
        }
    else:
        return {
            'label': get_text('low_priority', lang),
            'badge': "🟢",
            'color': "#32CD32"
        }

# ============================================
# DOMAIN & SITEMAP UTILITIES
# ============================================

def normalize_domain(domain_input):
    if not domain_input:
        return None
    
    try:
        domain = domain_input.strip().lower()
        
        if domain.startswith(('http://', 'https://')):
            parsed = urlparse(domain)
            domain = parsed.netloc or parsed.path.split('/')[0]
        
        domain = domain.split('/')[0]
        
        if domain.startswith('www.'):
            domain = domain[4:]
        
        if not is_valid_domain(domain):
            return None
        
        return domain
    except:
        return None

def is_valid_domain(domain):
    pattern = r'^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*\.[a-z]{2,}$'
    
    if not re.match(pattern, domain):
        return False
    
    if ' ' in domain or any(c in domain for c in ['ñ', 'á', 'é', 'í', 'ó', 'ú']):
        return False
    
    if '.' not in domain:
        return False
    
    return True

def validate_domains_multiple(user_domain, competitor_domains, lang="es"):
    normalized = {
        'user': normalize_domain(user_domain)
    }
    
    if normalized['user'] is None:
        return False, {}, f"❌ {get_text('invalid_domain', lang)}: {get_text('your_domain', lang)}"
    
    for idx, comp_domain in enumerate(competitor_domains):
        if comp_domain:
            norm = normalize_domain(comp_domain)
            if norm:
                normalized[f'comp{idx+1}'] = norm
            else:
                return False, {}, f"❌ {get_text('invalid_domain', lang)}: {get_text('competitor', lang)} {idx+1}"
    
    all_domains = list(normalized.values())
    if len(all_domains) != len(set(all_domains)):
        return False, {}, f"❌ {get_text('duplicate_domains', lang)}"
    
    return True, normalized, ""

def find_sitemap(domain, timeout=15):
    base_url = f"https://{domain}"
    
    sitemap_paths = [
        '/sitemap_index.xml',
        '/sitemap.xml',
        '/sitemap-index.xml',
        '/wp-sitemap.xml',
        '/post-sitemap.xml',
        '/page-sitemap.xml',
        '/sitemap.php',
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (LocalSEOGapAnalyzer/2.6; +https://github.com/user/local-seo-gap)'
    }
    
    for path in sitemap_paths:
        try:
            url = urljoin(base_url, path)
            
            try:
                response = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)
                
                if response.status_code == 200:
                    content_type = response.headers.get('Content-Type', '').lower()
                    if 'xml' in content_type or path.endswith('.xml'):
                        return {
                            'sitemap_url': url,
                            'method': 'direct',
                            'success': True,
                            'message': f"✅ {path}"
                        }
            except:
                try:
                    response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True, stream=True)
                    
                    if response.status_code == 200:
                        content_start = next(response.iter_content(200), b'').decode('utf-8', errors='ignore')
                        
                        if '<?xml' in content_start or '<urlset' in content_start or '<sitemapindex' in content_start:
                            return {
                                'sitemap_url': url,
                                'method': 'direct',
                                'success': True,
                                'message': f"✅ {path}"
                            }
                except:
                    pass
        except Exception as e:
            continue
    
    try:
        robots_url = urljoin(base_url, '/robots.txt')
        response = requests.get(robots_url, headers=headers, timeout=timeout)
        
        if response.status_code == 200:
            for line in response.text.split('\n'):
                if line.lower().startswith('sitemap:'):
                    sitemap_url = line.split(':', 1)[1].strip()
                    
                    try:
                        check = requests.head(sitemap_url, headers=headers, timeout=timeout, allow_redirects=True)
                        if check.status_code == 200:
                            return {
                                'sitemap_url': sitemap_url,
                                'method': 'robots',
                                'success': True,
                                'message': "✅ robots.txt"
                            }
                    except:
                        try:
                            check = requests.get(sitemap_url, headers=headers, timeout=timeout, allow_redirects=True, stream=True)
                            if check.status_code == 200:
                                return {
                                    'sitemap_url': sitemap_url,
                                    'method': 'robots',
                                    'success': True,
                                    'message': "✅ robots.txt"
                                }
                        except:
                            continue
    except:
        pass
    
    return {
        'sitemap_url': None,
        'method': 'none',
        'success': False,
        'message': "⚠️ Sin sitemap"
    }

def find_all_sitemaps(domains_dict):
    results = {}
    for key, domain in domains_dict.items():
        if domain:
            results[key] = find_sitemap(domain)
    return results

# ============================================
# HOME ZONE DETECTION
# ============================================

def detect_home_zone_from_domain(domain, service_key, lang="es"):
    domain_lower = domain.lower()
    cities = get_cities(lang)
    
    subdomain_match = re.match(r'^([a-z-]+)\.', domain_lower)
    if subdomain_match:
        potential_zone = subdomain_match.group(1)
        if potential_zone in cities:
            return potential_zone
    
    service_variations = get_service_variations(service_key, lang)
    
    for city in cities:
        for service_var in service_variations:
            patterns = [
                f"{service_var}{city}",
                f"{city}{service_var}",
                f"{service_var}-{city}",
                f"{city}-{service_var}",
            ]
            
            for pattern in patterns:
                if pattern in domain_lower:
                    return city
    
    return None

def detect_home_zone_from_homepage(domain, lang="es", timeout=10):
    try:
        url = f"https://{domain}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (LocalSEOGapAnalyzer/2.6)'
        }
        
        response = requests.get(url, headers=headers, timeout=timeout)
        
        if len(response.text) < 500:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        cities = get_cities(lang)
        
        title = soup.find('title')
        if title:
            title_text = unidecode(title.get_text().lower())
            for city in cities:
                if city in title_text:
                    return city
        
        h1 = soup.find('h1')
        if h1:
            h1_text = unidecode(h1.get_text().lower())
            for city in cities:
                if city in h1_text:
                    return city
        
        return None
    except:
        return None

def detect_home_zone(domain, service_key, lang="es"):
    zone_from_domain = detect_home_zone_from_domain(domain, service_key, lang)
    if zone_from_domain:
        return {
            'zone': zone_from_domain,
            'method': 'domain',
            'confidence': 90
        }
    
    zone_from_homepage = detect_home_zone_from_homepage(domain, lang)
    if zone_from_homepage:
        return {
            'zone': zone_from_homepage,
            'method': 'homepage',
            'confidence': 70
        }
    
    return {
        'zone': None,
        'method': 'manual',
        'confidence': 0
    }

# ============================================
# URL PROCESSING & ZONE EXTRACTION
# ============================================

def clean_slug(slug, stop_words, lang="es"):
    slug = slug.strip('/')
    slug = unidecode(slug)
    slug = slug.lower()
    
    parts = slug.split('-')
    cleaned_parts = [p for p in parts if p not in stop_words and p.strip()]
    
    cleaned = '-'.join(cleaned_parts)
    
    while '--' in cleaned:
        cleaned = cleaned.replace('--', '-')
    
    return cleaned.strip('-')

def normalize_multi_word_zones(slug, lang="es"):
    connectors = {
        "es": ["el", "la", "los", "las", "de"],
        "en": ["the", "of"]
    }
    
    parts = slug.split('-')
    cleaned_parts = [p for p in parts if p not in connectors.get(lang, [])]
    
    return '-'.join(cleaned_parts)

def is_url_valid_for_service(url, service_key, lang="es", threshold=80):
    exclusion_list = get_exclusion_list(service_key, lang)
    service_variations = get_service_variations(service_key, lang)
    
    url_lower = url.lower()
    
    has_service = any(
        var in url_lower or fuzz.partial_ratio(var, url_lower) > threshold
        for var in service_variations
    )
    
    if not has_service:
        return False
    
    for excluded_service in exclusion_list:
        if fuzz.partial_ratio(excluded_service, url_lower) > threshold:
            return False
    
    return True

def calculate_confidence(zone, cities, url, lang="es"):
    validations = {
        'regex': False,
        'top_cities': False,
    }
    
    if zone and len(zone) > 2:
        validations['regex'] = True
    
    if zone in cities:
        validations['top_cities'] = True
    
    passed = sum(validations.values())
    total = len(validations)
    score = int((passed / total) * 100)
    
    return {
        'score': score,
        'validations': validations
    }

def suggest_best_slug(gap_zone, service_key, comp_zones_data_list, lang="es"):
    competitor_urls = []
    
    for comp_data in comp_zones_data_list:
        for zone, conf, url in comp_data:
            if zone == gap_zone:
                competitor_urls.append(url)
    
    if not competitor_urls:
        return {
            'slug': f"/{service_key}-{gap_zone}/",
            'urls': []
        }
    
    return {
        'slug': f"/{service_key}-{gap_zone}/",
        'urls': competitor_urls
    }

def filter_urls(urls, lang="es"):
    """Filtra URLs con validación defensiva contra None/NaN"""
    discard_patterns = [
        '/blog/', '/tag/', '/tags/', '/category/', '/categories/',
        '/author/', '/page/', '/search/',
        '/wp-content/', '/wp-admin/', '/wp-includes/',
        '/feed/', '/rss/', '/sitemap/',
    ]
    
    extensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.css', '.js', '.pdf']
    
    filtered = []
    for url in urls:
        # VALIDACIÓN DEFENSIVA: Ignorar None y no-strings
        if not url or not isinstance(url, str):
            continue
            
        try:
            if any(pattern in url.lower() for pattern in discard_patterns):
                continue
            
            if any(url.lower().endswith(ext) for ext in extensions):
                continue
            
            if '?' in url:
                continue
            
            path = urlparse(url).path
            depth = len([p for p in path.split('/') if p])
            if depth > 3:
                continue
            
            filtered.append(url)
        except Exception:
            continue
    
    return filtered

def extract_zone_from_url(url, cities, service_key, stop_words, lang="es"):
    try:
        if not is_url_valid_for_service(url, service_key, lang):
            return None, None
        
        path = urlparse(url).path
        slug = path.strip('/').split('/')[-1]
        
        if not slug:
            return None, None
        
        cleaned = clean_slug(slug, stop_words, lang)
        cleaned = normalize_multi_word_zones(cleaned, lang)
        
        for city in cities:
            if city in cleaned:
                confidence = calculate_confidence(city, cities, url, lang)
                return city, confidence
        
        return None, None
    except:
        return None, None

# ============================================
# ANALYSIS ENGINE
# ============================================

def analyze_comprehensive(user_zones_data, comp_zones_data_list, home_zone):
    user_zones = set([z for z, _, _ in user_zones_data if z])
    user_zones.discard(home_zone)
    
    all_comp_zones = set()
    comp_zones_lists = []
    
    for comp_data in comp_zones_data_list:
        comp_zones = set([z for z, _, _ in comp_data if z])
        comp_zones.discard(home_zone)
        comp_zones_lists.append(comp_zones)
        all_comp_zones.update(comp_zones)
    
    gaps = all_comp_zones - user_zones
    
    strengths = {
        'tier_1': [],
        'tier_2': []
    }
    
    for zone in user_zones:
        comp_count = sum([1 for comp_zones in comp_zones_lists if zone in comp_zones])
        
        if comp_count == 0:
            strengths['tier_1'].append(zone)
        elif comp_count == 1:
            strengths['tier_2'].append(zone)
    
    ties = []
    for zone in user_zones:
        comp_count = sum([1 for comp_zones in comp_zones_lists if zone in comp_zones])
        if comp_count >= 2:
            ties.append(zone)
    
    return {
        'gaps': list(gaps),
        'strengths': strengths,
        'ties': ties
    }

def export_to_csv(gaps_data):
    output = io.StringIO()
    df = pd.DataFrame(gaps_data)
    df.to_csv(output, index=False, encoding='utf-8-sig')
    return output.getvalue()

# ============================================
# DOMAIN HISTORY MANAGEMENT
# ============================================

def add_to_domain_history(domain, history_type='user'):
    """Agrega dominio al historial (máx 10 para user, 20 para competitors)"""
    if not domain:
        return
    
    normalized = normalize_domain(domain)
    if not normalized:
        return
    
    if history_type == 'user':
        key = 'user_domain_history'
        max_size = 10
    else:
        key = 'competitor_domain_history'
        max_size = 20
    
    if key not in st.session_state:
        st.session_state[key] = []
    
    # Evitar duplicados y mantener orden (más reciente primero)
    if normalized in st.session_state[key]:
        st.session_state[key].remove(normalized)
    
    st.session_state[key].insert(0, normalized)
    
    # Limitar tamaño
    if len(st.session_state[key]) > max_size:
        st.session_state[key] = st.session_state[key][:max_size]

def get_domain_history(history_type='user'):
    """Obtiene historial de dominios"""
    if history_type == 'user':
        key = 'user_domain_history'
    else:
        key = 'competitor_domain_history'
    
    return st.session_state.get(key, [])

def clear_domain_history():
    """Limpia todo el historial de dominios"""
    st.session_state.user_domain_history = []
    st.session_state.competitor_domain_history = []

# ============================================
# DESIGN DNA EXTRACTION
# ============================================

def extract_colors_from_css(soup):
    """Extrae colores de CSS inline y style tags"""
    colors = []
    
    # Buscar en style tags
    for style_tag in soup.find_all('style'):
        css_text = style_tag.string
        if css_text:
            # Buscar colores hex
            hex_colors = re.findall(r'#[0-9a-fA-F]{6}', css_text)
            colors.extend(hex_colors)
            
            # Buscar rgb/rgba
            rgb_colors = re.findall(r'rgba?\([^)]+\)', css_text)
            colors.extend(rgb_colors)
    
    # Buscar en atributos style inline
    for tag in soup.find_all(style=True):
        style_attr = tag.get('style', '')
        hex_colors = re.findall(r'#[0-9a-fA-F]{6}', style_attr)
        colors.extend(hex_colors)
        rgb_colors = re.findall(r'rgba?\([^)]+\)', style_attr)
        colors.extend(rgb_colors)
    
    return colors

def extract_design_dna_from_url(url, timeout=10):
    """Scraper de diseño de una URL de competidor"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (LocalSEOGapAnalyzer/2.6)'
        }
        
        response = requests.get(url, headers=headers, timeout=timeout)
        
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extraer colores
        all_colors = extract_colors_from_css(soup)
        
        # Detectar gradientes
        has_gradients = 'linear-gradient' in response.text or 'radial-gradient' in response.text
        
        # Extraer CTAs (botones con enlaces)
        cta_texts = []
        for btn in soup.find_all(['a', 'button'], limit=10):
            text = btn.get_text(strip=True)
            if text and len(text) < 50:  # Evitar textos largos
                cta_texts.append(text)
        
        # Detectar secciones comunes
        has_testimonials = bool(soup.find(['section', 'div'], class_=re.compile(r'testimon', re.I)))
        has_gallery = bool(soup.find(['section', 'div'], class_=re.compile(r'gallery|galeria', re.I)))
        has_faq = bool(soup.find(['section', 'div'], class_=re.compile(r'faq|preguntas', re.I)))
        
        return {
            'url': url,
            'colors': all_colors[:20],  # Top 20 colores
            'has_gradients': has_gradients,
            'cta_texts': cta_texts[:5],  # Top 5 CTAs
            'sections': {
                'testimonials': has_testimonials,
                'gallery': has_gallery,
                'faq': has_faq
            }
        }
        
    except Exception as e:
        return None

def consolidate_design_dna(dna_list):
    """Consolida múltiples design DNAs en un perfil unificado"""
    if not dna_list:
        return None
    
    from collections import Counter
    
    # Consolidar colores (más frecuentes)
    all_colors = []
    for dna in dna_list:
        if dna and dna.get('colors'):
            all_colors.extend(dna['colors'])
    
    color_counts = Counter(all_colors)
    top_colors = [color for color, _ in color_counts.most_common(10)]
    
    # Consolidar CTAs
    all_ctas = []
    for dna in dna_list:
        if dna and dna.get('cta_texts'):
            all_ctas.extend(dna['cta_texts'])
    
    cta_counts = Counter(all_ctas)
    top_ctas = [cta for cta, _ in cta_counts.most_common(5)]
    
    # Consolidar secciones (mayoría gana)
    sections_votes = {
        'testimonials': 0,
        'gallery': 0,
        'faq': 0
    }
    
    for dna in dna_list:
        if dna and dna.get('sections'):
            for section, has_it in dna['sections'].items():
                if has_it:
                    sections_votes[section] += 1
    
    total_sites = len([d for d in dna_list if d])
    threshold = total_sites / 2
    
    return {
        'primary_colors': top_colors[:3] if top_colors else [],
        'secondary_colors': top_colors[3:6] if len(top_colors) > 3 else [],
        'accent_colors': top_colors[6:10] if len(top_colors) > 6 else [],
        'common_ctas': top_ctas,
        'recommended_sections': {
            k: v > threshold for k, v in sections_votes.items()
        },
        'analyzed_sites': total_sites
    }

# ============================================
# SUBSERVICES DETECTION
# ============================================

SUBSERVICE_PATTERNS = {
    "es": {
        "cerrajero": ["urgente", "24h", "24-horas", "apertura", "copia-llaves", "cambio-cerradura", "bombillo", "emergencia"],
        "fontanero": ["urgente", "24h", "desatascos", "fugas", "calderas", "calentador", "emergencia", "tuberias"],
        "electricista": ["urgente", "24h", "instalacion", "reparacion", "certificados", "boletines", "emergencia", "cuadro-electrico"],
        "pintor": ["interior", "exterior", "fachadas", "gotele", "lacado", "barnizado", "presupuesto"],
        "carpintero": ["muebles", "puertas", "ventanas", "armarios", "cocinas", "tarima", "presupuesto"],
        "cristalero": ["urgente", "ventanas", "mamparas", "espejos", "doble-acristalamiento", "emergencia"],
        "reformas": ["integral", "cocina", "baño", "parcial", "vivienda", "local", "presupuesto"],
        "mudanzas": ["nacional", "internacional", "embalaje", "pianos", "oficinas", "guardamuebles", "presupuesto"],
        "limpieza": ["hogar", "oficinas", "comunidades", "fin-obra", "cristales", "presupuesto"],
        "jardinero": ["poda", "diseño", "mantenimiento", "cesped", "riego", "presupuesto"],
        "aire-acondicionado": ["instalacion", "reparacion", "mantenimiento", "recarga-gas", "limpieza", "presupuesto"],
        "albañil": ["obras", "reformas", "fachadas", "tabiques", "solados", "presupuesto"],
        "tecnico-climatizacion": ["instalacion", "reparacion", "mantenimiento", "calderas", "aerotermia", "presupuesto"],
        "instalador-gas": ["calderas", "calentadores", "certificados", "revision", "instalacion", "presupuesto"],
        "tapicero": ["sofas", "sillas", "cortinas", "cabeceros", "restauracion", "presupuesto"],
    },
    "en": {
        "locksmith": ["emergency", "24-hour", "24h", "car-keys", "lock-change", "lock-repair", "rekey"],
        "plumber": ["emergency", "24-hour", "drain-cleaning", "leak-repair", "water-heater", "pipe-repair"],
        "electrician": ["emergency", "24-hour", "installation", "repair", "panel-upgrade", "outlets", "lighting"],
        "painter": ["interior", "exterior", "cabinet-painting", "deck-staining", "estimate"],
        "carpenter": ["cabinets", "doors", "windows", "framing", "decks", "furniture", "estimate"],
        "glazier": ["emergency", "window-repair", "shower-doors", "mirrors", "glass-replacement"],
        "remodeling": ["kitchen", "bathroom", "basement", "full-house", "additions", "estimate"],
        "moving": ["local", "long-distance", "packing", "piano", "office", "storage", "estimate"],
        "cleaning": ["house", "office", "post-construction", "deep-cleaning", "windows", "estimate"],
        "gardener": ["lawn-care", "landscaping", "tree-trimming", "irrigation", "design", "estimate"],
        "hvac": ["installation", "repair", "maintenance", "ac-repair", "heating-repair", "estimate"],
        "handyman": ["repairs", "installation", "assembly", "drywall", "painting", "estimate"],
        "roofer": ["repair", "replacement", "inspection", "gutters", "shingles", "estimate"],
        "mason": ["brickwork", "stonework", "chimneys", "patios", "walls", "estimate"],
        "pest-control": ["termites", "rodents", "bed-bugs", "ants", "mosquitoes", "estimate"],
    }
}

def extract_subservices_from_urls(urls, service_key, lang="es"):
    """Detecta subservicios del sitemap del usuario"""
    subservices = []
    patterns = SUBSERVICE_PATTERNS.get(lang, {}).get(service_key, [])
    
    for url in urls:
        if not url or not isinstance(url, str):
            continue
        
        url_lower = url.lower()
        
        # Buscar patrones de subservicios
        for pattern in patterns:
            if pattern in url_lower:
                # Extraer título del slug
                path = urlparse(url).path
                slug = path.strip('/').split('/')[-1]
                
                # Crear entrada de subservicio
                subservices.append({
                    'name': slug.replace('-', ' ').title(),
                    'url': url,
                    'pattern': pattern
                })
                break
    
    # Eliminar duplicados por URL
    seen = set()
    unique_subservices = []
    for sub in subservices:
        if sub['url'] not in seen:
            seen.add(sub['url'])
            unique_subservices.append(sub)
    
    return unique_subservices

# ============================================
# HTML TEMPLATE SYSTEM
# ============================================

def get_base_template(lang="es"):
    """Retorna plantilla HTML base responsive para cualquier servicio"""
    
    if lang == "es":
        template = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{SERVICIO_DISPLAY} en {ZONA_DISPLAY} - Servicio profesional {HORA_SERVICIO}. Presupuesto sin compromiso. Llamar ahora.">
    <title>{SERVICIO_DISPLAY} en {ZONA_DISPLAY} | Servicio Profesional {HORA_SERVICIO}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 60px 0; text-align: center; }
        h1 { font-size: 2.5rem; margin-bottom: 1rem; }
        .subtitle { font-size: 1.2rem; opacity: 0.9; }
        .cta-button { display: inline-block; background: #ff6b6b; color: white; padding: 15px 40px; text-decoration: none; border-radius: 50px; font-weight: bold; margin-top: 20px; transition: transform 0.3s; }
        .cta-button:hover { transform: scale(1.05); }
        section { padding: 60px 0; }
        h2 { font-size: 2rem; margin-bottom: 1.5rem; color: #2c3e50; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; margin-top: 30px; }
        .card { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        .card h3 { color: #667eea; margin-bottom: 15px; }
        .zones-list, .services-list { list-style: none; margin-top: 20px; }
        .zones-list li, .services-list li { padding: 10px 0; border-bottom: 1px solid #eee; }
        .zones-list a, .services-list a { color: #667eea; text-decoration: none; font-weight: 500; }
        .zones-list a:hover, .services-list a:hover { text-decoration: underline; }
        .faq { background: #f8f9fa; }
        .faq-item { background: white; padding: 20px; margin-bottom: 15px; border-radius: 8px; }
        .faq-item h3 { font-size: 1.1rem; color: #2c3e50; margin-bottom: 10px; }
        footer { background: #2c3e50; color: white; text-align: center; padding: 40px 0; }
        @media (max-width: 768px) {
            h1 { font-size: 1.8rem; }
            .grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>{SERVICIO_DISPLAY} en {ZONA_DISPLAY}</h1>
            <p class="subtitle">Servicio profesional de {SERVICIO} en {ZONA_DISPLAY} {HORA_SERVICIO}</p>
            <a href="tel:{TELEFONO}" class="cta-button">☎ Llamar Ahora</a>
        </div>
    </header>

    <section>
        <div class="container">
            <h2>Tu {SERVICIO_DISPLAY} de confianza en {ZONA_DISPLAY}</h2>
            <p>Ofrecemos servicios profesionales de {SERVICIO} en {ZONA_DISPLAY} con años de experiencia. Nuestro equipo está cualificado para resolver cualquier problema relacionado con {SERVICIO_DESCRIPCION}.</p>
            
            <div class="grid">
                <div class="card">
                    <h3>✓ Profesionales Cualificados</h3>
                    <p>Equipo con años de experiencia en {SERVICIO}</p>
                </div>
                <div class="card">
                    <h3>✓ Presupuesto Sin Compromiso</h3>
                    <p>Valoración gratuita antes de iniciar el trabajo</p>
                </div>
                <div class="card">
                    <h3>✓ Garantía de Servicio</h3>
                    <p>Todos nuestros trabajos están garantizados</p>
                </div>
            </div>
        </div>
    </section>

    <section class="services-section">
        <div class="container">
            <h2>Nuestros Servicios de {SERVICIO_DISPLAY}</h2>
            {ENLACES_SUBSERVICIOS}
        </div>
    </section>

    <section>
        <div class="container">
            <h2>También atendemos en zonas cercanas a {ZONA_DISPLAY}</h2>
            {ENLACES_ZONAS}
        </div>
    </section>

    <section class="faq">
        <div class="container">
            <h2>Preguntas Frecuentes</h2>
            {FAQ_CONTENT}
        </div>
    </section>

    <footer>
        <div class="container">
            <p>&copy; 2026 {SERVICIO_DISPLAY} {ZONA_DISPLAY}. Todos los derechos reservados.</p>
            <p>Servicio profesional de {SERVICIO} en {ZONA_DISPLAY} y alrededores</p>
        </div>
    </footer>

    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": "{SERVICIO_DISPLAY} {ZONA_DISPLAY}",
        "description": "Servicio profesional de {SERVICIO} en {ZONA_DISPLAY}",
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "{ZONA_DISPLAY}",
            "addressCountry": "ES"
        },
        "telephone": "{TELEFONO}",
        "areaServed": "{ZONA_DISPLAY}"
    }
    </script>
</body>
</html>
"""
    else:  # English
        template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{SERVICIO_DISPLAY} in {ZONA_DISPLAY} - Professional {HORA_SERVICIO} service. Free estimates. Call now.">
    <title>{SERVICIO_DISPLAY} in {ZONA_DISPLAY} | Professional {HORA_SERVICIO} Service</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 60px 0; text-align: center; }
        h1 { font-size: 2.5rem; margin-bottom: 1rem; }
        .subtitle { font-size: 1.2rem; opacity: 0.9; }
        .cta-button { display: inline-block; background: #ff6b6b; color: white; padding: 15px 40px; text-decoration: none; border-radius: 50px; font-weight: bold; margin-top: 20px; transition: transform 0.3s; }
        .cta-button:hover { transform: scale(1.05); }
        section { padding: 60px 0; }
        h2 { font-size: 2rem; margin-bottom: 1.5rem; color: #2c3e50; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; margin-top: 30px; }
        .card { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        .card h3 { color: #667eea; margin-bottom: 15px; }
        .zones-list, .services-list { list-style: none; margin-top: 20px; }
        .zones-list li, .services-list li { padding: 10px 0; border-bottom: 1px solid #eee; }
        .zones-list a, .services-list a { color: #667eea; text-decoration: none; font-weight: 500; }
        .zones-list a:hover, .services-list a:hover { text-decoration: underline; }
        .faq { background: #f8f9fa; }
        .faq-item { background: white; padding: 20px; margin-bottom: 15px; border-radius: 8px; }
        .faq-item h3 { font-size: 1.1rem; color: #2c3e50; margin-bottom: 10px; }
        footer { background: #2c3e50; color: white; text-align: center; padding: 40px 0; }
        @media (max-width: 768px) {
            h1 { font-size: 1.8rem; }
            .grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>{SERVICIO_DISPLAY} in {ZONA_DISPLAY}</h1>
            <p class="subtitle">Professional {SERVICIO} service in {ZONA_DISPLAY} {HORA_SERVICIO}</p>
            <a href="tel:{TELEFONO}" class="cta-button">☎ Call Now</a>
        </div>
    </header>

    <section>
        <div class="container">
            <h2>Your Trusted {SERVICIO_DISPLAY} in {ZONA_DISPLAY}</h2>
            <p>We offer professional {SERVICIO} services in {ZONA_DISPLAY} with years of experience. Our qualified team can solve any problem related to {SERVICIO_DESCRIPCION}.</p>
            
            <div class="grid">
                <div class="card">
                    <h3>✓ Qualified Professionals</h3>
                    <p>Team with years of experience in {SERVICIO}</p>
                </div>
                <div class="card">
                    <h3>✓ Free Estimates</h3>
                    <p>Free assessment before starting work</p>
                </div>
                <div class="card">
                    <h3>✓ Service Guarantee</h3>
                    <p>All our work is guaranteed</p>
                </div>
            </div>
        </div>
    </section>

    <section class="services-section">
        <div class="container">
            <h2>Our {SERVICIO_DISPLAY} Services</h2>
            {ENLACES_SUBSERVICIOS}
        </div>
    </section>

    <section>
        <div class="container">
            <h2>We also serve areas near {ZONA_DISPLAY}</h2>
            {ENLACES_ZONAS}
        </div>
    </section>

    <section class="faq">
        <div class="container">
            <h2>Frequently Asked Questions</h2>
            {FAQ_CONTENT}
        </div>
    </section>

    <footer>
        <div class="container">
            <p>&copy; 2026 {SERVICIO_DISPLAY} {ZONA_DISPLAY}. All rights reserved.</p>
            <p>Professional {SERVICIO} service in {ZONA_DISPLAY} and surrounding areas</p>
        </div>
    </footer>

    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": "{SERVICIO_DISPLAY} {ZONA_DISPLAY}",
        "description": "Professional {SERVICIO} service in {ZONA_DISPLAY}",
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "{ZONA_DISPLAY}",
            "addressCountry": "US"
        },
        "telephone": "{TELEFONO}",
        "areaServed": "{ZONA_DISPLAY}"
    }
    </script>
</body>
</html>
"""
    
    return template

def get_service_description(service_key, lang="es"):
    """Retorna descripción específica del servicio"""
    descriptions = {
        "es": {
            "cerrajero": "apertura de puertas, cambio de cerraduras, copia de llaves y servicios de emergencia",
            "fontanero": "reparación de fugas, desatascos, instalación de calderas y servicios de fontanería",
            "electricista": "instalaciones eléctricas, reparaciones, certificados y servicios eléctricos",
            "pintor": "pintura interior y exterior, lacado, restauración y acabados profesionales",
            "carpintero": "fabricación e instalación de muebles, puertas, ventanas y trabajos en madera",
            "cristalero": "instalación y reparación de cristales, ventanas, mamparas y espejos",
            "reformas": "reformas integrales, cocinas, baños y remodelaciones completas",
            "mudanzas": "mudanzas locales, nacionales, embalaje y almacenamiento",
            "limpieza": "limpieza de hogares, oficinas, comunidades y servicios de limpieza profesional",
            "jardinero": "diseño, mantenimiento de jardines, poda y servicios de jardinería",
            "aire-acondicionado": "instalación, reparación y mantenimiento de sistemas de climatización",
            "albañil": "obras de albañilería, reformas, fachadas y trabajos de construcción",
            "tecnico-climatizacion": "instalación y mantenimiento de sistemas de calefacción y climatización",
            "instalador-gas": "instalación de calderas, calentadores, certificados y revisiones de gas",
            "tapicero": "tapizado de sofás, sillas, cortinas y restauración de muebles",
        },
        "en": {
            "locksmith": "lock changes, key duplication, emergency lockout services and security solutions",
            "plumber": "leak repairs, drain cleaning, water heater installation and plumbing services",
            "electrician": "electrical installations, repairs, panel upgrades and electrical services",
            "painter": "interior and exterior painting, cabinet refinishing and professional finishes",
            "carpenter": "custom woodwork, cabinet installation, trim work and carpentry services",
            "glazier": "window installation, glass repair, shower doors and glazing services",
            "remodeling": "kitchen remodels, bathroom renovations and complete home renovations",
            "moving": "local and long-distance moves, packing services and storage solutions",
            "cleaning": "house cleaning, office cleaning, deep cleaning and professional cleaning services",
            "gardener": "landscape design, lawn maintenance, tree care and gardening services",
            "hvac": "AC installation, heating repair, maintenance and HVAC services",
            "handyman": "home repairs, installations, assembly and handyman services",
            "roofer": "roof repairs, replacements, inspections and roofing services",
            "mason": "brickwork, stonework, concrete work and masonry services",
            "pest-control": "pest inspections, treatments, prevention and pest control services",
        }
    }
    
    return descriptions.get(lang, {}).get(service_key, "servicios profesionales")

def get_service_hora(service_key, lang="es"):
    """Determina si el servicio es típicamente 24h o horario normal"""
    emergency_services = ["cerrajero", "fontanero", "electricista", "cristalero", 
                         "locksmith", "plumber", "electrician", "glazier"]
    
    if service_key in emergency_services:
        return "24 horas" if lang == "es" else "24/7"
    else:
        return "" if lang == "es" else ""

def get_faq_content(service_key, zone, lang="es"):
    """Genera FAQs específicas por servicio"""
    if lang == "es":
        faqs = {
            "cerrajero": [
                ("¿Cuánto cuesta un cerrajero en {ZONA}?", "El precio varía según el tipo de servicio. Ofrecemos presupuesto sin compromiso antes de realizar cualquier trabajo."),
                ("¿Tienen servicio de cerrajero 24 horas en {ZONA}?", "Sí, ofrecemos servicio de emergencia las 24 horas del día, los 7 días de la semana en {ZONA}."),
                ("¿Cuánto tardan en llegar?", "Nuestro tiempo de respuesta en {ZONA} es generalmente de 20-30 minutos dependiendo de la zona específica."),
            ],
            "fontanero": [
                ("¿Cuánto cuesta un fontanero en {ZONA}?", "El coste depende del tipo de reparación. Realizamos presupuestos gratuitos sin compromiso."),
                ("¿Atienden emergencias de fontanería?", "Sí, disponemos de servicio de urgencias 24h para fugas y averías graves en {ZONA}."),
                ("¿Qué servicios de fontanería ofrecen?", "Reparación de fugas, desatascos, instalación de calderas y todo tipo de servicios de fontanería."),
            ],
        }
    else:
        faqs = {
            "locksmith": [
                ("How much does a locksmith cost in {ZONA}?", "Pricing varies by service type. We provide free estimates before starting any work."),
                ("Do you have 24-hour locksmith service in {ZONA}?", "Yes, we offer 24/7 emergency locksmith services in {ZONA}."),
                ("How quickly can you arrive?", "Our typical response time in {ZONA} is 20-30 minutes depending on your exact location."),
            ],
            "plumber": [
                ("How much does a plumber cost in {ZONA}?", "Cost depends on the repair needed. We provide free estimates with no obligation."),
                ("Do you handle plumbing emergencies?", "Yes, we have 24-hour emergency service for leaks and serious issues in {ZONA}."),
                ("What plumbing services do you offer?", "Leak repairs, drain cleaning, water heater installation and all plumbing services."),
            ],
        }
    
    # FAQs genéricas si no hay específicas
    default_faqs = [
        ("¿Por qué elegirnos?" if lang == "es" else "Why choose us?", 
         "Somos profesionales con años de experiencia en {ZONA}." if lang == "es" else "We are professionals with years of experience in {ZONA}."),
        ("¿Ofrecen garantía?" if lang == "es" else "Do you offer warranty?", 
         "Sí, todos nuestros trabajos tienen garantía." if lang == "es" else "Yes, all our work is guaranteed."),
    ]
    
    service_faqs = faqs.get(service_key, default_faqs)
    
    html = ""
    for question, answer in service_faqs:
        q = question.replace("{ZONA}", zone.title())
        a = answer.replace("{ZONA}", zone.title())
        html += f'<div class="faq-item"><h3>{q}</h3><p>{a}</p></div>\n'
    
    return html

def render_template(service_key, zone, user_zones, subservices, lang="es", telefono="+34900000000"):
    """Renderiza plantilla HTML con datos reales"""
    template = get_base_template(lang)
    
    # Datos básicos
    service_display = SERVICES.get(lang, {}).get(service_key, service_key).title()
    zona_display = zone.replace('-', ' ').title()
    servicio_descripcion = get_service_description(service_key, lang)
    hora_servicio = get_service_hora(service_key, lang)
    
    # Enlaces a zonas cercanas
    enlaces_zonas_html = '<ul class="zones-list">\n'
    for z in sorted(user_zones)[:10]:  # Máximo 10 zonas
        if z != zone:  # No enlazar a sí misma
            z_display = z.replace('-', ' ').title()
            enlaces_zonas_html += f'    <li><a href="/{service_key}-{z}/">{service_display} en {z_display}</a></li>\n'
    enlaces_zonas_html += '</ul>'
    
    # Enlaces a subservicios
    if subservices:
        enlaces_sub_html = '<ul class="services-list">\n'
        for sub in subservices[:8]:  # Máximo 8 subservicios
            enlaces_sub_html += f'    <li><a href="{sub["url"]}">{sub["name"]}</a></li>\n'
        enlaces_sub_html += '</ul>'
    else:
        enlaces_sub_html = '<p>' + ('Consulta todos nuestros servicios especializados.' if lang == 'es' else 'Check out all our specialized services.') + '</p>'
    
    # FAQ
    faq_html = get_faq_content(service_key, zona_display, lang)
    
    # Reemplazar placeholders
    html = template.replace('{SERVICIO}', service_key)
    html = html.replace('{SERVICIO_DISPLAY}', service_display)
    html = html.replace('{ZONA}', zone)
    html = html.replace('{ZONA_DISPLAY}', zona_display)
    html = html.replace('{SERVICIO_DESCRIPCION}', servicio_descripcion)
    html = html.replace('{HORA_SERVICIO}', hora_servicio)
    html = html.replace('{TELEFONO}', telefono)
    html = html.replace('{ENLACES_ZONAS}', enlaces_zonas_html)
    html = html.replace('{ENLACES_SUBSERVICIOS}', enlaces_sub_html)
    html = html.replace('{FAQ_CONTENT}', faq_html)
    
    return html

# ============================================
# STREAMLIT UI
# ============================================

st.set_page_config(
    page_title="Local SEO Geo-Gap Analyzer",
    page_icon="🎯",
    layout="wide"
)

if 'lang' not in st.session_state:
    st.session_state.lang = 'es'

if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False

if 'gaps_data' not in st.session_state:
    st.session_state.gaps_data = []

if 'api_enabled' not in st.session_state:
    st.session_state.api_enabled = False

if 'show_extra_competitors' not in st.session_state:
    st.session_state.show_extra_competitors = False

if 'user_domain_history' not in st.session_state:
    st.session_state.user_domain_history = []

if 'competitor_domain_history' not in st.session_state:
    st.session_state.competitor_domain_history = []

if 'selected_service' not in st.session_state:
    st.session_state.selected_service = None

st.title(get_text('title', st.session_state.lang))

with st.sidebar:
    st.subheader(get_text('language', st.session_state.lang))
    lang_option = st.radio(
        "Language selector",
        options=['🇪🇸 Español', '🇬🇧 English'],
        index=0 if st.session_state.lang == 'es' else 1,
        label_visibility='collapsed'
    )
    
    new_lang = 'es' if '🇪🇸' in lang_option else 'en'
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.session_state.analysis_done = False
        st.rerun()
    
    st.divider()
    
    st.subheader(get_text('api_optional', st.session_state.lang))
    
    api_enabled = st.checkbox(
        get_text('enable_api', st.session_state.lang),
        value=st.session_state.api_enabled
    )
    
    if api_enabled:
        api_provider = st.selectbox(
            get_text('api_provider', st.session_state.lang),
            options=["SE Ranking", "Semrush", "Ahrefs"],
            index=0
        )
        
        api_key = st.text_input(
            get_text('api_key', st.session_state.lang),
            type="password",
            placeholder=get_text('api_key_placeholder', st.session_state.lang)
        )
        
        country_code = st.selectbox(
            get_text('country_code', st.session_state.lang),
            options=["es", "us", "uk", "fr", "de", "it"],
            index=0
        )
        
        st.session_state.api_enabled = True
        st.session_state.api_provider = api_provider
        st.session_state.api_key = api_key
        st.session_state.country_code = country_code
        
        if api_key:
            st.caption("✅ " + get_text('using_cache', st.session_state.lang))
    else:
        st.session_state.api_enabled = False

lang = st.session_state.lang

st.header("⚙️ " + ("Configuración" if lang == "es" else "Configuration"))

services_dict = get_services(lang)
service_label = get_text('service', lang)
selected_service_display = st.selectbox(
    service_label,
    options=list(services_dict.values()),
    index=0
)
selected_service = [k for k, v in services_dict.items() if v == selected_service_display][0]
st.session_state.selected_service = selected_service

st.divider()

col1, col2 = st.columns(2)

with col1:
    # Obtener historial de dominios de usuario
    user_history = get_domain_history('user')
    
    if user_history:
        domain_options = [get_text('new_domain', lang)] + user_history
        selected_user_domain = st.selectbox(
            f"🏠 {get_text('your_domain', lang)} *",
            options=domain_options,
            index=0,
            key='user_domain_select'
        )
        
        if selected_user_domain == get_text('new_domain', lang):
            user_domain_input = st.text_input(
                get_text('your_domain', lang),
                placeholder=get_text('domain_placeholder', lang),
                help="Solo el dominio, sin https:// ni rutas",
                label_visibility='collapsed',
                key='user_domain_manual'
            )
        else:
            user_domain_input = selected_user_domain
            st.caption(f"✅ {selected_user_domain}")
    else:
        user_domain_input = st.text_input(
            f"🏠 {get_text('your_domain', lang)} *",
            placeholder=get_text('domain_placeholder', lang),
            help="Solo el dominio, sin https:// ni rutas"
        )
    
    user_sitemap_input = st.text_input(
        f"📄 Sitemap URL (opcional)",
        placeholder="https://tudominio.com/sitemap.xml",
        help="Si tu sitemap no se detecta automáticamente, pégalo aquí"
    )

with col2:
    if user_domain_input:
        normalized = normalize_domain(user_domain_input)
        if normalized:
            st.success(f"✅ {normalized}")
        else:
            st.error(get_text('invalid_domain', lang))
    
    # Botón para limpiar historial
    if user_history or get_domain_history('competitor'):
        if st.button(get_text('clear_history', lang), key='clear_history_btn'):
            clear_domain_history()
            st.success(get_text('history_cleared', lang))
            st.rerun()

st.divider()

st.subheader(f"🔍 {get_text('competitors_required', lang)}")

# Obtener historial de competidores
comp_history = get_domain_history('competitor')

col1, col2 = st.columns(2)
with col1:
    # Competidor 1
    if comp_history:
        comp1_options = [get_text('new_domain', lang)] + comp_history
        selected_comp1 = st.selectbox(
            f"{get_text('competitor', lang)} 1 *",
            options=comp1_options,
            index=0,
            key='comp1_select'
        )
        
        if selected_comp1 == get_text('new_domain', lang):
            comp1_input = st.text_input(
                get_text('competitor', lang) + " 1",
                placeholder=get_text('domain_placeholder', lang),
                label_visibility='collapsed',
                key='comp1_manual'
            )
        else:
            comp1_input = selected_comp1
            st.caption(f"✅ {selected_comp1}")
    else:
        comp1_input = st.text_input(
            f"{get_text('competitor', lang)} 1 *",
            placeholder=get_text('domain_placeholder', lang)
        )
    
    # Competidor 2
    if comp_history:
        comp2_options = [get_text('new_domain', lang)] + comp_history
        selected_comp2 = st.selectbox(
            f"{get_text('competitor', lang)} 2 *",
            options=comp2_options,
            index=0,
            key='comp2_select'
        )
        
        if selected_comp2 == get_text('new_domain', lang):
            comp2_input = st.text_input(
                get_text('competitor', lang) + " 2",
                placeholder=get_text('domain_placeholder', lang),
                label_visibility='collapsed',
                key='comp2_manual'
            )
        else:
            comp2_input = selected_comp2
            st.caption(f"✅ {selected_comp2}")
    else:
        comp2_input = st.text_input(
            f"{get_text('competitor', lang)} 2 *",
            placeholder=get_text('domain_placeholder', lang)
        )

with col2:
    # Competidor 3
    if comp_history:
        comp3_options = [get_text('new_domain', lang)] + comp_history
        selected_comp3 = st.selectbox(
            f"{get_text('competitor', lang)} 3 *",
            options=comp3_options,
            index=0,
            key='comp3_select'
        )
        
        if selected_comp3 == get_text('new_domain', lang):
            comp3_input = st.text_input(
                get_text('competitor', lang) + " 3",
                placeholder=get_text('domain_placeholder', lang),
                label_visibility='collapsed',
                key='comp3_manual'
            )
        else:
            comp3_input = selected_comp3
            st.caption(f"✅ {selected_comp3}")
    else:
        comp3_input = st.text_input(
            f"{get_text('competitor', lang)} 3 *",
            placeholder=get_text('domain_placeholder', lang)
        )
    
    valid_required = sum([
        bool(normalize_domain(comp1_input)),
        bool(normalize_domain(comp2_input)),
        bool(normalize_domain(comp3_input))
    ])
    
    if valid_required < 3:
        st.warning(f"⚠️ {valid_required}/3 " + ("competidores válidos" if lang == "es" else "valid competitors"))
    else:
        st.success(f"✅ {valid_required}/3 " + ("competidores válidos" if lang == "es" else "valid competitors"))

with st.expander(f"➕ {get_text('add_competitors', lang)}", expanded=st.session_state.show_extra_competitors):
    st.caption(("Agregar más competidores mejora la precisión del análisis" if lang == "es" else "Adding more competitors improves analysis accuracy"))
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Competidores 4-7 con autocompletado
        if comp_history:
            comp4_options = [get_text('new_domain', lang)] + comp_history
            selected_comp4 = st.selectbox(f"{get_text('competitor', lang)} 4", options=comp4_options, index=0, key="comp4_select")
            comp4_input = st.text_input("Comp 4", placeholder=get_text('domain_placeholder', lang), label_visibility='collapsed', key="comp4_manual") if selected_comp4 == get_text('new_domain', lang) else selected_comp4
            if selected_comp4 != get_text('new_domain', lang):
                st.caption(f"✅ {selected_comp4}")
        else:
            comp4_input = st.text_input(f"{get_text('competitor', lang)} 4", placeholder=get_text('domain_placeholder', lang), key="comp4")
        
        if comp_history:
            comp5_options = [get_text('new_domain', lang)] + comp_history
            selected_comp5 = st.selectbox(f"{get_text('competitor', lang)} 5", options=comp5_options, index=0, key="comp5_select")
            comp5_input = st.text_input("Comp 5", placeholder=get_text('domain_placeholder', lang), label_visibility='collapsed', key="comp5_manual") if selected_comp5 == get_text('new_domain', lang) else selected_comp5
            if selected_comp5 != get_text('new_domain', lang):
                st.caption(f"✅ {selected_comp5}")
        else:
            comp5_input = st.text_input(f"{get_text('competitor', lang)} 5", placeholder=get_text('domain_placeholder', lang), key="comp5")
        
        if comp_history:
            comp6_options = [get_text('new_domain', lang)] + comp_history
            selected_comp6 = st.selectbox(f"{get_text('competitor', lang)} 6", options=comp6_options, index=0, key="comp6_select")
            comp6_input = st.text_input("Comp 6", placeholder=get_text('domain_placeholder', lang), label_visibility='collapsed', key="comp6_manual") if selected_comp6 == get_text('new_domain', lang) else selected_comp6
            if selected_comp6 != get_text('new_domain', lang):
                st.caption(f"✅ {selected_comp6}")
        else:
            comp6_input = st.text_input(f"{get_text('competitor', lang)} 6", placeholder=get_text('domain_placeholder', lang), key="comp6")
        
        if comp_history:
            comp7_options = [get_text('new_domain', lang)] + comp_history
            selected_comp7 = st.selectbox(f"{get_text('competitor', lang)} 7", options=comp7_options, index=0, key="comp7_select")
            comp7_input = st.text_input("Comp 7", placeholder=get_text('domain_placeholder', lang), label_visibility='collapsed', key="comp7_manual") if selected_comp7 == get_text('new_domain', lang) else selected_comp7
            if selected_comp7 != get_text('new_domain', lang):
                st.caption(f"✅ {selected_comp7}")
        else:
            comp7_input = st.text_input(f"{get_text('competitor', lang)} 7", placeholder=get_text('domain_placeholder', lang), key="comp7")
    
    with col2:
        # Competidores 8-10 con autocompletado
        if comp_history:
            comp8_options = [get_text('new_domain', lang)] + comp_history
            selected_comp8 = st.selectbox(f"{get_text('competitor', lang)} 8", options=comp8_options, index=0, key="comp8_select")
            comp8_input = st.text_input("Comp 8", placeholder=get_text('domain_placeholder', lang), label_visibility='collapsed', key="comp8_manual") if selected_comp8 == get_text('new_domain', lang) else selected_comp8
            if selected_comp8 != get_text('new_domain', lang):
                st.caption(f"✅ {selected_comp8}")
        else:
            comp8_input = st.text_input(f"{get_text('competitor', lang)} 8", placeholder=get_text('domain_placeholder', lang), key="comp8")
        
        if comp_history:
            comp9_options = [get_text('new_domain', lang)] + comp_history
            selected_comp9 = st.selectbox(f"{get_text('competitor', lang)} 9", options=comp9_options, index=0, key="comp9_select")
            comp9_input = st.text_input("Comp 9", placeholder=get_text('domain_placeholder', lang), label_visibility='collapsed', key="comp9_manual") if selected_comp9 == get_text('new_domain', lang) else selected_comp9
            if selected_comp9 != get_text('new_domain', lang):
                st.caption(f"✅ {selected_comp9}")
        else:
            comp9_input = st.text_input(f"{get_text('competitor', lang)} 9", placeholder=get_text('domain_placeholder', lang), key="comp9")
        
        if comp_history:
            comp10_options = [get_text('new_domain', lang)] + comp_history
            selected_comp10 = st.selectbox(f"{get_text('competitor', lang)} 10", options=comp10_options, index=0, key="comp10_select")
            comp10_input = st.text_input("Comp 10", placeholder=get_text('domain_placeholder', lang), label_visibility='collapsed', key="comp10_manual") if selected_comp10 == get_text('new_domain', lang) else selected_comp10
            if selected_comp10 != get_text('new_domain', lang):
                st.caption(f"✅ {selected_comp10}")
        else:
            comp10_input = st.text_input(f"{get_text('competitor', lang)} 10", placeholder=get_text('domain_placeholder', lang), key="comp10")
        
        optional_comps = [comp4_input, comp5_input, comp6_input, comp7_input, comp8_input, comp9_input, comp10_input]
        valid_optional = sum([bool(normalize_domain(c)) for c in optional_comps if c])
        
        if valid_optional > 0:
            st.info(f"✨ +{valid_optional} " + ("competidores adicionales" if lang == "es" else "additional competitors"))

st.divider()

all_competitor_inputs = [comp1_input, comp2_input, comp3_input, comp4_input, comp5_input, comp6_input, comp7_input, comp8_input, comp9_input, comp10_input]
total_valid = sum([bool(normalize_domain(c)) for c in all_competitor_inputs if c])

if total_valid >= 3:
    st.success(f"🎯 {get_text('total_competitors', lang)}: **{total_valid}**")

analyze_button = st.button(
    get_text('analyze_button', lang),
    type="primary",
    use_container_width=True,
    disabled=valid_required < 3 or not user_domain_input
)

if analyze_button:
    st.session_state.analysis_done = False
    st.session_state.gaps_data = []
    
    competitor_domains = []
    for comp_input in all_competitor_inputs:
        if comp_input:
            norm = normalize_domain(comp_input)
            if norm:
                competitor_domains.append(comp_input)
    
    success, normalized_domains, error_msg = validate_domains_multiple(
        user_domain_input, competitor_domains, lang
    )
    
    if not success:
        st.error(error_msg)
        st.stop()
    
    st.subheader("🔍 " + get_text('extracting_urls', lang))
    
    if user_sitemap_input and user_sitemap_input.strip():
        sitemap_results = {
            'user': {
                'sitemap_url': user_sitemap_input.strip(),
                'method': 'manual',
                'success': True,
                'message': '✅ Manual'
            }
        }
    else:
        sitemap_results = {'user': find_sitemap(normalized_domains['user'])}
    
    comp_domains_dict = {k: v for k, v in normalized_domains.items() if k.startswith('comp')}
    with st.spinner(''):
        comp_sitemaps = find_all_sitemaps(comp_domains_dict)
    
    sitemap_results.update(comp_sitemaps)
    
    for key, result in sitemap_results.items():
        domain = normalized_domains[key]
        
        if key == 'user':
            label = get_text('your_domain', lang)
        else:
            comp_num = key.replace('comp', '')
            label = f"{get_text('competitor', lang)} {comp_num}"
        
        if result['success']:
            st.success(f"{label}: **{domain}** → {result['message']}")
        else:
            st.warning(f"{label}: **{domain}** → {result['message']}")
    
    st.divider()
    
    st.subheader("🏠 " + get_text('home_zone_detected', lang))
    
    with st.spinner(''):
        home_zone_result = detect_home_zone(
            normalized_domains['user'],
            selected_service,
            lang
        )
    
    if home_zone_result['zone']:
        home_zone = home_zone_result['zone']
        st.success(f"✅ {get_text('home_zone_detected', lang)}: **{home_zone.title()}**")
    else:
        cities = get_cities(lang)
        home_zone = st.selectbox(
            get_text('select_city', lang),
            options=cities,
            index=0
        )
        st.info(f"ℹ️ Zona seleccionada manualmente: **{home_zone.title()}**")
    
    st.subheader("📊 " + get_text('processing', lang))
    
    all_urls = {}
    all_counts = {}
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    timer_placeholder = st.empty()
    start_time = time.time()
    
    total_domains = len(sitemap_results)
    
    for idx, (key, result) in enumerate(sitemap_results.items()):
        domain = normalized_domains[key]
        
        elapsed = int(time.time() - start_time)
        timer_placeholder.caption(f"⏱️ Tiempo transcurrido: {elapsed}s")
        
        status_text.text(f"{get_text('processing', lang)}: {domain}")
        
        if result['success']:
            urls, total = extract_urls_from_sitemap_cached(result['sitemap_url'])
            all_urls[key] = urls
            all_counts[key] = {'extracted': len(urls), 'total': total}
        else:
            all_urls[key] = []
            all_counts[key] = {'extracted': 0, 'total': 0}
        
        progress_bar.progress((idx + 1) / total_domains)
    
    status_text.empty()
    progress_bar.empty()
    timer_placeholder.empty()
    
    cities = get_cities(lang)
    stop_words = get_stop_words(lang)
    
    timer_placeholder = st.empty()
    start_time = time.time()
    
    all_zones_data = {}
    for key, urls in all_urls.items():
        elapsed = int(time.time() - start_time)
        timer_placeholder.caption(f"⏱️ {get_text('processing', lang)}: {elapsed}s")
        
        filtered = filter_urls(urls, lang)
        zones_data = []
        
        for url in filtered:
            zone, confidence = extract_zone_from_url(url, cities, selected_service, stop_words, lang)
            if zone:
                zones_data.append((zone, confidence, url))
        
        all_zones_data[key] = zones_data
    
    timer_placeholder.empty()
    
    comp_zones_list = [all_zones_data[k] for k in all_zones_data.keys() if k.startswith('comp')]
    
    analysis = analyze_comprehensive(
        all_zones_data['user'],
        comp_zones_list,
        home_zone
    )
    
    gaps_data = []
    
    if st.session_state.api_enabled and st.session_state.api_key:
        st.info(f"📊 {get_text('fetching_metrics', lang)}")
        api_progress = st.progress(0)
        
        for idx, gap in enumerate(sorted(analysis['gaps'])):
            comp_count = sum([
                1 for comp_data in comp_zones_list
                if any(z == gap for z, _, _ in comp_data)
            ])
            
            confidences = []
            for comp_data in comp_zones_list:
                for z, conf, _ in comp_data:
                    if z == gap and conf:
                        confidences.append(conf['score'])
            
            avg_conf = int(sum(confidences) / len(confidences)) if confidences else 0
            
            if avg_conf >= 67:
                slug_data = suggest_best_slug(
                    gap, 
                    selected_service, 
                    comp_zones_list,
                    lang
                )
                
                keyword = build_keyword_from_gap(selected_service, gap, lang)
                api_data = fetch_api_data(
                    keyword,
                    st.session_state.api_provider,
                    st.session_state.api_key,
                    st.session_state.country_code
                )
                
                volume = api_data.get('volume', 0) if api_data else 0
                kd = api_data.get('kd', 0) if api_data else 0
                
                score = calculate_gap_score(comp_count, volume, has_api=True)
                priority_info = get_priority_from_score(score, lang)
                
                url_keywords_data = None
                if slug_data['urls']:
                    first_url = slug_data['urls'][0]
                    url_keywords_data = fetch_url_keywords_api(
                        first_url,
                        st.session_state.api_provider,
                        st.session_state.api_key,
                        st.session_state.country_code
                    )
                
                gap_row = {
                    get_text('score', lang): score,
                    get_text('priority', lang): f"{priority_info['badge']} {priority_info['label']}",
                    get_text('zone', lang): gap.title(),
                    get_text('slug', lang): slug_data['slug'],
                    get_text('search_volume', lang): volume,
                    get_text('keyword_difficulty', lang): kd,
                    get_text('competitor_urls', lang): "\n".join(slug_data['urls']),
                    get_text('competitors_count', lang): comp_count,
                    get_text('confidence', lang): f"{avg_conf}%",
                    '_score': score,
                    '_priority_raw': priority_info['label'],
                    '_comp_count_raw': comp_count,
                    '_zone_raw': gap.lower()
                }
                
                if url_keywords_data:
                    gap_row[get_text('traffic', lang)] = url_keywords_data.get('traffic', 0)
                    gap_row[get_text('keywords_ranking', lang)] = url_keywords_data.get('keywords', '')
                
                gaps_data.append(gap_row)
            
            api_progress.progress((idx + 1) / len(analysis['gaps']))
        
        api_progress.empty()
    else:
        for gap in sorted(analysis['gaps']):
            comp_count = sum([
                1 for comp_data in comp_zones_list
                if any(z == gap for z, _, _ in comp_data)
            ])
            
            confidences = []
            for comp_data in comp_zones_list:
                for z, conf, _ in comp_data:
                    if z == gap and conf:
                        confidences.append(conf['score'])
            
            avg_conf = int(sum(confidences) / len(confidences)) if confidences else 0
            
            slug_data = suggest_best_slug(
                gap, 
                selected_service, 
                comp_zones_list,
                lang
            )
            
            if avg_conf >= 67:
                score = calculate_gap_score(comp_count, 0, has_api=False)
                priority_info = get_priority_from_score(score, lang)
                
                gap_row = {
                    get_text('score', lang): score,
                    get_text('priority', lang): f"{priority_info['badge']} {priority_info['label']}",
                    get_text('zone', lang): gap.title(),
                    get_text('slug', lang): slug_data['slug'],
                    get_text('competitor_urls', lang): "\n".join(slug_data['urls']),
                    get_text('competitors_count', lang): comp_count,
                    get_text('confidence', lang): f"{avg_conf}%",
                    '_score': score,
                    '_priority_raw': priority_info['label'],
                    '_comp_count_raw': comp_count,
                    '_zone_raw': gap.lower()
                }
                
                gaps_data.append(gap_row)
    
    gaps_data = sorted(gaps_data, key=lambda x: x.get('_score', 0), reverse=True)
    
    st.session_state.gaps_data = gaps_data
    st.session_state.analysis = analysis
    st.session_state.all_zones_data = all_zones_data
    st.session_state.all_urls = all_urls
    st.session_state.analysis_done = True
    st.session_state.home_zone = home_zone
    st.session_state.total_competitors = total_valid
    
    # Agregar dominios al historial
    add_to_domain_history(user_domain_input, 'user')
    for comp_input in all_competitor_inputs:
        if comp_input:
            add_to_domain_history(comp_input, 'competitor')
    
    st.rerun()

if st.session_state.analysis_done:
    analysis = st.session_state.analysis
    gaps_data = st.session_state.gaps_data
    all_zones_data = st.session_state.all_zones_data
    all_urls = st.session_state.get('all_urls', {})
    home_zone = st.session_state.home_zone
    
    st.divider()
    
    st.subheader("📊 " + ("Resumen del Análisis" if lang == "es" else "Analysis Summary"))
    
    st.caption(f"🎯 {get_text('total_competitors', lang)}: **{st.session_state.total_competitors}**")
    
    critical_priority = sum([1 for g in gaps_data if g.get('_score', 0) >= 90])
    high_priority = sum([1 for g in gaps_data if 70 <= g.get('_score', 0) < 90])
    medium_priority = sum([1 for g in gaps_data if 40 <= g.get('_score', 0) < 70])
    low_priority = sum([1 for g in gaps_data if g.get('_score', 0) < 40])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🎯 Total Gaps",
            value=len(gaps_data),
            delta=None
        )
    
    with col2:
        st.metric(
            label="💪 " + get_text('strengths_found', lang),
            value=len(analysis['strengths']['tier_1']) + len(analysis['strengths']['tier_2']),
            delta=None
        )
    
    with col3:
        st.metric(
            label="🏠 " + get_text('home_zone_detected', lang),
            value=home_zone.title(),
            delta=None
        )
    
    with col4:
        st.metric(
            label="⚖️ " + get_text('ties_found', lang),
            value=len(analysis['ties']),
            delta=None
        )
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🔴🔴 " + get_text('critical_priority', lang),
            value=f"{critical_priority} gaps",
            delta=None,
            help="Score 90-100"
        )
    
    with col2:
        st.metric(
            label="🔴 " + get_text('high_priority', lang),
            value=f"{high_priority} gaps",
            delta=None,
            help="Score 70-89"
        )
    
    with col3:
        st.metric(
            label="🟡 " + get_text('medium_priority', lang),
            value=f"{medium_priority} gaps",
            delta=None,
            help="Score 40-69"
        )
    
    with col4:
        st.metric(
            label="🟢 " + get_text('low_priority', lang),
            value=f"{low_priority} gaps",
            delta=None,
            help="Score 0-39"
        )
    
    st.divider()
    
    tab1, tab2, tab3 = st.tabs([
        f"🎯 {get_text('gaps_found', lang)} ({len(gaps_data)})",
        f"💪 {get_text('strengths_found', lang)} ({len(analysis['strengths']['tier_1']) + len(analysis['strengths']['tier_2'])})",
        f"📄 {get_text('generate_pages', lang)}"
    ])
    
    with tab1:
        st.subheader(get_text('gaps_found', lang))
        
        if gaps_data:
            col_f1, col_f2, col_f3 = st.columns([1, 1, 2])
            
            all_text = get_text('all', lang)
            
            with col_f1:
                priority_options = [
                    all_text,
                    get_text('critical_priority', lang),
                    get_text('high_priority', lang),
                    get_text('medium_priority', lang),
                    get_text('low_priority', lang)
                ]
                selected_priority = st.selectbox(
                    get_text('filter_by_priority', lang),
                    options=priority_options,
                    index=0,
                    key='filter_priority_select'
                )
            
            with col_f2:
                max_comps = max([g.get('_comp_count_raw', 0) for g in gaps_data]) if gaps_data else 3
                comp_options = [all_text] + [str(i) for i in range(1, max_comps + 1)]
                selected_comps = st.selectbox(
                    get_text('filter_by_competitors', lang),
                    options=comp_options,
                    index=0,
                    key='filter_comps_select'
                )
            
            with col_f3:
                search_query = st.text_input(
                    get_text('search_zone', lang),
                    placeholder="Madrid, Barcelona, Chamberí...",
                    key='search_query_input'
                )
            
            st.divider()
            
            filtered_gaps = gaps_data.copy()
            
            if selected_priority != all_text:
                filtered_gaps = [g for g in filtered_gaps if g.get('_priority_raw') == selected_priority]
            
            if selected_comps != all_text:
                filtered_gaps = [g for g in filtered_gaps if g.get('_comp_count_raw') == int(selected_comps)]
            
            if search_query:
                search_lower = unidecode(search_query.lower())
                filtered_gaps = [g for g in filtered_gaps if search_lower in g.get('_zone_raw', '')]
            
            if filtered_gaps:
                display_gaps = []
                for gap in filtered_gaps:
                    display_gap = {k: v for k, v in gap.items() if not k.startswith('_')}
                    display_gaps.append(display_gap)
                
                st.caption(f"{get_text('show_results', lang)}: **{len(display_gaps)}** {get_text('of', lang)} **{len(gaps_data)}** {get_text('results', lang)}")
                
                df_gaps = pd.DataFrame(display_gaps)
                st.dataframe(df_gaps, use_container_width=True, hide_index=True)
                
                st.divider()
                
                csv_data = export_to_csv(display_gaps)
                st.download_button(
                    get_text('export_csv', lang),
                    data=csv_data,
                    file_name="gaps_analysis.csv",
                    mime="text/csv",
                    use_container_width=False
                )
            else:
                st.info(f"ℹ️ {get_text('no_gaps_filter', lang)}")
        else:
            st.success("🎉 " + ("¡Ya cubres todas las zonas donde están tus competidores!" if lang == "es" else "You already cover all zones where your competitors are!"))
    
    with tab2:
        st.subheader(get_text('strengths_found', lang))
        
        if analysis['strengths']['tier_1']:
            st.markdown(f"### 🏆 {get_text('max_advantage', lang)}")
            st.caption(("Zonas donde SOLO tú estás presente (0 competidores)" if lang == "es" else "Zones where ONLY you are present (0 competitors)"))
            
            tier1_data = []
            for zone in sorted(analysis['strengths']['tier_1']):
                tier1_data.append({
                    get_text('zone', lang): zone.title(),
                    get_text('advantage', lang): get_text('max_advantage', lang),
                    get_text('strategy', lang): get_text('maintain_dominance', lang)
                })
            
            df_tier1 = pd.DataFrame(tier1_data)
            st.dataframe(df_tier1, use_container_width=True, hide_index=True)
        
        if analysis['strengths']['tier_2']:
            st.markdown(f"### 💪 {get_text('medium_advantage', lang)}")
            st.caption(("Zonas donde tú + 1 competidor" if lang == "es" else "Zones where you + 1 competitor"))
            
            tier2_data = []
            for zone in sorted(analysis['strengths']['tier_2']):
                tier2_data.append({
                    get_text('zone', lang): zone.title(),
                    get_text('advantage', lang): get_text('medium_advantage', lang),
                    get_text('strategy', lang): get_text('early_advantage', lang)
                })
            
            df_tier2 = pd.DataFrame(tier2_data)
            st.dataframe(df_tier2, use_container_width=True, hide_index=True)
        
        if not analysis['strengths']['tier_1'] and not analysis['strengths']['tier_2']:
            st.info("ℹ️ " + ("No tienes fortalezas únicas en este momento" if lang == "es" else "You don't have unique strengths at this time"))
    
    with tab3:
        st.subheader(get_text('generate_pages', lang))
        
        if gaps_data:
            st.info("💡 " + ("Selecciona los gaps para los que deseas generar páginas HTML" if lang == "es" else "Select gaps to generate HTML pages"))
            
            # Extraer subservicios del sitemap del usuario
            user_urls = st.session_state.get('all_urls', {}).get('user', [])
            selected_service = st.session_state.get('selected_service', selected_service)
            subservices = extract_subservices_from_urls(user_urls, selected_service, lang)
            
            if subservices:
                st.success(f"✅ {len(subservices)} " + ("subservicios detectados en tu sitemap" if lang == "es" else "subservices detected in your sitemap"))
            
            # Obtener zonas existentes del usuario
            user_zones = set([z for z, _, _ in all_zones_data.get('user', []) if z])
            
            # Tabla con checkboxes para seleccionar gaps
            st.markdown("### " + get_text('select_gaps', lang))
            
            selected_gaps = []
            
            for idx, gap in enumerate(gaps_data[:20]):  # Limitar a 20 para no saturar UI
                col1, col2, col3, col4 = st.columns([0.5, 2, 1, 1])
                
                with col1:
                    is_selected = st.checkbox("", key=f"select_gap_{idx}", label_visibility="collapsed")
                
                with col2:
                    st.write(gap.get(get_text('zone', lang), ''))
                
                with col3:
                    priority_badge = gap.get(get_text('priority', lang), '')
                    st.write(priority_badge)
                
                with col4:
                    score = gap.get(get_text('score', lang), 0)
                    st.write(f"Score: {score}")
                
                if is_selected:
                    selected_gaps.append({
                        'zone': gap.get('_zone_raw', ''),
                        'zone_display': gap.get(get_text('zone', lang), ''),
                        'score': score,
                        'priority': priority_badge
                    })
            
            st.divider()
            
            if selected_gaps:
                st.success(f"✅ {len(selected_gaps)} " + ("gaps seleccionados" if lang == "es" else "gaps selected"))
                
                #
