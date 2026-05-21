# Gráficos Interactivos Plotly.js - Guía de Uso

## Descripción General

FASE 2 implementa 3 gráficos interactivos usando Plotly.js que se renderizan automáticamente cuando se carga un informe de un ticker.

## Flujo de Datos

```
GET /api/reports/{ticker}
    ↓
ReportResponse (incluye metrics.json)
    ↓
web/js/report.js → loadChartData(metrics)
    ↓
import { initCharts } from './charts.js'
    ↓
createPriceChart()
createValuationsChart()
createPerformanceChart()
    ↓
Plotly.newPlot() × 3 gráficos
```

## Los 3 Gráficos

### 1. Gráfico de Precio Histórico
**Tipo:** Line Chart  
**Ubicación:** priceChart (primera columna)

**Datos necesarios:**
```javascript
metrics.precios_historicos.ultimos_12m: [
  { date: "2025-05-21", close: 180.45 },
  { date: "2025-06-15", close: 185.23 },
  // ... más datos
]
```

**Características:**
- Línea azul (#035AA6)
- Relleno semi-transparente bajo la línea
- Hover: muestra fecha y precio exacto
- Zoom: drag para zoom, doble-click para reset
- Pan: shift + drag para desplazar
- Download: botón para guardar como PNG
- Grid visible para referencia
- Responsive: se adapta al tamaño del contenedor

**Ejemplo de uso:**
```javascript
const dates = ["2025-05-21", "2025-06-15", ...];
const prices = [180.45, 185.23, ...];
// Automático: createPriceChart(metrics)
```

---

### 2. Gráfico de Valuaciones
**Tipo:** Horizontal Bar Chart (Grouped)  
**Ubicación:** valuationChart (segunda columna)

**Datos necesarios:**
```javascript
metrics.valuations: {
  pe_ratio: 45.2,
  pb_ratio: 35.8,
  ps_ratio: 18.5,
  price_to_fcf: 12.3
}

metrics.sector_comparison: {
  pe_sector: 42.5,
  pe_sp500: 25.0,
  pb_sector: 32.0,
  pb_sp500: 3.2,
  ps_sector: 16.8,
  ps_sp500: 2.5
}
```

**Características:**
- 4 métricas comparadas: P/E, P/B, P/S, Price to FCF
- 3 series de datos:
  - Ticker (azul oscuro #049DD9)
  - Sector (azul claro #04B2D9)
  - S&P 500 (amarillo #F2C438)
- Valores mostrados sobre las barras
- Hover: muestra valor exacto
- Leyenda interactiva (click para mostrar/ocultar serie)
- Download: botón para guardar como PNG

**Interpretación:**
- Ticker por debajo de Sector: valoración más barata
- Ticker por encima de S&P500: más cara que el mercado general
- Útil para comparar si una acción es cara o barata

---

### 3. Gráfico de Desempeño
**Tipo:** Grouped Bar Chart  
**Ubicación:** performanceChart (tercera columna)

**Datos necesarios:**
```javascript
metrics.performance: {
  roe: 0.45,              // Return on Equity (45%)
  roa: 0.28,              // Return on Assets (28%)
  fcf_billions: 52.0,     // Free Cash Flow ($52B)
  dividend_yield: 0.008   // Dividend Yield (0.8%)
}
```

**Características:**
- 4 métricas de desempeño
- Colores diferentes para cada métrica (gradiente azul)
- Valores mostrados sobre las barras con unidades:
  - ROE: `45.00%`
  - ROA: `28.00%`
  - FCF: `$52.00B`
  - Dividend Yield: `0.80%`
- Hover: muestra métrica y valor
- Download: botón para guardar como PNG
- Interpretación inmediata: barras más altas = mejor desempeño

**Interpretación:**
- ROE > 15%: excelente rentabilidad
- FCF positivo: generación de efectivo saludable
- Dividend Yield > 0%: paga dividendos a accionistas

---

## Características Interactivas Generales

### Hover (Todas)
Pasa el ratón sobre cualquier parte:
- Muestra valores exactos
- Etiqueta descriptiva
- Se adapta al contexto

### Download
Botón en la esquina superior derecha de cada gráfico:
- Descarga como PNG
- Tamaño: 1024 × 768 px
- Incluye leyenda y titulo

### Zoom
Drag sobre el gráfico:
- Zoom en área seleccionada
- Doble-click para reset
- Scroll rueda del ratón también funciona

### Pan
Shift + Drag:
- Desplaza el gráfico sin cambiar escala

### Leyenda (Valuaciones)
Click en elementos de la leyenda:
- Show/hide series
- Facilita comparación enfocada

### Responsive
Cambio de tamaño de ventana:
- Gráficos se redimensionan automáticamente
- listener en `window.resize`
- Grid se adapta a pantalla móvil

---

## Integración con el Código

### En HTML
```html
<!-- Los contenedores existen -->
<div id="priceChart" class="chart-container"></div>
<div id="valuationChart" class="chart-container"></div>
<div id="performanceChart" class="chart-container"></div>

<!-- Plotly.js CDN ya cargado -->
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>

<!-- Script como módulo -->
<script type="module" src="/js/report.js"></script>
```

### En JavaScript
```javascript
// report.js
import { initCharts } from './charts.js';

async function loadChartData(metrics) {
    if (metrics) {
        document.getElementById('chartsSection').style.display = 'block';
        await initCharts(metrics);
    }
}
```

### En CSS
```css
.charts-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
    gap: 20px;
}

.chart-container {
    background: #F2F2F2;
    border-radius: 6px;
    padding: 15px;
    min-height: 400px;
}
```

---

## Manejo de Errores

Si faltan datos:

1. **Sin metrics.json**: Muestra error "No se disponibiliza datos para los gráficos"
2. **Sin precios históricos**: Muestra "Datos de precios no disponibles"
3. **Sin valuaciones/performance**: Muestra valores como `-` en el gráfico
4. **Error general**: Muestra "Error al renderizar gráfico"

Todos los errores se manejan gracefully sin romper la página.

---

## Responsividad

### Desktop (> 768px)
- 3 gráficos en fila (grid auto-fit, minmax 500px)
- Altura mínima: 400px
- Espacio entre gráficos: 20px

### Tablet (≤ 768px)
- 1 gráfico por fila (grid-template-columns: 1fr)
- Altura mínima: 300px
- Fuentes y padding reducidos

### Móvil
- Stack vertical
- Full width
- Elementos más compactos

---

## Validación de Datos

Los tests en `tests/test_charts_integration.py` validan:

1. Estructura de MetricsData
2. Presencia de todas las métricas requeridas
3. Tipos de datos correctos
4. Valores nulos permitidos
5. Serialización correcta
6. Compatibilidad API

```bash
pytest tests/test_charts_integration.py -v
# Resultado: 11 passed
```

---

## Próximas Mejoras Posibles

1. **Filtrado de fechas**: Permitir usuario seleccionar rango de fechas
2. **Comparación múltiple**: Comparar 2-3 tickers en mismo gráfico
3. **Exportación avanzada**: Descargar como CSV, PDF
4. **Temas**: Light/Dark mode para gráficos
5. **Animación**: Animación suave al cargar gráficos
6. **Tooltips personalizados**: Más información en hover
7. **Benchmarking**: Línea de referencia (sector promedio)
8. **Histórico comparativo**: Mostrar cambios mes a mes

---

## Referencias

- [Plotly.js Documentation](https://plotly.com/javascript/)
- [Plotly Chart Types](https://plotly.com/javascript/chart-types/)
- [Responsive Charts](https://plotly.com/javascript/responsive-chart/)
- Código: `web/js/charts.js`
- Tests: `tests/test_charts_integration.py`
