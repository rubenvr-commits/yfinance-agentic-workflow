#!/usr/bin/env python3
"""
Generate metrics.json with real yfinance data.
Usage: python generate_metrics_from_yfinance.py NVDA
       python generate_metrics_from_yfinance.py REP.MC
"""

import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

try:
    import yfinance as yf
    import pandas as pd
except ImportError:
    print("Error: yfinance and pandas required. Install with: pip install yfinance pandas")
    sys.exit(1)


def generate_weekly_data(ticker_symbol, periods_back):
    """
    Generate weekly price data for the specified periods.
    
    Args:
        ticker_symbol: Ticker symbol (e.g., 'NVDA')
        periods_back: How many periods back ('1y' for 12 months, '6mo' for 6 months)
    
    Returns:
        List of dicts with 'date' and 'close' keys
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period=periods_back)
        
        if hist.empty:
            print(f"Warning: No data for {ticker_symbol} with period {periods_back}")
            return []
        
        # Resample to weekly data (every 7 days) to get approximately 52 points for 1y
        weekly_data = hist.resample('W').agg({'Close': 'last'})
        
        # Convert to list of dicts
        price_list = []
        for date, row in weekly_data.iterrows():
            if pd.notna(row['Close']):
                price_list.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "close": round(float(row['Close']), 2)
                })
        
        return price_list
    
    except Exception as e:
        print(f"Error fetching data for {ticker_symbol}: {e}")
        return []


def generate_valuations(ticker_symbol):
    """Extract valuation metrics from yfinance."""
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        valuations = {
            "pe_ratio": info.get('trailingPE', None),
            "pb_ratio": info.get('priceToBook', None),
            "ps_ratio": info.get('priceToSalesTrailing12Months', None),
            "price_to_fcf": None  # Not directly available in yfinance
        }
        
        return {k: round(v, 2) if v and isinstance(v, (int, float)) else None for k, v in valuations.items()}
    
    except Exception as e:
        print(f"Error getting valuations for {ticker_symbol}: {e}")
        return {"pe_ratio": None, "pb_ratio": None, "ps_ratio": None, "price_to_fcf": None}


def generate_performance(ticker_symbol):
    """Extract performance metrics from yfinance."""
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        performance = {
            "roe": info.get('returnOnEquity', None),
            "roa": info.get('returnOnAssets', None),
            "fcf_billions": None,  # Would need quarterly data
            "dividend_yield": info.get('dividendYield', None)
        }
        
        # Calculate FCF in billions if available
        fcf = info.get('freeCashflow')
        if fcf:
            performance['fcf_billions'] = round(fcf / 1e9, 2)
        
        # Format percentages and ratios
        result = {}
        for k, v in performance.items():
            if v is None:
                result[k] = None
            elif isinstance(v, (int, float)):
                result[k] = round(v, 4) if k in ['roe', 'roa', 'dividend_yield'] else round(v, 2)
            else:
                result[k] = v
        
        return result
    
    except Exception as e:
        print(f"Error getting performance for {ticker_symbol}: {e}")
        return {"roe": None, "roa": None, "fcf_billions": None, "dividend_yield": None}


def generate_sector_comparison(ticker_symbol):
    """Get sector comparison metrics."""
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        return {
            "pe_sector": info.get('epsTrailingTwelveMonths', None),  # Proxy
            "pe_sp500": 25.0  # S&P 500 average (approximate)
        }
    
    except Exception as e:
        print(f"Error getting sector comparison for {ticker_symbol}: {e}")
        return {"pe_sector": None, "pe_sp500": None}


def generate_metrics(ticker_symbol):
    """Generate complete metrics.json structure."""
    
    print(f"Fetching data for {ticker_symbol}...")
    
    ticker = yf.Ticker(ticker_symbol)
    info = ticker.info
    
    # Get current price
    current_price = info.get('currentPrice') or info.get('regularMarketPrice')
    
    # Generate historical data
    print("  Fetching 12-month history...")
    ultimos_12m = generate_weekly_data(ticker_symbol, '1y')
    
    print("  Fetching 6-month history...")
    ultimos_6m = generate_weekly_data(ticker_symbol, '6mo')
    
    # Get today's price and add to both lists if not already there
    today = datetime.now().strftime("%Y-%m-%d")
    
    metrics = {
        "ticker": ticker_symbol,
        "fecha": today,
        "precio_actual": current_price,
        "precios_historicos": {
            "ultimos_6m": ultimos_6m,
            "ultimos_12m": ultimos_12m
        },
        "valuations": generate_valuations(ticker_symbol),
        "performance": generate_performance(ticker_symbol),
        "sector_comparison": generate_sector_comparison(ticker_symbol)
    }
    
    return metrics


def save_metrics(ticker_symbol, metrics):
    """Save metrics to evaluaciones/{ticker}/raw-search/metrics.json"""
    
    output_dir = Path("evaluaciones") / ticker_symbol / "raw-search"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "metrics.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    
    print(f"Metrics saved to: {output_file}")
    
    # Print summary
    ultimos_12m = metrics['precios_historicos']['ultimos_12m']
    ultimos_6m = metrics['precios_historicos']['ultimos_6m']
    
    if ultimos_12m:
        print(f"\n12-month data: {len(ultimos_12m)} weekly points")
        print(f"  From: {ultimos_12m[0]['date']} (${ultimos_12m[0]['close']})")
        print(f"  To:   {ultimos_12m[-1]['date']} (${ultimos_12m[-1]['close']})")
    
    if ultimos_6m:
        print(f"\n6-month data: {len(ultimos_6m)} weekly points")
        print(f"  From: {ultimos_6m[0]['date']} (${ultimos_6m[0]['close']})")
        print(f"  To:   {ultimos_6m[-1]['date']} (${ultimos_6m[-1]['close']})")


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_metrics_from_yfinance.py TICKER [TICKER2 ...]")
        print("Example: python generate_metrics_from_yfinance.py NVDA REP.MC")
        sys.exit(1)
    
    tickers = sys.argv[1:]
    
    for ticker in tickers:
        print(f"\nProcessing {ticker}...")
        try:
            metrics = generate_metrics(ticker)
            save_metrics(ticker, metrics)
            print(f"Success: {ticker}\n")
        except Exception as e:
            print(f"Error processing {ticker}: {e}\n")


if __name__ == "__main__":
    main()
