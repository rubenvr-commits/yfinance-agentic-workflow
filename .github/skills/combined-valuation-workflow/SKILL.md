---
name: combined-valuation-workflow
description: "Generates a complete investment analysis by combining yfinance technical reports, web-based fundamentals research, and Berkshire Hathaway valuation principles. Executes yfinance-report and tavily-research IN PARALLEL, then applies Berkshire analysis. Triggers on mentions of 'informe', 'ticker', 'análisis', 'valoración', or 'valuation' — use this whenever the user mentions a stock ticker and wants financial analysis, investment research, or valuation assessment. Automatically orchestrates all phases, generating four comprehensive markdown reports saved to evaluaciones/{ticker}/. This is your go-to skill when analyzing stocks through the lens of value investing principles with complete contextual research."
compatibility: "Python 3.7+, yfinance, notebooklm-py, pandas (optional)"
---

# Combined Valuation Workflow

Automate the complete analysis of any stock ticker using a three-phase parallel approach: generate comprehensive technical financial data, conduct parallel web-based fundamental research, then apply Berkshire Hathaway investment principles to assess full valuation and investment merit.

## What This Skill Does

1. **Phase 1 – Parallel Data Collection**:
   - **Stream A (Technical)**: Executes yfinance-report skill to pull real-time financial data from Yahoo Finance and generate structured technical report covering ~100+ financial metrics (pricing, valuations, balance sheet, dividends, cash flows, options, technical indicators, corporate events, executive info, SWOT).
   - **Stream B (Fundamentals)**: Executes tavily-research mini-workflow to conduct web-based research across 4 strategic dimensions (long-term vision, corporate values, competitive advantages, critical management decisions) and automatically generates formatted fundamentals report.
   - Both streams execute **in parallel** for faster analysis.

2. **Phase 2 – Value Assessment**: Automatically feeds both technical and fundamentals reports to a NotebookLM trained on 27 years of Berkshire Hathaway shareholder letters, which analyzes the company through the lens of Warren Buffett and Charlie Munger's investment philosophy — assessing competitive moats, management quality, margin of safety, and growth sustainability with complete contextual information.

3. **Output**: Four markdown reports saved to `evaluaciones/{TICKER}/`:
   - `informe-tecnico.md` — Technical financial baseline (~100+ metrics)
   - `raw-search/web-search.json` — Structured web research data (4 dimensions)
   - `informe-fundamentales.md` — Formatted fundamentals from web research
   - `informe-berkshire.md` — Investment thesis and valuation recommendation (using both technical and fundamentals data)

## When to Use This Skill

**Use this skill whenever you encounter:**
- User asks to "analyze" a stock (e.g., "analyze AAPL", "research Tesla")
- User mentions a ticker and wants financial or investment analysis (e.g., "what about MSFT?", "should I buy GOOGL?")
- User says "generate a report" or "create an informe" for a company
- User wants to evaluate a company using value investing principles with complete research
- User asks for "investment research", "due diligence", "valuation", "fundamental analysis", or "worth of a stock"
- User mentions "ticker" or "informe" in any context related to analyzing a company
- User provides ticker in any format (explicit like "ticker: AAPL", natural like "check out Apple (AAPL)", or just "AAPL")

Even if the user's phrasing is casual or informal, if they're clearly asking about a specific stock and want analysis, **use this skill**.

## How It Works

### Step 1: Extract Ticker
The skill intelligently extracts the stock ticker symbol from user input:
- **Direct input**: `AAPL` → ticker recognized
- **Explicit format**: `ticker: AAPL` or `ticker=AAPL`
- **Parenthetical format**: `Apple (AAPL)` or `Tesla Inc (TSLA)`
- **Natural mention**: `analyze MSFT`, `research GOOGL`, `what about FB`
- **Case-insensitive**: `aapl` → `AAPL`

### Step 2: Execute Parallel Streams
Simultaneously executes two independent data collection streams:

