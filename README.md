# YFinance Agentic Workflow

Un flujo de trabajo de análisis de inversiones que combina datos de `yfinance`, búsquedas web estructuradas y principios de inversión de Berkshire Hathaway mediante skills de GitHub Copilot.

## Descripción general

Este repositorio reúne componentes para analizar empresas desde varias perspectivas:

- **Reportes técnicos** con `yfinance`
- **Investigación de fundamentos** con `tavily` y NotebookLM
- **Valoración basada en Buffett/Munger**
- **Skills de GitHub Copilot** para automatizar análisis
- **Persistencia en PostgreSQL**
- **Orquestación con Docker Compose**

## Skills disponibles

El proyecto incluye varias skills instalables y reusables:

- `.github/skills/berkshire-valuation/`
- `.github/skills/combined-valuation-workflow/`
- `.github/skills/frontend-design/`
- `.github/skills/skill-creator/`
- `.github/skills/tavily-research/`
- `.github/skills/web-search-fundamentales/`
- `.github/skills/yfinance-report/`

## Estructura del proyecto

```
yfinance-agentic-workflow/
├── .github/
│   └── skills/                    # Skills de GitHub Copilot
├── evaluaciones/                  # Reportes de análisis por ticker
│   ├── AAPL/
│   ├── GOOGL/
│   ├── MSFT/
│   ├── REP.MC/
│   └── ^IBEX/
├── postgres/                      # Datos de PostgreSQL
├── docker-compose.yml            # Orquestación de servicios
├── example.env                    # Ejemplo de variables de entorno
├── mcp_config.json               # Configuración local de MCP
├── requirements.txt              # Dependencias de Python
└── README.md                     # Documentación del proyecto
```

## Primeros pasos

### Requisitos

- Python 3.8+
- Docker y Docker Compose
- Git
- GitHub Copilot Chat (para usar las skills)

### Instalación

1. Clonar el repositorio:

```bash
git clone <repository-url>
cd yfinance-agentic-workflow
```

2. Crear un entorno virtual:

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:

Copia el ejemplo de entorno:

```bash
# Linux/macOS
cp example.env .env
# Windows PowerShell
copy example.env .env
```

Edita `.env` y añade tu clave de `TAVILY_API_KEY`.

5. Iniciar PostgreSQL con Docker Compose:

```bash
docker-compose up -d
```

## Flujo típico de análisis

### 1. Generar un reporte técnico con `yfinance`

```bash
python .github/skills/yfinance-report/scripts/generate_report.py AAPL
```

### 2. Ejecutar investigación fundamental con Tavily

```bash
python .github/skills/tavily-research/scripts/run_workflow.py --ticker REP.MC
```

### 3. Convertir resultados web en informe de fundamentos

```bash
python .github/skills/web-search-fundamentales/scripts/extract_fundamentales.py evaluaciones/REP.MC/raw-search/web-search.json
```

### 4. Aplicar valoración tipo Berkshire Hathaway

```bash
python .github/skills/berkshire-valuation/scripts/notebooklm_client.py ask \
  --notebook-id 6904dc8b-742e-4192-82db-32e81e1f5e0f \
  --question "¿Cómo vería Buffett una empresa con este perfil financiero?"
```

### 5. Ejecutar el flujo combinado

```bash
python .github/skills/combined-valuation-workflow/scripts/run_workflow.py REP.MC
```

## Ejemplo de salida

Los resultados se almacenan en `evaluaciones/{ticker}/`.
Por ejemplo:

- `evaluaciones/AAPL/informe-tecnico.md`
- `evaluaciones/REP.MC/informe-berkshire.md`
- `evaluaciones/REP.MC/informe-fundamentales.md`
- `evaluaciones/REP.MC/raw-search/web-search.json`

## Uso de las skills

### NotebookLM Client

```bash
python .github/skills/berkshire-valuation/scripts/notebooklm_client.py list
python .github/skills/berkshire-valuation/scripts/notebooklm_client.py ask \
  --notebook-id <ID> \
  --question "Tu pregunta aquí"
```

### Skill Creator

```bash
python .github/skills/skill-creator/scripts/quick_validate.py
python .github/skills/skill-creator/scripts/generate_report.py
python .github/skills/skill-creator/scripts/package_skill.py
```

## Principios de inversión clave

Este proyecto se apoya en los principios de Berkshire Hathaway:

- **Moat económico**: ventajas competitivas sostenibles
- **Círculo de competencia**: invertir en negocios con los que se tiene entendimiento
- **Margen de seguridad**: evaluar riesgo y precio de entrada conservadoramente
- **Calidad de gestión**: valorar integridad y capital allocation
- **Rendimiento sobre capital**: evaluar ROE y capacidad de reinversión

## Docker Compose

El servicio principal es PostgreSQL 18:

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

Comandos útiles:

```bash
docker-compose up -d
docker-compose logs -f postgres
docker-compose down
```

## Notas

- El archivo `example.env` contiene el ejemplo de configuración de entorno.
- `docker-compose.yml` carga `.env` para la configuración de PostgreSQL.
- `requirements.txt` incluye `yfinance`, `notebooklm-py`, `tavily` y otras dependencias necesarias.
