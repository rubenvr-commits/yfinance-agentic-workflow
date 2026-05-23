---
applyTo: "**"
---

# Reglas: Creación de agentes (`.agent.md`)

1. Frontmatter mínimo:
   - `name`, `description`, `tools` (lista mínima), `user-invocable` (bool)
   - `model` opcional; preferir dejar que el usuario elija si no es crítico
2. Principio de menor privilegio: declarar solo las herramientas necesarias.
3. Handoffs: si el flujo incluye pasos encadenados, definir `handoffs` con `label`, `agent` y `prompt`.
4. Body: responsabilidades, límites claros, ejemplos de prompts, y secciones de "qué NO hacer".
5. Hooks agente-específicos: usar solo si `chat.useCustomAgentHooks` está habilitado; documentar efectos y salida JSON.
6. Compartir: guardar en `.github/agents/` para visibilidad del equipo; agregar instrucciones cortas en `README.md` del repo si el agente es crítico.
