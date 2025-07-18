import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import os
import sys

def fetch_vuelos(aeropuerto_code):
    url = f"https://www.aeropuertosargentina.com/vuelos/partidas/{aeropuerto_code}"
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    # Intentamos encontrar la tabla de vuelos
    tabla = soup.find('table', class_='tabla-vuelos')
    if tabla is None:
        # si cambia la clase o el ID en el futuro, agregar nuevos selectores aquí
        tabla = soup.find('table', id='partidas-table')

    if tabla is None:
        print(f"[WARN] No se encontró la tabla de vuelos en {url}", file=sys.stderr)
        return []

    vuelos = []
    for row in tabla.tbody.find_all('tr'):
        cols = [td.get_text(strip=True) for td in row.find_all('td')]
        try:
            hora_salida, vuelo, aerolinea, destino, estado = cols[:5]
        except ValueError:
            continue
        if 'CNQ' not in destino.upper():
            continue
        # Calcular hora estimada de arribo (+1h20m)
        dt = datetime.strptime(hora_salida, '%H:%M') + timedelta(hours=1, minutes=20)
        hora_arribo = dt.strftime('%H:%M')
        vuelos.append({
            'origen': aeropuerto_code,
            'hora_salida': hora_salida,
            'aerolinea': aerolinea,
            'numero_vuelo': vuelo,
            'estado': estado,
            'hora_estimacion_arribo': hora_arribo
        })
    return vuelos

def main():
    resultados = {}
    for code in ('AEP', 'EZE'):
        try:
            resultados[code] = fetch_vuelos(code)
        except Exception as e:
            print(f"[ERROR] scraping {code}: {e}", file=sys.stderr)
            resultados[code] = []

    # Aseguramos que exista la carpeta de salida
    out_dir = 'frontend/public/data'
    os.makedirs(out_dir, exist_ok=True)

    # Guardamos los JSON resultantes
    with open(os.path.join(out_dir, 'vuelos-aep.json'), 'w', encoding='utf-8') as f:
        json.dump(resultados.get('AEP', []), f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir, 'vuelos-eze.json'), 'w', encoding='utf-8') as f:
        json.dump(resultados.get('EZE', []), f, ensure_ascii=False, indent=2)

    print("Scraping completado con éxito.")

if __name__ == '__main__':
    main()