**Stream A – Technical Financial Analysis**:
- Executes yfinance-report skill script
- Downloads data from Yahoo Finance using `yfinance` library
- Extracts 100+ financial metrics (price, P/E, dividend, revenue, EPS, ROE, debt ratios, etc.)
- Saves to `evaluaciones/{TICKER}/informe-tecnico.md`

**Stream B – Web-Based Fundamentals Research**:
- Executes tavily-research mini-workflow
- Conducts structured web research across 4 strategic dimensions:
  - Long-term vision & strategic direction
  - Corporate values & philosophy
  - Competitive advantages & market position
  - Critical management decisions
- Generates both structured JSON and formatted markdown
- Saves to `evaluaciones/{TICKER}/raw-search/web-search.json` and `evaluaciones/{TICKER}/informe-fundamentales.md`

Both streams run **in parallel**, reducing total execution time.

### Step 3: Call berkshire-valuation
Feeds both technical and fundamentals reports to NotebookLM which:
- Reads both the yfinance technical report and fundamentals report without modifications
- Applies Berkshire Hathaway's investment framework, analyzing:
  - **Competitive moat**: Is there a durable competitive advantage? (using both technical metrics and strategic research)
  - **Management quality**: Do executives have a strong track record?
  - **Margin of safety**: Is the valuation attractive enough to justify the risk?
  - **Growth sustainability**: Can the company maintain competitive advantage long-term?
  - **Investment thesis**: Buy/hold/avoid with structured reasoning integrating all available data
- Returns a markdown analysis incorporating Berkshire's principles with full contextual awareness
- Saves to `evaluaciones/{TICKER}/informe-berkshire.md`

## Input Format

**Required**: A valid stock ticker symbol. Provide it as:
- **Directly**: `AAPL`, `MSFT`, `TSLA`
- **Explicitly**: `ticker: AAPL` or `ticker MSFT`
- **In context**: `(AAPL)`, `AAPL Inc`, `Apple AAPL`
- **Naturally**: `analyze AAPL`, `research MSFT`, `check GOOGL`

The skill handles all these formats automatically.

## Output

**Location**: `evaluaciones/{TICKER}/`

**Files generated**:
1. **informe-tecnico.md** — 15+ sections covering:
   - Asset identification & current pricing
   - Valuation metrics (P/E, P/B, PEG, dividend yield)
   - Financial statements (balance sheet, income statement, cash flow)
   - Profitability & efficiency (ROE, ROA, asset turnover)
   - Financial health & leverage ratios
   - Growth metrics (revenue/earnings growth, forward estimates)
   - Technical analysis & corporate events
   - Management & SWOT analysis

2. **raw-search/web-search.json** — Structured web research:
   - Metadata (ticker, company name, sector, search date)
   - Vision section (long-term strategy and plans)
   - Values section (corporate philosophy and ESG)
   - Competitive advantages (market position, unique strengths)
   - Critical decisions (management response to crises)

3. **informe-fundamentales.md** — Formatted fundamentals report:
   - Header with company info and search metadata
   - Sections for each research dimension
   - Factual findings with relevance scores
   - Ready for human review and analysis

4. **informe-berkshire.md** — Berkshire Hathaway investment analysis including:
   - Competitive advantage assessment (integrating both technical and web research)
   - Management quality evaluation
   - Valuation vs. intrinsic value
   - Risk assessment (margin of safety)
   - Long-term growth potential
   - Investment recommendation with reasoning

## Example Usage

**User input**:
```
Analiza AAPL y dame tu recomendación de inversión
```

**Workflow executes** (parallel phase):
```
[PARALELO] Ejecutando investigación técnica e investigación web en paralelo...
  [A] Generando informe técnico (yfinance) para AAPL...
  [B] Generando investigación web (Tavily) para AAPL...
  OK Informe técnico generado
  OK Investigación web y fundamentales generados

COMPLETADO Investigación técnica y web completadas

  [C] Generando análisis Berkshire para AAPL...
  OK Análisis Berkshire generado

COMPLETADO Workflow completado exitosamente para AAPL

Archivos generados: Archivos generados:
   • Informe técnico (yfinance): .../evaluaciones/AAPL/informe-tecnico.md
   • Investigación web JSON (Tavily): .../evaluaciones/AAPL/raw-search/web-search.json
   • Informe de fundamentales (web): .../evaluaciones/AAPL/informe-fundamentales.md
   • Análisis Berkshire: .../evaluaciones/AAPL/informe-berkshire.md
```

