#!/usr/bin/env python3
"""
Orquestador de workflow combinado: yfinance-report + tavily-research + berkshire-valuation.

Este script:
1. Extrae el ticker de la entrada del usuario
2. Ejecuta EN PARALELO:
   - yfinance-report para generar informe técnico
   - tavily-research + web-search-fundamentales para generar informe de fundamentales
3. Lee ambos informes generados
4. Ejecuta berkshire-valuation para análisis Berkshire con contexto completo
5. Retorna rutas a todos los archivos generados

Uso:
    python run_workflow.py AAPL
    python run_workflow.py --ticker MSFT
    python run_workflow.py --from-natural "analiza Apple Inc (AAPL)"
"""

import sys
import os
import subprocess
import re
import json
import time
import argparse
from pathlib import Path
from typing import Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed


def extract_ticker(input_str: str) -> Optional[str]:
    """
    Extrae un ticker válido de la entrada del usuario.
    Soporta:
    - Entrada directa: "AAPL"
    - Explícita: "ticker: AAPL" o "ticker=AAPL"
    - Mención natural: "analiza AAPL", "research MSFT", "evaluate GOOGL"
    """
    input_str = input_str.strip()
    
    # Patrón 1: Entrada directa (word de 1-5 caracteres en mayúsculas)
    if re.match(r'^[A-Z]{1,5}$', input_str):
        return input_str.upper()
    
    # Patrón 2: Explícito con "ticker: " o "ticker="
    explicit_match = re.search(r'ticker\s*[:=]\s*([A-Z0-9]{1,5})', input_str, re.IGNORECASE)
    if explicit_match:
        return explicit_match.group(1).upper()
    
    # Patrón 3: Mención natural - busca palabra de 1-5 chars entre paréntesis
    paren_match = re.search(r'\(([A-Z0-9]{1,5})\)', input_str)
    if paren_match:
        return paren_match.group(1).upper()
    
    # Patrón 4: Mención natural - palabra aislada después de verbos comunes
    verb_pattern = r'(?:analiza|analyze|research|evaluate|valora|estima|compara)\s+(?:[^()]*?)?\s*([A-Z0-9]{1,5})(?:\s|$|\.)'
    verb_match = re.search(verb_pattern, input_str, re.IGNORECASE)
    if verb_match:
        ticker = verb_match.group(1).upper()
        if 1 <= len(ticker) <= 5:
            return ticker
    
    # Patrón 5: Cualquier palabra de 1-5 mayúsculas (fallback)
    words = input_str.split()
    for word in words:
        clean_word = re.sub(r'[^A-Z0-9]', '', word.upper())
        if 1 <= len(clean_word) <= 5 and clean_word.isalnum():
            return clean_word
    
    return None


def get_workspace_root() -> Path:
    """
    Encuentra la raíz del workspace (contiene .github/skills/)
    """
    current = Path(__file__).resolve()
    while current != current.parent:
        if (current / '.github' / 'skills').exists():
            return current
        current = current.parent
    raise RuntimeError("No se encontró la raíz del workspace")


