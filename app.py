"""
Local SEO Geo-Gap Analyzer v2.2
Sprint 1 - Fundamentos Críticos
Production Ready
"""

import streamlit as st
import pandas as pd
import advertools as adv
import re
import requests
from bs4 import BeautifulSoup
from unidecode import unidecode
from urllib.parse import urlparse, urljoin
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
        "gaps_found": "Gaps encontrados",
        "zone": "Zona",
        "slug": "Slug",
        "competitors_count": "Nº Competidores",
        "confirm": "Confirmar",
        "required_field": "Campo obligatorio",
        "duplicate_domains": "Los dominios deben ser diferentes entre sí",
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
        "gaps_found": "Gaps found",
        "zone": "Zone",
        "slug": "Slug",
        "competitors_count": "# Competitors",
        "confirm": "Confirm",
        "required_field": "Required field",
        "duplicate_domains": "Domains must be different from each other",
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
        "chamberi", "salamanca", "retiro", "tetuan", "fuencarral", "moncloa",
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
    """Obtiene texto traducido"""
    return TRANSLATIONS.get(lang, TRANSLATIONS["es"]).get(key, key)

def get_services(lang="es"):
    """Obtiene lista de servicios"""
    return SERVICES.get(lang, SERVICES["es"])

def get_cities(lang="es"):
    """Obtiene lista de ciudades"""
    return TOP_CITIES.get(lang, TOP_CITIES["es"])

def get_stop_words(lang="es"):
    """Obtiene lista de stop words"""
    return STOP_WORDS.get(lang, STOP_WORDS["es"])

# ============================================
# VALIDACIÓN DE DOMINIOS
# ============================================

def normalize_domain(domain_input):
    """Normaliza input de dominio a formato limpio"""
    if not domain_input:
        return None
    
    try:
        domain = domain_input.strip().lower()
        
        # Si tiene protocolo, extraer con urlparse
        if domain.startswith(('http://', 'https://')):
            parsed = urlparse(domain)
            domain = parsed.netloc or parsed.path.split('/')[0]
        
        # Remover path residual
        domain = domain.split('/')[0]
        
        # Remover www.
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Validar formato
        if not is_valid_domain(domain):
            return None
        
        return domain
    except:
        return None

def is_valid_domain(domain):
    """Valida formato de dominio"""
    pattern = r'^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)*\.[a-z]{2,}$'
    
    if not re.match(pattern, domain):
        return False
    
    if ' ' in domain or any(c in domain for c in ['ñ', 'á', 'é', 'í', 'ó', 'ú']):
        return False
    
    if '.' not in domain:
        return False
    
    return True

def validate_domains(user_domain, comp1, comp2, comp3, lang="es"):
    """Valida todos los dominios"""
    domains = {
        'user': normalize_domain(user_domain),
        'comp1': normalize_domain(comp1),
        'comp2': normalize_domain(comp2),
        'comp3': normalize_domain(comp3),
    }
    
    # Verificar válidos
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
    
    # Verificar duplicados
    domain_list = list(domains.values())
    if len(domain_list) != len(set(domain_list)):
        return False, {}, f"❌ {get_text('duplicate_domains', lang)}"
    
    return True, domains, ""

# ============================================
# AUTO-DISCOVERY SITEMAPS
# ============================================

