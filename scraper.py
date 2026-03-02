import requests
from bs4 import BeautifulSoup
import os
import time
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import re
import urllib3

# Desactivar advertencias
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Códigos internos de  y Coordenadas GPS
AIRPORT_MAPPING = [
    # (ICAO, ID_POST, LAT, LON)
    ('SPTU', 'sptu', -3.552, -80.379), ('SPME', 'spme', -4.442, -81.224),
    ('SPYL', 'spyl', -4.580, -81.251), ('SPUR', 'spur', -5.209, -80.616),
    ('SPJE', 'spje', -5.592, -78.771), ('SPJA', 'spja', -6.061, -77.157),
    ('SPHI', 'sphi', -6.787, -79.828), ('SPJR', 'spjr', -7.139, -78.489),
    ('SPRU', 'spru', -8.082, -79.109), ('SPPY', 'sppy', -6.202, -77.856),
    ('SPQT', 'spqt', -3.785, -73.309), ('SPMS', 'spms', -5.894, -76.118),
    ('SPST', 'spst', -6.509, -76.372), ('SPJI', 'spji', -7.170, -76.729),
    ('SPCL', 'spcl', -8.378, -74.574), ('SPAY', 'spay', -10.729, -73.766),
    ('SPWT', 'spwt', -7.352, -75.006), ('SPMF', 'spmf', -11.325, -74.536),
    ('SPEO', 'speo', -9.150, -78.524), ('SPHZ', 'sphz', -9.347, -77.598),
    ('SPNC', 'spnc', -9.879, -76.204), ('SPJC', 'spjc', -12.022, -77.114),
    ('SPJJ', 'spjj', -11.783, -75.473), ('SPGM', 'spgm', -9.300, -76.000),
    ('SPSO', 'spso', -13.744, -76.222), ('SPZA', 'spza', -14.853, -74.962),
    ('SPJL', 'spjl', -15.467, -70.158), ('SPQU', 'spqu', -16.341, -71.571),
    ('SPLO', 'splo', -17.697, -71.343), ('SPTN', 'sptn', -18.053, -70.276),
    ('SPZO', 'spzo', -13.535, -71.939)
]

# Coordenadas ciudades del mapa index
CITY_COORDINATES = {
    "Tumbes": (-3.566, -80.451), "Piura": (-5.194, -80.632), "Talara": (-4.577, -81.271),
    "Chiclayo": (-6.771, -79.844), "Trujillo": (-8.116, -79.029), "Chimbote": (-9.085, -78.578),
    "Huaraz": (-9.526, -77.528), "Lima": (-12.046, -77.042), "Pisco": (-13.708, -76.205),
    "Nazca": (-14.830, -74.938), "Ilo": (-17.641, -71.341), "Tacna": (-18.014, -70.250),
    "Arequipa": (-16.409, -71.537), "Cajamarca": (-7.163, -78.500), "Jaen": (-5.708, -78.807),
    "Chachapoyas": (-6.229, -77.872), "Moyobamba": (-6.034, -76.971), "Tarapoto": (-6.485, -76.359),
    "Juanjui": (-7.181, -76.730), "Yurimaguas": (-5.891, -76.102), "Iquitos": (-3.749, -73.253),
    "Contamana": (-7.333, -75.016), "Pucallpa": (-8.379, -74.553), "Atalaya": (-10.733, -73.750),
    "Mazamari": (-11.325, -74.530), "Puertomaldonado": (-12.593, -69.183), "Cuzco": (-13.531, -71.967),
    "Ayacucho": (-13.158, -74.223), "Andahuaylas": (-13.655, -73.387), "Jauja": (-11.777, -75.500),
    "Huanuco": (-9.930, -76.240), "Tingomaria": (-9.293, -76.002), "Rioja": (-6.062, -77.166),
    "Juliaca": (-15.496, -70.133)
}

