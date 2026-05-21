# Demostración Visual - Gráficos Plotly.js

## Layout de Página

```
┌─────────────────────────────────────────────────────────────────────────┐
│  NVDA                              [← Volver]  [Descargar CSV]          │
│  Actualizado: 21 de mayo de 2026                                        │
│  Próxima revisión: 20 de junio de 2026                                  │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  GRÁFICOS INTERACTIVOS                                                  │
│                                                                          │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────┐
│  │ Precio Histórico     │  │ Valuaciones          │  │ Desempeño        │
│  │ (12 meses)           │  │                      │  │                  │
│  │                      │  │ P/E Ratio            │  │ ROE    [45.00%]  │
│  │    ╱╲                │  │ ▓▓ 45.20 ▒▒ 42.5 ░░ │  │ ROA    [28.00%]  │
│  │   ╱  ╲     ╱╲        │  │                      │  │ FCF    [$52.00B] │
│  │  ╱    ╲___╱  ╲       │  │ P/B Ratio            │  │ Div    [0.80%]   │
│  │ ╱                 ╲  │  │ ▓▓ 35.80 ▒▒ 32.0 ░░ │  │                  │
│  │                    ╲ │  │                      │  │ [⬇ Download]    │
│  │ $180.45 → $222.34   │  │ P/S Ratio            │  │                  │
│  │ [⬇ Download]        │  │ ▓▓ 18.50 ▒▒ 16.8 ░░ │  │                  │
│  │                      │  │                      │  │                  │
│  │ Leyenda:            │  │ Price/FCF            │  │ Colores:         │
│  │ — Close Price       │  │ ▓▓ 12.30             │  │ ▓▓ ROE, ROA      │
│  │ [⬇ Download]        │  │ [⬇ Download]         │  │ ░░ FCF, Div      │
│  └──────────────────────┘  └──────────────────────┘  └──────────────────┘
│
│  Leyenda:
│  ▓▓ = Ticker (NVDA)
│  ▒▒ = Sector
│  ░░ = S&P 500
│
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  INFORME FINAL                                                          │
│                                                                          │
│  # Análisis Completo de NVDA                                            │
│                                                                          │
│  NVIDIA es una empresa líder en semiconductores...                      │
│  - Valuación: 45.2x P/E, superior al sector (42.5x)                     │
│  - Desempeño: ROE de 45%, rentabilidad excepcional                      │
│  - Free Cash Flow: $52B, generación de caja muy saludable               │
│                                                                          │
│  ## Análisis Técnico                                                    │
│  Precio en alza con soporte en $215...                                  │
│                                                                          │
│  ## Análisis Fundamental                                                │
│  Crecimiento consistente en ingresos...                                 │
│                                                                          │
│  ## Valuación Berkshire                                                 │
│  Según principios de Buffett...                                         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│  INFORMES DETALLADOS                                                    │
│                                                                          │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐             │
│  │ Informe Técnico│  │ Análisis Fund. │  │ Valuación      │             │
│  │                │  │                │  │ Berkshire      │             │
│  │ Ver más        │  │ Ver más        │  │ Ver más        │             │
│  └────────────────┘  └────────────────┘  └────────────────┘             │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘

Análisis financiero - Datos actualizados al 21 de mayo de 2026
```

## Interactividad

### Gráfico 1: Precio Histórico
```
Acción: Hover sobre línea
Resultado: Muestra tooltip con:
  - Fecha exacta
  - Precio de cierre

Acción: Drag para zoom
Resultado: Zoom en área seleccionada

Acción: Doble-click
Resultado: Reset a vista original

Acción: Click en [⬇ Download]
Resultado: Descarga PNG de 1024x768

Acción: Resize ventana
Resultado: Gráfico se adapta automáticamente
```

