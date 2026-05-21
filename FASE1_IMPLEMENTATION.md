# FASE 1: Backend FastAPI + Frontend + Generación de Métricas JSON

Implementación completa de la Fase 1 del proyecto de reportes financieros.

## Cambios Realizados

### 1. Modificación de yfinance-report

**Archivo:** `.github/skills/yfinance-report/scripts/generate_report.py`

Se agregaron dos funciones para generar JSON con métricas cuantitativas:

- `_to_float_safe()`: Conversión segura de valores a float
- `_extract_price_history()`: Extrae histórico de precios (6m y 12m)
- `_build_metrics_json()`: Construye la estructura JSON con métricas

**Salida:** Genera `evaluaciones/{TICKER}/raw-search/metrics.json` con estructura:
```json
{
  "ticker": "NVDA",
  "fecha": "2026-05-21",
  "precio_actual": 222.34,
  "precios_historicos": {
    "ultimos_6m": [...],
    "ultimos_12m": [...]
  },
  "valuations": {
    "pe_ratio": 45.2,
    "pb_ratio": 35.8,
    "ps_ratio": 18.5,
    "price_to_fcf": null
  },
  "performance": {
    "roe": 0.45,
    "roa": 0.28,
    "fcf_billions": 52.0,
    "dividend_yield": 0.008
  },
  "sector_comparison": {
    "pe_sector": null,
    "pe_sp500": null
  }
}
```

### 2. Aplicación FastAPI

**Carpeta:** `app/`

Estructura completa siguiendo best practices de FastAPI:

```
app/
├── __init__.py
├── config.py              # Configuración general
├── main.py               # Entrada FastAPI con CORS y montaje de archivos estáticos
├── models.py             # Modelos Pydantic para requests/responses
├── routes/
│   ├── __init__.py
│   ├── health.py         # Endpoint de salud
│   └── reports.py        # Endpoints principales
└── services/
    ├── __init__.py
    ├── report_service.py    # Lectura de reportes y métricas
    ├── generation_service.py # Lógica de generación (placeholder Phase 1)
    └── csv_service.py       # Exportación a CSV
```

**Endpoints Implementados:**

1. `GET /api/reports/{ticker}/status` - Verificar si existe un informe
2. `GET /api/reports/{ticker}` - Obtener contenido completo del informe + métricas
3. `POST /api/reports/{ticker}/generate` - Iniciar generación (placeholder)
4. `GET /api/reports/{ticker}/generate/progress` - Obtener progreso (placeholder)
5. `GET /api/reports/{ticker}/precios.csv` - Descargar precios como CSV
6. `GET /api/reports/{ticker}/charts-data` - Obtener datos para gráficos
7. `GET /health` - Health check
8. `GET /docs` - Documentación interactiva Swagger

**Validaciones:**
- Formato de ticker: `[A-Z0-9.]{1,6}`
- Manejo de errores HTTP apropiados
- CORS habilitado para desarrollo

### 3. Frontend

**Carpeta:** `web/`

```
web/
├── index.html            # Página de búsqueda
├── report.html           # Página de informe
├── css/
│   ├── styles.css        # Estilos generales
│   └── report.css        # Estilos específicos de reportes
└── js/
    ├── search.js         # Lógica de búsqueda
    └── report.js         # Lógica de renderizado de reportes
```

**index.html - Página de Búsqueda:**
- Input para ticker + botón de búsqueda
- Tabla de reportes recientes (ejemplos)
- Indicador de carga y manejo de errores
- Validación de formato de ticker
- Opción para generar nuevo informe si no existe

**report.html - Página de Informe:**
- Header con navegación (volver, descargar CSV)
- Metadata (fecha de actualización, próxima revisión)
- Sección de gráficos (placeholders - Fase 2)
- Contenido markdown renderizado
- Sección de informes detallados (3 links modales)
- Indicadores de loading/error

**Características CSS:**
- Paleta de colores personalizada (#035AA6, #049DD9, #04B2D9, #F2C438, #F2F2F2)
- Diseño responsivo (mobile-first)
- Gradientes y sombras profesionales
- Transiciones suaves
- Sin emojis en código (solo en comentarios)

**Funcionalidad JavaScript:**
- `search.js`: Valida ticker, verifica existencia de informe, desencadena generación
- `report.js`: Carga informe, renderiza markdown, prepara datos para gráficos
- Markdown rendering con markdown-it
- Exportación CSV directa desde el navegador

### 4. Dependencias Actualizadas

**requirements.txt:**
```
fastapi==0.115.0
uvicorn==0.32.1
pydantic==2.10.0
```

**pyproject.toml:** Agregado con configuración del proyecto

## Cómo Usar

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Generar métricas (paso previo)
```bash
python .github/skills/yfinance-report/scripts/generate_report.py NVDA
```

Esto generará:
- `evaluaciones/NVDA/informe-tecnico.md`
- `evaluaciones/NVDA/raw-search/metrics.json`

### 3. Iniciar el servidor
```bash
python run.py
```

El servidor estará disponible en: http://localhost:8000

### 4. Acceder a la interfaz
- Frontend: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs

## API Reference

### GET /api/reports/{ticker}/status
```bash
curl http://localhost:8000/api/reports/NVDA/status
```

Response:
```json
{
  "exists": true,
  "age_days": 5,
  "generated_date": "2026-05-16"
}
```

### GET /api/reports/{ticker}
```bash
curl http://localhost:8000/api/reports/NVDA
```

Response incluye: content (markdown), ticker, generated_date, metrics (JSON)

### GET /api/reports/{ticker}/precios.csv
```bash
curl http://localhost:8000/api/reports/NVDA/precios.csv > precios.csv
```

### GET /api/reports/{ticker}/charts-data
```bash
curl http://localhost:8000/api/reports/NVDA/charts-data
```

## Notas de Fase 1

1. **Gráficos Plotly:** Están preparados pero vacíos (Fase 2)
2. **Generación de Reportes:** El endpoint POST es un placeholder (Fase 2)
3. **Informes Detallados:** Los modales están listos pero cargan de placeholder (Fase 2)
4. **Sector Comparison:** Los datos son null por ahora (se rellenarán en análisis posterior)

## Testing

Para verificar que todo funciona:

1. Ir a http://localhost:8000
2. Ingresar un ticker existente (ej: NVDA)
3. Buscar informe
4. Ver informe renderizado
5. Descargar CSV de precios

## Errores Comunes

**"Report not found"**
- Solución: Ejecutar `generate_report.py TICKER` primero

**CORS errors en cliente**
- Ya está habilitado, verificar console del navegador

**"Invalid ticker format"**
- Solo caracteres alfanuméricos y punto (max 6 caracteres)

## Próximos Pasos (Fase 2)

1. Implementar gráficos Plotly en el frontend
2. Integrar con el agente analista-financiero
3. Implementar WebSocket para progreso en tiempo real
4. Agregar datos sector_comparison
5. Completar los informes detallados (técnico, fundamentales, berkshire)