URL_DADOS = "https://meteorologia.corpac.gob.pe/app/Meteorologia/tiempo/consultas/select1.php"
URL_INDEX = "https://meteorologia.corpac.gob.pe/app/Meteorologia/index.php"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://meteorologia.corpac.gob.pe/app/Meteorologia/tiempo/tiempoactual.php',
    'Content-Type': 'application/x-www-form-urlencoded',
}

def clean(text):
    if not text: return "---"
    # Quitar &nbsp;, saltos de línea y espacios múltiples
    text = text.replace('\xa0', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    return text if text else "---"

def get_airport_weather(session, code_post, icao_real, lat=0, lon=0):
    try:
        r = session.post(URL_DADOS, data={'aerop': code_post}, headers=HEADERS, timeout=20, verify=False)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'html.parser')
        
        data = {
            'icao': icao_real, 'update_time': datetime.now().strftime("%H:%M"),
            'nombre': '---', 'hora': '---', 'viento': '---', 'visibilidad': '---',
            'temperatura': '---', 'rocio': '---', 'humedad': '---', 'presion': '---', 'nubosidad': '---', 'fenomenos': '---',
            'lat': lat, 'lon': lon
        }

        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                th_tags = row.find_all('th')
                td_tags = row.find_all('td')
                
                # Caso 1: Aeropuerto y Hora (th y td en la misma fila)
                if len(th_tags) == 1 and len(td_tags) == 1:
                    label = th_tags[0].get_text().lower()
                    val = td_tags[0].get_text()
                    if 'aeropuerto' in label: data['nombre'] = clean(val)
                    elif 'hora' in label: data['hora'] = clean(val)
                
                # Caso 2: Viento (Título 'Viento' seguido de valores en otra fila)
                if any('viento' in t.get_text().lower() for t in th_tags):
                    try:
                        # Los valores están 2 filas más abajo (Direccion | Velocidad)
                        val_row = table.find_all('tr')[2]
                        vals = [v.get_text(strip=True) for v in val_row.find_all('td')]
                        if len(vals) >= 2:
                            data['viento'] = f"{clean(vals[0])} / {clean(vals[1])}"
                    except: pass

                # Caso 3: Temperatura / Rocío / Humedad (Encabezados arriba, valores abajo)
                if any('temperatura' in t.get_text().lower() for t in th_tags) and len(th_tags) >= 2:
                    try:
                        val_row = table.find_all('tr')[1]
                        vals = [v.get_text(strip=True) for v in val_row.find_all('td')]
                        if len(vals) >= 2:
                            data['temperatura'] = clean(vals[0])
                            data['rocio'] = clean(vals[1])
                        if len(vals) >= 3:
                            data['humedad'] = clean(vals[2])
                    except: pass

                # Caso 4: Presión / Visibilidad / Nubosidad / Fenómenos / Humedad (Layout Horizontal: Th -> Td(img) -> Td(valor))
                if len(th_tags) == 1 and len(td_tags) >= 1:
                    label = th_tags[0].get_text().lower()
                    # El valor suele ser el último td
                    val = td_tags[-1].get_text()
                    if 'presión' in label or 'presion' in label: data['presion'] = clean(val)
                    elif 'visibilidad' in label: data['visibilidad'] = clean(val)
                    elif 'nubosidad' in label: data['nubosidad'] = clean(val)
                    elif 'humedad' in label: data['humedad'] = clean(val)
                    elif 'fenómenos' in label or 'fenomenos' in label: data['fenomenos'] = clean(val)

        return data if data['nombre'] != '---' else None
    except:
        return None

