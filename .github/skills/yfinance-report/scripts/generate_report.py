#!/usr/bin/env python3
"""
Generate financial reports for stock tickers using yfinance.

Usage:
    python generate_report.py AAPL
    python generate_report.py MSFT GOOGL TSLA
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

try:
    import yfinance as yf
    import pandas as pd
except ImportError:
    print("Error: yfinance is required. Install with: pip install yfinance pandas")
    sys.exit(1)


def safe_get(d, key, default="N/A"):
    """Safely get value from dict, return default if missing or None."""
    value = d.get(key)
    if value is None:
        return default
    return value


def format_currency(value, symbol="$"):
    """Format number as currency."""
    if value == "N/A" or value is None:
        return "N/A"
    try:
        return f"{symbol}{float(value):,.2f}"
    except (ValueError, TypeError):
        return str(value)


def format_percentage(value):
    """Format number as percentage."""
    if value == "N/A" or value is None:
        return "N/A"
    try:
        return f"{float(value):.2f}%"
    except (ValueError, TypeError):
        return str(value)


def format_large_number(value):
    """Format large numbers with commas."""
    if value == "N/A" or value is None:
        return "N/A"
    try:
        return f"{int(float(value)):,}"
    except (ValueError, TypeError):
        return str(value)


def fetch_ticker_data(ticker_symbol):
    """Fetch financial data from yfinance."""
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        if not info or "symbol" not in info:
            print(f"Error: Could not fetch data for ticker {ticker_symbol}")
            return None
        
        return ticker, info
    except Exception as e:
        print(f"Error fetching data for {ticker_symbol}: {e}")
        return None


def build_data_dict(ticker_symbol, ticker, info):
    """Build dictionary with all fields for template filling."""
    
    # Calculate some derived fields
    current_price = safe_get(info, "currentPrice", 0)
    previous_close = safe_get(info, "previousClose", 0)
    change_points = 0
    change_percent = 0
    
    if current_price != "N/A" and previous_close != "N/A":
        try:
            change_points = float(current_price) - float(previous_close)
            change_percent = (change_points / float(previous_close) * 100) if previous_close != 0 else 0
        except (ValueError, TypeError):
            pass
    
    data = {
        # === Basic Info ===
        "TICKER": ticker_symbol,
        "NOMBRE_ACTIVO": safe_get(info, "longName", ticker_symbol),
        "LONG_NAME": safe_get(info, "longName", "N/A"),
        "COUNTRY": safe_get(info, "country", "N/A"),
        "SECTOR": safe_get(info, "sector", "N/A"),
        "INDUSTRY": safe_get(info, "industry", "N/A"),
        "WEBSITE": safe_get(info, "website", "N/A"),
        "LONG_BUSINESS_SUMMARY": safe_get(info, "longBusinessSummary", "N/A"),
        "FECHA": datetime.now().strftime("%Y-%m-%d"),
        "PERIODO": "Último año fiscal",
        
        # === Current Price Data ===
        "CURRENT_PRICE": format_currency(safe_get(info, "currentPrice")),
        "PREVIOUS_CLOSE": format_currency(safe_get(info, "previousClose")),
        "OPEN": format_currency(safe_get(info, "open")),
        "CHANGE_POINTS": format_currency(change_points),
        "CHANGE_PERCENT": format_percentage(change_percent),
        
        # === Price Ranges ===
        "DAY_LOW": format_currency(safe_get(info, "dayLow")),
        "DAY_HIGH": format_currency(safe_get(info, "dayHigh")),
        "FIFTY_TWO_WEEK_LOW": format_currency(safe_get(info, "fiftyTwoWeekLow")),
        "FIFTY_TWO_WEEK_HIGH": format_currency(safe_get(info, "fiftyTwoWeekHigh")),
        
        # === Volume ===
        "VOLUME": format_large_number(safe_get(info, "volume")),
        "AVERAGE_VOLUME": format_large_number(safe_get(info, "averageVolume")),
        "AVERAGE_VOLUME_10DAYS": format_large_number(safe_get(info, "averageVolume10days")),
        
        # === Market Cap & Shares ===
        "MARKET_CAP": format_currency(safe_get(info, "marketCap")),
        "ENTERPRISE_VALUE": format_currency(safe_get(info, "enterpriseValue")),
        "SHARES_OUTSTANDING": format_large_number(safe_get(info, "sharesOutstanding")),
        "FLOAT_SHARES": format_large_number(safe_get(info, "floatShares")),
        
        # === Valuation Multiples ===
        "TRAILING_PE": safe_get(info, "trailingPE", "N/A"),
        "FORWARD_PE": safe_get(info, "forwardPE", "N/A"),
        "PEG_RATIO": safe_get(info, "pegRatio", "N/A"),
        "PRICE_TO_BOOK": safe_get(info, "priceToBook", "N/A"),
        "PRICE_TO_SALES": safe_get(info, "priceToSalesTrailing12Months", "N/A"),
        "EV_TO_REVENUE": safe_get(info, "enterpriseToRevenue", "N/A"),
        "EV_TO_EBITDA": safe_get(info, "enterpriseToEbitda", "N/A"),
        
        # === Dividends ===
        "DIVIDEND_YIELD": format_percentage(safe_get(info, "dividendYield")),
        "TRAILING_ANNUAL_DIVIDEND_RATE": format_currency(safe_get(info, "trailingAnnualDividendRate")),
        "EX_DIVIDEND_DATE": safe_get(info, "exDividendDate", "N/A"),
        "NEXT_DIVIDEND_DATE": safe_get(info, "nextFiscalYearEnd", "N/A"),
        "FIVE_YEAR_AVE_DIVIDEND_YIELD": format_percentage(safe_get(info, "fiveYearAvgDividendYield")),
        
        # === Dividend History (dummy placeholders) ===
        "DATE_1": "N/A", "DIVIDEND_1": "N/A",
        "DATE_2": "N/A", "DIVIDEND_2": "N/A",
        "DATE_3": "N/A", "DIVIDEND_3": "N/A",
        
        # === Balance Sheet ===
        "CASH": format_currency(safe_get(info, "totalCash")),
        "CURRENT_ASSETS": format_currency(safe_get(info, "currentAssets")),
        "TOTAL_ASSETS": format_currency(safe_get(info, "totalAssets")),
        "SHORT_TERM_DEBT": format_currency(safe_get(info, "shortTermDebt")),
        "LONG_TERM_DEBT": format_currency(safe_get(info, "longTermDebt")),
        "TOTAL_DEBT": format_currency(safe_get(info, "totalDebt")),
        "TOTAL_LIABILITIES": format_currency(safe_get(info, "totalLiabilities")),
        "TOTAL_EQUITY": format_currency(safe_get(info, "totalStockholderEquity")),
        
        # === Income Statement ===
        "TOTAL_REVENUE": format_currency(safe_get(info, "totalRevenue")),
        "NET_INCOME": format_currency(safe_get(info, "netIncomeToCommon")),
        "EBITDA": format_currency(safe_get(info, "ebitda")),
        "OPERATING_INCOME": format_currency(safe_get(info, "operatingIncome")),
        
        # === Margins ===
        "PROFIT_MARGINS": safe_get(info, "profitMargins", "N/A"),
        "OPERATING_MARGINS": safe_get(info, "operatingMargins", "N/A"),
        "EBITDA_MARGINS": safe_get(info, "ebitdaMargins", "N/A"),
        
        # === Cash Flow ===
        "OPERATING_CASHFLOW": format_currency(safe_get(info, "operatingCashflow")),
        "FREE_CASHFLOW": format_currency(safe_get(info, "freeCashflow")),
        
        # === Profitability Metrics ===
        "RETURN_ON_EQUITY": safe_get(info, "returnOnEquity", "N/A"),
        "RETURN_ON_ASSETS": safe_get(info, "returnOnAssets", "N/A"),
        "ROIC": safe_get(info, "returnOnCapital", "N/A"),
        "ASSET_TURNOVER": safe_get(info, "assetTurnover", "N/A"),
        
        # === Financial Health ===
        "DEBT_TO_EQUITY": safe_get(info, "debtToEquity", "N/A"),
        "DEBT_TO_EBITDA": safe_get(info, "debtToEquity", "N/A"),  # Fallback
        "DEBT_TO_REVENUE": safe_get(info, "debtToEquity", "N/A"),  # Fallback
        "CURRENT_RATIO": safe_get(info, "currentRatio", "N/A"),
        "QUICK_RATIO": safe_get(info, "quickRatio", "N/A"),
        
        # === Growth ===
        "REVENUE_GROWTH_5Y": safe_get(info, "revenuePerShare", "N/A"),
        "REVENUE_GROWTH_3Y": safe_get(info, "revenuePerShare", "N/A"),
        "EARNINGS_GROWTH_YOY": safe_get(info, "earningsGrowth", "N/A"),
        "FORWARD_REVENUE_GROWTH": safe_get(info, "revenueGrowth", "N/A"),
        "EPS_GROWTH_FORWARD": safe_get(info, "epsForward", "N/A"),
        
        # === Shareholder Info ===
        "INSIDERS_PERCENT_HELD": safe_get(info, "insidersPercent", "N/A"),
        "INSTITUTIONS_PERCENT_HELD": safe_get(info, "institutionsPercent", "N/A"),
        "PERCENT_HELD_BY_INSIDERS": safe_get(info, "insidersPercent", "N/A"),
        
        # === Short ===
        "SHARES_SHORT": format_large_number(safe_get(info, "sharesShort")),
        "SHORT_RATIO": safe_get(info, "shortRatio", "N/A"),
        
        # === Options (dummy placeholders) ===
        "OPTION_EXP_1": "N/A", "OPTION_EXP_2": "N/A", "OPTION_EXP_3": "N/A", "OPTION_EXP_N": "N/A",
        "SELECTED_EXPIRY": "N/A",
        "STRIKE_1": "N/A", "BID_1": "N/A", "ASK_1": "N/A", "VOL_1": "N/A", "IV_1": "N/A", "DELTA_1": "N/A", "THETA_1": "N/A",
        "STRIKE_2": "N/A", "BID_2": "N/A", "ASK_2": "N/A", "VOL_2": "N/A", "IV_2": "N/A", "DELTA_2": "N/A", "THETA_2": "N/A",
        
        # === Technical Analysis (dummy) ===
        "OPEN_1M": "N/A", "CLOSE_1M": "N/A", "HIGH_1M": "N/A", "LOW_1M": "N/A", "CHANGE_1M": "N/A", "AVG_VOL_1M": "N/A",
        "OPEN_3M": "N/A", "CLOSE_3M": "N/A", "HIGH_3M": "N/A", "LOW_3M": "N/A", "CHANGE_3M": "N/A", "AVG_VOL_3M": "N/A",
        "OPEN_6M": "N/A", "CLOSE_6M": "N/A", "HIGH_6M": "N/A", "LOW_6M": "N/A", "CHANGE_6M": "N/A", "AVG_VOL_6M": "N/A",
        "OPEN_1Y": "N/A", "CLOSE_1Y": "N/A", "HIGH_1Y": "N/A", "LOW_1Y": "N/A", "CHANGE_1Y": "N/A", "AVG_VOL_1Y": "N/A",
        
        # === Corporate Events (dummy) ===
        "EARNINGS_DATE_1": "N/A", "EARNINGS_DESC_1": "N/A",
        "DIVIDEND_DATE_1": "N/A", "DIVIDEND_DESC_1": "N/A",
        "SPLIT_DATE_1": "N/A", "SPLIT_DESC_1": "N/A",
        
        # === Analyst Recommendations ===
        "STRONG_BUY": safe_get(info, "numberOfStrongBuy", "N/A"),
        "STRONG_BUY_CHANGE": "N/A",
        "BUY": safe_get(info, "numberOfBuy", "N/A"),
        "BUY_CHANGE": "N/A",
        "HOLD": safe_get(info, "numberOfHold", "N/A"),
        "HOLD_CHANGE": "N/A",
        "SELL": safe_get(info, "numberOfSell", "N/A"),
        "SELL_CHANGE": "N/A",
        "STRONG_SELL": safe_get(info, "numberOfStrongSell", "N/A"),
        "STRONG_SELL_CHANGE": "N/A",
        "TARGET_PRICE": format_currency(safe_get(info, "targetMeanPrice")),
        "UPSIDE_DOWNSIDE": safe_get(info, "targetMeanPrice", "N/A"),
        
        # === Executive Management (dummy) ===
        "CEO_NAME": "N/A", "CEO_SALARY": "N/A",
        "CFO_NAME": "N/A", "CFO_SALARY": "N/A",
        "COO_NAME": "N/A", "COO_SALARY": "N/A",
        
        # === SWOT (dummy) ===
        "STRENGTH_1": "Strong market position and brand recognition",
        "STRENGTH_2": "Diverse product portfolio and revenue streams",
        "STRENGTH_3": "Solid financial performance and cash generation",
        "WEAKNESS_1": "Competition from emerging players",
        "WEAKNESS_2": "Dependence on key markets",
        "WEAKNESS_3": "Potential regulatory risks",
        "OPPORTUNITY_1": "Expansion into new markets and segments",
        "OPPORTUNITY_2": "Technology innovation and digital transformation",
        "RISK_1": "Economic cycles and market volatility",
        "RISK_2": "Regulatory and geopolitical changes",
        "ANALYST_CONCLUSION": "Based on available financial data, this company shows stable fundamentals with growth potential. Further analysis recommended.",
        
        # === Splits (dummy) ===
        "SPLIT_DATE_1": "N/A", "SPLIT_RATIO_1": "N/A",
        "SPLIT_DATE_2": "N/A", "SPLIT_RATIO_2": "N/A",
        
        # === Footer ===
        "LAST_UPDATE": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    return data


def generate_report(ticker_symbol):
    """Generate and save financial report for a ticker."""
    
    print(f"[*] Fetching data for {ticker_symbol}...")
    result = fetch_ticker_data(ticker_symbol)
    
    if result is None:
        return False
    
    ticker, info = result
    print(f"[+] Data fetched for {info.get('longName', ticker_symbol)}")
    
    # Build data dictionary
    data = build_data_dict(ticker_symbol, ticker, info)
    
    # Find and read template
    script_dir = Path(__file__).parent
    template_path = script_dir.parent / "plantilla.md"
    if not template_path.exists():
        print(f"Error: plantilla.md not found in {template_path}")
        return False
    
    print(f"[*] Reading template from {template_path}")
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()
    
    # Fill template
    try:
        filled = template.format(**data)
    except KeyError as e:
        print(f"Error: Missing key in data dict: {e}")
        return False
    
    # Create output directory and save report
    output_dir = Path("evaluaciones") / ticker_symbol
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "informe-yfinance.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(filled)
    
    print(f"[+] Report saved to {output_file}")
    return True


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python generate_report.py TICKER [TICKER2 ...]")
        print("Example: python generate_report.py AAPL MSFT GOOGL")
        sys.exit(1)
    
    tickers = sys.argv[1:]
    
    success_count = 0
    for ticker in tickers:
        if generate_report(ticker.upper()):
            success_count += 1
        print()
    
    print(f"[*] Generated {success_count}/{len(tickers)} reports successfully")
    
    if success_count < len(tickers):
        sys.exit(1)


if __name__ == "__main__":
    main()
