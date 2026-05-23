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


def calculate_sharpe_ratio(ticker_symbol, history_data, years, risk_free_rate=0.02):
    """
    Calculate Sharpe ratio for a given period.
    
    Args:
        ticker_symbol: Ticker symbol (for error reporting)
        history_data: Cached historical data dictionary
        years: Number of years to analyze
        risk_free_rate: Annual risk-free rate (default 2%)
    
    Returns:
        Sharpe ratio or "N/A" if calculation fails
    """
    try:
        period_str = f"{years}y"
        hist = history_data.get(period_str)
        
        if hist is None or hist.empty or len(hist) < 30:
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


def calculate_sortino_ratio(ticker_symbol, history_data, years, risk_free_rate=0.02):
    """
    Calculate Sortino ratio for a given period.
    Only considers downside volatility (negative returns).
    
    Args:
        ticker_symbol: Ticker symbol (for error reporting)
        history_data: Cached historical data dictionary
        years: Number of years to analyze
        risk_free_rate: Annual risk-free rate (default 2%)
    
    Returns:
        Sortino ratio or "N/A" if calculation fails
    """
    try:
        period_str = f"{years}y"
        hist = history_data.get(period_str)
        
        if hist is None or hist.empty or len(hist) < 30:
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


def build_swot_from_metrics(info, sector="sector desconocido", country="país desconocido"):
    """
    Build SWOT analysis from actual financial metrics.
    
    Args:
        info: yfinance Ticker info dict
        sector: Company sector
        country: Company country
    
    Returns:
        Dict with STRENGTH_*, WEAKNESS_*, OPPORTUNITY_*, RISK_*, ANALYST_CONCLUSION keys
    """
    result = {}
    
    # Extract metrics safely
    roe = safe_get(info, "returnOnEquity")
    profit_margins = safe_get(info, "profitMargins")
    debt_to_equity = safe_get(info, "debtToEquity")
    fcf = safe_get(info, "freeCashflow")
    current_ratio = safe_get(info, "currentRatio")
    revenue_growth = safe_get(info, "revenueGrowth")
    pe_ratio = safe_get(info, "trailingPE")
    
    # Convert to float safely
    def to_float(val):
        if val == "N/A":
            return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None
    
    roe_val = to_float(roe)
    profit_margins_val = to_float(profit_margins)
    debt_to_equity_val = to_float(debt_to_equity)
    fcf_val = to_float(fcf)
    current_ratio_val = to_float(current_ratio)
    revenue_growth_val = to_float(revenue_growth)
    pe_val = to_float(pe_ratio)
    
    # Build Strengths (select best 3 from candidates)
    strengths_candidates = []
    
    if roe_val is not None and roe_val > 0.15:
        strengths_candidates.append(f"ROE del {roe_val:.1%}: genera valor sostenido para el accionista")
    
    if profit_margins_val is not None and profit_margins_val > 0.20:
        strengths_candidates.append(f"Margen neto del {profit_margins_val:.1%}: poder de fijación de precios elevado")
    
    if debt_to_equity_val is not None and debt_to_equity_val < 1.0:
        strengths_candidates.append(f"Balance saneado con ratio deuda/patrimonio de {debt_to_equity_val:.2f}")
    
    if fcf_val is not None and fcf_val > 0:
        fcf_formatted = format_currency(fcf_val)
        strengths_candidates.append(f"Generación de FCF de {fcf_formatted}")
    
    # Take best 3 strengths
    for i in range(1, 4):
        if i - 1 < len(strengths_candidates):
            result[f"STRENGTH_{i}"] = strengths_candidates[i - 1]
        else:
            result[f"STRENGTH_{i}"] = "N/A"
    
    # Build Weaknesses (select worst up to 3)
    weaknesses_candidates = []
    
    if current_ratio_val is not None and current_ratio_val < 1.0:
        weaknesses_candidates.append(f"Razón circulante de {current_ratio_val:.2f}: posible presión de liquidez a corto plazo")
    
    if debt_to_equity_val is not None and debt_to_equity_val > 2.0:
        weaknesses_candidates.append(f"Apalancamiento elevado: deuda/patrimonio de {debt_to_equity_val:.2f}")
    
    if revenue_growth_val is not None and revenue_growth_val < 0:
        weaknesses_candidates.append(f"Contracción de ingresos YoY del {revenue_growth_val:.1%}")
    
    if profit_margins_val is not None and profit_margins_val < 0.05:
        weaknesses_candidates.append(f"Márgenes netos ajustados del {profit_margins_val:.1%}")
    
    # Take up to 3 weaknesses
    for i in range(1, 4):
        if i - 1 < len(weaknesses_candidates):
            result[f"WEAKNESS_{i}"] = weaknesses_candidates[i - 1]
        else:
            result[f"WEAKNESS_{i}"] = "N/A"
    
    # Opportunities (use sector and country info)
    result["OPPORTUNITY_1"] = f"Expansión en mercados emergentes del sector {sector}"
    result["OPPORTUNITY_2"] = "Tendencias de digitalización e IA aplicables al negocio"
    
    # Risks (use sector and country info)
    result["RISK_1"] = f"Ciclos económicos y volatilidad de mercado en el sector {sector}"
    result["RISK_2"] = f"Cambios regulatorios o geopolíticos que afecten a {country}"
    
    # Analyst Conclusion: summarize 3 most relevant metrics
    conclusion_parts = []
    
    if pe_val is not None:
        conclusion_parts.append(f"P/E de {pe_val:.2f}")
    
    if roe_val is not None:
        conclusion_parts.append(f"ROE del {roe_val:.1%}")
    
    if fcf_val is not None:
        fcf_formatted = format_currency(fcf_val)
        conclusion_parts.append(f"FCF de {fcf_formatted}")
    
    if conclusion_parts:
        metrics_summary = ", ".join(conclusion_parts)
        result["ANALYST_CONCLUSION"] = f"Basado en datos financieros disponibles, con {metrics_summary}, la empresa presenta fundamentales apropiados para análisis posterior."
    else:
        result["ANALYST_CONCLUSION"] = "Basado en datos financieros disponibles, la empresa presenta fundamentales que requieren análisis posterior."
    
    return result


