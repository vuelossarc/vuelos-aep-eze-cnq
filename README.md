# Vuelos AEP/EZE → CNQ

Página web simple que muestra diariamente los vuelos desde Aeroparque y Ezeiza hacia Corrientes.

## Estructura

- `scraper/scraper.py`: script de scraping.
- `.github/workflows/scrape.yml`: workflow de GitHub Actions.
- `frontend`: aplicación Next.js.
- `frontend/public/data`: archivos JSON con los vuelos.

## Uso

1. **Scraper**: `python scraper/scraper.py`
2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
3. **Deploy**: Configurar Vercel apuntando al directorio `frontend`.
