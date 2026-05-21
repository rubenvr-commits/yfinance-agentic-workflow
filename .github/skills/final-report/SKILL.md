---
name: final-report
description: "Consolida los 3 informes de análisis (técnico, fundamentales, berkshire) en un informe final ejecutivo de 300-350 líneas que integra la información más relevante. Cuando el usuario pide consolidar informes, crear un informe final, o unificar análisis de un ticker, usa esta skill. Extrae datos de los archivos existentes (informe-tecnico.md, informe-fundamentales.md, informe-berkshire.md) en evaluaciones/{TICKER}/ y genera evaluaciones/{TICKER}/informe-final.md rellenando automáticamente la plantilla con información cuantitativa y cualitativa de calidad institucional."
---

# Final Report Skill

Consolida análisis financiero multi-dimensional en un informe ejecutivo integrado.

## Cuándo usar

Esta skill es la herramienta final después de generar los 3 reportes base. Úsala cuando:
- El usuario pide "consolidar" o "unificar" los informes
- Solicita un "informe final" o "resumen ejecutivo"
- Quiere un documento único de ~300-350 líneas que integre técnico + fundamentales + berkshire
- Dice "junta todo" o "resumen de los 3 informes"

## Qué hace

La skill:

1. **Busca los 3 informes** en `evaluaciones/{TICKER}/`
   - `informe-tecnico.md` - métricas cuantitativas
   - `informe-fundamentales.md` - contexto estratégico
   - `informe-berkshire.md` - valuación y recomendación

2. **Extrae datos clave** usando patrones específicos:
   - Ticker, empresa, sector del técnico
   - Precio, P/E, PEG, ROE, múltiplos del técnico
   - Visión, ventajas, riesgos del informe fundamentales
   - Moat rating, gestión, recomendación del Berkshire

3. **Rellena la plantilla** en 8 secciones:
   - Resumen ejecutivo con tesis integrada
   - Snapshot financiero (10 métricas clave)
   - Posición competitiva y moat económico
   - Calidad de gestión y decisiones críticas
   - Fundamentales estratégicos
   - Dinámica de crecimiento
   - Valuación por múltiples enfoques
   - Recomendación de inversión + catalizadores

4. **Genera** `evaluaciones/{TICKER}/informe-final.md`

## Output esperado

Un archivo markdown consolidado de ~350 líneas con:
- Información financiera concisa (del técnico)
- Contexto estratégico (del fundamentales)
- Análisis Berkshire (del Berkshire)
- Recomendación estructurada con razonamiento integrado
- Tablas que resumen datos, sin redundancia

## Patrones de extracción

**De informe-tecnico.md:**
- Ticker, Nombre, Sector desde tabla de identificación
- Precio, Cambio%, Capitalización desde "Datos de Precio"
- P/E Trailing/Forward, PEG, Price/Book desde "Múltiplos de Valoración"
- ROE, Deuda/Equity desde balances

**De informe-fundamentales.md:**
- Visión estratégica desde sección "Visión Estratégica a Largo Plazo"
- Ventajas competitivas desde "Ventajas Competitivas y Posición de Mercado"
- Riesgos desde análisis contextual
- Liderazgo desde "Decisiones Críticas de Gestión"

**De informe-berkshire.md:**
- Moat rating desde "ANÁLISIS DEL MOAT COMPETITIVO"
- Defensas principales desde tabla de moat
- Recomendación desde "Resumen Ejecutivo"
- Valuación desde "Valuación Objetiva Range"
- Margen de seguridad desde "Margen de Seguridad Actual"
- Tesis de inversión desde sección final

## Reglas de consolidación

1. **Prioriza relevancia sobre completitud** — incluye solo los datos más estratégicos
2. **Evita redundancia** — no repitas información entre secciones
3. **Mantén rigor institucional** — conserva métricas, no "suavices" datos
4. **Integra perspectivas** — técnico + fundamental + Berkshire en cada sección cuando sea posible
5. **Genera resumen ejecutivo nuevo** que capture la tesis integrada en 3-4 párrafos

## Estructura del informe final

```
1. Header (ticker, empresa, sector, recomendación)
2. Resumen Ejecutivo (tesis integrada)
3. Snapshot Financiero (10 métricas)
4. Posición Competitiva: Moat (rating, defensas, cuota)
5. Calidad de Gestión (CEO, decisiones, cultura)
6. Fundamentales Estratégicos (visión, ventajas, riesgos)
7. Dinámica de Crecimiento (métricas proyectadas)
8. Valuación por Múltiples (3 enfoques)
9. Análisis Margen de Seguridad + Recomendación
10. Apéndice: Métricas del Sector
```

## Ejemplo de mapeo

| Sección | Fuente Técnico | Fuente Fundamentales | Fuente Berkshire |
|---------|---|---|---|
| Snapshot Financiero | Todas las métricas | — | — |
| Moat Competitivo | Cuota de mercado | Ventajas competitivas | Análisis moat completo |
| Gestión | — | Decisiones críticas | Track record |
| Valuación | P/E, múltiplos | — | DCF, margen de seguridad |
| Recomendación | — | Contexto | Tesis Berkshire |

## Notas importantes

- **Formato**: El output debe ser markdown válido con tablas bien formateadas
- **Líneas**: Apunta a ~300-350 líneas (sin contar metadata)
- **Variables no rellenas**: Si algún dato no existe, deja la variable o marca con "N/D"
- **Fecha**: Usa la fecha de generación del informe técnico
- **Fuentes**: Incluye en footer que data viene de yFinance, Tavily, SEC Filings

## Casos de uso

**Caso 1: Usuario quiere consolidar NVDA**
- Busca: `evaluaciones/NVDA/informe-*.md`
- Consolida información
- Genera: `evaluaciones/NVDA/informe-final.md`

**Caso 2: Usuario quiere un resumen corto de inversión**
- Ejecuta skill en ticker existente
- Output es el informe final ejecutivo
- Listo para presentar o compartir

## Datos que deben estar disponibles

Los 3 informes deben existir en `evaluaciones/{TICKER}/`:
- Técnico: Métricas yfinance + múltiplos
- Fundamentales: Investigación web + contexto
- Berkshire: Moat, valuación, recomendación

Si falta alguno, detente y pide al usuario que genere los reportes faltantes primero.
