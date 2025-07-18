import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta

def fetch_vuelos(aeropuerto_code):
    url = f"https://www.aeropuertosargentina.com/vuelos/partidas/{aeropuerto_code}"
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    tabla = soup.find('table', class_='tabla-vuelos')
    vuelos = []
    for row in tabla.tbody.find_all('tr'):
        cols = [td.get_text(strip=True) for td in row.find_all('td')]
        hora_salida, vuelo, aerolinea, destino, estado = cols[:5]
        if destino.upper() != 'CORRIENTES (CNQ)':
            continue
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

if __name__ == '__main__':
    data_aep = fetch_vuelos('AEP')
    data_eze = fetch_vuelos('EZE')
    os.makedirs('frontend/public/data', exist_ok=True)
    with open('frontend/public/data/vuelos-aep.json', 'w', encoding='utf-8') as f:
        json.dump(data_aep, f, ensure_ascii=False, indent=2)
    with open('frontend/public/data/vuelos-eze.json', 'w', encoding='utf-8') as f:
        json.dump(data_eze, f, ensure_ascii=False, indent=2)
    print('Datos de vuelos actualizados.')
