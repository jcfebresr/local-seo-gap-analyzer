"""
Local SEO Geo-Gap Analyzer v2.2
Sprint 2 - Precisión Avanzada
- Dynamic Service Validation
- Confidence Scoring System
- Fortalezas y Empates
- Multi-Word Zones Mejorado
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
        "competitors_count": "Nº Comps",
        "confidence": "Confianza",
        "advantage": "Ventaja",
        "strategy": "Estrategia",
        "priority": "Prioridad",
        "confirm": "Confirmar",
        "required_field": "Campo obligatorio",
        "duplicate_domains": "Los dominios deben ser diferentes entre sí",
        "urls_filtered": "URLs filtradas por servicio diferente",
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
        "competitors_count": "# Comps",
        "confidence": "Confidence",
        "advantage": "Advantage",
        "strategy": "Strategy",
        "priority": "Priority",
        "confirm": "Confirm",
        "required_field": "Required field",
        "duplicate_domains": "Domains must be different from each other",
        "urls_filtered": "URLs filtered by different service",
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

# Diccionario de exclusión automática
EXCLUSION_DICTIONARY = {
    "es": {
        "cerrajero": ["fontanero", "fontaneria", "electricista", "electrico", "pintor", "pintura", "reformas", "obra", "limpieza", "mudanzas", "carpintero", "carpinteria"],
        "fontanero": ["cerrajero", "cerrajeria", "electricista", "electrico", "pintor", "pintura", "reformas", "obra", "limpieza", "mudanzas", "carpintero"],
        "electricista": ["cerrajero", "cerrajeria", "fontanero", "fontaneria", "pintor", "pintura", "reformas", "obra", "limpieza", "mudanzas", "carpintero"],
        "pintor": ["cerrajero", "cerrajeria", "fontanero", "fontaneria", "electricista", "electrico", "reformas", "limpieza", "mudanzas", "carpintero"],
        "reformas": ["cerrajero", "fontanero", "electricista", "pintor", "limpieza", "mudanzas"],
    },
    "en": {
        "locksmith": ["plumber", "plumbing", "electrician", "electrical", "painter", "painting", "remodeling", "renovation", "cleaning", "moving", "carpenter"],
        "plumber": ["locksmith", "locks", "electrician", "electrical", "painter", "painting", "remodeling", "renovation", "cleaning", "moving", "carpenter"],
        "electrician": ["locksmith", "locks", "plumber", "plumbing", "painter", "painting", "remodeling", "renovation", "cleaning", "moving", "carpenter"],
        "painter": ["locksmith", "locks", "plumber", "plumbing", "electrician", "electrical", "remodeling", "cleaning", "moving", "carpenter"],
        "remodeling": ["locksmith", "plumber", "electrician", "painter", "cleaning", "moving"],
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
    """Obtiene lista de servicios a excluir"""
    return EXCLUSION_DICTIONARY.get(lang, {}).get(service_key, [])

# ============================================
# VALIDACIÓN DE DOMINIOS
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

def validate_domains(user_domain, comp1, comp2, comp3, lang="es"):
    domains = {
        'user': normalize_domain(user_domain),
        'comp1': normalize_domain(comp1),
        'comp2': normalize_domain(comp2),
        'comp3': normalize_domain(comp3),
    }
    
    invalid = [k for k, v in domains.items() if v is None]
    if invalid:
        error = get_text('invalid_domain', lang)
        labels = {
            'user': get_text('your_domain', lang),
            'comp1': f"{get_text('competitor', lang)} 1",
            'comp2': f"{get_text('competitor', lang)} 2",
            'comp3': f"{get_text('competitor', lang)} 3",
        }
        invalid_labels = [labels[k] for k in invalid]
        return False, {}, f"{error}: {', '.join(invalid_labels)}"
    
    domain_list = list(domains.values())
    if len(domain_list) != len(set(domain_list)):
        return False, {}, f"❌ {get_text('duplicate_domains', lang)}"
    
    return True, domains, ""

# ============================================
# AUTO-DISCOVERY SITEMAPS
# ============================================

def find_sitemap(domain, timeout=10):
    """Busca automáticamente el sitemap con orden de prioridad corregido"""
    base_url = f"https://{domain}"
    
    # ORDEN CORREGIDO: sitemap_index.xml PRIMERO (más común en WordPress/Yoast)
    sitemap_paths = [
        '/sitemap_index.xml',      # Primero - Yoast SEO, Rank Math
        '/sitemap.xml',             # Segundo - Genérico
        '/sitemap-index.xml',       # Variante con guión
        '/wp-sitemap.xml',          # WordPress nativo
        '/post-sitemap.xml',        # Yoast posts
        '/page-sitemap.xml',        # Yoast pages
        '/sitemap.php',             # Dinámico
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (LocalSEOGapAnalyzer/2.2; +https://github.com/user/local-seo-gap)'
    }
    
    # Método 1: URLs directas
    for path in sitemap_paths:
        try:
            url = urljoin(base_url, path)
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
        except Exception as e:
            # Continuar con siguiente path si falla
            continue
    
    # Método 2: robots.txt
    try:
        robots_url = urljoin(base_url, '/robots.txt')
        response = requests.get(robots_url, headers=headers, timeout=timeout)
        
        if response.status_code == 200:
            for line in response.text.split('\n'):
                if line.lower().startswith('sitemap:'):
                    sitemap_url = line.split(':', 1)[1].strip()
                    try:
                        check = requests.head(sitemap_url, headers=headers, timeout=5)
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
    
    # Método 3: No encontrado
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
    
    service_variations = [
        service_key,
        service_key + 's',
        service_key + 'es',
    ]
    
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
            'User-Agent': 'Mozilla/5.0 (LocalSEOGapAnalyzer/2.2)'
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
# LIMPIEZA DE SLUGS
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
    """Normaliza zonas multi-palabra avanzado"""
    connectors = {
        "es": ["el", "la", "los", "las", "de"],
        "en": ["the", "of"]
    }
    
    parts = slug.split('-')
    cleaned_parts = [p for p in parts if p not in connectors.get(lang, [])]
    
    return '-'.join(cleaned_parts)

# ============================================
# DYNAMIC SERVICE VALIDATION (NUEVO)
# ============================================

def is_url_valid_for_service(url, service_key, lang="es", threshold=80):
    """
    Valida si una URL pertenece al servicio buscado.
    Retorna True si es válida, False si contiene servicios excluidos.
    """
    exclusion_list = get_exclusion_list(service_key, lang)
    
    url_lower = url.lower()
    
    for excluded_service in exclusion_list:
        # Fuzzy matching para detectar variaciones
        if fuzz.partial_ratio(excluded_service, url_lower) > threshold:
            return False
    
    return True

# ============================================
# CONFIDENCE SCORING (NUEVO)
# ============================================

def calculate_confidence(zone, cities, url, lang="es"):
    """
    Calcula score de confianza basado en validaciones múltiples.
    
    Validaciones:
    1. Regex match (¿zona en slug limpio?)
    2. Top Cities match (¿zona en lista oficial?)
    3. Multi-validation (futura expansión para SpaCy)
    
    Returns:
        dict: {
            'score': int (0-100),
            'validations': {
                'regex': bool,
                'top_cities': bool,
            }
        }
    """
    validations = {
        'regex': False,
        'top_cities': False,
    }
    
    # Validación 1: Regex match
    if zone and len(zone) > 2:
        validations['regex'] = True
    
    # Validación 2: Top Cities
    if zone in cities:
        validations['top_cities'] = True
    
    # Calcular score
    passed = sum(validations.values())
    total = len(validations)
    score = int((passed / total) * 100)
    
    return {
        'score': score,
        'validations': validations
    }

# ============================================
# EXTRACCIÓN Y ANÁLISIS
# ============================================

def extract_urls_from_sitemap(sitemap_url, max_urls=5000):
    try:
        df = adv.sitemap_to_df(sitemap_url)
        urls = df['loc'].tolist()
        
        if len(urls) > max_urls:
            import random
            urls = random.sample(urls, max_urls)
        
        return urls, len(df)
    except Exception as e:
        return [], 0

def filter_urls(urls, lang="es"):
    discard_patterns = [
        '/blog/', '/tag/', '/tags/', '/category/', '/categories/',
        '/author/', '/page/', '/search/',
        '/wp-content/', '/wp-admin/', '/wp-includes/',
        '/feed/', '/rss/', '/sitemap/',
    ]
    
    extensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.css', '.js', '.pdf']
    
    filtered = []
    for url in urls:
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
    
    return filtered

def extract_zone_from_url(url, cities, service_key, stop_words, lang="es"):
    """Extrae zona con validación de confianza"""
    try:
        # Validación de servicio primero
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

def analyze_comprehensive(user_zones_data, comp_zones_data_list, home_zone):
    """
    Análisis completo: Gaps, Fortalezas, Empates
    
    Args:
        user_zones_data: [(zone, confidence, url), ...]
        comp_zones_data_list: [[(zone, confidence, url), ...], ...]
        home_zone: str
    
    Returns:
        dict: {
            'gaps': [...],
            'strengths': {...},
            'ties': [...]
        }
    """
    # Extraer solo zonas (sin confidence)
    user_zones = set([z for z, _, _ in user_zones_data if z])
    user_zones.discard(home_zone)
    
    all_comp_zones = set()
    comp_zones_lists = []
    
    for comp_data in comp_zones_data_list:
        comp_zones = set([z for z, _, _ in comp_data if z])
        comp_zones.discard(home_zone)
        comp_zones_lists.append(comp_zones)
        all_comp_zones.update(comp_zones)
    
    # GAPS: lo que competidores tienen y usuario no
    gaps = all_comp_zones - user_zones
    
    # FORTALEZAS: lo que usuario tiene y competencia no/mínima
    strengths = {
        'tier_1': [],  # Solo usuario (0 competidores)
        'tier_2': []   # Usuario + 1 competidor
    }
    
    for zone in user_zones:
        comp_count = sum([1 for comp_zones in comp_zones_lists if zone in comp_zones])
        
        if comp_count == 0:
            strengths['tier_1'].append(zone)
        elif comp_count == 1:
            strengths['tier_2'].append(zone)
    
    # EMPATES: Usuario + 2-3 competidores
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

if 'home_zone_confirmed' not in st.session_state:
    st.session_state.home_zone_confirmed = False

if 'show_city_selector' not in st.session_state:
    st.session_state.show_city_selector = False

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
        st.session_state.home_zone_confirmed = False
        st.rerun()

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

st.divider()

col1, col2 = st.columns(2)

with col1:
    user_domain_input = st.text_input(
        f"🏠 {get_text('your_domain', lang)} *",
        placeholder=get_text('domain_placeholder', lang),
        help="Solo el dominio, sin https:// ni rutas"
    )

with col2:
    if user_domain_input:
        normalized = normalize_domain(user_domain_input)
        if normalized:
            st.success(f"✅ {normalized}")
        else:
            st.error(get_text('invalid_domain', lang))

st.divider()

st.subheader(f"🔍 {get_text('competitor', lang)}s")

col1, col2 = st.columns(2)
with col1:
    comp1_input = st.text_input(
        f"{get_text('competitor', lang)} 1 *",
        placeholder=get_text('domain_placeholder', lang)
    )
    comp2_input = st.text_input(
        f"{get_text('competitor', lang)} 2 *",
        placeholder=get_text('domain_placeholder', lang)
    )

with col2:
    comp3_input = st.text_input(
        f"{get_text('competitor', lang)} 3 *",
        placeholder=get_text('domain_placeholder', lang)
    )
    
    valid_comps = sum([
        bool(normalize_domain(comp1_input)),
        bool(normalize_domain(comp2_input)),
        bool(normalize_domain(comp3_input))
    ])
    
    if valid_comps < 3:
        st.warning(f"⚠️ {valid_comps}/3 " + ("competidores válidos" if lang == "es" else "valid competitors"))
    else:
        st.success(f"✅ {valid_comps}/3 " + ("competidores válidos" if lang == "es" else "valid competitors"))

st.divider()

analyze_button = st.button(
    get_text('analyze_button', lang),
    type="primary",
    use_container_width=True,
    disabled=not all([user_domain_input, comp1_input, comp2_input, comp3_input])
)

if analyze_button:
    success, normalized_domains, error_msg = validate_domains(
        user_domain_input, comp1_input, comp2_input, comp3_input, lang
    )
    
    if not success:
        st.error(error_msg)
        st.stop()
    
    st.subheader("🔍 " + get_text('extracting_urls', lang))
    
    with st.spinner(''):
        sitemap_results = find_all_sitemaps(normalized_domains)
    
    for key in ['user', 'comp1', 'comp2', 'comp3']:
        result = sitemap_results[key]
        domain = normalized_domains[key]
        
        if key == 'user':
            label = get_text('your_domain', lang)
        else:
            label = f"{get_text('competitor', lang)} {key[-1]}"
        
        if result['success']:
            st.success(f"{label}: **{domain}** → {result['message']}")
        else:
            st.warning(f"{label}: **{domain}** → {result['message']}")
    
    st.divider()
    
    # DETECCIÓN AUTOMÁTICA SIN CONFIRMACIÓN (TEMPORAL PARA TESTING)
    if 'home_zone' not in st.session_state:
        st.subheader("🏠 " + get_text('home_zone_detected', lang))
        
        with st.spinner(''):
            home_zone_result = detect_home_zone(
                normalized_domains['user'],
                selected_service,
                lang
            )
        
        if home_zone_result['zone']:
            # AUTO-CONFIRMAR detectada
            st.session_state.home_zone = home_zone_result['zone']
            st.success(f"✅ {get_text('home_zone_detected', lang)}: **{home_zone_result['zone'].title()}** (auto-detectada)")
        else:
            # Si no detecta, usar dropdown
            cities = get_cities(lang)
            manual_zone = st.selectbox(
                get_text('select_city', lang),
                options=cities,
                index=0
            )
            st.session_state.home_zone = manual_zone
            st.info(f"ℹ️ Zona seleccionada manualmente: **{manual_zone.title()}**")
    else:
        st.success(f"✅ " + get_text('home_zone_detected', lang) + f": **{st.session_state.home_zone.title()}**")
    
    st.subheader("📊 " + get_text('processing', lang))
    
    all_urls = {}
    all_counts = {}
    filtered_counts = {}
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, key in enumerate(['user', 'comp1', 'comp2', 'comp3']):
        domain = normalized_domains[key]
        sitemap_result = sitemap_results[key]
        
        status_text.text(f"{get_text('processing', lang)}: {domain}")
        
        if sitemap_result['success']:
            urls, total = extract_urls_from_sitemap(sitemap_result['sitemap_url'])
            all_urls[key] = urls
            all_counts[key] = {'extracted': len(urls), 'total': total}
        else:
            all_urls[key] = []
            all_counts[key] = {'extracted': 0, 'total': 0}
        
        progress_bar.progress((idx + 1) / 4)
    
    status_text.empty()
    progress_bar.empty()
    
    cities = get_cities(lang)
    stop_words = get_stop_words(lang)
    
    # Procesar con confidence scoring
    all_zones_data = {}
    for key, urls in all_urls.items():
        filtered = filter_urls(urls, lang)
        zones_data = []
        filtered_by_service = 0
        
        for url in filtered:
            zone, confidence = extract_zone_from_url(url, cities, selected_service, stop_words, lang)
            if zone:
                zones_data.append((zone, confidence, url))
            elif not is_url_valid_for_service(url, selected_service, lang):
                filtered_by_service += 1
        
        all_zones_data[key] = zones_data
        filtered_counts[key] = filtered_by_service
    
    # Mostrar estadísticas de filtrado
    if any(filtered_counts.values()):
        st.info(f"ℹ️ {get_text('urls_filtered', lang)}: " + 
                ", ".join([f"{k}: {v}" for k, v in filtered_counts.items() if v > 0]))
    
    # Análisis comprehensivo
    analysis = analyze_comprehensive(
        all_zones_data['user'],
        [all_zones_data['comp1'], all_zones_data['comp2'], all_zones_data['comp3']],
        st.session_state.home_zone
    )
    
    st.divider()
    
    # TABS
    tab1, tab2, tab3, tab4 = st.tabs([
        f"🎯 {get_text('gaps_found', lang)} ({len(analysis['gaps'])})",
        f"💪 {get_text('strengths_found', lang)} ({len(analysis['strengths']['tier_1']) + len(analysis['strengths']['tier_2'])})",
        f"⚖️ {get_text('ties_found', lang)} ({len(analysis['ties'])})",
        f"⚠️ {get_text('low_confidence', lang)}"
    ])
    
    with tab1:
        st.subheader(get_text('gaps_found', lang))
        
        if analysis['gaps']:
            gaps_data = []
            
            for gap in sorted(analysis['gaps']):
                # Contar competidores
                comp_count = sum([
                    1 for comp_data in [all_zones_data['comp1'], all_zones_data['comp2'], all_zones_data['comp3']]
                    if any(z == gap for z, _, _ in comp_data)
                ])
                
                # Obtener confidence promedio
                confidences = []
                for comp_data in [all_zones_data['comp1'], all_zones_data['comp2'], all_zones_data['comp3']]:
                    for z, conf, _ in comp_data:
                        if z == gap and conf:
                            confidences.append(conf['score'])
                
                avg_conf = int(sum(confidences) / len(confidences)) if confidences else 0
                
                # Prioridad
                if comp_count == 3:
                    priority = get_text('high_priority', lang)
                    color = "🔴"
                elif comp_count == 2:
                    priority = get_text('medium_priority', lang)
                    color = "🟡"
                else:
                    priority = get_text('low_priority', lang)
                    color = "🟢"
                
                # Solo mostrar gaps con confianza >= 67%
                if avg_conf >= 67:
                    gaps_data.append({
                        get_text('priority', lang): f"{color} {priority}",
                        get_text('zone', lang): gap.title(),
                        get_text('slug', lang): f"/{selected_service}-{gap}/",
                        get_text('competitors_count', lang): comp_count,
                        get_text('confidence', lang): f"{avg_conf}%"
                    })
            
            if gaps_data:
                df_gaps = pd.DataFrame(gaps_data)
                st.dataframe(df_gaps, use_container_width=True, hide_index=True)
                
                all_slugs = '\n'.join([row[get_text('slug', lang)] for row in gaps_data])
                st.download_button(
                    "📋 " + ("Copiar todos los slugs" if lang == "es" else "Copy all slugs"),
                    data=all_slugs,
                    file_name="gaps_slugs.txt",
                    mime="text/plain"
                )
            else:
                st.info("ℹ️ " + ("No hay gaps de alta confianza" if lang == "es" else "No high-confidence gaps"))
        else:
            st.success("🎉 " + ("¡Ya cubres todas las zonas de tus competidores!" if lang == "es" else "You already cover all competitor zones!"))
    
    with tab2:
        st.subheader(get_text('strengths_found', lang))
        
        strengths_data = []
        
        for zone in analysis['strengths']['tier_1']:
            strengths_data.append({
                get_text('zone', lang): zone.title(),
                get_text('advantage', lang): get_text('max_advantage', lang),
                get_text('competitors_count', lang): 0,
                get_text('strategy', lang): get_text('maintain_dominance', lang)
            })
        
        for zone in analysis['strengths']['tier_2']:
            strengths_data.append({
                get_text('zone', lang): zone.title(),
                get_text('advantage', lang): get_text('medium_advantage', lang),
                get_text('competitors_count', lang): 1,
                get_text('strategy', lang): get_text('early_advantage', lang)
            })
        
        if strengths_data:
            df_strengths = pd.DataFrame(strengths_data)
            st.dataframe(df_strengths, use_container_width=True, hide_index=True)
        else:
            st.info("ℹ️ " + ("No se detectaron fortalezas únicas" if lang == "es" else "No unique strengths detected"))
    
    with tab3:
        st.subheader(get_text('ties_found', lang))
        
        if analysis['ties']:
            ties_data = []
            
            for zone in sorted(analysis['ties']):
                comp_count = sum([
                    1 for comp_data in [all_zones_data['comp1'], all_zones_data['comp2'], all_zones_data['comp3']]
                    if any(z == zone for z, _, _ in comp_data)
                ])
                
                ties_data.append({
                    get_text('zone', lang): zone.title(),
                    get_text('competitors_count', lang): comp_count,
                    get_text('strategy', lang): get_text('competitive_market', lang)
                })
            
            df_ties = pd.DataFrame(ties_data)
            st.dataframe(df_ties, use_container_width=True, hide_index=True)
        else:
            st.info("ℹ️ " + ("No hay mercados saturados" if lang == "es" else "No saturated markets"))
    
    with tab4:
        st.subheader(get_text('low_confidence', lang))
        
        low_conf_gaps = []
        
        for gap in analysis['gaps']:
            confidences = []
            for comp_data in [all_zones_data['comp1'], all_zones_data['comp2'], all_zones_data['comp3']]:
                for z, conf, _ in comp_data:
                    if z == gap and conf:
                        confidences.append(conf['score'])
            
            avg_conf = int(sum(confidences) / len(confidences)) if confidences else 0
            
            if avg_conf < 67:
                low_conf_gaps.append({
                    get_text('zone', lang): gap.title(),
                    get_text('confidence', lang): f"{avg_conf}%",
                    get_text('slug', lang): f"/{selected_service}-{gap}/"
                })
        
        if low_conf_gaps:
            st.warning("⚠️ " + ("Estas zonas requieren verificación manual antes de crear contenido" if lang == "es" else "These zones require manual verification before creating content"))
            df_low = pd.DataFrame(low_conf_gaps)
            st.dataframe(df_low, use_container_width=True, hide_index=True)
        else:
            st.success("✅ " + ("Todos los gaps tienen alta confianza" if lang == "es" else "All gaps have high confidence"))
