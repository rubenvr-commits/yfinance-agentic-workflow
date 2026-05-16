# yfinance-report Skill

A powerful skill for generating professional financial reports for any stock ticker using real-time Yahoo Finance data.

## Overview

The **yfinance-report** skill automates the process of gathering comprehensive financial metrics and generating professional markdown reports. It extracts 100+ financial fields from yfinance and fills them into a structured template.

## What It Does

- **Fetches real-time data** from Yahoo Finance (via yfinance)
- **Extracts 100+ metrics** including prices, valuations, balance sheet, dividends, cash flows, and profitability ratios
- **Handles missing data** gracefully — shows "N/A" instead of breaking
- **Generates professional reports** in markdown format
- **Supports multiple tickers** in a single run
- **Organizes output** in `evaluaciones/{TICKER}/informe-yfinance.md`

## Quick Start

### Installation

1. Ensure yfinance is installed:
```bash
pip install yfinance pandas
```

2. Copy the skill directory to your `.github/skills/` folder:
```bash
.github/skills/yfinance-report/
├── SKILL.md
├── README.md
├── plantilla.md
├── scripts/
│   └── generate_report.py
└── evals/
    └── evals.json
```

### Usage

Run the script directly:
```bash
python .github/skills/yfinance-report/scripts/generate_report.py AAPL
```

Or generate multiple reports at once:
```bash
python .github/skills/yfinance-report/scripts/generate_report.py AAPL MSFT GOOGL
```

This creates professional reports in:
- `evaluaciones/AAPL/informe-yfinance.md`
- `evaluaciones/MSFT/informe-yfinance.md`
- `evaluaciones/GOOGL/informe-yfinance.md`

## Report Contents

Each report includes 15 major sections:

1. **Asset Identification** — Company name, sector, industry, website, business summary
2. **Current Price Data** — Current price, change %, volume
3. **Capitalization** — Market cap, enterprise value, shares outstanding
4. **Valuation Multiples** — P/E, P/B, P/S, EV/Revenue, EV/EBITDA
5. **Dividends** — Yield, dividend rate, ex-dividend date
6. **Balance Sheet** — Assets, liabilities, equity
7. **Income Statement** — Revenue, net income, EBITDA, operating income
8. **Profitability** — ROE, ROA, ROIC, margins
9. **Financial Health** — Debt ratios, liquidity ratios
10. **Growth Metrics** — Revenue/earnings growth
11. **Shareholder Info** — Insider/institutional holdings, short positions
12. **Options Data** — Options chains (when available)
13. **Technical Analysis** — Price history over different periods
14. **Corporate Events** — Earnings dates, dividends, splits
15. **SWOT & Conclusions** — Strengths, weaknesses, opportunities, risks

## File Structure

```
yfinance-report/
├── SKILL.md                          # Skill definition & documentation
├── scripts/
│   └── generate_report.py           # Main Python script
└── evals/
    └── evals.json                   # Test case definitions
```

## Technical Details

- **Language:** Python 3.7+
- **Dependencies:** `yfinance`, `pandas` (pandas is optional)
- **Template:** Uses `plantilla.md` from `.github/skills/yfinance-report/`
- **Output:** Markdown files in UTF-8 encoding
- **Execution time:** 10-30 seconds per report

## Data Handling

### Missing Fields
When yfinance doesn't provide a value:
- Numeric fields → "N/A"
- Text fields → "N/A"
- Currency fields → Formatted as "N/A"

### Formatting
- Prices and market cap → Currency format ($1,234.56)
- Percentages → Decimal format (45.23%)
- Large numbers → Comma-separated (1,234,567)

## Examples

### Single Ticker
```bash
python .github/skills/yfinance-report/scripts/generate_report.py AAPL
```
**Output:** `evaluaciones/AAPL/informe-yfinance.md`

### Multiple Tickers (Batch)
```bash
python .github/skills/yfinance-report/scripts/generate_report.py MSFT GOOGL TSLA
```
**Output:**
- `evaluaciones/MSFT/informe-yfinance.md`
- `evaluaciones/GOOGL/informe-yfinance.md`
- `evaluaciones/TSLA/informe-yfinance.md`

### Complex Tickers
```bash
python .github/skills/yfinance-report/scripts/generate_report.py BRK.B
```
**Output:** `evaluaciones/BRK.B/informe-yfinance.md`

## Supported Tickers

- **US Stocks:** AAPL, MSFT, GOOGL, TSLA, etc.
- **International:** ASML (Amsterdam), SAP (Frankfurt), etc.
- **Multiple Share Classes:** BRK.A, BRK.B (Berkshire Hathaway)
- **Indices:** ^GSPC (S&P 500), ^IXIC (Nasdaq), etc.

## Limitations

- **Data Availability:** Sparse for small-cap/penny stocks
- **Currency:** yfinance returns native currency (USD for US stocks)
- **Options:** Limited to available expiry dates and strikes
- **Historical Data:** Limited for delisted stocks

## Tips

1. **Use standard ticker symbols** (check Yahoo Finance for correct symbol)
2. **Large-cap stocks have the most complete data**
3. **Batch process multiple tickers** for efficiency
4. **Convert currencies manually** if needed (yfinance returns native currency)

## Development

### Running Tests
```bash
python -m pytest .github/skills/yfinance-report/evals/
```

### Test Cases

1. **AAPL Report** — Single large-cap US stock
2. **MSFT + TSLA** — Multiple stocks for comparison
3. **BRK.B** — Complex ticker with different share classes

## Dependencies

### Required
- `yfinance` >= 0.1.70

### Optional
- `pandas` >= 1.0 (recommended for large-scale processing)

Install with:
```bash
pip install yfinance pandas
```

## Troubleshooting

### "plantilla.md not found"

Ensure `plantilla.md` exists in `.github/skills/yfinance-report/`.

### "Could not fetch data for ticker X"
Verify the ticker symbol is correct on Yahoo Finance.

### Missing fields in output
Some metrics are not available for all tickers — these show as "N/A".

### SSL errors
Update certificates:
```bash
pip install --upgrade certifi
```

## License

Same as the main repository.

## Contributing

To improve this skill:
1. Test with more tickers
2. Add additional financial metrics
3. Enhance error handling
4. Optimize performance

## Support

For issues or feature requests, open an issue in the repository.
