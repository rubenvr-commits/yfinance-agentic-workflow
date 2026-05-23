---
applyTo: "**"
---

# Reglas: Creación y mantenimiento de `SKILL.md`

1. Frontmatter obligatorio:
   - `name`: identificador corto
   - `description`: breve *y* explícita sobre cuándo debe activarse el skill (frases/escenarios)
   - `tools` (opcional): listar solo las herramientas necesarias
2. Estructura mínima del cuerpo:
   - Propósito y ámbito (1 párrafo)
   - Input esperado (formatos, archivos de entrada)
   - Output esperado (archivos, rutas, formatos)
   - Ejemplos de uso (2–3 prompts reales)
   - Guía rápida de pruebas / evls (dónde y cómo ejecutar)
3. Tamaño y recursos:
   - Mantener el `SKILL.md` < 500 líneas; referencias extensas deben colocarse en `references/` dentro de la carpeta del skill.
4. Tests y evals:
   - Incluir 2-3 prompts para `evals/evals.json` y describir criterios de éxito mensurables.
5. Seguridad y permisos:
   - No hardcodear secretos; documentar dependencias externas y variables de entorno.
6. Versionado y cambios:
   - Cada cambio funcional en un skill debe acompañarse de un `CHANGELOG.md` mínimo en la carpeta del skill.
