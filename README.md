# YFinance Agentic Workflow

Un sistema inteligente de análisis de inversiones que aplica los principios de Berkshire Hathaway (Warren Buffett y Charlie Munger) a datos financieros reales usando GitHub Copilot Skills y NotebookLM.

## 📋 Descripción General

Este proyecto integra múltiples tecnologías para crear un flujo de trabajo completo de análisis de inversiones:

- **Análisis de Berkshire Hathaway**: Consulta principios de inversión de 27 conferencias anuales mediante NotebookLM
- **Datos Financieros en Tiempo Real**: Integración con `yfinance` para obtener métricas de acciones
- **GitHub Copilot Skills**: Extensiones personalizadas que automatizan análisis y generan reportes
- **Base de Datos PostgreSQL**: Persistencia de análisis y datos históricos
- **Docker Compose**: Orquestación de servicios

## 🎯 Características Principales

### 1. **Skill: Berkshire Valuation**
Análisis de inversión basado en los principios fundamentales de Berkshire Hathaway.

- **Consulta Inteligente**: Acceso a NotebookLM con las enseñanzas de Warren Buffett y Charlie Munger
- **Evaluación de Moat Económico**: Análisis de ventajas competitivas duraderas
- **Margen de Seguridad**: Valoración conservadora de activos
- **Salida Estructurada**: Reportes en Markdown con análisis detallado

**Ubicación**: `.github/skills/berkshire-valuation/`

**Ejemplo de Output**: 
```
evaluaciones/apple-aapl/informe-berkshire.md
```

### 2. **Skill: Frontend Design**
Herramienta para crear interfaces web de alta calidad y componentes visuales.

- Diseño de dashboards y páginas web
- Generación de HTML/CSS/React
- Visualización de datos financieros

**Ubicación**: `.github/skills/frontend-design/`

### 3. **Skill: Skill Creator**
Framework para crear, evaluar y optimizar nuevas skills de Copilot.

- Creación de skills personalizadas
- Ejecución de evaluaciones (evals)
- Benchmarking de rendimiento
- Optimización de descripciones

**Ubicación**: `.github/skills/skill-creator/`

## 🏗️ Estructura del Proyecto

```
yfinance-agentic-workflow/
├── .github/
│   └── skills/                          # GitHub Copilot Skills
│       ├── berkshire-valuation/         # Análisis de inversiones
│       ├── frontend-design/             # Diseño web
│       └── skill-creator/               # Framework de skills
├── evaluaciones/                         # Reportes de análisis
│   └── apple-aapl/
│       └── informe-berkshire.md        # Ejemplo: Análisis de Apple
├── postgres/
│   └── 18/docker/                      # Datos de PostgreSQL
├── docker-compose.yml                   # Orquestación de servicios
├── .env                                 # Variables de entorno
└── LICENSE                              # Licencia MIT
```

## 🚀 Primeros Pasos

### Prerequisitos

- Python 3.8+
- Docker y Docker Compose
- Git
- GitHub Copilot Chat (para usar las skills)

### Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd yfinance-agentic-workflow
```

2. **Crear entorno virtual**
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

3. **Instalar dependencias**

Para usar la Skill de Berkshire Valuation:
```bash
pip install notebooklm-py playwright yfinance
python -m notebooklm login --browser chromium
```

4. **Configurar variables de entorno**

Editar `.env`:
```env
POSTGRES_USER=rubenvr
POSTGRES_DB=yfinancedb
POSTGRES_PASSWORD=12345

NOTEBOOKLM_ID=6904dc8b-742e-4192-82db-32e81e1f5e0f
NOTEBOOKLM_EMAIL=your-email@example.com
NOTEBOOKLM_PASSWORD=your-password
```

5. **Iniciar PostgreSQL**
```bash
docker-compose up -d
```

## 💼 Flujo de Trabajo: Análisis de Inversión

### Paso 1: Recolectar Datos Financieros
```python
import yfinance as yf

# Obtener datos de la acción
ticker = yf.Ticker("AAPL")
info = ticker.info
hist = ticker.history(period="1y")
```

### Paso 2: Consultar Berkshire Valuation Skill

En GitHub Copilot Chat, usa:
```
@berkshire-valuation 
Analiza Apple (AAPL) con estos datos:
- P/E: 28.5
- Crecimiento ingresos: 14.85%
- Margen neto: 30%
- Deuda/Equity: 1.2
```

### Paso 3: Skill Ejecuta NotebookLM
```bash
python scripts/notebooklm_client.py ask \
  --notebook-id 6904dc8b-742e-4192-82db-32e81e1f5e0f \
  --question "¿Cómo vería Buffett una empresa con P/E 28.5 y márgenes del 30%?"
