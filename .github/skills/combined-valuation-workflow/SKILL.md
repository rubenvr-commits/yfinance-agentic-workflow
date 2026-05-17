---
name: combined-valuation-workflow
description: "Generates a complete investment analysis by combining yfinance technical reports with Berkshire Hathaway valuation principles. Triggers on mentions of 'informe', 'ticker', 'análisis', 'valoración', or 'valuation' — use this whenever the user mentions a stock ticker and wants financial analysis, investment research, or valuation assessment. Automatically orchestrates both the technical financial report and the Berkshire-based value analysis in sequence, generating two comprehensive markdown reports saved to evaluaciones/{ticker}/. This is your go-to skill when analyzing stocks through the lens of value investing principles."
compatibility: "Python 3.7+, yfinance, notebooklm-py, pandas (optional)"
---

# Combined Valuation Workflow

Automate the complete analysis of any stock ticker using a two-phase approach: generate a comprehensive technical financial report, then apply Berkshire Hathaway investment principles to assess valuation and investment merit.

## What This Skill Does

1. **Phase 1 – Technical Analysis**: Executes the yfinance-report skill to pull real-time financial data from Yahoo Finance and generate a structured technical report covering ~100+ financial metrics (pricing, valuations, balance sheet, dividends, cash flows, options, technical indicators, corporate events, executive info, SWOT).

2. **Phase 2 – Value Assessment**: Automatically feeds the technical report to a NotebookLM trained on 27 years of Berkshire Hathaway shareholder letters, which analyzes the company through the lens of Warren Buffett and Charlie Munger's investment philosophy — assessing competitive moats, management quality, margin of safety, and growth sustainability.

3. **Output**: Two markdown reports saved to `evaluaciones/{TICKER}/`:
   - `informe-yfinance.md` — Technical financial baseline
   - `informe-berkshire.md` — Investment thesis and valuation recommendation

## When to Use This Skill

**Use this skill whenever you encounter:**
- User asks to "analyze" a stock (e.g., "analyze AAPL", "research Tesla")
- User mentions a ticker and wants financial or investment analysis (e.g., "what about MSFT?", "should I buy GOOGL?")
- User says "generate a report" or "create an informe" for a company
- User wants to evaluate a company using value investing principles
- User asks for "investment research", "due diligence", "valuation", or "worth of a stock"
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

### Step 2: Call yfinance-report
Executes the yfinance-report skill script which:
- Downloads financial data from Yahoo Finance using the `yfinance` library
- Extracts 100+ financial metrics (current price, P/E ratio, dividend yield, revenue, EPS, ROE, debt ratios, etc.)
- Fills the professional report template with actual values
- Saves the report to `evaluaciones/{TICKER}/informe-yfinance.md`

### Step 3: Call berkshire-valuation
Feeds the technical report to NotebookLM which:
- Reads the entire yfinance informe without modifications
- Applies Berkshire Hathaway's investment framework, analyzing:
  - **Competitive moat**: Is there a durable competitive advantage?
  - **Management quality**: Do executives have a strong track record?
  - **Margin of safety**: Is the valuation attractive enough to justify the risk?
  - **Growth sustainability**: Can the company maintain competitive advantage long-term?
  - **Investment thesis**: Buy/hold/avoid with structured reasoning
- Returns a markdown analysis incorporating Berkshire's principles
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
1. **informe-yfinance.md** — 15+ sections covering:
   - Asset identification & current pricing
   - Valuation metrics (P/E, P/B, PEG, dividend yield)
   - Financial statements (balance sheet, income statement, cash flow)
   - Profitability & efficiency (ROE, ROA, asset turnover)
   - Financial health & leverage ratios
   - Growth metrics (revenue/earnings growth, forward estimates)
   - Technical analysis & corporate events
   - Management & SWOT analysis

2. **informe-berkshire.md** — Berkshire Hathaway investment analysis including:
   - Competitive advantage assessment
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

**Workflow executes**:
1. Extracts ticker: `AAPL`
2. Calls yfinance-report → generates `evaluaciones/AAPL/informe-yfinance.md`
3. Calls berkshire-valuation → generates `evaluaciones/AAPL/informe-berkshire.md`
4. Reports both files to user

**User input**:
```
Should I buy Microsoft?
```

**Workflow executes**:
1. Extracts ticker from context: `MSFT` (via skill parsing)
2. Runs full two-phase analysis
3. Returns both comprehensive reports

## Error Handling

If either phase fails:
- **yfinance-report fails** (invalid ticker, API issues): Workflow stops with clear error message
- **berkshire-valuation fails** (auth issues, timeout): Returns partial result (technical report only) with explanation
- **File not found**: Reports which file wasn't generated and suggests manual review

## Dependencies

- **Python 3.7+** (inherited from both base skills)
- **yfinance** (for financial data)
- **notebooklm-py** (for Berkshire analysis via NotebookLM)
- **pandas** (optional, recommended for data processing)
- **NotebookLM authentication** (pre-configured storage_state.json required)

## Limitations & Considerations

- **Ticker validation**: Accepts 1-5 character alphanumeric symbols (standard stock tickers)
- **Market hours**: Most accurate during market hours when real-time data is fresh
- **NotebookLM dependency**: Berkshire analysis requires active NotebookLM authentication
- **Rate limits**: Respect yfinance and NotebookLM API rate limits for batch operations

## Tips for Best Results

1. **Provide clear context**: "Analyze AAPL" is better than "what do you think?" (helps extraction)
2. **One ticker at a time**: Run this workflow separately for each ticker you want to compare
3. **Review both reports**: The yfinance report is technical baseline; the Berkshire analysis is the investment thesis
4. **Use for comparison**: Run workflow for multiple tickers, then compare the informe-berkshire.md outputs to see Berkshire's relative assessments
5. **Export for sharing**: Both markdown files are formatted for easy sharing, printing, or conversion to PDF

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
Wait for informe-yfinance.md creation (up to 30 seconds)
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
