# scraper/scraper.py
from datetime import datetime, timedelta
import json
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://www.aeropuertosargentina.com/es/vuelos"

def fetch_vuelos(aero_code):
    # Configuro Chrome en modo headless
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=opts
    )
    driver.get(BASE_URL)

    wait = WebDriverWait(driver, 15)

    # 1) Seleccionar pestaña de "Partidas" (si es necesario)
    #    Ejemplo: driver.find_element(By.ID, "tab-departures").click()

    # 2) Select aeropuerto
    select_airport = wait.until(EC.element_to_be_clickable((By.ID, "fltOriginAirport")))
    Select(select_airport).select_by_value(aero_code)

    # 3) Fecha (dd/mm/YYYY)
    date_input = driver.find_element(By.ID, "fltDate")
    date_input.clear()
    today_str = datetime.now().strftime("%d/%m/%Y")
    date_input.send_keys(today_str)

    # 4) Destino
    dest_input = driver.find_element(By.ID, "fltDestinationAirport")
    dest_input.clear()
    dest_input.send_keys("Corrientes")

    # 5) Botón buscar
    driver.find_element(By.ID, "searchBtn").click()

    # 6) Esperar a que cargue la tabla de resultados
    tabla = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table#flightResults tbody")))
    time.sleep(1)  # un segundito extra por si hay animación

    filas = tabla.find_elements(By.TAG_NAME, "tr")
    vuelos = []
    for fila in filas:
        cols = fila.find_elements(By.TAG_NAME, "td")
        hora_salida = cols[0].text.strip()
        aerolinea  = cols[1].text.strip()
        numero     = cols[2].text.strip()
        estado     = cols[3].text.strip()

        # Calcular llegada +1h20m
        try:
            t0 = datetime.strptime(hora_salida, "%H:%M")
            hora_lleg  = (t0 + timedelta(hours=1, minutes=20)).strftime("%H:%M")
        except:
            hora_lleg = ""

        vuelos.append({
            "hora_salida": hora_salida,
            "aerolinea": aerolinea,
            "numero_vuelo": numero,
            "estado": estado,
            "hora_estimada_llegada": hora_lleg
        })

    driver.quit()
    return vuelos

def main():
    os.makedirs("frontend/public/data", exist_ok=True)
    for code in ["AEP", "EZE"]:
        lista = fetch_vuelos(code)
        out_path = f"frontend/public/data/vuelos-{code.lower()}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(lista, f, ensure_ascii=False, indent=2)
        print(f"Guardé {len(lista)} vuelos en {out_path}")

if __name__ == "__main__":
    main()
