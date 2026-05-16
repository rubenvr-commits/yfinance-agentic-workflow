---
applyTo: "**"
---

# Regla: Protección de rama main

## NUNCA modifiques archivos directamente en la rama `main`

Antes de realizar **cualquier cambio** en el código (editar, crear, renombrar o eliminar archivos), **debes comprobar la rama activa**.

### Flujo obligatorio

1. **Comprueba la rama actual:**
   ```bash
   git branch --show-current
   ```

2. **Si estás en `main`**, crea una rama nueva antes de tocar nada:
   ```bash
   # Para nuevas funcionalidades:
   git checkout -b feature/nombre-descriptivo

   # Para correcciones de bugs:
   git checkout -b fix/nombre-descriptivo
   ```

3. **Solo entonces** procede con los cambios.

### Convención de nombres de rama

| Tipo | Prefijo | Ejemplo |
|------|---------|---------|
| Nueva funcionalidad | `feature/` | `feature/add-rag-pipeline` |
| Corrección de bug | `fix/` | `fix/mlflow-callback-error` |
| Refactor | `refactor/` | `refactor/etl-ingestion` |
| Documentación | `docs/` | `docs/update-readme` |
| Hotfix urgente | `hotfix/` | `hotfix/critical-auth-bug` |

### Ejemplos correctos

```bash
# Antes de editar cualquier archivo
git branch --show-current   # → main  ← PELIGRO
git checkout -b feature/new-endpoint

# Ahora sí, editar archivos
```

```bash
# Si ya estás en una rama de trabajo
git branch --show-current   # → feature/my-feature  ← OK
# Puedes editar directamente
```

### Ejemplos incorrectos

```bash
# Nunca hagas esto
git checkout main
# ... editar archivos directamente en main
git add .
git commit -m "cambios directos en main"
```

---

> Esta regla aplica a **todos los archivos del repositorio** (`applyTo: "**"`).  
> Es de cumplimiento obligatorio en cada sesión de trabajo, sin excepciones.