def main():
    print("="*60)
    print(" 🕵️ EXTRACCIÓN QUIRÚRGICA DE DATOS ")
    print("="*60)
    
    session = requests.Session()
    # Calentamiento
    session.get("https://meteorologia.corpac.gob.pe/app/Meteorologia/tiempo/tiempoactual.php", headers=HEADERS, verify=False)
    
    # 1. Index (Fenómenos y Mapa)
    index_fenomenos = []
    map_temps = []
    try:
        r_index = session.get(URL_INDEX, headers=HEADERS, verify=False)
        r_index.encoding = 'utf-8'
        soup_index = BeautifulSoup(r_index.text, 'html.parser')
        
        # Extraer Fenómenos Meteorológicos de la barra lateral
        for a in soup_index.find_all('a', id='aero'):
            # El texto del fenómeno suele estar fuera del tag <b> o <font>
            font_tag = a.find_parent('font')
            if font_tag:
                desc_node = font_tag.next_sibling
                desc_text = str(desc_node).strip() if desc_node else "Sin reporte"
            else:
                desc_text = "Sin reporte"
            
            # Limpiar el texto (quitar "presenta ", ":", etc)
            desc_text = desc_text.replace('presenta ', '').strip().capitalize()
            if not desc_text or desc_text == '.': desc_text = "Sin reporte"
            
            index_fenomenos.append({
                'aeropuerto': a.get_text(strip=True), 
                'fenomeno': desc_text
            })

        for pt in soup_index.select('div.tiempoMapa'):
            city_id = pt.get('id', '').capitalize()
            val = pt.select_one('div.value b')
            icon = pt.find('img')
            icon_url = icon['src'] if icon else ""
            if icon_url and not icon_url.startswith('http'): 
                icon_url = "https://meteorologia.corpac.gob.pe" + (icon_url if icon_url.startswith('/') else "/app/Meteorologia/" + icon_url)
            
            # Obtener Coordenadas
            coords = CITY_COORDINATES.get(city_id, (0, 0))
            
            map_temps.append({
                'id': city_id, 
                'temp': val.get_text(strip=True) if val else "N/A", 
                'icon': icon_url,
                'lat': coords[0],
                'lon': coords[1]
            })
    except Exception as e:
        print(f"  [!] Error en scraping de index: {e}")

    # 2. Aeropuertos
    results = []
    print(f">>> Sincronizando {len(AIRPORT_MAPPING)} estaciones con pausas humanas...")
    for i, (icao, code_post, lat, lon) in enumerate(AIRPORT_MAPPING):
        print(f"  [{i+1}/{len(AIRPORT_MAPPING)}] Capturando {icao}...", end="\r")
        res = get_airport_weather(session, code_post, icao, lat, lon)
        if res:
            results.append(res)
            print(f"  [OK] {icao} - {res['temperatura']} / {res['viento']}           ")
        else:
            print(f"  [!] {icao} - Fallo en la captura.                   ")
        time.sleep(1.2)
        
    # Render
    env = Environment(loader=FileSystemLoader('templates'))
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    # 1. Dashboard Principal (ICAO)
    with open('tiempo_hoy.html', 'w', encoding='utf-8') as f:
        f.write(env.get_template('tiempo_hoy_template.html').render(
            fenomenos=index_fenomenos, 
            map_data=map_temps, 
            airports=results, 
            last_update=ahora
        ))

    # 2. NUEVA PÁGINA: Estado del Tiempo Hoy (Ciudades + Fenómenos resaltados)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(env.get_template('tiempo_hoy_ciudades_template.html').render(
            fenomenos=index_fenomenos, 
            map_data=map_temps, 
            airports=results, 
            last_update=ahora
        ))
            
    with open('tiempo_aeropuertos.html', 'w', encoding='utf-8') as f:
        f.write(env.get_template('tiempo_aeropuertos_template.html').render(airports=results, last_update=ahora))
    
    with open('panel_alerta.html', 'w', encoding='utf-8') as f:
        f.write(env.get_template('panel_alerta_template.html').render(airports=results, last_update=ahora))

    with open('panel_tecnico.html', 'w', encoding='utf-8') as f:
        f.write(env.get_template('panel_tecnico_template.html').render(airports=results, last_update=ahora))
    
    print("\n" + "="*60)
    print(f"🚀 DASHBOARDS ACTUALIZADOS: {len(results)} estaciones reales.")
    print("="*60)

if __name__ == "__main__":
    main()