def call_yfinance_report(ticker: str) -> Tuple[bool, str]:
    """
    Llama al script de yfinance-report y espera a que se genere el informe.
    
    Retorna: (éxito: bool, ruta del informe o mensaje de error: str)
    """
    workspace_root = get_workspace_root()
    script_path = workspace_root / '.github' / 'skills' / 'yfinance-report' / 'scripts' / 'generate_report.py'
    output_path = workspace_root / 'evaluaciones' / ticker / 'informe-tecnico.md'
    
    if not script_path.exists():
        return False, f"Script no encontrado: {script_path}"
    
    try:
        print(f"  [A] Generando informe técnico (yfinance) para {ticker}...")
        result = subprocess.run(
            [sys.executable, str(script_path), ticker],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            return False, f"Error yfinance-report: {result.stderr}"
        
        # Esperar a que se cree el archivo (máx 30 segundos)
        for attempt in range(30):
            if output_path.exists():
                print(f"      ✓ Informe técnico generado")
                return True, str(output_path)
            time.sleep(1)
        
        return False, f"Informe no generado después de esperar: {output_path}"
    
    except subprocess.TimeoutExpired:
        return False, f"Timeout ejecutando yfinance-report para {ticker}"
    except Exception as e:
        return False, f"Error ejecutando yfinance-report: {str(e)}"


def call_tavily_research_and_fundamentales(ticker: str) -> Tuple[bool, str, str]:
    """
    Ejecuta el mini-workflow de tavily-research para generar web-search.json e informe-fundamentales.md
    
    Retorna: (éxito: bool, ruta_json: str, ruta_md: str)
    """
    workspace_root = get_workspace_root()
    script_path = workspace_root / '.github' / 'skills' / 'tavily-research' / 'scripts' / 'run_workflow.py'
    json_output_path = workspace_root / 'evaluaciones' / ticker / 'raw-search' / 'web-search.json'
    md_output_path = workspace_root / 'evaluaciones' / ticker / 'informe-fundamentales.md'
    
    if not script_path.exists():
        return False, "", f"Script no encontrado: {script_path}"
    
    try:
        print(f"  [B] Generando investigación web (Tavily) para {ticker}...")
        result = subprocess.run(
            [sys.executable, str(script_path), '--ticker', ticker],
            capture_output=True,
            text=True,
            timeout=180
        )
        
        if result.returncode != 0:
            return False, "", f"Error tavily-research: {result.stderr}"
        
        # Esperar a que se creen ambos archivos (máx 30 segundos)
        for attempt in range(30):
            if json_output_path.exists() and md_output_path.exists():
                print(f"      ✓ Investigación web y fundamentales generados")
                return True, str(json_output_path), str(md_output_path)
            time.sleep(1)
        
        if not json_output_path.exists():
            return False, "", f"web-search.json no generado: {json_output_path}"
        if not md_output_path.exists():
            return False, "", f"informe-fundamentales.md no generado: {md_output_path}"
        
        return True, str(json_output_path), str(md_output_path)
    
    except subprocess.TimeoutExpired:
        return False, "", f"Timeout ejecutando tavily-research para {ticker}"
    except Exception as e:
        return False, "", f"Error ejecutando tavily-research: {str(e)}"


def call_berkshire_valuation(ticker: str, yfinance_path: str, fundamentales_path: Optional[str] = None) -> Tuple[bool, str]:
    """
    Llama al script berkshire-valuation con el contenido de los informes.
    
    Retorna: (éxito: bool, ruta del informe berkshire o mensaje de error: str)
    """
    workspace_root = get_workspace_root()
    script_path = workspace_root / '.github' / 'skills' / 'berkshire-valuation' / 'scripts' / 'notebooklm_client.py'
    output_path = workspace_root / 'evaluaciones' / ticker / 'informe-berkshire.md'
    
    if not script_path.exists():
        return False, f"Script no encontrado: {script_path}"
    
    # Leer el informe técnico
    try:
        with open(yfinance_path, 'r', encoding='utf-8') as f:
            yfinance_content = f.read()
    except Exception as e:
        return False, f"Error leyendo informe yfinance: {str(e)}"
    
    # Leer informe de fundamentales si existe
    fundamentales_content = ""
    if fundamentales_path and Path(fundamentales_path).exists():
        try:
            with open(fundamentales_path, 'r', encoding='utf-8') as f:
                fundamentales_content = f.read()
        except Exception as e:
            print(f"   ⚠️  Advertencia: No se pudo leer informe de fundamentales: {e}")
    
    # Construir la pregunta para NotebookLM con ambos contextos
    if fundamentales_content:
        question = f"""Informe técnico y de investigación web para el análisis:

## INFORME DE FUNDAMENTALES (INVESTIGACIÓN WEB)
{fundamentales_content}

## INFORME TÉCNICO (YFINANCE)
{yfinance_content}

Basándote en los principios de inversión de Berkshire Hathaway (Warren Buffett y Charlie Munger), analiza estos informes y proporciona una valoración de la empresa considerando:
1. La fortaleza competitiva y moat económico
2. La calidad de la gestión
3. La seguridad del margen (margin of safety)
4. El potencial de crecimiento sostenible
5. La recomendación de inversión (comprar/mantener/vender)

Integra tanto el análisis técnico como el contexto estratégico de la investigación web.
Proporciona un análisis estructurado y fundamentado."""
    else:
        question = f"""Informe para el análisis:

{yfinance_content}

Basándote en los principios de inversión de Berkshire Hathaway (Warren Buffett y Charlie Munger), analiza este informe financiero y proporciona una valoración de la empresa considerando:
1. La fortaleza competitiva y moat económico
2. La calidad de la gestión
3. La seguridad del margen (margin of safety)
4. El potencial de crecimiento sostenible
5. La recomendación de inversión (comprar/mantener/vender)

Proporciona un análisis estructurado y fundamentado."""
    
    try:
        print(f"  [C] Generando análisis Berkshire para {ticker}...")
        
        # Ejecutar notebooklm_client.py
        # Nota: Usa ID de notebook fijo en la config
        notebook_id = "6904dc8b-742e-4192-82db-32e81e1f5e0f"
        
        result = subprocess.run(
            [
                sys.executable,
                str(script_path),
                'ask',
                '--notebook-id', notebook_id,
                '--question', question
            ],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
            if not error_msg:
                error_msg = "Error desconocido (sin salida)"
            
            if "Authentication expired" in error_msg or "invalid" in error_msg.lower():
                print(f"      ⚠️  NotebookLM autenticación expirada. Ejecute: notebooklm login")
                print(f"      📝 Generando archivo placeholder...")
                # Crear un archivo placeholder con instrucciones
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"""# Análisis Berkshire Hathaway - {ticker}

## ⚠️ Autenticación Requerida

El análisis Berkshire requiere autenticación con NotebookLM. Para completar este análisis:

1. Ejecute el siguiente comando en su terminal:
   ```bash
   notebooklm login
   ```

2. Complete la autenticación en el navegador que se abra

3. Ejecute nuevamente el workflow:
   ```bash
   python .github/skills/combined-valuation-workflow/scripts/run_workflow.py {ticker}
   ```

## Estado de Completitud
- ✓ Informe técnico (yfinance): Completado
- ✓ Investigación web (Tavily): Completado
- ⏳ Análisis Berkshire: Pendiente de autenticación

## Próximos Pasos
Después de autenticarse con NotebookLM, el análisis incluirá:
- Evaluación de fortaleza competitiva (moat)
- Análisis de calidad de gestión
- Valoración vs precio actual (margin of safety)
- Potencial de crecimiento sostenible
- Recomendación de inversión fundamentada
""")
                return True, str(output_path)
            else:
                print(f"      📝 Generando archivo placeholder debido a error de NotebookLM...")
                # Crear un archivo placeholder indicando el error
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"""# Análisis Berkshire Hathaway - {ticker}

## ⚠️ Error de Conexión

No se pudo completar el análisis Berkshire debido a un error al conectar con NotebookLM.

**Error:** {error_msg}

## Estado de Completitud
- ✓ Informe técnico (yfinance): Completado
- ✓ Investigación web (Tavily): Completado
- ⏳ Análisis Berkshire: Requiere solución de problemas

## Solución de Problemas
1. Verifique su conexión a internet
2. Intente autenticarse nuevamente: `notebooklm login`
3. Verifique que NotebookLM esté disponible en https://notebooklm.google.com

## Contenido Disponible
✓ Informe técnico (yfinance) completado
✓ Investigación web (Tavily) completada
✓ Datos disponibles para revisión manual
""")
                return True, str(output_path)

        
        # Parsear respuesta JSON
        try:
            response = json.loads(result.stdout)
            answer = response.get('answer', '')
        except json.JSONDecodeError:
            answer = result.stdout
        
        # Guardar respuesta en el archivo de salida
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(answer)
        
        print(f"      ✓ Análisis Berkshire generado")
        return True, str(output_path)
    
    except subprocess.TimeoutExpired:
        return False, f"Timeout ejecutando berkshire-valuation para {ticker}"
    except Exception as e:
        return False, f"Error ejecutando berkshire-valuation: {str(e)}"