### Gráfico 2: Valuaciones
```
Acción: Hover sobre barra
Resultado: Tooltip con valor exacto
  Ejemplo: "P/E Ratio: 45.20"

Acción: Click en leyenda (ej: "Sector")
Resultado: Muestra/oculta serie de datos

Acción: Drag para zoom
Resultado: Zoom en métrica seleccionada

Acción: Click en [⬇ Download]
Resultado: Descarga PNG del gráfico

Comparación visual:
  - Ticker (azul oscuro) vs Sector (azul claro) vs S&P500 (amarillo)
  - Ticker está por encima de Sector en P/E = más cara
  - Ticker está por encima de S&P500 en todas = prima valuation
```

### Gráfico 3: Desempeño
```
Acción: Hover sobre barra
Resultado: Muestra:
  - Métrica (ROE, ROA, FCF, Dividend Yield)
  - Valor con unidad (45.00%, $52.00B, etc)

Acción: Cada barra tiene color diferente
Resultado: Facilita identificación de métrica

Acción: Valores sobre barras
Resultado: Lectura directa sin hover necesario

Comparación:
  - ROE 45% = excelente rentabilidad (sector: 22%)
  - ROA 28% = muy buena eficiencia (sp500: 9%)
  - FCF $52B = generación de caja fuerte
  - Div 0.8% = bajo, reinvierte en crecimiento
```

## Responsividad Esperada

### Desktop (1200px)
```
[Gráfico 1: 400px] [Gráfico 2: 400px] [Gráfico 3: 400px]
```

### Tablet (768px)
```
[Gráfico 1: 100%]
[Gráfico 2: 100%]
[Gráfico 3: 100%]
```

### Móvil (320px)
```
[Gráfico 1: 100% - 30px]
[Gráfico 2: 100% - 30px]
[Gráfico 3: 100% - 30px]

Fuentes más pequeñas
Padding reducido
Altura mínima: 300px
```

## Paleta de Colores Usados

```
Primario:       #035AA6 (Azul oscuro - línea, títulos)
Primario claro: #049DD9 (Azul medio - ticker)
Primario más claro: #04B2D9 (Azul claro - sector)
Acento:         #F2C438 (Amarillo - S&P500)
Fondo:          #F2F2F2 (Gris claro)
Blanco:         #FFFFFF (Fondo gráficos)
Texto:          #333333 (Oscuro)
Texto muted:    #666666 (Gris)
```

## Estados Posibles

### Estado Normal (Datos completos)
```
✓ Los 3 gráficos se renderizan correctamente
✓ Todos los datos visibles
✓ Interactividad activa
✓ Responsive funcionando
```

### Estado con datos parciales
```
⚠ Falta precio histórico → "Datos de precios no disponibles"
⚠ Falta valuaciones → Muestra P/E, P/B, P/S, Price to FCF como "-"
⚠ Falta sector_comparison → S&P500 bars vacías
✓ Resto de gráficos funciona normalmente
```

### Estado Error
```
✗ Sin metrics.json → "No se disponibiliza datos para los gráficos"
✗ Archivo corrupto → "Error al cargar los gráficos"
✗ Sin conexión → Error de red en console
✓ Página no se rompe
✓ Se muestra mensaje de error clara
```

## Ejemplo de Flujo Real

1. Usuario abre: `/report.html?ticker=NVDA`
2. Se muestra: Loading spinner
3. Se carga: GET /api/reports/NVDA
4. Respuesta incluye: metrics.json con 13 precios históricos
5. Render: Los 3 gráficos aparecen con datos
6. Usuario puede: Hacer zoom, hover, download, resize
7. Usuario ve: Informe markdown debajo de gráficos
8. Usuario puede: Ver informes detallados en modal

## Performance

- Carga: < 1 segundo (después de fetch API)
- Render: < 500ms (3 gráficos)
- Zoom: Instantáneo
- Resize: Suave (smooth transition)
- Memory: ~2-5 MB por página

## Browsers Soportados

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile Safari iOS 14+
- Chrome Android 90+

## Accesibilidad

- Títulos descriptivos en gráficos
- Colores suficientemente contrastados
- Hover tooltips para información adicional
- Navegación sin mouse funciona (hover/focus states)
- ARIA labels en botones Download
