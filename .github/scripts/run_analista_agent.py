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
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Tuple, Optional
import os


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
EVALUACIONES_DIR = WORKSPACE_ROOT / 'evaluaciones'
PLACEHOLDER_PATTERNS = (
    re.compile(r'\{\{\s*[A-Z0-9_]+\s*\}\}'),
    re.compile(r'\bPLACEHOLDER\b', re.IGNORECASE),
    re.compile(r'\bTBD\b', re.IGNORECASE),
    re.compile(r'\bTODO\b', re.IGNORECASE),
)
NUMERIC_TOKEN_PATTERN = re.compile(r'(?<![A-Za-z])(?:\$?-?\d[\d,]*(?:\.\d+)?%?)')


def run_cmd(cmd: list, timeout: Optional[int] = None) -> Tuple[int, str, str]:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout or "", result.stderr or ""
    except subprocess.TimeoutExpired as e:
        return 124, "", f"Timeout after {timeout}s"
    except Exception as e:
        return 1, "", str(e)


def load_request_data(request_file: Path) -> Optional[dict]:
    try:
        return json.loads(request_file.read_text(encoding='utf-8'))
    except Exception as e:
        print(f"Invalid JSON in {request_file}: {e}")
        return None


def request_is_todo(data: dict) -> bool:
    status = str(data.get('status', '')).strip().lower()
    return status == 'to do'


def mark_request_done(request_file: Path, data: dict) -> None:
    updated = dict(data)
    updated['status'] = 'done'
    try:
        request_file.write_text(json.dumps(updated, ensure_ascii=False, indent=2), encoding='utf-8')
    except Exception as e:
        print(f"Failed to update request status for {request_file}: {e}")


def validate_generated_report(report_file: Path, min_numeric_tokens: int = 1) -> Tuple[bool, str]:
    if not report_file.exists():
        return False, f"missing report file: {report_file.name}"

    try:
        content = report_file.read_text(encoding='utf-8')
    except Exception as exc:
        return False, f"unable to read {report_file.name}: {exc}"

    placeholder_hits = [pattern.pattern for pattern in PLACEHOLDER_PATTERNS if pattern.search(content)]
    if placeholder_hits:
        return False, f"unreplaced placeholders found in {report_file.name}"

    numeric_tokens = NUMERIC_TOKEN_PATTERN.findall(content)
    if len(numeric_tokens) < min_numeric_tokens:
        return False, f"insufficient real figures in {report_file.name} (found {len(numeric_tokens)}, expected at least {min_numeric_tokens})"

    return True, f"validated {report_file.name} with {len(numeric_tokens)} numeric tokens"


def fail_request(status: dict, resp_file: Path, message: str, ticker: str) -> None:
    status.update({'status': 'error', 'message': message})
    resp_file.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"[{ticker}] {message}")


def process_request(request_file: Path) -> None:
    data = load_request_data(request_file)
    if not data:
        return

    ticker = data.get('ticker')
    if not ticker:
        print(f"Missing ticker in {request_file}")
        return

    ticker = ticker.upper()
    ticker_dir = EVALUACIONES_DIR / ticker
    resp_file = ticker_dir / 'agent-response.json'
    mark_done = True

    try:
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
            fail_request(status, resp_file, 'technical generation failed', ticker)
            print(f"[{ticker}] Technical generation failed: {err}")
            return

        valid, validation_message = validate_generated_report(ticker_dir / 'informe-tecnico.md', min_numeric_tokens=8)
        status['log'].append({'step': 'technical_validation', 'valid': valid, 'message': validation_message})
        resp_file.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
        if not valid:
            fail_request(status, resp_file, validation_message, ticker)
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
            fail_request(status, resp_file, 'tavily workflow failed', ticker)
            print(f"[{ticker}] Tavily workflow failed: {err}")
            return

        valid, validation_message = validate_generated_report(ticker_dir / 'informe-fundamentales.md', min_numeric_tokens=1)
        status['log'].append({'step': 'fundamentals_validation', 'valid': valid, 'message': validation_message})
        resp_file.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
        if not valid:
            fail_request(status, resp_file, validation_message, ticker)
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
                fail_request(status, resp_file, 'berkshire generation failed or produced no output', ticker)
                print(f"[{ticker}] Berkshire generation failed or produced no output: {err}")
                return

            valid, validation_message = validate_generated_report(ticker_dir / 'informe-berkshire.md', min_numeric_tokens=2)
            status['log'].append({'step': 'berkshire_validation', 'valid': valid, 'message': validation_message})
            resp_file.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
            if not valid:
                fail_request(status, resp_file, validation_message, ticker)
                return

        # Step 4: Consolidate final report
        print(f"[{ticker}] Step 4: Consolidating final report...")
        status['log'].append('Starting consolidation')
        resp_file.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
        consolidate_script = WORKSPACE_ROOT / '.github' / 'skills' / 'final-report' / 'scripts' / 'consolidate_reports.py'
        code, out, err = run_cmd([sys.executable, str(consolidate_script), str(ticker_dir)], timeout=120)
        status['log'].append({'step': 'consolidate', 'returncode': code, 'out': out[:400], 'err': err[:400]})
        if code != 0:
            fail_request(status, resp_file, 'consolidation failed', ticker)
            print(f"[{ticker}] Consolidation failed: {err}")
            return

        valid, validation_message = validate_generated_report(ticker_dir / 'informe-final.md', min_numeric_tokens=5)
        status['log'].append({'step': 'final_validation', 'valid': valid, 'message': validation_message})
        resp_file.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
        if not valid:
            fail_request(status, resp_file, validation_message, ticker)
            return

        # Success
        status.update({'status': 'completed', 'completed_at': int(time.time()), 'message': 'Reports generated successfully'})
        resp_file.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"[{ticker}] Processing completed successfully")
    finally:
        if mark_done:
            mark_request_done(request_file, data)


def scan_and_process(one_shot: bool = False) -> None:
    while True:
        # find agent-request.json files
        for p in EVALUACIONES_DIR.glob('*'):
            req = p / 'agent-request.json'
            if req.exists():
                data = load_request_data(req)
                if not data or not request_is_todo(data):
                    continue

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