def find_sitemap(domain, timeout=10):
    """Busca automáticamente el sitemap"""
    base_url = f"https://{domain}"
    
    sitemap_paths = [
        '/sitemap.xml',
        '/sitemap_index.xml',
        '/sitemap-index.xml',
        '/post-sitemap.xml',
        '/page-sitemap.xml',
        '/wp-sitemap.xml',
        '/sitemap.php',
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
        except:
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
    """Busca sitemaps para todos los dominios"""
    results = {}
    for key, domain in domains_dict.items():
        if domain:
            results[key] = find_sitemap(domain)
    return results

# ============================================
# HOME ZONE DETECTION
# ============================================

def detect_home_zone_from_domain(domain, service_key, lang="es"):
    """Detecta zona desde dominio con regex"""
    domain_lower = domain.lower()
    cities = get_cities(lang)
    
    # Método 1: Subdomain
    subdomain_match = re.match(r'^([a-z-]+)\.', domain_lower)
    if subdomain_match:
        potential_zone = subdomain_match.group(1)
        if potential_zone in cities:
            return potential_zone
    
    # Método 2: Service-City patterns
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
    """Detecta zona desde homepage"""
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
        
        # Buscar en title
        title = soup.find('title')
        if title:
            title_text = unidecode(title.get_text().lower())
            for city in cities:
                if city in title_text:
                    return city
        
        # Buscar en h1
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
    """Detección completa de home zone"""
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
    """Limpia slug removiendo stop words"""
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
    """Normaliza zonas multi-palabra"""
    connectors = {
        "es": ["el", "la", "los", "las", "de"],
        "en": ["the", "of"]
    }
    
    parts = slug.split('-')
    cleaned_parts = [p for p in parts if p not in connectors.get(lang, [])]
    
    return '-'.join(cleaned_parts)

# ============================================
# EXTRACCIÓN Y ANÁLISIS
# ============================================

def extract_urls_from_sitemap(sitemap_url, max_urls=5000):
    """Extrae URLs de sitemap usando advertools"""
    try:
        df = adv.sitemap_to_df(sitemap_url)
        urls = df['loc'].tolist()
        
        # Sampling si >5000
        if len(urls) > max_urls:
            import random
            urls = random.sample(urls, max_urls)
        
        return urls, len(df)
    except Exception as e:
        return [], 0

def filter_urls(urls, lang="es"):
    """Filtra URLs de ruido (Step 2)"""
    discard_patterns = [
        '/blog/', '/tag/', '/tags/', '/category/', '/categories/',
        '/author/', '/page/', '/search/',
        '/wp-content/', '/wp-admin/', '/wp-includes/',
        '/feed/', '/rss/', '/sitemap/',
    ]
    
    extensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.css', '.js', '.pdf']
    
    filtered = []
    for url in urls:
        # Descartar patterns
        if any(pattern in url.lower() for pattern in discard_patterns):
            continue
        
        # Descartar extensiones
        if any(url.lower().endswith(ext) for ext in extensions):
            continue
        
        # Descartar query params
        if '?' in url:
            continue
        
        # Verificar depth
        path = urlparse(url).path
        depth = len([p for p in path.split('/') if p])
        if depth > 3:
            continue
        
        filtered.append(url)
    
    return filtered

def extract_zone_from_url(url, cities, service_key, stop_words, lang="es"):
    """Extrae zona de URL"""
    try:
        path = urlparse(url).path
        slug = path.strip('/').split('/')[-1]
        
        if not slug:
            return None
        
        # Limpiar slug
        cleaned = clean_slug(slug, stop_words, lang)
        cleaned = normalize_multi_word_zones(cleaned, lang)
        
        # Buscar ciudad en slug limpio
        for city in cities:
            if city in cleaned:
                return city
        
        return None
    except:
        return None

def analyze_gaps(user_zones, comp_zones_list, home_zone):
    """Analiza gaps excluyendo home zone"""
    # Union de competidores
    all_comp_zones = set()
    for comp_zones in comp_zones_list:
        all_comp_zones.update(comp_zones)
    
    # Excluir home zone
    all_comp_zones.discard(home_zone)
    
    # Gaps = lo que competidores tienen y usuario no
    user_zones_set = set(user_zones)
    user_zones_set.discard(home_zone)
    
    gaps = all_comp_zones - user_zones_set
    
    return list(gaps)

# ============================================
# STREAMLIT UI
# ============================================

st.set_page_config(
    page_title="Local SEO Geo-Gap Analyzer",
    page_icon="🎯",
    layout="wide"
)

# Inicializar session state
if 'lang' not in st.session_state:
    st.session_state.lang = 'es'

if 'home_zone_confirmed' not in st.session_state:
    st.session_state.home_zone_confirmed = False

if 'show_city_selector' not in st.session_state:
    st.session_state.show_city_selector = False

# Header
st.title(get_text('title', st.session_state.lang))

# Sidebar - Idioma
with st.sidebar:
    st.subheader(get_text('language', st.session_state.lang))
    lang_option = st.radio(
        "Select language",  # Label no vacío
        options=['🇪🇸 Español', '🇬🇧 English'],
        index=0 if st.session_state.lang == 'es' else 1,
        label_visibility='collapsed'  # Se oculta visualmente pero existe para accesibilidad
    )
    
    new_lang = 'es' if '🇪🇸' in lang_option else 'en'
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.session_state.home_zone_confirmed = False
        st.rerun()

lang = st.session_state.lang

# Configuración
st.header("⚙️ " + ("Configuración" if lang == "es" else "Configuration"))

# Servicio
services_dict = get_services(lang)
service_label = get_text('service', lang)
selected_service_display = st.selectbox(
    service_label,
    options=list(services_dict.values()),
    index=0
)
selected_service = [k for k, v in services_dict.items() if v == selected_service_display][0]

st.divider()

# Dominios
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

# Botón analizar
analyze_button = st.button(
    get_text('analyze_button', lang),
    type="primary",
    use_container_width=True,
    disabled=not all([user_domain_input, comp1_input, comp2_input, comp3_input])
)

# Procesamiento
if analyze_button:
    # Validar dominios
    success, normalized_domains, error_msg = validate_domains(
        user_domain_input, comp1_input, comp2_input, comp3_input, lang
    )
    
    if not success:
        st.error(error_msg)
        st.stop()
    
    # Auto-discovery sitemaps
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
    
    # Home zone detection
    if not st.session_state.home_zone_confirmed:
        st.subheader("🏠 " + get_text('home_zone_detected', lang))
        
        with st.spinner(''):
            home_zone_result = detect_home_zone(
                normalized_domains['user'],
                selected_service,
                lang
            )
        
        if home_zone_result['zone']:
            st.info(f"{get_text('home_zone_detected', lang)}: **{home_zone_result['zone'].title()}**")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(get_text('yes', lang), use_container_width=True):
                    st.session_state.home_zone = home_zone_result['zone']
                    st.session_state.home_zone_confirmed = True
                    st.rerun()
            
            with col2:
                if st.button(get_text('no', lang), use_container_width=True):
                    st.session_state.show_city_selector = True
                    st.rerun()
        
        if home_zone_result['zone'] is None or st.session_state.show_city_selector:
            cities = get_cities(lang)
            manual_zone = st.selectbox(
                get_text('select_city', lang),
                options=cities,
                index=0
            )
            
            if st.button("✓ " + get_text('confirm', lang)):
                st.session_state.home_zone = manual_zone
                st.session_state.home_zone_confirmed = True
                st.session_state.show_city_selector = False
                st.rerun()
        
        st.stop()
    
    # Análisis principal
    st.success(f"✅ " + get_text('home_zone_detected', lang) + f": **{st.session_state.home_zone.title()}**")
    
    st.subheader("📊 " + get_text('processing', lang))
    
    # Extraer URLs
    all_urls = {}
    all_counts = {}
    
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
    
    # Filtrar URLs
    cities = get_cities(lang)
    stop_words = get_stop_words(lang)
    
    all_zones = {}
    for key, urls in all_urls.items():
        filtered = filter_urls(urls, lang)
        zones = []
        
        for url in filtered:
            zone = extract_zone_from_url(url, cities, selected_service, stop_words, lang)
            if zone:
                zones.append(zone)
        
        all_zones[key] = zones
    
    # Analizar gaps
    gaps = analyze_gaps(
        all_zones['user'],
        [all_zones['comp1'], all_zones['comp2'], all_zones['comp3']],
        st.session_state.home_zone
    )
    
    # Mostrar resultados
    st.divider()
    st.subheader(f"🎯 {get_text('gaps_found', lang)}: {len(gaps)}")
    
    if gaps:
        results_data = []
        for gap in sorted(gaps):
            # Contar en cuántos competidores aparece
            comp_count = sum([
                1 for comp_zones in [all_zones['comp1'], all_zones['comp2'], all_zones['comp3']]
                if gap in comp_zones
            ])
            
            results_data.append({
                get_text('zone', lang): gap.title(),
                get_text('slug', lang): f"/{selected_service}-{gap}/",
                get_text('competitors_count', lang): comp_count
            })
        
        df_results = pd.DataFrame(results_data)
        st.dataframe(df_results, use_container_width=True, hide_index=True)
        
        # Botón copiar slugs
        all_slugs = '\n'.join([row[get_text('slug', lang)] for row in results_data])
        st.download_button(
            "📋 " + ("Copiar todos los slugs" if lang == "es" else "Copy all slugs"),
            data=all_slugs,
            file_name="gaps_slugs.txt",
            mime="text/plain"
        )
    else:
        st.success("🎉 " + ("¡Ya cubres todas las zonas de tus competidores!" if lang == "es" else "You already cover all competitor zones!"))
