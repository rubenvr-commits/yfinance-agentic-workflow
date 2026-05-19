---
applyTo: "**"
---

# Regla: Ubicación centralizada de tests

## TODOS los tests deben estar en la carpeta `tests/`

Antes de crear cualquier archivo de test, **debes verificar que esté ubicado en la carpeta raíz `tests/`** del proyecto. No deben haber tests dispersos en otras carpetas.

### Ubicaciones PROHIBIDAS para tests

Los tests **NUNCA** deben estar en:
- `.github/` - Reservado para configuración, scripts y hooks
- `evaluaciones/` - Reservado para reportes y análisis de activos
- Raíz del proyecto (`/`) - Excepto `run_staged_tests.py` que es un script de validación
- `src/` o directorios de código - Los tests van centralizados
- Cualquier otra subcarpeta del proyecto

### Ubicación CORRECTA para tests

```
proyecto/
├── tests/
│   ├── test_pre_commit_validator.py
│   ├── test_validator_integration.py
│   └── run_staged_tests.py          # Script de validación de tests
├── .github/
├── evaluaciones/
└── src/
```

### Convención de nombres de test

| Tipo | Ubicación | Ejemplo |
|------|-----------|---------|
| Unit tests | `tests/test_*.py` | `tests/test_pre_commit_validator.py` |
| Integration tests | `tests/test_*_integration.py` | `tests/test_validator_integration.py` |
| Test runners | `tests/run_*.py` | `tests/run_staged_tests.py` |
| Test fixtures | `tests/fixtures/` | `tests/fixtures/sample_data.json` |

### Flujo obligatorio

1. **Antes de crear un test**, verifica que esté dentro de la carpeta `tests/`:
   ```bash
   # Correcto
   tests/test_mi_feature.py

   # Incorrecto
   .github/test_mi_feature.py
   ```

2. **El pre-commit hook excluye automáticamente** la carpeta `tests/`, por lo que no necesitas crear tests para los tests.

3. **Los scripts de validación** como `run_staged_tests.py` van en `tests/` pero su propósito es ejecutar la suite completa, no ejecutarse a sí mismos.

### Ejemplos correctos

```bash
# Crear test unitario
touch tests/test_nuevo_modulo.py

# Crear test de integración
touch tests/test_nuevo_modulo_integration.py

# Crear fixtures reutilizables
mkdir tests/fixtures
touch tests/fixtures/test_data.json
```

### Ejemplos incorrectos

```bash
# Nunca hagas esto
touch .github/test_nuevo_modulo.py
touch evaluaciones/test_nuevo_modulo.py
touch test_nuevo_modulo.py  # en raíz
```

---

> Esta regla aplica a **todos los archivos del repositorio** (`applyTo: "**"`).  
> Es de cumplimiento obligatorio en cada sesión de trabajo, sin excepciones.  
> Los tests dispersos en otras carpetas deben ser movidos a `tests/` antes de cualquier commit.
