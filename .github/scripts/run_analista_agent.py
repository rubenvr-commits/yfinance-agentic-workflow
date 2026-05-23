#!/usr/bin/env python3
"""Run Analista Financiero agent: watch for agent-request.json and process reports.

Usage:
  python run_analista_agent.py         # run loop (polling)
  python run_analista_agent.py --once  # process pending requests once and exit

The agent will execute the following steps for each request:
  1. Generate technical report (yfinance): .github/skills/yfinance-report/scripts/generate_report.py
  2. Run Tavily research workflow: .github/skills/tavily-research/scripts/run_workflow.py
  3. Ask NotebookLM to create Berkshire valuation and save as informe-berkshire.md
  4. Consolidate final report: .github/skills/final-report/scripts/consolidate_reports.py

The agent writes `agent-response.json` in the ticker folder with final status.
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Tuple, Optional
import os


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
EVALUACIONES_DIR = WORKSPACE_ROOT / 'evaluaciones'


def run_cmd(cmd: list, timeout: Optional[int] = None) -> Tuple[int, str, str]:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout or "", result.stderr or ""
    except subprocess.TimeoutExpired as e:
        return 124, "", f"Timeout after {timeout}s"
    except Exception as e:
        return 1, "", str(e)


def process_request(request_file: Path) -> None:
    try:
        data = json.loads(request_file.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"Invalid JSON in {request_file}: {e}")
        return

    ticker = data.get('ticker')
    if not ticker:
        print(f"Missing ticker in {request_file}")
        return

    ticker = ticker.upper()
    ticker_dir = EVALUACIONES_DIR / ticker
    resp_file = ticker_dir / 'agent-response.json'

    # mark processing
    status = {
        'status': 'processing',
        'ticker': ticker,
        'started_at': int(time.time()),
        'log': []
    }
    ticker_dir.mkdir(parents=True, exist_ok=True)
    resp_file.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')

    # Step 1: Generate technical report
    print(f"[{ticker}] Step 1: Generating technical report...")
    status['log'].append('Starting technical report')
    resp_file.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
    tech_script = WORKSPACE_ROOT / '.github' / 'skills' / 'yfinance-report' / 'scripts' / 'generate_report.py'
    code, out, err = run_cmd([sys.executable, str(tech_script), ticker], timeout=300)
    status['log'].append({'step': 'technical', 'returncode': code, 'out': out[:400], 'err': err[:400]})
    resp_file.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
    if code != 0:
        status.update({'status': 'error', 'message': 'technical generation failed'})
        resp_file.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"[{ticker}] Technical generation failed: {err}")
        return

    # Step 2: Tavily research + fundamentals
    print(f"[{ticker}] Step 2: Running Tavily research workflow...")
    status['log'].append('Starting tavily workflow')
    resp_file.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
    tavily_script = WORKSPACE_ROOT / '.github' / 'skills' / 'tavily-research' / 'scripts' / 'run_workflow.py'
    code, out, err = run_cmd([sys.executable, str(tavily_script), '--ticker', ticker], timeout=600)
    status['log'].append({'step': 'tavily', 'returncode': code, 'out': out[:400], 'err': err[:400]})
    resp_file.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
    if code != 0:
        status.update({'status': 'error', 'message': 'tavily workflow failed'})
        resp_file.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"[{ticker}] Tavily workflow failed: {err}")
        return

    # Step 3: Berkshire via NotebookLM
    print(f"[{ticker}] Step 3: Generating Berkshire valuation via NotebookLM...")
    status['log'].append('Starting berkshire valuation')
    resp_file.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
    notebook_script = WORKSPACE_ROOT / '.github' / 'skills' / 'berkshire-valuation' / 'scripts' / 'notebooklm_client.py'

    # Build question: ask notebook to generate a full markdown Berkshire report
    notebook_id = os.environ.get('NOTEBOOKLM_ID')
    if not notebook_id:
        # try example.env fallback
        env_path = WORKSPACE_ROOT / 'example.env'
        if env_path.exists():
            for line in env_path.read_text(encoding='utf-8').splitlines():
                if line.startswith('NOTEBOOKLM_ID='):
                    notebook_id = line.split('=', 1)[1].strip()
                    break

    if not notebook_id:
        status.update({'status': 'error', 'message': 'NOTEBOOKLM_ID not configured'})
        resp_file.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"[{ticker}] NOTEBOOKLM_ID not set; skipping berkshire")
    else:
        question = (
            f"Genera un informe Berkshire para {ticker} en formato markdown. "
            "Usa los archivos existentes en la carpeta evaluaciones/" + ticker + "/ (informe-tecnico.md y informe-fundamentales.md). "
            "Incluye: resumen ejecutivo, moat analysis, valoración objetivo con rango, margen de seguridad y recomendación final."
        )

        code, out, err = run_cmd([sys.executable, str(notebook_script), 'ask', '--notebook-id', notebook_id, '--question', question], timeout=180)
        status['log'].append({'step': 'berkshire', 'returncode': code, 'out': out[:1000], 'err': err[:400]})
        resp_file.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')

        if code == 0 and out:
            # parse JSON output from notebooklm_client (it prints JSON)
            try:
                parsed = json.loads(out)
                answer = parsed.get('answer') or parsed.get('raw_response') or out
                berkshire_path = ticker_dir / 'informe-berkshire.md'
                berkshire_path.write_text(answer, encoding='utf-8')
                status['log'].append({'berkshire_saved': str(berkshire_path)})
            except Exception:
                # fallback: write raw stdout
                berkshire_path = ticker_dir / 'informe-berkshire.md'
                berkshire_path.write_text(out, encoding='utf-8')
                status['log'].append({'berkshire_saved_raw': str(berkshire_path)})
        else:
            print(f"[{ticker}] Berkshire generation failed or produced no output: {err}")

    # Step 4: Consolidate final report
    print(f"[{ticker}] Step 4: Consolidating final report...")
    status['log'].append('Starting consolidation')
    resp_file.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
    consolidate_script = WORKSPACE_ROOT / '.github' / 'skills' / 'final-report' / 'scripts' / 'consolidate_reports.py'
    code, out, err = run_cmd([sys.executable, str(consolidate_script), str(ticker_dir)], timeout=120)
    status['log'].append({'step': 'consolidate', 'returncode': code, 'out': out[:400], 'err': err[:400]})
    if code != 0:
        status.update({'status': 'error', 'message': 'consolidation failed'})
        resp_file.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"[{ticker}] Consolidation failed: {err}")
        return

    # Success
    status.update({'status': 'completed', 'completed_at': int(time.time()), 'message': 'Reports generated successfully'})
    resp_file.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"[{ticker}] Processing completed successfully")


def scan_and_process(one_shot: bool = False) -> None:
    while True:
        # find agent-request.json files
        for p in EVALUACIONES_DIR.glob('*'):
            req = p / 'agent-request.json'
            if req.exists():
                # avoid racing with already-processing marker (agent-response exists and status processing)
                resp = p / 'agent-response.json'
                if resp.exists():
                    try:
                        r = json.loads(resp.read_text(encoding='utf-8'))
                        if r.get('status') == 'processing':
                            continue
                    except Exception:
                        pass
                process_request(req)

        if one_shot:
            break

        time.sleep(5)


def main():
    parser = argparse.ArgumentParser(description='Run analista-financiero agent')
    parser.add_argument('--once', action='store_true', help='Process pending requests once and exit')
    args = parser.parse_args()
    scan_and_process(one_shot=args.once)


if __name__ == '__main__':
    main()
