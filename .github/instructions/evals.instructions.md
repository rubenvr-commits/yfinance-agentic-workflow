---
applyTo: "**"
---

# Reglas: Evals, tests y calidad para skills/agents

1. Ubicación de tests: todos los tests deben residir en `tests/` (seguir `test-location.instructions.md`).
2. Evals para skills:
   - Guardar prompts iniciales en `evals/evals.json` con `skill_name` y `evals` array.
   - Para cada eval crear `iteration-N/eval-X/` con `with_skill/` y `without_skill/` outputs.
3. Aserciones:
   - Priorizar aserciones objetivas; si son subjetivas, definir criterios de revisión humana.
4. Grading y benchmark:
   - Ejecutar grader subagent o script automatizado que produzca `grading.json` con `text`, `passed`, `evidence`.
   - Agregar `benchmark.json` con métricas de pass_rate, tiempo y tokens.
5. Registro de tiempos:
   - Guardar `timing.json` con `total_tokens` y `duration_ms` para cada run.
6. Reproducibilidad:
   - Documentar comandos para ejecutar los evals localmente y las dependencias necesarias.
