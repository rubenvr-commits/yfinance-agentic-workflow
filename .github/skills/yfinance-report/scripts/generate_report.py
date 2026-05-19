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
    import numpy as np
except ImportError:
    print("Error: yfinance and numpy are required. Install with: pip install yfinance pandas numpy")
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


def calculate_sharpe_ratio(ticker, years, risk_free_rate=0.02):
    """
    Calculate Sharpe ratio for a given period.
    
    Args:
        ticker: yfinance Ticker object
        years: Number of years to analyze
        risk_free_rate: Annual risk-free rate (default 2%)
    
    Returns:
        Sharpe ratio or "N/A" if calculation fails
    """
    try:
        # Get historical price data
        hist = ticker.history(period=f"{years}y")
        
        if hist.empty or len(hist) < 30:
            return "N/A"
        
        # Calculate daily returns
        returns = hist['Close'].pct_change().dropna()
        
        if len(returns) == 0:
            return "N/A"
        
        # Calculate annualized metrics
        annual_return = returns.mean() * 252
        annual_volatility = returns.std() * np.sqrt(252)
        
        if annual_volatility == 0:
            return "N/A"
        
        # Sharpe ratio formula: (return - risk_free_rate) / volatility
        sharpe = (annual_return - risk_free_rate) / annual_volatility
        return round(sharpe, 2)
    
    except Exception as e:
        print(f"Error calculating Sharpe ratio for {years}y: {e}")
        return "N/A"


def calculate_sortino_ratio(ticker, years, risk_free_rate=0.02):
    """
    Calculate Sortino ratio for a given period.
    Only considers downside volatility (negative returns).
    
    Args:
        ticker: yfinance Ticker object
        years: Number of years to analyze
        risk_free_rate: Annual risk-free rate (default 2%)
    
    Returns:
        Sortino ratio or "N/A" if calculation fails
    """
    try:
        # Get historical price data
        hist = ticker.history(period=f"{years}y")
        
        if hist.empty or len(hist) < 30:
            return "N/A"
        
        # Calculate daily returns
        returns = hist['Close'].pct_change().dropna()
        
        if len(returns) == 0:
            return "N/A"
        
        # Calculate annualized return
        annual_return = returns.mean() * 252
        
        # Calculate downside deviation (only negative returns)
        downside_returns = returns[returns < 0]
        if len(downside_returns) == 0:
            # If there are no negative returns, downside deviation is 0
            # In this case, Sortino is theoretically infinite
            return "Inf" if annual_return > 0 else "0"
        
        downside_deviation = downside_returns.std() * np.sqrt(252)
        
        if downside_deviation == 0:
            return "Inf" if annual_return > 0 else "0"
        
        # Sortino ratio formula: (return - risk_free_rate) / downside_deviation
        sortino = (annual_return - risk_free_rate) / downside_deviation
        return round(sortino, 2)
    
    except Exception as e:
        print(f"Error calculating Sortino ratio for {years}y: {e}")
        return "N/A"


def calculate_revenue_cagr(ticker, years):
    """
    Calculate revenue compound annual growth rate (CAGR) from annual financials.
    
    Args:
        ticker: yfinance Ticker object
        years: Number of years to calculate CAGR over
    
    Returns:
        Formatted percentage string, or "N/A" if calculation fails
    """
    try:
        # Get annual income statement
        financials = ticker.financials
        
        if financials is None or financials.empty:
            return "N/A"
        
        # Find the revenue row (case-insensitive search)
        revenue_row = None
        for idx in financials.index:
            if "revenue" in str(idx).lower():
                revenue_row = financials.loc[idx]
                break
        
        if revenue_row is None or revenue_row.empty:
            return "N/A"
        
        # Sort columns descending (most recent first)
        revenue_row = revenue_row.sort_index(ascending=False)
        
        # Filter out NaN values
        revenue_row = revenue_row.dropna()
        
        # Need at least 2 data points and at least 1 year of data
        if len(revenue_row) < 2:
            return "N/A"
        
        # Calculate number of years available
        available_years = len(revenue_row) - 1
        n = min(years, available_years)
        
        if n < 1:
            return "N/A"
        
        # Get most recent and past values
        recent = float(revenue_row.iloc[0])
        past = float(revenue_row.iloc[n])
        
        if recent <= 0 or past <= 0:
            return "N/A"
        
        # Calculate CAGR: (recent / past) ** (1/n) - 1
        cagr = (recent / past) ** (1 / n) - 1
        
        # Return formatted percentage
        return format_percentage(cagr * 100)
    
    except Exception as e:
        print(f"Error calculating revenue CAGR for {years}y: {e}")
        return "N/A"


