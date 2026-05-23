---
applyTo: "**"
---

# Reglas: Prompt engineering y prompt files

1. Diferenciar artefactos:
   - `prompt files`: uso ad-hoc para generar texto con reglas específicas
   - `agents`: personas persistentes con restricciones de herramientas
   - `skills`: capacidades reutilizables con recursos y tests
2. Tool list priority: si un prompt file declara `tools`, entender que la prioridad del prompt sobre herramientas es menor que la del agent frontmatter.
3. Plantillas:
   - Siempre incluir: objetivo, contexto mínimo, ejemplos de entrada, formato de salida esperado
   - Incluir instrucciones explícitas sobre qué suprimir (p.ej. no preguntar por secretos)
4. Robustez:
   - Añadir validaciones de entrada cuando el prompt interpreta formatos o archivos
5. Seguridad y privacidad:
   - Evitar prompts que pidan copiar/mostrar credenciales o datos privados
