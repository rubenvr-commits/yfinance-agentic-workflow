---
name: yfinance-report
description: "Generate comprehensive financial reports for any stock ticker using yfinance data and a professional markdown template. Use this skill whenever the user asks to analyze a stock, create a financial report, research a company's financials, or when they mention a ticker symbol and want financial analysis. This skill pulls real-time data from Yahoo Finance (via yfinance), extracts key financial metrics (prices, valuations, balance sheet, dividends, options), and fills a professional report template automatically. Output is saved to evaluaciones/{ticker}/informe-tecnico.md for easy organization."
compatibility: "Python 3.7+, yfinance, pandas (optional but recommended)"
---

# yfinance Financial Report Generator

Generate professional financial reports for any stock ticker. This skill automates the process of gathering financial data and creating a structured, comprehensive markdown report using real-time Yahoo Finance data.

## What This Skill Does

1. **Downloads financial data** from yfinance for the requested ticker
2. **Extracts and processes** ~100+ financial metrics (prices, valuations, balance sheet, dividends, cash flows, options)
3. **Handles missing data** gracefully (shows "N/A" for unavailable fields)
4. **Fills the report template** (`references/plantilla.md`) with actual values
5. **Saves the report** to `evaluaciones/{TICKER}/informe-tecnico.md`

## When to Use This Skill

- User wants to analyze a stock ticker (e.g., "What's Apple's financials?")
- User needs a financial report for investment analysis
- User mentions a ticker symbol and wants comprehensive financial data
- User asks to "research" or "analyze" a company's financials
- User wants to compare stocks (run the skill once per ticker, then compare outputs)

## Input

**Required:** A valid stock ticker symbol (e.g., `AAPL`, `MSFT`, `GOOGL`)

**Optional context:**
- Focus area (e.g., "focus on dividends", "check valuation metrics")
- Comparison with other tickers (run separately, then compare)

The skill will automatically locate `plantilla.md` in the `.github/skills/yfinance-report/` directory and use it as the template.

## Output

**File location:** `evaluaciones/{TICKER}/informe-tecnico.md`

**Contents:** 15 major sections covering asset identification, current pricing, capitalization, valuation multiples, dividends, financial statements, profitability, financial health, growth metrics, shareholder info, options data, technical analysis, corporate events, executive management, and SWOT analysis.

## How It Works

### Step 1: Setup
The skill uses a Python script that imports `yfinance` and reads `plantilla.md` from the `.github/skills/yfinance-report/` directory, then downloads ticker data.

### Step 2: Data Extraction & Processing
For each template field (`{TICKER}`, `{CURRENT_PRICE}`, `{TRAILING_PE}`, etc.):
- Extracts the value from yfinance
- Handles missing values → "N/A"
- Formats numbers (currency, percentages, etc.)

### Step 3: Template Filling
Uses Python's `.format()` method to fill all placeholders with actual yfinance data.

### Step 4: Save
Creates `evaluaciones/{TICKER}/` directory and saves the report as `informe-tecnico.md`.

## Example Usage

**User asks:**
```
Generate a financial report for AAPL
```

**Script runs:**
```python
import yfinance as yf
import os

ticker_symbol = "AAPL"
ticker = yf.Ticker(ticker_symbol)
info = ticker.info

with open("plantilla.md", "r", encoding="utf-8") as f:
    template = f.read()

# Map yfinance fields to template placeholders
data = {
    "TICKER": ticker_symbol,
    "LONG_NAME": info.get('longName', 'N/A'),
    "CURRENT_PRICE": info.get('currentPrice', 'N/A'),
    "TRAILING_PE": info.get('trailingPE', 'N/A'),
    # ... 100+ more fields from yfinance.info
}

filled = template.format(**data)

os.makedirs(f"evaluaciones/{ticker_symbol}", exist_ok=True)
with open(f"evaluaciones/{ticker_symbol}/informe-tecnico.md", "w", encoding="utf-8") as f:
    f.write(filled)
```

**Output:** Professional markdown report in `evaluaciones/AAPL/informe-tecnico.md`

## Handling Missing Data

When yfinance doesn't provide a value:
- Numeric fields → "N/A"
- Text fields → "N/A"
- Empty sections → Filled with "N/A"

## Tips for Best Results

1. **Standard tickers only** (AAPL, MSFT, TSLA). Avoid OTC or delisted stocks.
2. **Large-cap stocks have more complete data** — small caps may have sparse metrics.
3. **yfinance returns native currency** (USD for US stocks, etc.) — convert manually if needed.
4. **Run once per ticker** if comparing multiple stocks.

## Dependencies & Notes

- **Required:** Python 3.7+, `yfinance`
- **Optional:** `pandas` for advanced processing
- **Template:** in `./references/plantilla.md`
- **Execution time:** 10-30 seconds per report
- **Script:** See `scripts/generate_report.py`
