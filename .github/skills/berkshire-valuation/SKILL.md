---
name: berkshire-valuation
description: Valora un activo financiero basándose en los principios de inversión de Berkshire Hathaway (Warren Buffett y Charlie Munger). Lee automáticamente el informe técnico desde evaluaciones/{ticker}/informe-tecnico.md y formula preguntas al oráculo de Berkshire Hathaway (NotebookLM) basándose en esos datos sin realizar modificaciones.
---

# Berkshire Hathaway Valuation Skill

Esta skill te permite actuar como un analista financiero experto en los principios de inversión de Berkshire Hathaway, utilizando un NotebookLM que contiene transcripciones de 27 conferencias anuales.

## Activación de la Skill

Usa esta skill cuando el usuario te pida:
- Valorar una acción o activo usando principios de Warren Buffett o Berkshire Hathaway
- Realizar un análisis de inversión basado en datos de yfinance
- Evaluar si una empresa cumple con los criterios de inversión de Berkshire

**Ejemplo de invocación:**
```
Analiza PCT.L (Polar Capital Technology Trust plc) usando los principios de Berkshire Hathaway
```

La skill automáticamente:
1. Buscará el archivo `evaluaciones/PCT.L/informe-tecnico.md`
2. Extraerá los datos financieros sin modificaciones
3. Formulará preguntas a NotebookLM basadas en esos datos
4. Generará un informe en `evaluaciones/PCT.L/informe-berkshire.md`

## Recursos Bundled

Esta skill incluye las siguientes herramientas:

- **`scripts/notebooklm_client.py`**: Cliente Python para consultar el NotebookLM con autenticación automática. Expone comandos para listar, crear y consultar notebooks de NotebookLM.
  - Comando: `python scripts/notebooklm_client.py ask --notebook-id <ID> --question "<PREGUNTA>"`
  - Requiere: `notebooklm-py` instalado en el entorno Python

## Instrucciones Principales

1. **Lee el informe técnico directamente**. El sistema buscará automáticamente el informe financiero en `evaluaciones/{ticker}/informe-tecnico.md`. Lee todo el contenido sin realizar ninguna modificación.
2. **Pasa el informe completo a NotebookLM**. Incluye el contenido íntegro del archivo `informe-tecnico.md` directamente en la query que enviarás a NotebookLM. La query contendrá tanto el informe como una pregunta analítica sobre él, basada en los principios de inversión de Berkshire Hathaway.
3. **Consulta el NotebookLM**. Para consultar el Notebook, DEBES usar el cliente de NotebookLM ejecutando el siguiente comando en la terminal:
   ```bash
   python scripts/notebooklm_client.py ask --notebook-id 6904dc8b-742e-4192-82db-32e81e1f5e0f --question "Informe para el análisis:

  {informe-tecnico.md}

   ```
   **Requisitos previos:**
   - Instalar `notebooklm-py` y `playwright` en el entorno: `pip install notebooklm-py playwright`
   - Realizar autenticación con NotebookLM: `python -m notebooklm login --browser chromium`
   - Este proceso genera `~/.notebooklm/profiles/default/storage_state.json` con tu sesión autenticada
   
   *Nota: Sustituye `{informe-tecnico.md}` por el contenido completo del archivo del informe técnico sin modificaciones.*
4. **Almacena la respuesta**. Copia la respuesta completa de NotebookLM (el campo `answer` del JSON devuelto) y guárdala en el archivo de salida sin realizar modificaciones.

## Estructura de Salida (Output Format)

SIEMPRE debes estructurar tu respuesta final exactamente con el siguiente formato y **almacenarla en la ruta indicada**:

**Ubicación del archivo:**
```
evaluaciones/
  └── {ticker-activo}/
        └── informe-berkshire.md
```

*Ejemplo: Para Apple (AAPL), el archivo se guardará en `evaluaciones/aapl/informe-berkshire.md`*

**Contenido del archivo:**

La respuesta de notebooklm sin modificaciones.

