import os, json, time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "https://www.aeropuertosargentina.com/es/vuelos"
AIRPORTS = {"AEP": "Aeroparque", "EZE": "Ezeiza"}

def fetch_vuelos(code):
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    # opts.binary_location = "/usr/bin/google-chrome-stable"  # si hiciera falta

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=opts
    )
    driver.get(URL)

    wait = WebDriverWait(driver, 30)
    # 1) Seleccionar aeropuerto
    sel = wait.until(EC.presence_of_element_located((By.NAME, "idarpt")))
    Select(sel).select_by_visible_text(f"{AIRPORTS[code]}, {code}")

    # 2) Ingresar fecha de hoy (DD-MM-YYYY)
    inp_date = driver.find_element(By.NAME, "fecha")
    inp_date.clear()
    inp_date.send_keys(datetime.now().strftime("%d-%m-%Y"))

    # 3) Ingresar destino “Corrientes”
    inp_dest = driver.find_element(By.NAME, "destorig")
    inp_dest.clear()
    inp_dest.send_keys("Corrientes")

    # 4) Hacer click en el botón de búsqueda
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    # 5) Esperar tabla de resultados
    tbody = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table#flightResults tbody")))
    time.sleep(1)
    rows = tbody.find_elements(By.TAG_NAME, "tr")

    vuelos = []
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) < 4:
            continue
        salida, aero, num, est = [c.text.strip() for c in cols[:4]]
        # calcular llegada +1h20m
        try:
            t0 = datetime.strptime(salida, "%H:%M")
            llegada = (t0 + timedelta(hours=1, minutes=20)).strftime("%H:%M")
        except:
            llegada = ""
        vuelos.append({
            "hora_salida": salida,
            "aerolinea": aero,
            "numero_vuelo": num,
            "estado": est,
            "hora_estimada_llegada": llegada
        })

    driver.quit()
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
