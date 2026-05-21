"""CSV export service."""

import io
from typing import Optional
from app.services.report_service import get_price_history


def generate_price_csv(ticker: str) -> Optional[str]:
    """
    Generate CSV from price history.
    Returns CSV string with columns: Date,Close
    """
    
    history = get_price_history(ticker)
    if not history:
        return None
    
    csv_buffer = io.StringIO()
    csv_buffer.write("Date,Close\n")
    
    for entry in sorted(history, key=lambda x: x["date"]):
        csv_buffer.write(f"{entry['date']},{entry['close']}\n")
    
    return csv_buffer.getvalue()
