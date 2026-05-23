---
applyTo: "**"
---

# Reglas: Hooks (`.github/hooks/*.json` y agent-scoped hooks)

1. Ubicación y prioridad:
   - Workspace hooks: `.github/hooks/*.json` (se cargan automáticamente)
   - Agent-scoped hooks: declarar en frontmatter `hooks:` de `.agent.md` (Preview)
2. Formato de hook:
   - Objeto `hooks` con lifecycle events como claves (SessionStart, PreToolUse, PostToolUse, SubagentStart, SubagentStop, PreCompact, Stop)
   - Cada entrada: `type: "command"`, `command`, opcionales `windows`, `linux`, `osx`, `cwd`, `env`, `timeout`
3. Control y salida:
   - Salida stdout JSON con `continue`, `stopReason`, `hookSpecificOutput` para controlar la sesión
   - Exit code `2` para bloqueos críticos
4. PreToolUse:
   - Implementar `permissionDecision` (`allow` | `deny` | `ask`) cuando sea necesario para operaciones destructivas
5. Seguridad:
   - No ejecutar scripts desconocidos sin revisión manual
   - No incluir secrets en los archivos; usar variables de entorno
6. Logs y auditoría:
   - Hooks que modifiquen código deben registrar `transcript_path` y escribir en el log de hooks