1. Extracts ticker: `AAPL`
2. Launches parallel streams for yfinance and web research
3. Waits for both to complete
4. Calls berkshire-valuation with both reports
5. Returns all four comprehensive documents

## Error Handling

If any phase fails:
- **yfinance-report fails** (invalid ticker, API issues): Workflow stops with clear error message
- **tavily-research fails** (API limit, connection): Workflow stops with clear error message
- **berkshire-valuation fails** (auth issues, timeout): Returns partial result (technical + fundamentals reports) with explanation
- **File not found**: Reports which file wasn't generated and suggests manual review

## Dependencies

- **Python 3.7+** (inherited from base skills)
- **yfinance** (for financial data)
- **notebooklm-py** (for Berkshire analysis via NotebookLM)
- **pandas** (optional, recommended for data processing)
- **TAVILY_API_KEY** (environment variable for web research)
- **NotebookLM authentication** (pre-configured storage_state.json required)

## Parallel Execution Performance

- **Sequential approach** (old): yfinance (60s) + berkshire (120s) = ~180s
- **Parallel approach** (new): max(yfinance: 60s, tavily: 180s) + berkshire (120s) = ~300s total
  - Yfinance and tavily run simultaneously, so total time is max of both + berkshire
  - Provides more comprehensive analysis with minimal time penalty

## Limitations & Considerations

- **Ticker validation**: Accepts 1-5 character alphanumeric symbols (standard stock tickers)
- **Market hours**: Most accurate during market hours when real-time data is fresh
- **Tavily API**: Web research requires TAVILY_API_KEY environment variable
- **NotebookLM dependency**: Berkshire analysis requires active NotebookLM authentication
- **Rate limits**: Respect yfinance, Tavily, and NotebookLM API rate limits for batch operations

## Tips for Best Results

1. **Provide clear context**: "Analyze AAPL" is better than "what do you think?" (helps extraction)
2. **One ticker at a time**: Run this workflow separately for each ticker you want to compare
3. **Review all reports**: 
   - yfinance report is technical baseline
   - Fundamentals report provides strategic context
   - Berkshire analysis integrates both for investment thesis
4. **Use for comparison**: Run workflow for multiple tickers, then compare all reports
5. **Export for sharing**: All markdown files are formatted for easy sharing, printing, or PDF conversion
6. **Enable environment variable**: Ensure `TAVILY_API_KEY` is set for web research functionality

## Technical Details

**Ticker extraction logic** (in priority order):
1. Direct match: Single word 1-5 chars uppercase → uses as-is
2. Explicit: Pattern `ticker: AAPL` or `ticker=AAPL` → extracts AAPL
3. Parenthetical: Pattern `Apple (AAPL)` → extracts AAPL
4. Verb-based: Pattern `analyze AAPL` or `research MSFT` → extracts symbol
5. Fallback: First alphanumeric 1-5 char word found → tries as ticker

**Orchestration flow**:
```
User input with ticker mention
    ↓
Extract ticker (robust parsing)
    ↓
Validate ticker format (1-5 chars, alphanumeric)
    ↓
Call yfinance-report script
    ↓
Wait for informe-tecnico.md creation (up to 30 seconds)
    ↓
Read informe file content
    ↓
Call berkshire-valuation script with full informe
    ↓
Parse NotebookLM response JSON
    ↓
Save to informe-berkshire.md
    ↓
Return both file paths to user
```

---

**Next steps after using this skill**: 
- Review both reports side-by-side for a complete investment picture
- Use the Berkshire analysis recommendation to guide your research
- Compare multiple tickers' berkshire reports to shortlist investment candidates
- Deep-dive into any specific section from either report for more details
