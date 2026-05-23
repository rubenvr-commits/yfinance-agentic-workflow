---
name: tavily-research
description: "Research a financial asset across four key dimensions using Tavily API: long-term vision, corporate values, competitive advantages, and critical management decisions. Trigger on user requests like 'investigar', 'analizar', 'buscar info', 'research ticker', 'analyze company', or when they mention a stock ticker and want comprehensive web research. Outputs structured JSON with investigation results to evaluaciones/{ticker}/raw-search/web-search.json. Uses HTTP API for reliable, scalable search integration."
compatibility: "Python 3.8+, requests library, TAVILY_API_KEY environment variable or project root .env"
---

# Tavily Research Skill (API)

Conduct structured financial research on any asset across four strategic dimensions using Tavily's advanced search capabilities through HTTP API.

## What This Skill Does

1. **Researches 4 dimensions:**
   - **Long-term vision**: Strategic direction, future plans, energy transition strategy, 2030/2035 goals
   - **Corporate values**: Mission, ESG commitments, sustainability, corporate social responsibility
   - **Competitive advantages**: Unique strengths, differentiation, market position, technological capabilities
   - **Critical decisions**: Management response to crises, strategic pivots, major business decisions

2. **Executes intelligent search strategy:**
   - Broad query first for comprehensive coverage (using advanced search depth)
   - Fallback to focused queries if broad search returns few results (using basic search depth)
   - Normalizes all results to consistent schema

3. **Saves structured output:**
   - File: `evaluaciones/{TICKER}/raw-search/web-search.json`
   - Contains: metadata, 4 dimension sections, each with query used + ranked results

## When to Use This Skill

Trigger this skill when users ask to:
- Investigate a financial asset or company
- Research a stock ticker (e.g., "Research REP.MC", "Analyze Repsol")
- Gather strategic information about a company
- Conduct preliminary financial due diligence
- Understand competitive positioning and corporate philosophy
- Get web-based research across multiple dimensions

**Trigger keywords:**
- "investigar", "analizar", "buscar info", "research", "investigate", "analyze"
- Mention of stock ticker + research context
- "dime sobre", "cuéntame de", "tell me about", "what about"

## Input

**Required:**
- `--ticker` (str): Stock ticker symbol (e.g., `REP.MC`, `AAPL`, `MSFT`)

**Optional:**
- `--company-name` (str): Full company name (e.g., "Repsol, S.A."). Defaults to ticker.
- `--sector` (str): Industry sector (e.g., "Energy / Oil & Gas"). Defaults to "Unknown".
- `--output-dir` (str): Custom base output directory. Defaults to `project_root/evaluaciones`.

## Output

**File location:** `evaluaciones/{TICKER}/raw-search/web-search.json`

**Schema:**
```json
{
  "metadata": {
    "ticker": "REP.MC",
    "company_name": "Repsol, S.A.",
    "sector": "Energy / Oil & Gas",
    "search_date": "2026-05-17T10:30:45.123456",
    "search_status": "completed|partial_failure",
    "failed_criteria": []
  },
  "vision": {
    "query_used": "...",
    "results": [
      {
        "title": "Source Title",
        "snippet": "Relevant excerpt from source...",
        "source": "https://...",
        "relevance_score": 0.95
      }
    ]
  },
  "values": { "query_used": "...", "results": [...] },
  "competitive_advantages": { "query_used": "...", "results": [...] },
  "critical_decisions": { "query_used": "...", "results": [...] }
}
```

## How It Works

### Step 1: Initialize API Client
- Read `TAVILY_API_KEY` from environment
- If missing, read it from the repository root `.env`
- Validate API key availability
- Prepare HTTP headers for Tavily API requests

### Step 2: Define Search Queries
- Create broad and focused queries for each of 4 dimensions
- Tailor queries to company name, ticker, and sector context

### Step 3: Execute Searches
- Broad query first via HTTP POST to Tavily API (search_depth="advanced")
- If results < 2, try focused queries as fallback (search_depth="basic")
- Continue until finding meaningful results or exhausting focused queries

### Step 4: Normalize Results
- Extract from MCP response: title, content, URL, relevance
- Normalize to standard schema
- Filter empty/low-quality results

