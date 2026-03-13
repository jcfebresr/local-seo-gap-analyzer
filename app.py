"""
Local SEO Geo-Gap Analyzer v2.7
Sprint 5.1 - Design DNA Extraction + Template System
- Sistema de scraping de diseño de competidores
- Plantillas HTML adaptativas con diseño real
- Detección de subservicios mejorada
- Enlaces internos inteligentes
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
from collections import Counter
from collections import Counter

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

# API functions continue below (keeping existing code)...
# Due to length limits, I'll continue in next message if needed

# Note: The file is too long to fit in one artifact update.
# Would you like me to:
# 1. Split into multiple parts
# 2. Focus only on fixing the specific consolidate_design_dna function
# 3. Provide just the corrected line

Let me just fix the specific problematic line:
