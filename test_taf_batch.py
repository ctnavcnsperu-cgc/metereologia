import requests
from bs4 import BeautifulSoup
import urllib3
import time

# Desactivar advertencias de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL_TAF_BATCH = "https://meteorologia.corpac.gob.pe/app/Meteorologia/pronosticos/manualTaf.php"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://meteorologia.corpac.gob.pe/app/Meteorologia/pronosticos/reportetaf.php',
    'Content-Type': 'application/x-www-form-urlencoded',
}

def test_taf_batch(airport_codes):
    """
    airport_codes: string like 'SPJC SPQT SPSO SPCL'
    """
    session = requests.Session()
    session.get("https://meteorologia.corpac.gob.pe/app/Meteorologia/pronosticos/reportetaf.php", headers=HEADERS, timeout=20, verify=False)
    
    print(f"\n--- Probando Lote de TAF para: {airport_codes} ---")
    
    payload = {
        'aeropT': airport_codes,
        'incMetar': 'on'
    }
    
    try:
        start_time = time.time()
        r = session.post(URL_TAF_BATCH, data=payload, headers=HEADERS, timeout=20, verify=False)
        r.encoding = 'utf-8'
        elapsed = time.time() - start_time
        
        print(f"Tiempo de respuesta: {elapsed:.2f} segundos")
        
        if r.status_code == 200:
            # CORPAC devuelve un bloque de texto separado por líneas de guiones bajos
            # Usamos BeautifulSoup para obtener el texto plano pero respetando saltos de línea
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # Buscamos el contenedor principal (suele ser el body o un div central)
            # Como no hay IDs claros, buscamos el texto que tiene los guiones bajos.
            raw_text = soup.get_text(separator="\n", strip=True)
            
            # Dividimos por la línea de guiones bajos (al menos 20 guiones)
            blocks = re.split(r'_{20,}', raw_text)
            
            print(f"Bloques encontrados: {len(blocks)}")
            
            for i, block in enumerate(blocks):
                block = block.strip()
                if not block or "Volver" in block: continue
                
                print(f"\n--- REPORTE {i+1} ---")
                
                # Intentar separar METAR de TAF
                # El formato es "METAR: [texto] TAF: [texto]"
                lines = [line.strip() for line in block.split('\n') if line.strip()]
                
                metar = "N/A"
                taf = "N/A"
                
                current_section = None
                metar_acc = []
                taf_acc = []
                
                for line in lines:
                    if line.upper().startswith("METAR:"):
                        current_section = "METAR"
                        metar_acc.append(line.replace("METAR:", "").strip())
                    elif line.upper().startswith("TAF:"):
                        current_section = "TAF"
                        taf_acc.append(line.replace("TAF:", "").strip())
                    elif current_section == "METAR":
                        metar_acc.append(line)
                    elif current_section == "TAF":
                        taf_acc.append(line)
                
                print(f"METAR: {' '.join(metar_acc)}")
                print(f"TAF: {' '.join(taf_acc)}")
                
        else:
            print(f"Error en servidor: {r.status_code}")
            
    except Exception as e:
        print(f"Error en la petición: {e}")

if __name__ == "__main__":
    import re
    # Probando 4 aeropuertos principales juntos
    test_taf_batch("SPJC SPQT SPSO SPCL")