def compute_debt_metrics(info):
    """
    Compute debt-related financial metrics.
    
    Args:
        info: yfinance Ticker info dict
    
    Returns:
        Dict with keys DEBT_TO_EBITDA and DEBT_TO_REVENUE, 
        or "N/A" if computation fails
    """
    result = {}
    
    # DEBT_TO_EBITDA = totalDebt / ebitda
    try:
        total_debt = safe_get(info, "totalDebt")
        ebitda = safe_get(info, "ebitda")
        
        if total_debt == "N/A" or ebitda == "N/A":
            result["DEBT_TO_EBITDA"] = "N/A"
        else:
            total_debt_val = float(total_debt)
            ebitda_val = float(ebitda)
            
            if total_debt_val == 0 or ebitda_val == 0:
                result["DEBT_TO_EBITDA"] = "N/A"
            else:
                result["DEBT_TO_EBITDA"] = round(total_debt_val / ebitda_val, 2)
    except (ValueError, TypeError, ZeroDivisionError):
        result["DEBT_TO_EBITDA"] = "N/A"
    
    # DEBT_TO_REVENUE = totalDebt / totalRevenue
    try:
        total_debt = safe_get(info, "totalDebt")
        total_revenue = safe_get(info, "totalRevenue")
        
        if total_debt == "N/A" or total_revenue == "N/A":
            result["DEBT_TO_REVENUE"] = "N/A"
        else:
            total_debt_val = float(total_debt)
            total_revenue_val = float(total_revenue)
            
            if total_debt_val == 0 or total_revenue_val == 0:
                result["DEBT_TO_REVENUE"] = "N/A"
            else:
                result["DEBT_TO_REVENUE"] = round(total_debt_val / total_revenue_val, 2)
    except (ValueError, TypeError, ZeroDivisionError):
        result["DEBT_TO_REVENUE"] = "N/A"
    
    return result