def extract_executives(info):
    """
    Extract executive names and salaries from companyOfficers.
    
    Args:
        info: yfinance Ticker info dict
    
    Returns:
        Dict with CEO_NAME, CEO_SALARY, CFO_NAME, CFO_SALARY, COO_NAME, COO_SALARY.
    """
    officers = info.get("companyOfficers", []) or []
    
    def find_officer(keyword):
        for officer in officers:
            title = str(officer.get("title", "")).lower()
            if keyword.lower() in title:
                return officer
        return None
    
    def format_exec(officer):
        if not officer:
            return "N/A", "N/A"
        name = officer.get("name", "N/A") or "N/A"
        total_pay = officer.get("totalPay")
        return name, format_currency(total_pay)
    
    ceo = find_officer("chief executive")
    cfo = find_officer("chief financial")
    coo = find_officer("chief operating")
    
    ceo_name, ceo_salary = format_exec(ceo)
    cfo_name, cfo_salary = format_exec(cfo)
    coo_name, coo_salary = format_exec(coo)
    
    return {
        "CEO_NAME": ceo_name,
        "CEO_SALARY": ceo_salary,
        "CFO_NAME": cfo_name,
        "CFO_SALARY": cfo_salary,
        "COO_NAME": coo_name,
        "COO_SALARY": coo_salary,
    }


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


def build_technical_section(ticker_symbol, history_data):
    """
    Build technical analysis section with historical price data.
    
    Args:
        ticker_symbol: Ticker symbol (for error reporting)
        history_data: Cached historical data dictionary
    
    Returns:
        Dict with keys OPEN_{period}, CLOSE_{period}, HIGH_{period}, LOW_{period}, 
        CHANGE_{period}, AVG_VOL_{period} for periods 1M, 3M, 6M, 1Y
    """
    result = {}
    periods = [("1mo", "1M"), ("3mo", "3M"), ("6mo", "6M"), ("1y", "1Y")]
    
    for period, suffix in periods:
        try:
            hist = history_data.get(period)
            
            if hist is None or hist.empty or len(hist) == 0:
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
    # Try to fetch ticker info with retries/backoff and record minimal metrics
    max_attempts = 3
    backoff = 1.0
    attempts = []
    for attempt in range(1, max_attempts + 1):
        t0 = datetime.now()
        try:
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info

            if not info or "symbol" not in info:
                attempts.append({"attempt": attempt, "ok": False, "reason": "no_info"})
                raise RuntimeError(f"No info for {ticker_symbol}")

            # success
            attempts.append({"attempt": attempt, "ok": True, "duration_ms": int((datetime.now() - t0).total_seconds() * 1000)})
            # attach metrics to ticker object for downstream use
            try:
                ticker._fetch_metrics = {"info_fetch": {"attempts": attempts}}
            except Exception:
                pass
            return ticker, info

        except Exception as e:
            attempts.append({"attempt": attempt, "ok": False, "error": str(e)})
            if attempt < max_attempts:
                import time as _time
                _time.sleep(backoff * (2 ** (attempt - 1)))
            else:
                print(f"Error fetching data for {ticker_symbol}: {e}")
                return None


