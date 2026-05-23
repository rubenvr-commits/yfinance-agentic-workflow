# YFinance Agentic Workflow

Plataforma de investigación financiera que combina `yfinance`, búsquedas web estructuradas, agentes especializados y reglas de valoración inspiradas en Berkshire Hathaway.

## Resumen rápido

- API en `app/` (FastAPI) y frontend estático en `web/`.
- Punto de entrada: `run.py` para desarrollo local.
- Salidas organizadas en `evaluaciones/{TICKER}/` (informes técnicos, fundamentales y de valoración).

## Cambios recientes en este README

- Actualizado: requisitos de Python, comandos de inicio y guía mínima de contribución.

## Requisitos mínimos

- Python 3.10+
- Git
- Claves API: `TAVILY_API_KEY`, `NOTEBOOKLM_ID`

## Inicio rápido (desarrollo)

1. Clona el repositorio y sitúate en la carpeta:

```bash
git clone <repository-url>
cd yfinance-agentic-workflow
```

2. Crea y activa el entorno virtual:

```bash
python -m venv .venv
# Windows PowerShell
.venv\\Scripts\\Activate.ps1
# macOS/Linux
source .venv/bin/activate
```

3. Instala dependencias:

```bash
pip install -r requirements.txt
```

4. Configura variables de entorno (Windows):

```powershell
copy example.env .env
# Edita .env y añade tus claves
```

5. Ejecuta la aplicación:

```bash
python run.py
```

Abre `http://localhost:8000` para el frontend y `http://localhost:8000/docs` para la API.

## Estructura resumida del proyecto

Vea las carpetas principales:

- `app/`: código de la API y servicios
- `.github/`: agentes, skills, hooks e instrucciones de desarrollo
- `evaluaciones/`: informes generados por ticker
- `tests/`: tests centralizados
- `web/`: frontend estático

## Buenas prácticas y contribución

- No edites `main` directamente: crea una rama descriptiva (`feature/`, `fix/`, `docs/`).
- Todos los tests deben residir en la carpeta `tests/`.
- Pre-commit hooks validan la presencia de tests y convenciones del repo.

Si vas a cambiar código, crea primero una rama y añade tests que cubran tu cambio.

## Rutas principales de la API

Algunas rutas expuestas por `app/routes`:

- `GET /health`
- `GET /api/reports/{ticker}`
- `POST /api/reports/{ticker}/generate`
- `GET /api/reports/{ticker}/informe-tecnico.md`

Consulta `app/routes` para la lista completa.

## Documentación y reglas de desarrollo

Las reglas obligatorias están en `.github/instructions/` (protección de `main`, detección de tests, no usar emojis, etc.). Revísalas antes de contribuir.

## Ejecutar tests

```bash
python tests/run_staged_tests.py
```

## Contribuir

1. Crea una rama: `git checkout -b docs/update-readme`.
2. Haz tus cambios y añade tests si aplican.
3. Ejecuta los tests locales.
4. Abre un Pull Request describiendo el cambio.

## Licencia

Consulta el fichero [LICENSE](LICENSE).

## Contacto & Contribuciones

Este es un proyecto personal de investigación. Para preguntas o mejoras, crea un issue o pull request.

---

**Última actualización**: Mayo 2026
