import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json, os

BASE = "https://www.aeropuertosargentina.com/es/vuelos"

# Mapeo de código a nombre para el parámetro idarpt
AEROPUERTOS = {
    "AEP": "Aeroparque",
    "EZE": "Ezeiza"
}

def fetch_vuelos(code):
    # Fecha de hoy en formato DD‑MM‑YYYY
    hoy = datetime.now().strftime("%d-%m-%Y")
    params = {
        "movtp": "partidas",
        "idarpt": f"{AEROPUERTOS[code]}, {code}",
        "fecha": hoy,
        "destorig": "Corrientes"
    }
    res = requests.get(BASE, params=params)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    tabla = soup.select_one("table#flightResults tbody")
    if not tabla:
        return []

    vuelos = []
    for fila in tabla.find_all("tr"):
        cols = fila.find_all("td")
        if len(cols) < 4:
            continue
        hora_salida = cols[0].get_text(strip=True)
        aerolinea  = cols[1].get_text(strip=True)
        numero     = cols[2].get_text(strip=True)
        estado     = cols[3].get_text(strip=True)

        # Calcular llegada +1h20m
        try:
            t0 = datetime.strptime(hora_salida, "%H:%M")
            llegada = (t0 + timedelta(hours=1, minutes=20)).strftime("%H:%M")
        except:
            llegada = ""

        vuelos.append({
            "hora_salida": hora_salida,
            "aerolinea": aerolinea,
            "numero_vuelo": numero,
            "estado": estado,
            "hora_estimada_llegada": llegada
        })
    return vuelos

def main():
    os.makedirs("frontend/public/data", exist_ok=True)
    for code in ("AEP", "EZE"):
        lista = fetch_vuelos(code)
        path = f"frontend/public/data/vuelos-{code.lower()}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(lista, f, ensure_ascii=False, indent=2)
        print(f"Guardé {len(lista)} vuelos en {path}")

if __name__ == "__main__":
    main()