### Step 5: Save & Report
- Create `evaluaciones/{ticker}/raw-search/` directory
- Save complete JSON to `web-search.json`
- Print summary with total results per dimension

## Example Usage

**From CLI:**
```bash
cd .github/skills/tavily-research/scripts

# Basic usage
python researcher.py --ticker REP.MC

# With metadata
python researcher.py --ticker REP.MC --company-name "Repsol, S.A." --sector "Energy / Oil & Gas"

# Custom output directory
python researcher.py --ticker AAPL --output-dir /custom/path
```

**User request (triggers skill):**
```
"Investiga Repsol (REP.MC) por favor"
→ Skill runs: python researcher.py --ticker REP.MC --company-name "Repsol, S.A." --sector "Energy / Oil & Gas"
→ Generates: evaluaciones/REP.MC/raw-search/web-search.json
```

**Expected output:**
```
======================================================================
Tavily Research (MCP) - Repsol, S.A. (REP.MC)
======================================================================

[1] Setting up search queries...

[2] Executing searches for Repsol, S.A....

  [*] Searching for vision...
      Query: Repsol, S.A. long-term vision strategic direction...
      OK Found 5 results

  [*] Searching for values...
      Query: Repsol, S.A. corporate values philosophy ESG...
      OK Found 4 results

  [*] Searching for competitive_advantages...
      Query: Repsol, S.A. competitive advantages differentiation...
      OK Found 5 results

  [*] Searching for critical_decisions...
      Query: Repsol, S.A. management decisions crisis moments...
      OK Found 3 results

[3] Organizing results into JSON...

[4] Saving results to /path/to/evaluaciones/REP.MC/raw-search/web-search.json...

======================================================================
RESEARCH SUMMARY
======================================================================
  Asset: Repsol, S.A. (REP.MC)
  Sector: Energy / Oil & Gas
  Total criteria searched: 4
  Successful: 4
  Failed: 0
  Total results collected: 17
  Output file: /path/to/evaluaciones/REP.MC/raw-search/web-search.json
======================================================================
```

## Technical Details

### MCP Integration
- **Server:** `tavily-mcp@latest` via npx
- **Protocol:** stdio (JSON-RPC)
- **Tools used:**
  - Primary: `tavily_research` (model="pro", advanced search)
  - Fallback: `tavily_search` (if research unavailable)
- **Authentication:** API key from `TAVILY_API_KEY` environment variable

### Search Strategy
- **Broad query first:** Captures general information, establishes baseline
- **Fallback to focused queries:** If broad search returns < 2 results, try 3 specific focused queries
- **Threshold:** Continue until finding ≥ 2 meaningful results
- **Max results per query:** 5 results per API call

### Normalization
- Handles different response formats from Tavily (content, snippet, answer fields)
- Calculates relevance score based on content length (proxy for quality)
- Filters results with empty snippets
- Maps field names (title/name, snippet/content, source/url)

### Error Handling
- Connection failures: Logs error and continues with graceful degradation
- Empty results: Marks criterion as "no_results", continues with next
- Partial failures: Continues with remaining criteria, reports in metadata
- Final status: "completed" (all 4 criteria found results) or "partial_failure"

## Dependencies

### Required Python Packages
```bash
# Core (usually pre-installed)
json, argparse, sys, pathlib, logging, datetime, subprocess

# Optional (for enhanced logging/monitoring)
pip install mcp  # MCP SDK (if not using stdio directly)
```

### System Requirements
- Node.js + npm (for npx to run tavily-mcp)
- Python 3.8+
- Network connectivity to Tavily servers (through MCP)

### Configuration
- The skill reads `TAVILY_API_KEY` from the process environment first.
- If the variable is not set, it falls back to the repository root `.env` file.
- Keep the key in `/.env` at the project root when you want local, file-based configuration.

  Example (PowerShell):
  ```powershell
  $env:TAVILY_API_KEY = "tvly-dev-..."
  python .github\skills\tavily-research\scripts\researcher.py --ticker REP.MC
  ```

## Mini-Workflow: Automated Fundamentals Report Generation

