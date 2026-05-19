# YFinance Agentic Workflow

Un sistema integrado de análisis de inversiones que combina datos de `yfinance`, búsquedas web estructuradas, agentes especializados y principios de inversión de Berkshire Hathaway mediante skills de GitHub Copilot.

## Descripción General

Este repositorio es una plataforma de investigación financiera empresarial que automatiza el análisis de activos desde múltiples perspectivas:

- **Análisis técnico cuantitativo** con yfinance (precios, ratios, balance sheet)
- **Investigación fundamental cualitativa** con Tavily API y NotebookLM
- **Valoración según principios Berkshire Hathaway** (moat, management, margin of safety)
- **Agentes especializados** para análisis automatizado y orquestación
- **Skills reutilizables** de GitHub Copilot para cada componente
- **Control de calidad automático** con pre-commit hooks
- **Persistencia de datos** en PostgreSQL
- **Orquestación** con Docker Compose

## Componentes del Proyecto

### Agentes Especializados (4)

| Agente | Descripción | Caso de Uso |
|--------|-------------|-----------|
| **analista-financiero** | CFA Level III especializado en value investing | Análisis completo de activos con tesis de inversión |
| **product-owner** | Especificaciones y requisitos de productos | Definir features, escribir user stories, revisar código |
| **q-a-tester** | Creación automática de tests | Validar funcionalidad con casos de test mínimos |
| **web-app-developer** | Desarrollo de interfaces web profesionales | Crear componentes React, dashboards, UIs production-ready |

### Skills de GitHub Copilot (6)

| Skill | Descripción | Entrada | Salida |
|-------|-------------|---------|--------|
| **yfinance-report** | Genera reportes técnicos financieros completos | Ticker (ej: AAPL, REP.MC) | `evaluaciones/{ticker}/informe-tecnico.md` |
| **tavily-research** | Investigación web estructurada en 4 dimensiones | Ticker + empresa (ej: REP.MC, "Repsol, S.A.") | `evaluaciones/{ticker}/raw-search/web-search.json` |
| **web-search-fundamentales** | Convierte JSON de búsqueda a informe markdown | `raw-search/web-search.json` | `evaluaciones/{ticker}/informe-fundamentales.md` |
| **berkshire-valuation** | Análisis de valuación Buffett/Munger con NotebookLM | Informe técnico + contexto | `evaluaciones/{ticker}/informe-berkshire.md` |
| **skill-creator** | Herramientas para crear y optimizar skills | Descripción de nueva skill | Skill empaquetada y lista para instalar |
| **frontend-design** | UI/UX profesional para web (React, HTML/CSS) | Descripción de interfaz | Código component production-ready |

### Sistema de Control de Calidad

- **Pre-commit hooks automáticos** (`.github/hooks/pre-commit-validator.json`): Valida tests antes de commits
- **Git hooks opcionales** (`.github/scripts/git-pre-commit`): Detección local de archivos sin tests
- **Detección inteligente de tests**: Por nombre convencional, por importaciones, por ubicación relativa
- **Protección de rama `main`**: Requiere rama de feature/fix antes de cambios
- **Instrucciones de desarrollo** centralizadas en `.github/instructions/`

## Estructura del Proyecto

```
yfinance-agentic-workflow/
├── .github/
│   ├── agents/                           # Agentes especializados
│   │   ├── analista-financiero.agent.md
│   │   ├── product-owner.agent.md
│   │   ├── q-a-tester.agent.md
│   │   └── web-app-developer.agent.md
│   ├── hooks/                            # Pre-commit hooks
│   │   ├── pre-commit-validator.json    # Hook automático de agent
│   │   └── README.md                    # Documentación de hooks
│   ├── instructions/                     # Reglas de desarrollo
│   │   ├── branch-protection.instructions.md
│   │   ├── no-emojis.instructions.md
│   │   ├── test-detection.instructions.md
│   │   └── test-location.instructions.md
│   ├── scripts/                          # Scripts de utilidad
│   │   ├── git-pre-commit               # Hook de git (opcional)
│   │   └── validate_pre_commit.py       # Validador de pre-commit
│   └── skills/                           # Skills de GitHub Copilot
│       ├── berkshire-valuation/          # Análisis Berkshire
│       ├── frontend-design/              # Interfaz web
│       ├── skill-creator/                # Creador de skills
│       ├── tavily-research/              # Investigación web
│       ├── web-search-fundamentales/     # Conversión web a informe
│       └── yfinance-report/              # Reportes técnicos
├── evaluaciones/                         # Reportes generados
│   ├── ^IBEX/                           # Índice IBEX-35
│   ├── NVDA/                            # NVIDIA
│   ├── REP.MC/                          # Repsol
│   └── [ticker]/                        # Nuevas evaluaciones
├── tests/                                # Tests centralizados
│   ├── test_pre_commit_validator.py
│   ├── test_validator_integration.py
│   ├── test_tavily_api_migration.py
│   ├── test_researcher.py
│   ├── test_utils.py
│   ├── test_configuration_files.py
│   ├── run_staged_tests.py
│   └── run_tavily_tests.py
├── postgres/                             # Datos PostgreSQL (volumen Docker)
├── .env                                  # Variables de entorno (privado)
├── example.env                           # Ejemplo de configuración
├── docker-compose.yml                    # Orquestación de servicios
├── requirements.txt                      # Dependencias Python
└── README.md                             # Este archivo
```