def _fetch_history_cache(ticker):
    """
    Fetch and cache historical price data for all required periods.
    
    Periods fetched: 1mo, 3mo, 6mo, 1y (for technical analysis)
                    3y, 5y, 10y (for ratio calculations)
    
    The cache avoids duplicate ticker.history() calls by fetching each period once.
    
    Args:
        ticker: yfinance Ticker object
    
    Returns:
        Dict with period strings as keys (e.g., "1y", "3y") and DataFrames as values.
        Returns empty dict on complete failure.
    """
    history_cache = {}
    fetch_metrics = {}
    
    # Periods needed for technical analysis (short-term)
    technical_periods = ["1mo", "3mo", "6mo", "1y"]
    
    # Additional periods needed for ratio calculations (medium/long-term)
    ratio_periods = ["3y", "5y", "10y"]
    
    # Combine all periods, avoiding duplicates
    all_periods = list(dict.fromkeys(technical_periods + ratio_periods))
    
    for period_str in all_periods:
        period_attempts = []
        success = False
        for attempt in range(1, 4):
            t0 = datetime.now()
            try:
                df = ticker.history(period=period_str)
                duration_ms = int((datetime.now() - t0).total_seconds() * 1000)
                if df is not None:
                    history_cache[period_str] = df
                    fetch_metrics[period_str] = {"attempts": attempt, "duration_ms": duration_ms, "success": True}
                    success = True
                    break
                else:
                    period_attempts.append({"attempt": attempt, "error": "empty_dataframe", "duration_ms": duration_ms})
            except Exception as e:
                duration_ms = int((datetime.now() - t0).total_seconds() * 1000)
                period_attempts.append({"attempt": attempt, "error": str(e), "duration_ms": duration_ms})
                import time as _time
                _time.sleep(1 * (2 ** (attempt - 1)))

        if not success:
            history_cache[period_str] = pd.DataFrame()
            fetch_metrics[period_str] = {"attempts": len(period_attempts), "success": False, "errors": period_attempts}

    return history_cache, fetch_metrics


def build_data_dict(ticker_symbol, ticker, info):
    """Build dictionary with all fields for template filling."""

    # Fetch and cache historical data to avoid duplicate ticker.history() calls
    history_cache, fetch_metrics = _fetch_history_cache(ticker)

    if not history_cache:
        print(f"Warning: No history data available for {ticker_symbol}")
        history_cache = {}
    
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
        "SHARPE_RATIO_1Y": calculate_sharpe_ratio(ticker_symbol, history_cache, 1),
        "SHARPE_RATIO_3Y": calculate_sharpe_ratio(ticker_symbol, history_cache, 3),
        "SHARPE_RATIO_5Y": calculate_sharpe_ratio(ticker_symbol, history_cache, 5),
        "SHARPE_RATIO_10Y": calculate_sharpe_ratio(ticker_symbol, history_cache, 10),
        "SORTINO_RATIO_1Y": calculate_sortino_ratio(ticker_symbol, history_cache, 1),
        "SORTINO_RATIO_3Y": calculate_sortino_ratio(ticker_symbol, history_cache, 3),
        "SORTINO_RATIO_5Y": calculate_sortino_ratio(ticker_symbol, history_cache, 5),
        "SORTINO_RATIO_10Y": calculate_sortino_ratio(ticker_symbol, history_cache, 10),
        
        # === Executive Management ===
        "CEO_NAME": "N/A", "CEO_SALARY": "N/A",
        "CFO_NAME": "N/A", "CFO_SALARY": "N/A",
        "COO_NAME": "N/A", "COO_SALARY": "N/A",
        
        # === Splits (dummy) ===
        "SPLIT_DATE_1": "N/A", "SPLIT_RATIO_1": "N/A",
        "SPLIT_DATE_2": "N/A", "SPLIT_RATIO_2": "N/A",
        
        # === Footer ===
        "LAST_UPDATE": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    # Merge technical analysis data
    data.update(build_technical_section(ticker_symbol, history_cache))
    
    # Merge computed debt metrics
    data.update(compute_debt_metrics(info))
    
    # Merge executive officer data
    data.update(extract_executives(info))
    
    # Merge SWOT analysis from metrics
    sector = safe_get(info, "sector", "sector desconocido")
    country = safe_get(info, "country", "país desconocido")
    data.update(build_swot_from_metrics(info, sector, country))
    
    # return data plus history cache and fetch metrics for downstream
    try:
        data["_internal_fetch_metrics"] = fetch_metrics
    except Exception:
        pass

    return data, history_cache, fetch_metrics


