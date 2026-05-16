---
name: berkshire-valuation
description: Valora un activo financiero basándose en los principios de inversión de Berkshire Hathaway (Warren Buffett y Charlie Munger). Usa esta skill cada vez que el usuario te pida valorar una acción, activo, o empresa, o te pida un análisis de inversión usando principios de Warren Buffett o Berkshire Hathaway. El usuario te proporcionará el nombre del activo y sus datos financieros (ej. desde yfinance).
---

# Berkshire Hathaway Valuation Skill

Esta skill te permite actuar como un analista financiero experto en los principios de inversión de Berkshire Hathaway, utilizando un NotebookLM que contiene transcripciones de 27 conferencias anuales.

## Recursos Bundled

Esta skill incluye las siguientes herramientas:

- **`scripts/notebooklm_client.py`**: Cliente Python para consultar el NotebookLM con autenticación automática. Expone comandos para listar, crear y consultar notebooks de NotebookLM.
  - Comando: `python scripts/notebooklm_client.py ask --notebook-id <ID> --question "<PREGUNTA>"`
  - Requiere: `notebooklm-py` instalado en el entorno Python

## Instrucciones Principales

1. **NO busques datos financieros por tu cuenta**. El usuario ya te proporcionará toda la información financiera relevante (como datos extraídos de `yfinance`) en su prompt. Tu única tarea de recuperación de información es consultar a Warren Buffett / Charlie Munger a través de la herramienta de NotebookLM.
2. **Formula una buena pregunta para NotebookLM**. Basándote en la empresa y los datos financieros proporcionados por el usuario, formula una o más preguntas para el oráculo de Berkshire Hathaway. Por ejemplo: "¿Cómo vería Warren Buffett una empresa con esta ventaja competitiva, un ratio P/E de X, y este nivel de deuda?".
3. **Consulta el NotebookLM**. Para consultar el Notebook, DEBES usar el cliente de NotebookLM ejecutando el siguiente comando en la terminal:
   ```bash
   python scripts/notebooklm_client.py ask --notebook-id 6904dc8b-742e-4192-82db-32e81e1f5e0f --question "TU_PREGUNTA_AQUI"
   ```
   **Requisitos previos:**
   - Instalar `notebooklm-py` y `playwright` en el entorno: `pip install notebooklm-py playwright`
   - Realizar autenticación con NotebookLM: `python -m notebooklm login --browser chromium`
   - Este proceso genera `~/.notebooklm/profiles/default/storage_state.json` con tu sesión autenticada
   
   *Nota: Sustituye `TU_PREGUNTA_AQUI` por la pregunta o preguntas que hayas formulado. Si necesitas hacer múltiples preguntas para obtener diferentes perspectivas, ejecuta el comando varias veces o formula una pregunta detallada y compuesta.*
4. **Sintetiza la respuesta**. Lee atentamente la salida del script (el campo `answer` devuelto en formato JSON). Combina los principios expuestos en la respuesta de NotebookLM con los datos financieros precisos que el usuario proporcionó.

## Estructura de Salida (Output Format)

SIEMPRE debes estructurar tu respuesta final exactamente con el siguiente formato y **almacenarla en la ruta indicada**:

**Ubicación del archivo:**
```
evaluaciones/
  └── {nombre-activo}/
        └── informe-berkshire.md
```

*Ejemplo: Para Apple (AAPL), el archivo se guardará en `evaluaciones/apple-aapl/informe-berkshire.md`*

**Contenido del archivo:**

### 1. Análisis Detallado
Escribe un análisis cualitativo y cuantitativo detallado (3-5 párrafos) aplicando los principios extraídos de las conferencias de Berkshire Hathaway a los parámetros financieros proporcionados. Debes entrelazar los datos (por ejemplo, márgenes, crecimiento, deuda) con la filosofía de inversión (foso económico, círculo de competencia, margen de seguridad).

### 2. Tabla Resumen
Proporciona una tabla resumen en Markdown con los puntos clave de la valoración:

| Métrica / Principio | Evaluación (Berkshire Hathaway) |
| :--- | :--- |
| **Foso Económico (Moat)** | [Evaluación basada en los datos y los principios] |
| **Salud Financiera** | [Evaluación de la deuda, retorno sobre capital, etc.] |
| **Valoración (Precio/Atracción)**| [Evaluación basada en múltiplos y margen de seguridad] |
| **Veredicto Final** | [Positivo / Neutral / Negativo] |

## Restricciones
- Nunca simules o inventes citas directas si no provienen de la respuesta de NotebookLM.
- Si la respuesta del NotebookLM indica que no hay suficiente información sobre un tema específico, evalúa usando los principios más generales de Buffett sobre negocios de ese tipo.