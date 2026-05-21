# Final Report Skill

Consolida 3 informes financieros (técnico, fundamentales, berkshire) en un informe final ejecutivo de 300-350 líneas.

## Estructura de la Skill

```
final-report/
├── SKILL.md                          # Definición y documentación de la skill
├── references/
│   └── plantilla.md                  # Plantilla de 350 líneas para rellenar
├── scripts/
│   └── consolidate_reports.py        # Script Python de consolidación
├── evals.json                        # Casos de prueba
└── README.md                         # Este archivo
```

## Cómo Funciona

### 1. Automáticamente (cuando la skill se activa)

- Detecta el ticker del usuario
- Busca los 3 informes en `evaluaciones/{TICKER}/`
- Extrae datos clave de cada uno
- Rellena la plantilla automáticamente
- Genera `evaluaciones/{TICKER}/informe-final.md`

### 2. Manualmente (con el script)

```bash
python .github/skills/final-report/scripts/consolidate_reports.py evaluaciones/NVDA
```

**Salida:**
```
Consolidando informes para NVDA...
Extrayendo datos para NVDA...
Informe guardado en: evaluaciones/NVDA/informe-final.md
Consolidación completada exitosamente para NVDA
```

## Datos Extraídos

### Del Técnico (informe-tecnico.md)
- Ticker, empresa, sector, industria
- Precio actual, capitalización
- P/E Trailing/Forward, PEG, Price/Book
- ROE, Deuda/Equity, Dividendos

### Del Fundamental (informe-fundamentales.md)
- Visión estratégica a largo plazo
- Ventajas competitivas (top 3)
- Valores corporativos
- Decisiones críticas de gestión

### Del Berkshire (informe-berkshire.md)
- Moat rating (1-10)
- Defensas principales (3 principales)
- Cuota de mercado
- Recomendación (COMPRA/MANTENER/EVITAR)
- Valuación objetivo (12-24 meses)
- Margen de seguridad
- Tesis de inversión integrada

## Output: Estructura del Informe Final

```
1. Header
   - Ticker, Empresa, Sector, Recomendación

2. Resumen Ejecutivo
   - Tesis integrada de 100-150 palabras
   - Valuación objetivo
   - Margen de seguridad

3. Snapshot Financiero
   - Tabla con 10 métricas clave
   - Precio, cap, múltiplos, rentabilidades

4. Posición Competitiva: Moat Económico
   - Fortaleza del moat (X/10)
   - 3 defensas principales
   - Cuota de mercado
   - Ventaja de precios

5. Calidad de Gestión
   - CEO y propiedad personal
   - 2 decisiones críticas
   - Análisis de gestión
   - Cultura corporativa

6. Fundamentales Estratégicos
   - Visión a largo plazo
   - 3 ventajas sostenibles
   - 3 factores de riesgo

7. Dinámica de Crecimiento
   - TTM vs Proyectado (+1y)
   - Ingresos, EBITDA, Flujo Libre
   - Drivers de crecimiento

8. Valuación por Múltiples
   - Comparable Forward (P/E)
   - DCF Normalizado
   - EV/EBITDA

9. Análisis Margen de Seguridad
   - Escenarios: Bajista, Base, Alcista
   - Valor esperado ponderado
   - Margen de seguridad

10. Recomendación de Inversión
    - Tesis en 3 puntos
    - Decisión por perfil de inversor
    - Catalizadores (próx. 6-12 meses)
    - Puntos de revisión de tesis

11. Apéndice
    - Métricas del sector
```

## Tamaño

- ~350 líneas de contenido
- Densidad: Ejecutivo sin perder rigor
- Integralmente: Técnico + Fundamental + Berkshire

## Casos de Uso

**Usuario solicita:**
- "Consolida los informes de NVDA"
- "Crea un informe final para REP.MC"
- "Dame un resumen de MSFT que una todo"
- "Quiero un documento con técnico + fundamental + berkshire"

**Skill activa automáticamente cuando:**
- Menciona consolidar/unificar informes
- Pide informe final/ejecutivo
- Dice "junta todo"

## Prerequisitos

Para que la skill funcione, deben existir los 3 informes:
- `evaluaciones/{TICKER}/informe-tecnico.md`
- `evaluaciones/{TICKER}/informe-fundamentales.md`
- `evaluaciones/{TICKER}/informe-berkshire.md`

Si falta alguno, la skill detiene y pide generarlos primero.

## Mejoras Futuras

- [ ] Generar gráficos ASCII de valuación
- [ ] Incluir comparación sector
- [ ] Generar PDF directamente
- [ ] Agregar análisis de sensibilidad
- [ ] Integración con NotebookLM para evals

## Ejemplo de Output

Ver: `evaluaciones/NVDA/informe-final.md` (después de ejecutar la skill)

## Soporte

Si encuentras problemas:
1. Verifica que los 3 informes existan
2. Revisa la estructura de directorios
3. Ejecuta el script con verbose: `python ... 2>&1 | tee consolidation.log`
