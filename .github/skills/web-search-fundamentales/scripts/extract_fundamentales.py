import argparse
import json
import os
import re
from pathlib import Path

ERROR_PATTERNS = [
    re.compile(r"tavily api error", flags=re.I),
    re.compile(r"api error", flags=re.I),
    re.compile(r"request exceeds", flags=re.I),
    re.compile(r"usage limit", flags=re.I),
]


def looks_like_api_error(text: str) -> bool:
    if not text or not text.strip():
        return False
    normalized = text.strip().lower()
    return any(pattern.search(normalized) for pattern in ERROR_PATTERNS)


def is_empty_result(result: dict) -> bool:
    title = str(result.get("title", "") or "").strip()
    snippet = str(result.get("snippet", "") or "").strip()
    source = str(result.get("source", "") or "").strip()
    return not (title or snippet or source)


def filter_result(result: dict) -> bool:
    title = str(result.get("title", "") or "")
    snippet = str(result.get("snippet", "") or "")
    if is_empty_result(result):
        return False
    if looks_like_api_error(title) or looks_like_api_error(snippet):
        return False
    return True


def safe_str(value) -> str:
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        return str(value)
    return str(value).strip()


def format_result(result: dict) -> str:
    title = safe_str(result.get("title"))
    snippet = safe_str(result.get("snippet"))
    relevance = safe_str(result.get("relevance_score"))
    lines = [f"- **Title:** {title}" if title else "- **Title:** (no title)" ]
    if snippet:
        lines.append(f"  - Snippet: {snippet}")
    if relevance:
        lines.append(f"  - Relevance score: {relevance}")
    return "\n".join(lines)


def build_markdown(data: dict, source_path: Path) -> str:
    metadata = data.get("metadata", {}) or {}
    ticker = safe_str(metadata.get("ticker"))
    company_name = safe_str(metadata.get("company_name") or metadata.get("company", ""))
    sector = safe_str(metadata.get("sector", ""))
    search_date = safe_str(metadata.get("search_date", ""))
    search_status = safe_str(metadata.get("search_status", ""))
    failed_criteria = metadata.get("failed_criteria", []) or []

    lines = [f"# Informe Fundamentales: {ticker}"]
    if company_name:
        lines.append(f"## Empresa: {company_name}")
    if sector:
        lines.append(f"- Sector: {sector}")
    if search_date:
        lines.append(f"- Fecha de búsqueda: {search_date}")
    if search_status:
        lines.append(f"- Estado de búsqueda: {search_status}")
    if failed_criteria:
        lines.append(f"- Criterios fallidos: {', '.join(map(str, failed_criteria))}")
    lines.append("")

    for section_name, section_body in data.items():
        if section_name == "metadata":
            continue
        if not isinstance(section_body, dict):
            continue
        query_used = safe_str(section_body.get("query_used"))
        results = section_body.get("results", []) or []
        filtered = [res for res in results if filter_result(res)]

        section_title = section_name.replace("_", " ").capitalize()
        lines.append(f"## {section_title}")
        if not filtered:
            lines.append("- No se encontraron resultados factuales válidos en esta sección.")
            lines.append("")
            continue

        for result in filtered:
            lines.append(format_result(result))
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def resolve_input_path(path_str: str | None) -> Path:
    if path_str is None:
        raise ValueError("Se requiere la ruta de entrada a web-search.json o al directorio del ticker.")
    path = Path(path_str)
    if path.is_dir():
        candidate = path / "raw-search" / "web-search.json"
        if candidate.exists():
            return candidate
        raise FileNotFoundError(f"No se encontró web-search.json en {candidate}")
    if path.is_file():
        return path
    # maybe input is ticker like REP.MC
    candidate = Path("evaluaciones") / path_str / "raw-search" / "web-search.json"
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"No se encontró web-search.json en {path_str} ni en {candidate}")


def infer_output_path(input_path: Path, explicit_output: str | None) -> Path:
    if explicit_output:
        return Path(explicit_output)
    ticker_dir = input_path.parents[1]
    output_dir = ticker_dir
    return output_dir / "informe-fundamentales.md"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert a raw web-search JSON file into informe-fundamentales.md"
    )
    parser.add_argument(
        "input",
        nargs="?",
        default=None,
        help="Path to web-search.json, the ticker folder, or the path to the ticker name under evaluaciones/"
    )
    parser.add_argument(
        "--output",
        help="Explicit output markdown path",
    )
    args = parser.parse_args()

    input_path = resolve_input_path(args.input)
    output_path = infer_output_path(input_path, args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    markdown = build_markdown(data, input_path)

    with output_path.open("w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"Informe generado: {output_path}")


if __name__ == "__main__":
    main()