## Evaluaciones Disponibles

Actualmente disponibles estos análisis completos:

- **^IBEX** - Índice IBEX-35 (informe-técnico.md, informe-berkshire.md)
- **NVDA** - NVIDIA Corp (informe-técnico.md, informe-fundamentales.md, informe-berkshire.md)
- **REP.MC** - Repsol, S.A. (informe-técnico.md, informe-fundamentales.md, informe-berkshire.md)

## Reglas de Desarrollo

Antes de modificar código, **lee obligatoriamente las reglas**:

### 1. Protección de Rama `main`
- **Nunca modifiques archivos directamente en `main`**
- Siempre crea una rama nueva:
  ```bash
  git branch --show-current  # Verifica rama actual
  git checkout -b feature/descripcion  # Para features
  git checkout -b fix/descripcion      # Para bugs
  ```

### 2. Convención de Nombres de Rama
| Tipo | Prefijo | Ejemplo |
|------|---------|---------|
| Nueva funcionalidad | `feature/` | `feature/add-valuation-engine` |
| Corrección de bug | `fix/` | `fix/tavily-api-timeout` |
| Refactor | `refactor/` | `refactor/portfolio-module` |
| Documentación | `docs/` | `docs/update-skill-guide` |
| Hotfix urgente | `hotfix/` | `hotfix/critical-auth-issue` |

### 3. Ubicación Centralizada de Tests
- **Todos los tests van en `tests/`** (no dispersos)
- Nombres convencionales:
  - `tests/test_nombre_modulo.py` (unit tests)
  - `tests/test_nombre_integration.py` (integration tests)
  - `tests/fixtures/` (datos de prueba)

### 4. Detección Automática de Tests
El pre-commit hook busca tests por:
1. **Nombre convencional**: `tests/test_<módulo>.py`
2. **Importación en tests**: Si algún archivo en `tests/` importa el módulo
3. **Ubicación relativa**: Carpeta `tests/` al mismo nivel del módulo

Ejemplo:
```bash
# Archivo a commitear
.github/skills/tavily-research/scripts/utils.py

# Tests detectados automáticamente si existe:
tests/test_utils.py
tests/test_tavily_api_migration.py (que importa utils)
```

### 5. No Usar Emojis
- Todos los archivos deben ser texto claro y profesional
- Elimina emojis antes de guardar

## Primeros Pasos

### Requisitos
- Python 3.8+
- Docker y Docker Compose
- Git
- GitHub Copilot Chat (para usar agentes y skills)
- Claves API: `TAVILY_API_KEY`, `NOTEBOOKLM_ID`

### Instalación

1. **Clonar repositorio**:
   ```bash
   git clone <repository-url>
   cd yfinance-agentic-workflow
   ```

2. **Crear entorno virtual**:
   ```bash
   python -m venv .venv
   
   # macOS/Linux
   source .venv/bin/activate
   
   # Windows PowerShell
   .venv\Scripts\Activate.ps1
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**:
   ```bash
   # Copiar archivo ejemplo
   cp example.env .env  # Linux/macOS
   # o
   copy example.env .env  # Windows
   ```
   
   Edita `.env` y añade:
   - `TAVILY_API_KEY` - Obtén en https://app.tavily.com
   - `NOTEBOOKLM_ID` - Ya está configurado en `example.env` (6904dc8b-742e-4192-82db-32e81e1f5e0f) y no es personalizable

5. **Iniciar PostgreSQL** (opcional, para persistencia):
   ```bash
   docker-compose up -d
   ```

## Flujo de Trabajo Recomendado

### Escenario 1: Análisis Completo de un Nuevo Ticker (Using Analista Financiero)

```bash
# Comando en GitHub Copilot Chat
@analista-financiero Analiza AAPL con visión Berkshire

# El agente orquesta automáticamente:
# 1. Genera informe técnico con yfinance
# 2. Ejecuta investigación web con Tavily
# 3. Convierte búsqueda a informe de fundamentales
# 4. Aplica análisis Berkshire Hathaway
# 5. Produce tesis de inversión

# Resultado: 4 archivos en evaluaciones/AAPL/
```

### Escenario 2: Crear Nueva Funcionalidad

```bash
# 1. Crear rama de feature
git checkout -b feature/add-momentum-analysis

# 2. Implementar cambios
# ... editar archivos ...

# 3. Crear tests (automáticamente detectados)
touch tests/test_momentum.py

# 4. Pre-commit valida automáticamente
git add .
git commit -m "feat: add momentum analysis"
# ✓ Hook detecta test_momentum.py y valida

# 5. Push a rama de feature
git push origin feature/add-momentum-analysis
```

### Escenario 3: Crear Nueva Skill

```bash
# Solicita al agente skill-creator
@skill-creator Crea una skill para análisis de opciones