def _to_float_safe(value):
    """Safely convert value to float, returns None if fails."""
    if value == "N/A" or value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _extract_price_history(ticker, history_cache):
    """Extract price history for last 6 and 12 months."""
    price_data_6m = []
    price_data_12m = []
    
    # 6 months data
    hist_6m = history_cache.get("6mo")
    if hist_6m is not None and not hist_6m.empty:
        for date, row in hist_6m.iterrows():
            price_data_6m.append({
                "date": date.strftime("%Y-%m-%d"),
                "close": round(float(row["Close"]), 2)
            })
    
    # 12 months data
    hist_12m = history_cache.get("1y")
    if hist_12m is not None and not hist_12m.empty:
        for date, row in hist_12m.iterrows():
            price_data_12m.append({
                "date": date.strftime("%Y-%m-%d"),
                "close": round(float(row["Close"]), 2)
            })
    
    return price_data_6m, price_data_12m


def _build_metrics_json(ticker_symbol, ticker, info, history_cache, fetch_metrics=None):
    """Build JSON structure with quantitative metrics."""
    
    # Extract current price
    current_price = _to_float_safe(safe_get(info, "currentPrice"))
    
    # Get price histories
    price_history_6m, price_history_12m = _extract_price_history(ticker, history_cache)
    
    # Valuations
    pe_ratio = _to_float_safe(safe_get(info, "trailingPE"))
    pb_ratio = _to_float_safe(safe_get(info, "priceToBook"))
    ps_ratio = _to_float_safe(safe_get(info, "priceToSalesTrailing12Months"))
    price_to_fcf = None
    fcf = _to_float_safe(safe_get(info, "freeCashflow"))
    market_cap = _to_float_safe(safe_get(info, "marketCap"))
    if fcf and market_cap and fcf != 0:
        price_to_fcf = round(market_cap / fcf, 2)
    
    # Performance metrics
    roe = _to_float_safe(safe_get(info, "returnOnEquity"))
    roa = _to_float_safe(safe_get(info, "returnOnAssets"))
    fcf_billions = None
    if fcf:
        fcf_billions = round(fcf / 1e9, 2)
    dividend_yield = _to_float_safe(safe_get(info, "dividendYield"))
    
    # Sector comparison
    pe_sector = None  # Would need to fetch sector data separately
    pe_sp500 = None   # Would need to fetch S&P500 data separately
    
    metrics_json = {
        "ticker": ticker_symbol,
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "precio_actual": current_price,
        "precios_historicos": {
            "ultimos_6m": price_history_6m,
            "ultimos_12m": price_history_12m
        },
        "valuations": {
            "pe_ratio": pe_ratio,
            "pb_ratio": pb_ratio,
            "ps_ratio": ps_ratio,
            "price_to_fcf": price_to_fcf
        },
        "performance": {
            "roe": roe,
            "roa": roa,
            "fcf_billions": fcf_billions,
            "dividend_yield": dividend_yield
        },
        "sector_comparison": {
            "pe_sector": pe_sector,
            "pe_sp500": pe_sp500
        }
    }
    # Attach execution metrics if available
    if fetch_metrics:
        metrics_json["execution_metrics"] = {"history_fetch": fetch_metrics}
    else:
        # attempt to get metrics from ticker object
        try:
            obj_metrics = getattr(ticker, '_fetch_metrics', None)
            if obj_metrics:
                metrics_json["execution_metrics"] = obj_metrics
        except Exception:
            pass
    
    return metrics_json


def generate_report(ticker_symbol):
    """Generate and save financial report for a ticker."""
    
    print(f"[*] Fetching data for {ticker_symbol}...")
    result = fetch_ticker_data(ticker_symbol)
    
    if result is None:
        return False
    
    ticker, info = result
    print(f"[+] Data fetched for {info.get('longName', ticker_symbol)}")
    
    # Build data dictionary (also fetch history cache and fetch metrics)
    data, history_cache, fetch_metrics = build_data_dict(ticker_symbol, ticker, info)
    
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
    
    # Save markdown report
    output_file = output_dir / "informe-tecnico.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(filled)
    
    print(f"[+] Report saved to {output_file}")
    
    # Generate and save metrics JSON
    try:
        metrics_json = _build_metrics_json(ticker_symbol, ticker, info, history_cache, fetch_metrics)
        
        # Create raw-search directory
        raw_search_dir = output_dir / "raw-search"
        raw_search_dir.mkdir(parents=True, exist_ok=True)
        
        # Save metrics JSON
        metrics_file = raw_search_dir / "metrics.json"
        with open(metrics_file, "w", encoding="utf-8") as f:
            json.dump(metrics_json, f, indent=2, ensure_ascii=False)
        
        print(f"[+] Metrics JSON saved to {metrics_file}")
    except Exception as e:
        print(f"Warning: Failed to generate metrics JSON: {e}")
    
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
