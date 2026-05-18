---
name: web-search-fundamentales
description: "Transform evaluaciones/{ticker}/raw-search/web-search.json into evaluaciones/{ticker}/informe-fundamentales.md by extracting only the factual search results and removing API error noise. Use this skill whenever the user asks to summarize or convert Tavily web-search JSON output into a focused markdown fundamentals report."
compatibility: "Python 3.8+"
---

# Web Search Fundamentals Report Generator

Transform raw web search output into a clean markdown fundamentals report.
This skill reads `evaluaciones/{ticker}/raw-search/web-search.json`, removes API error entries, and writes a structured report to `evaluaciones/{ticker}/informe-fundamentales.md`.

## When to Use

- The user wants to convert `evaluaciones/{ticker}/raw-search/web-search.json` into a markdown research report.
- The user wants a fundamentals summary from Tavily web-search results.
- The user wants only factual findings, not API error messages or request failures.
- The user needs standardized output for stock research or due diligence.

## Input

- Required: `evaluaciones/{ticker}/raw-search/web-search.json`
- Optional: an explicit path to `web-search.json` or a ticker folder containing `raw-search/web-search.json`

## Output

- `evaluaciones/{ticker}/informe-fundamentales.md`
- Contains:
  - header with ticker, company name, and search metadata
  - one section per top-level category found in the JSON
  - a list of valid search results for each category
  - relevance scores when available

## Filtering Rules

- Exclude results whose `title` or `snippet` clearly contain API error messages like `Tavily API error` or `API error`.
- Exclude results with empty `title`, `snippet`, and `source`.
- Preserve only the information explicitly present in the JSON.
- Do not invent conclusions or hallucinate facts beyond the extracted fields.

## How it works

1. Parse the `web-search.json` file.
2. Keep `metadata` and every search category present.
3. For each category, keep only non-error results.
4. Render each result as a markdown bullet with title, snippet, and relevance score.
5. If a category has no valid results, note that no factual results were found.
6. Save the markdown report to `evaluaciones/{ticker}/informe-fundamentales.md`.

## Mini-Workflow Integration

This skill is automatically invoked by the **tavily-research mini-workflow** to generate the fundamentals report immediately after research completion.

**Run both tavily-research and web-search-fundamentales together:**
```bash
python .github/skills/tavily-research/scripts/run_workflow.py --ticker REP.MC
```

This command:
1. Executes tavily-research → generates `evaluaciones/{ticker}/raw-search/web-search.json`
2. Automatically calls web-search-fundamentales → generates `evaluaciones/{ticker}/informe-fundamentales.md`
3. Reports both output files

See [tavily-research Mini-Workflow documentation](../tavily-research/SKILL.md#mini-workflow-automated-fundamentals-report-generation) for full details.

## Script

Use `scripts/extract_fundamentales.py` in this skill folder for deterministic conversion.

## Example usage

```bash
python .github/skills/web-search-fundamentales/scripts/extract_fundamentales.py evaluaciones/REP.MC/raw-search/web-search.json
```

If the current working directory is the repo root, the output will be:

```text
evaluaciones/REP.MC/informe-fundamentales.md
```