### Overview
Use the **run_workflow.py** script to automatically generate both the raw research JSON **and** the formatted fundamentals markdown report in a single command.

This workflow:
1. Executes `tavily-research` to generate `evaluaciones/{ticker}/raw-search/web-search.json`
2. Upon success, automatically invokes `web-search-fundamentales` to generate `evaluaciones/{ticker}/informe-fundamentales.md`
3. Reports both output files at completion

### Usage

**From the workspace root:**
```bash
python .github/skills/tavily-research/scripts/run_workflow.py --ticker REP.MC
```

**With company metadata:**
```bash
python .github/skills/tavily-research/scripts/run_workflow.py \
  --ticker REP.MC \
  --company-name "Repsol, S.A." \
  --sector "Energy / Oil & Gas"
```

**Extract ticker from natural language:**
```bash
python .github/skills/tavily-research/scripts/run_workflow.py \
  --from-natural "investigar Apple Inc (AAPL)"
```

### Output

The workflow generates both files in the `evaluaciones/{ticker}/` directory:

```
evaluaciones/REP.MC/
├── raw-search/
│   └── web-search.json          # ← Structured research output
└── informe-fundamentales.md     # ← Formatted fundamentals report
```

**Example output:**
```
 Starting research workflow for ticker: REP.MC

[1/2] Generating Tavily research for REP.MC...
   OK Research completed: .../evaluaciones/REP.MC/raw-search/web-search.json

[2/2] Generating fundamentals report...
   OK Fundamentals report generated: .../evaluaciones/REP.MC/informe-fundamentales.md

COMPLETADO Workflow completed successfully for REP.MC

Archivos generados: Generated files:
   • Research JSON: .../evaluaciones/REP.MC/raw-search/web-search.json
   • Fundamentals Report: .../evaluaciones/REP.MC/informe-fundamentales.md
```

### When to Use

- You want a complete research analysis **with formatted output** in one step
- You need both structured JSON (for downstream processing) **and** human-readable markdown (for review)
- You're integrating with other analysis workflows that expect `informe-fundamentales.md` to already exist

### Integration with Other Skills

After running this workflow, you can use the generated `informe-fundamentales.md` with:
- **Analista Financiero (Agent)**: Feeds fundamentals into the complete valuation pipeline
- **berkshire-valuation**: Provides web research context for Berkshire-based investment analysis

## Advanced Usage

### Custom Queries
Modify the `searches` dictionary in `researcher.py` to customize broad/focused queries per criterion.

### Integration with Other Skills
This skill feeds data to downstream analysis skills:
- **berkshire-valuation**: Use web-search.json results as input for Berkshire-based valuation
- **Analista Financiero (Agent)**: Combines web research with yfinance and Berkshire analysis

### Monitoring & Logs
Enable debug logging:
```python
import logging
logging.getLogger('utils').setLevel(logging.DEBUG)
```

## Performance Notes

- **Latency per criterion:** 5-15 seconds (depends on network, MCP server startup)
- **Total execution:** 30-60 seconds for all 4 criteria
- **Output file size:** 50-200 KB (varies with result volume)
- **Caching:** None in V1 (future enhancement: cache results by ticker)

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| "No response from server" | MCP server failed to start | Check npx, Node.js installation, TAVILY_API_KEY |
| "Config file not found" | This skill no longer reads mcp_config.json | Remove old config dependency and use `TAVILY_API_KEY` environment variable |
| "Failed to start MCP server" | Invalid API key or network issue | Verify `TAVILY_API_KEY` is set in environment, test network |
| "No results found" | Query too specific or data unavailable | Try broader queries, check ticker existence |
| Empty JSON output | All 4 criteria failed | Check logs for server/connection errors |

## Future Enhancements

1. **Result caching:** Cache research by ticker to avoid duplicate searches
2. **Confidence scores:** Add NLP-based relevance scoring beyond content length
3. **Multi-language support:** Extend searches to Spanish, Portuguese, etc.
4. **Real-time updates:** Periodic re-research of assets with change detection
5. **Custom criteria:** Allow users to specify custom research dimensions
6. **Export formats:** Add CSV, Markdown, HTML export options