def build_technical_section(ticker):
    """
    Build technical analysis section with historical price data.
    
    Args:
        ticker: yfinance Ticker object
    
    Returns:
        Dict with keys OPEN_{period}, CLOSE_{period}, HIGH_{period}, LOW_{period}, 
        CHANGE_{period}, AVG_VOL_{period} for periods 1M, 3M, 6M, 1Y
    """
    result = {}
    periods = [("1mo", "1M"), ("3mo", "3M"), ("6mo", "6M"), ("1y", "1Y")]
    
    for period, suffix in periods:
        try:
            hist = ticker.history(period=period)
            
            if hist.empty or len(hist) == 0:
                result[f"OPEN_{suffix}"] = "N/A"
                result[f"CLOSE_{suffix}"] = "N/A"
                result[f"HIGH_{suffix}"] = "N/A"
                result[f"LOW_{suffix}"] = "N/A"
                result[f"CHANGE_{suffix}"] = "N/A"
                result[f"AVG_VOL_{suffix}"] = "N/A"
                continue
            
            # Extract values
            open_price = hist["Open"].iloc[0]
            close_price = hist["Close"].iloc[-1]
            high_price = hist["High"].max()
            low_price = hist["Low"].min()
            avg_volume = hist["Volume"].mean()
            
            # Calculate percentage change
            if open_price != 0:
                change_pct = ((close_price - open_price) / open_price) * 100
            else:
                change_pct = 0
            
            # Format and store
            result[f"OPEN_{suffix}"] = format_currency(open_price)
            result[f"CLOSE_{suffix}"] = format_currency(close_price)
            result[f"HIGH_{suffix}"] = format_currency(high_price)
            result[f"LOW_{suffix}"] = format_currency(low_price)
            result[f"CHANGE_{suffix}"] = format_percentage(change_pct)
            result[f"AVG_VOL_{suffix}"] = format_large_number(avg_volume)
            
        except Exception as e:
            print(f"Error processing {period} history: {e}")
            result[f"OPEN_{suffix}"] = "N/A"
            result[f"CLOSE_{suffix}"] = "N/A"
            result[f"HIGH_{suffix}"] = "N/A"
            result[f"LOW_{suffix}"] = "N/A"
            result[f"CHANGE_{suffix}"] = "N/A"
            result[f"AVG_VOL_{suffix}"] = "N/A"
    
    return result


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
        "CURRENT_RATIO": safe_get(info, "currentRatio", "N/A"),
        "QUICK_RATIO": safe_get(info, "quickRatio", "N/A"),
        
        # === Growth ===
        "REVENUE_GROWTH_5Y": calculate_revenue_cagr(ticker, 5),
        "REVENUE_GROWTH_3Y": calculate_revenue_cagr(ticker, 3),
        "EARNINGS_GROWTH_YOY": safe_get(info, "earningsGrowth", "N/A"),
        "FORWARD_REVENUE_GROWTH": safe_get(info, "revenueGrowth", "N/A"),
        "EPS_GROWTH_FORWARD": safe_get(info, "epsForward", "N/A"),
        
        # === Shareholder Info ===
        "INSIDERS_PERCENT_HELD": format_percentage(safe_get(info, "heldPercentInsiders")),
        "INSTITUTIONS_PERCENT_HELD": format_percentage(safe_get(info, "heldPercentInstitutions")),
        "PERCENT_HELD_BY_INSIDERS": format_percentage(safe_get(info, "heldPercentInsiders")),
        
        # === Short ===
        "SHARES_SHORT": format_large_number(safe_get(info, "sharesShort")),
        "SHORT_RATIO": safe_get(info, "shortRatio", "N/A"),
        
        # === Options (dummy placeholders) ===
        "OPTION_EXP_1": "N/A", "OPTION_EXP_2": "N/A", "OPTION_EXP_3": "N/A", "OPTION_EXP_N": "N/A",
        "SELECTED_EXPIRY": "N/A",
        "STRIKE_1": "N/A", "BID_1": "N/A", "ASK_1": "N/A", "VOL_1": "N/A", "IV_1": "N/A", "DELTA_1": "N/A", "THETA_1": "N/A",
        "STRIKE_2": "N/A", "BID_2": "N/A", "ASK_2": "N/A", "VOL_2": "N/A", "IV_2": "N/A", "DELTA_2": "N/A", "THETA_2": "N/A",
        
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
        
        # === Sharpe & Sortino Ratios ===
        "SHARPE_RATIO_1Y": calculate_sharpe_ratio(ticker, 1),
        "SHARPE_RATIO_3Y": calculate_sharpe_ratio(ticker, 3),
        "SHARPE_RATIO_5Y": calculate_sharpe_ratio(ticker, 5),
        "SHARPE_RATIO_10Y": calculate_sharpe_ratio(ticker, 10),
        "SORTINO_RATIO_1Y": calculate_sortino_ratio(ticker, 1),
        "SORTINO_RATIO_3Y": calculate_sortino_ratio(ticker, 3),
        "SORTINO_RATIO_5Y": calculate_sortino_ratio(ticker, 5),
        "SORTINO_RATIO_10Y": calculate_sortino_ratio(ticker, 10),
        
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
    
    # Merge technical analysis data
    data.update(build_technical_section(ticker))
    
    # Merge computed debt metrics
    data.update(compute_debt_metrics(info))
    
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
    # Try multiple locations for plantilla.md
    template_path = script_dir.parent / "plantilla.md"
    if not template_path.exists():
        template_path = script_dir.parent / "references" / "plantilla.md"
    if not template_path.exists():
        # Try at workspace root
        workspace_root = script_dir.parent.parent.parent.parent
        template_path = workspace_root / "plantilla.md"
    if not template_path.exists():
        print(f"Error: plantilla.md not found in expected locations")
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
    
    output_file = output_dir / "informe-tecnico.md"
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
