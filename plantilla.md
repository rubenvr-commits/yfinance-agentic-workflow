# ⚠️ REFERENCIA: Plantilla de Informe Financiero

> **Nota**: La versión canónica y mantenida de esta plantilla se encuentra en:
> 
> **`.github/skills/yfinance-report/plantilla.md`**
>
> Esta es una referencia de la estructura. Para modificaciones o actualizaciones, edita el archivo en la ubicación anterior.

---

## Descripción

Esta plantilla define la estructura de los informes financieros generados por la skill `yfinance-report`. Contiene 20 secciones principales que cubren:

1. Identificación del activo
2. Datos de precio actual
3. Capitalización de mercado
4. Múltiplos de valoración
5. Dividendos
6. Balance general
7. Estado de resultados
8. Rentabilidad
9. Flujo de caja
10. Salud financiera
11. Crecimiento
12. Información de accionistas
13. Datos de opciones
14. Análisis técnico
15. Eventos corporativos
16. Recomendaciones de analistas
17. Gestión ejecutiva
18. Análisis FODA
19. Divisiones de acciones
20. Conclusiones

## Campos Disponibles

La plantilla usa placeholders en formato `{NOMBRE_CAMPO}` que son automáticamente reemplazados con datos de yfinance.

### Ejemplos de campos:
- `{TICKER}` - Símbolo de la acción
- `{CURRENT_PRICE}` - Precio actual
- `{TRAILING_PE}` - P/E ratio (trailing)
- `{DIVIDEND_YIELD}` - Rendimiento de dividendo
- Y más de 100 campos adicionales

## Uso

La skill `yfinance-report` lee esta plantilla y la completa automáticamente con datos en tiempo real de Yahoo Finance.

```bash
python .github/skills/yfinance-report/scripts/generate_report.py AAPL
```

Resultado: `evaluaciones/AAPL/informe-yfinance.md`

---

**Última versión canónica**: `.github/skills/yfinance-report/plantilla.md`