def main():
    parser = argparse.ArgumentParser(
        description="Workflow combinado: yfinance-report + tavily-research + berkshire-valuation"
    )
    parser.add_argument('ticker', nargs='?', help='Ticker de acciones (ej: AAPL)')
    parser.add_argument('--from-natural', help='Extraer ticker de entrada natural')
    
    args = parser.parse_args()
    
    # Determinar el ticker
    if args.from_natural:
        ticker = extract_ticker(args.from_natural)
        if not ticker:
            print(f"❌ No se pudo extraer un ticker válido de: {args.from_natural}")
            return 1
    elif args.ticker:
        ticker = extract_ticker(args.ticker)
        if not ticker:
            print(f"❌ Ticker inválido: {args.ticker}")
            return 1
    else:
        parser.print_help()
        return 1
    
    print(f"\n🔍 Iniciando workflow combinado para ticker: {ticker}\n")
    print(f"[PARALELO] Ejecutando investigación técnica e investigación web en paralelo...\n")
    
    # Paso 1: Ejecutar EN PARALELO yfinance-report y tavily-research
    yfinance_path = None
    tavily_json_path = None
    tavily_md_path = None
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        # Enviar ambas tareas al ejecutor
        yfinance_future = executor.submit(call_yfinance_report, ticker)
        tavily_future = executor.submit(call_tavily_research_and_fundamentales, ticker)
        
        # Recopilar resultados a medida que se completan
        for future in as_completed([yfinance_future, tavily_future]):
            if future == yfinance_future:
                success, result = future.result()
                if not success:
                    print(f"\n❌ {result}")
                    return 1
                yfinance_path = result
            else:
                success, json_path, md_path = future.result()
                if not success:
                    print(f"\n❌ {json_path}")  # json_path contiene el mensaje de error en caso de fallo
                    return 1
                tavily_json_path = json_path
                tavily_md_path = md_path
    
    print(f"\n✅ Investigación técnica y web completadas\n")
    
    # Paso 2: Ejecutar berkshire-valuation con ambos informes
    success, result = call_berkshire_valuation(ticker, yfinance_path, tavily_md_path)
    if not success:
        print(f"❌ {result}")
        return 1
    
    berkshire_path = result
    
    # Éxito
    print(f"\n✅ Workflow completado exitosamente para {ticker}")
    print(f"\n📄 Archivos generados:")
    print(f"   • Informe técnico (yfinance): {yfinance_path}")
    print(f"   • Investigación web JSON (Tavily): {tavily_json_path}")
    print(f"   • Informe de fundamentales (web): {tavily_md_path}")
    print(f"   • Análisis Berkshire: {berkshire_path}")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