```

### Paso 4: Generar Reporte
El sistema genera automáticamente:
```
evaluaciones/apple-aapl/informe-berkshire.md
```

Con secciones:
- ✅ Análisis Detallado (aplicación de principios)
- ✅ Tabla Resumen (métricas vs. Berkshire)
- ✅ Valoración y Recomendación
- ✅ Riesgos y Monitoreo

## 📊 Ejemplo: Análisis de Apple Inc.

El archivo [`evaluaciones/apple-aapl/informe-berkshire.md`](evaluaciones/apple-aapl/informe-berkshire.md) contiene un análisis completo que incluye:

- **Foso Económico**: Evaluación del ecosistema iOS y poder de marca
- **Proyecciones de Crecimiento**: Análisis de desaceleración de 17% a 10%
- **Márgenes de Ganancia**: Sostenibilidad del 30% de margen neto
- **Asignación de Capital**: Estrategia de recompras y devoluciones
- **Círculo de Competencia**: Riesgos de obsolescencia tecnológica
- **Margen de Seguridad**: Recomendación de valoración

## 🛠️ Herramientas Incluidas

### NotebookLM Client
```bash
# Listar notebooks disponibles
python .github/skills/berkshire-valuation/scripts/notebooklm_client.py list

# Hacer una pregunta
python .github/skills/berkshire-valuation/scripts/notebooklm_client.py ask \
  --notebook-id <ID> \
  --question "Tu pregunta aqui"
```

### Skill Creator Scripts
```bash
# Validar una skill
python .github/skills/skill-creator/scripts/quick_validate.py

# Generar reporte de evaluación
python .github/skills/skill-creator/scripts/generate_report.py

# Empaquetar skill
python .github/skills/skill-creator/scripts/package_skill.py
```

## 📈 Principios de Inversión de Berkshire Hathaway

El proyecto se basa en estos conceptos clave:

| Principio | Descripción |
|-----------|-------------|
| **Moat Económico (Foso)** | Ventaja competitiva duradera que protege la rentabilidad |
| **Círculo de Competencia** | Solo invertir en empresas que comprendes profundamente |
| **Margen de Seguridad** | Comprar por debajo del valor intrínseco |
| **Calidad de Gestión** | Integridad y competencia del equipo ejecutivo |
| **Asignación de Capital** | Uso eficiente del flujo de caja disponible |
| **Rendimiento sobre Equity** | ROE sostenible como indicador de generación de valor |

## 🗄️ Base de Datos PostgreSQL

El proyecto incluye PostgreSQL 18 pre-configurado para almacenar:
- Análisis históricos
- Datos financieros cacheados
- Evaluaciones de inversiones
- Seguimiento de cambios

**Conexión**:
```
Host: localhost
Port: 5432
Usuario: rubenvr
Base de datos: yfinancedb
```

## 🐳 Docker Compose

Servicios disponibles:

```yaml
postgres:
  image: postgres:18
  container_name: yfinance_postgres
  ports: 5432:5432
  volumes: ./postgres/18/docker:/var/lib/postgresql/data
```

**Comandos**:
```bash
# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f postgres

# Detener servicios
docker-compose down
```

## 📝 Licencia

MIT License © 2026 Rubén Valverde Romero

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📚 Recursos Adicionales

- [yfinance Documentation](https://yfinance.readthedocs.io/)
- [NotebookLM](https://notebooklm.google/)
- [GitHub Copilot Chat Skills](https://docs.github.com/en/copilot/chat/github-copilot-chat-in-your-ide)
- [PostgreSQL 18 Docs](https://www.postgresql.org/docs/18/)
- [Warren Buffett - Berkshire Hathaway](https://www.berkshirehathaway.com/)

## ❓ FAQ

**P: ¿Necesito una clave API de yfinance?**
R: No, yfinance es gratuito y no requiere autenticación.

**P: ¿Puedo usar otras acciones además de Apple?**
R: Sí, cualquier ticker válido de yfinance funciona. El sistema generará reportes en `evaluaciones/{nombre-activo}/`.

**P: ¿Qué sucede si NotebookLM no está disponible?**
R: El análisis fallará. Asegúrate de estar autenticado con `python -m notebooklm login`.

**P: ¿Puedo modificar las skills?**
R: Sí, usa la Skill Creator para crear nuevas skills personalizadas.

---

**Última actualización**: Mayo 2026
