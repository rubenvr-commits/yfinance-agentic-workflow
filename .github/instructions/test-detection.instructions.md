---
applyTo: "**"
---

# Guía: Detección automática de tests en pre-commit hook

El hook `git-pre-commit` usa una estrategia multi-nivel para detectar automáticamente si existen tests para los archivos Python que estás commitiendo.

## Estrategias de Detección (en orden)

### 1. Por Nombre de Archivo (Convención)
El hook busca archivos de test con estos patrones:
- `tests/test_<nombre_módulo>.py`
- `__tests__/<nombre_módulo>.test.py`
- `<directorio_módulo>/test_<nombre_módulo>.py`
- `<directorio_módulo>/<nombre_módulo>_test.py`

**Ejemplo:**
```
Archivo a commitear: .github/skills/tavily-research/scripts/utils.py
Tests detectados automáticamente:
  ✓ tests/test_utils.py
  ✓ tests/test_tavily_api_migration.py (si importa utils)
```

### 2. Por Importación en Tests (NUEVO)
Si no encuentra tests por nombre, busca en la carpeta `tests/` cualquier archivo que importe el módulo.

**Ejemplo:**
```python
# tests/test_tavily_api_migration.py
from utils import TavilyAPIClient  # ✓ Detectado: "from utils import"
import utils                        # ✓ Detectado: "import utils"
```

### 3. Por Ubicación Relativa
Si el módulo tiene una carpeta `tests/` al mismo nivel, cualquier archivo `test_*.py` allí se considera válido.

**Ejemplo:**
```
.github/skills/tavily-research/
  ├── scripts/
  │   ├── utils.py
  │   └── researcher.py
  └── tests/
      └── test_integration.py  ✓ Detectado automáticamente
```

## Cuándo NO necesitas tests

El hook **excluye automáticamente**:
- Archivos que comienzan con `test_` (son tests en sí)
- Archivos que terminan con `_test.py` (son tests en sí)
- Scripts de validación (`validate_*.py`)
- Runners/orquestadores (`run_*.py`)
- Infraestructura en `.github/scripts/`

## Casos de Uso

### Caso 1: Crear test con nombre convencional
```bash
# Archivo a commitear:
.github/skills/mi-skill/scripts/processor.py

# Crear test con:
tests/test_processor.py  # ✓ Será detectado automáticamente
```

### Caso 2: Test genérico que cubre múltiples módulos
```bash
# Archivos a commitear:
.github/skills/tavily-research/scripts/utils.py
.github/skills/tavily-research/scripts/researcher.py

# Crear test único que cubre ambos:
tests/test_tavily_api_migration.py
  ├── from utils import TavilyAPIClient           # ✓ Cubre utils.py
  └── from researcher import TavilyResearcherAPI  # ✓ Cubre researcher.py
```

### Caso 3: Tests en carpeta del módulo
```bash
.github/skills/custom-skill/
  ├── scripts/
  │   └── core.py
  └── tests/
      └── test_core.py  # ✓ Detectado por ubicación relativa
```

## Flujo de Validación

Cuando haces `git commit`, para cada archivo `.py` (excepto tests e infraestructura):

1. ¿Existe `tests/test_<nombre>.py`? → OK
2. ¿Existe `tests/<nombre>_test.py`? → OK
3. ¿Algún archivo en `tests/` importa este módulo? → OK
4. ¿Existe carpeta `tests/` relativa al módulo? → OK
5. Si nada lo cubre → **WARNING** (puedes continuar con `y`)

## Recomendaciones

- **Preferencia 1**: Usa nombres convencionales (`test_<módulo>.py`)
- **Preferencia 2**: Si un test cubre múltiples módulos, asegúrate de hacer imports explícitos
- **Preferencia 3**: Para skills, puedes crear una carpeta `<skill>/tests/` con tus tests

---

> Esta guía se aplica al hook configurado en `.github/scripts/git-pre-commit` desde 2026-05-19.