# El agente:
# 1. Define estructura SKILL.md
# 2. Genera scripts necesarios
# 3. Empaqueta como skill instalable
# 4. Proporciona instrucciones de instalación
```

## Flujo Típico de Análisis (Manual)

### 1. Generar Reporte Técnico con yfinance

```bash
python .github/skills/yfinance-report/scripts/generate_report.py AAPL
# → evaluaciones/AAPL/informe-tecnico.md
```

### 2. Ejecutar Investigación Fundamental con Tavily

```bash
python .github/skills/tavily-research/scripts/run_workflow.py \
  --ticker REP.MC \
  --company-name "Repsol, S.A." \
  --sector "Energy / Oil & Gas"
# → evaluaciones/REP.MC/raw-search/web-search.json
```

### 3. Convertir Resultados Web a Informe

```bash
python .github/skills/web-search-fundamentales/scripts/extract_fundamentales.py \
  evaluaciones/REP.MC/raw-search/web-search.json
# → evaluaciones/REP.MC/informe-fundamentales.md
```

### 4. Aplicar Valoración Berkshire Hathaway

```bash
python .github/skills/berkshire-valuation/scripts/notebooklm_client.py ask \
  --notebook-id 6904dc8b-742e-4192-82db-32e81e1f5e0f \
  --question "¿Cómo vería Buffett a Repsol con estos fundamentos?"
# → evaluaciones/REP.MC/informe-berkshire.md
```

## Uso de Herramientas Principales

### NotebookLM Client (Berkshire Valuation)

```bash
# Listar notebooks disponibles
python .github/skills/berkshire-valuation/scripts/notebooklm_client.py list

# Hacer pregunta al oráculo
python .github/skills/berkshire-valuation/scripts/notebooklm_client.py ask \
  --notebook-id <ID> \
  --question "Tu pregunta aquí"
```

### Skill Creator (Crear Skills)

```bash
# Validar skill
python .github/skills/skill-creator/scripts/quick_validate.py

# Generar reporte de performance
python .github/skills/skill-creator/scripts/generate_report.py

# Empaquetar skill para instalar
python .github/skills/skill-creator/scripts/package_skill.py
```

### Running Tests

```bash
# Ejecutar todos los tests
python tests/run_staged_tests.py

# Ejecutar tests de Tavily específicamente
python tests/run_tavily_tests.py
```

## Principios de Inversión Clave

Este proyecto implementa la filosofía de inversión de Berkshire Hathaway:

- **Moat Económico**: Identificar ventajas competitivas sostenibles
- **Círculo de Competencia**: Invertir en negocios que se entienden profundamente
- **Margen de Seguridad**: Evaluar conservadoramente riesgo vs. recompensa
- **Calidad de Gestión**: Valorar integridad, visión y capital allocation
- **Retorno sobre Capital**: Analizar ROE, ROIC y capacidad de reinversión
- **Precio vs. Valor**: Buscar empresas cotizando por debajo del valor intrínseco

## Docker Compose

Servicio PostgreSQL 18 para persistencia de datos:

```yaml
services:
  postgres:
    image: postgres:18
    container_name: yfinance_postgres
    env_file:
      - .env
    ports:
      - '5432:5432'
    volumes:
      - ./postgres/18/docker:/var/lib/postgresql/data
    restart: unless-stopped
```

**Comandos útiles**:
```bash
docker-compose up -d      # Iniciar servicios
docker-compose logs -f    # Ver logs
docker-compose down       # Detener servicios
docker-compose ps         # Ver estado
```

## Documentación de Desarrollo

Archivos de instrucción obligatorios en `.github/instructions/`:

- `branch-protection.instructions.md` - Protección de main
- `no-emojis.instructions.md` - Convención de texto
- `test-location.instructions.md` - Ubicación de tests
- `test-detection.instructions.md` - Detección automática

## Notas de Configuración

- `example.env` contiene ejemplo de configuración (no editar, usar para crear `.env`)
- `.env` contiene claves privadas (no commitear, añadir a `.gitignore`)
- `docker-compose.yml` carga `.env` para configurar PostgreSQL
- `requirements.txt` incluye: yfinance, notebooklm-py, tavily-py, y más
- Pre-commit hooks se auto-cargan en VS Code (no requiere instalación manual)

## Ejemplo de Salida

Los resultados se organizan como:
```
evaluaciones/{ticker}/
├── informe-tecnico.md              # Análisis técnico yfinance
├── informe-fundamentales.md        # Investigación cualitativa
├── informe-berkshire.md            # Valoración Berkshire
└── raw-search/
    └── web-search.json             # JSON bruto de Tavily
```

Ejemplo: `evaluaciones/REP.MC/informe-berkshire.md`

## Licencia

Ver [LICENSE](LICENSE)

## Contacto & Contribuciones

Este es un proyecto personal de investigación. Para preguntas o mejoras, crea un issue o pull request.

---

**Última actualización**: Mayo 2026
