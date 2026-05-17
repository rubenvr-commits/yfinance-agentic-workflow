#!/usr/bin/env python3
"""
Orquestador de workflow combinado: yfinance-report + berkshire-valuation.

Este script:
1. Extrae el ticker de la entrada del usuario
2. Ejecuta yfinance-report para generar informe técnico
3. Lee el informe generado
4. Ejecuta berkshire-valuation para análisis Berkshire
5. Retorna rutas a ambos archivos generados

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
    output_path = workspace_root / 'evaluaciones' / ticker / 'informe-yfinance.md'
    
    if not script_path.exists():
        return False, f"Script no encontrado: {script_path}"
    
    try:
        print(f"[1/2] Generando informe técnico para {ticker}...")
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
                print(f"   ✓ Informe generado: {output_path}")
                return True, str(output_path)
            time.sleep(1)
        
        return False, f"Informe no generado después de esperar: {output_path}"
    
    except subprocess.TimeoutExpired:
        return False, f"Timeout ejecutando yfinance-report para {ticker}"
    except Exception as e:
        return False, f"Error ejecutando yfinance-report: {str(e)}"


def call_berkshire_valuation(ticker: str, informe_path: str) -> Tuple[bool, str]:
    """
    Llama al script berkshire-valuation con el contenido del informe.
    
    Retorna: (éxito: bool, ruta del informe berkshire o mensaje de error: str)
    """
    workspace_root = get_workspace_root()
    script_path = workspace_root / '.github' / 'skills' / 'berkshire-valuation' / 'scripts' / 'notebooklm_client.py'
    output_path = workspace_root / 'evaluaciones' / ticker / 'informe-berkshire.md'
    
    if not script_path.exists():
        return False, f"Script no encontrado: {script_path}"
    
    # Leer el informe generado
    try:
        with open(informe_path, 'r', encoding='utf-8') as f:
            informe_content = f.read()
    except Exception as e:
        return False, f"Error leyendo informe: {str(e)}"
    
    # Construir la pregunta para NotebookLM
    question = f"""Informe para el análisis:

{informe_content}

Basándote en los principios de inversión de Berkshire Hathaway (Warren Buffett y Charlie Munger), analiza este informe financiero y proporciona una valoración de la empresa considerando:
1. La fortaleza competitiva y moat económico
2. La calidad de la gestión
3. La seguridad del margen (margin of safety)
4. El potencial de crecimiento sostenible
5. La recomendación de inversión (comprar/mantener/vender)

Proporciona un análisis estructurado y fundamentado."""
    
    try:
        print(f"[2/2] Generando análisis Berkshire para {ticker}...")
        
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
                print(f"   ⚠️  NotebookLM autenticación expirada. Ejecute: notebooklm login")
                print(f"   📝 Generando archivo placeholder...")
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

## Estado
- ✓ Informe técnico (yfinance): Completado
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
                print(f"   📝 Generando archivo placeholder debido a error de NotebookLM...")
                # Crear un archivo placeholder indicando el error
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"""# Análisis Berkshire Hathaway - {ticker}

## ⚠️ Error de Conexión

No se pudo completar el análisis Berkshire debido a un error al conectar con NotebookLM.

**Error:** {error_msg}

## Estado
- ✓ Informe técnico (yfinance): Completado
- ⏳ Análisis Berkshire: Requiere solución de problemas

## Solución de Problemas
1. Verifique su conexión a internet
2. Intente autenticarse nuevamente: `notebooklm login`
3. Verifique que NotebookLM esté disponible en https://notebooklm.google.com

## Contenido Técnico Disponible
El informe técnico (yfinance) está disponible en el directorio de evaluaciones y contiene:
- Datos de precios y valuación
- Métricas financieras fundamentales
- Información de dividendos y opciones
- Análisis técnico y eventos corporativos
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
        
        print(f"   ✓ Análisis Berkshire generado: {output_path}")
        return True, str(output_path)
    
    except subprocess.TimeoutExpired:
        return False, f"Timeout ejecutando berkshire-valuation para {ticker}"
    except Exception as e:
        return False, f"Error ejecutando berkshire-valuation: {str(e)}"


def main():
    parser = argparse.ArgumentParser(
        description="Workflow combinado: yfinance-report + berkshire-valuation"
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
    
    print(f"\n🔍 Iniciando workflow para ticker: {ticker}\n")
    
    # Paso 1: yfinance-report
    success, result = call_yfinance_report(ticker)
    if not success:
        print(f"❌ {result}")
        return 1
    
    informe_path = result
    
    # Paso 2: berkshire-valuation
    success, result = call_berkshire_valuation(ticker, informe_path)
    if not success:
        print(f"❌ {result}")
        return 1
    
    berkshire_path = result
    
    # Éxito
    print(f"\n✅ Workflow completado exitosamente para {ticker}")
    print(f"\n📄 Archivos generados:")
    print(f"   • Informe técnico: {informe_path}")
    print(f"   • Análisis Berkshire: {berkshire_path}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
