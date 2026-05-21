"""Report endpoints."""

from fastapi import APIRouter, HTTPException, Response
from typing import Optional

from app.models import ReportStatus, ReportResponse, GenerationStatus, GenerationResult
from app.services.report_service import get_report_status, get_report_data, get_price_history
from app.services.generation_service import trigger_generation, get_generation_progress
from app.services.csv_service import generate_price_csv

router = APIRouter(prefix="/api/reports", tags=["reports"])


def validate_ticker(ticker: str) -> str:
    """Validate and normalize ticker."""
    if not ticker or not all(c.isalnum() or c == '.' for c in ticker):
        raise HTTPException(status_code=400, detail="Invalid ticker format")
    return ticker.upper()


@router.get("/{ticker}/status", response_model=ReportStatus)
async def get_report_status_endpoint(ticker: str):
    """Get report status for a ticker."""
    ticker = validate_ticker(ticker)
    status = get_report_status(ticker)
    return status


@router.get("/{ticker}", response_model=ReportResponse)
async def get_report_endpoint(ticker: str):
    """Get full report content and metadata."""
    ticker = validate_ticker(ticker)
    
    data = get_report_data(ticker)
    if not data:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return data


@router.post("/{ticker}/generate", response_model=GenerationStatus)
async def generate_report_endpoint(ticker: str):
    """Trigger report generation."""
    ticker = validate_ticker(ticker)
    
    result = await trigger_generation(ticker)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message"))
    
    return result


@router.get("/{ticker}/generate/progress", response_model=GenerationStatus)
async def get_generation_progress_endpoint(ticker: str):
    """Get generation progress."""
    ticker = validate_ticker(ticker)
    
    progress = await get_generation_progress(ticker)
    return progress


@router.get("/{ticker}/precios.csv")
async def export_prices_csv(ticker: str):
    """Export price history as CSV."""
    ticker = validate_ticker(ticker)
    
    csv_data = generate_price_csv(ticker)
    if not csv_data:
        raise HTTPException(status_code=404, detail="Price history not found")
    
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={ticker}_precios.csv"}
    )


@router.get("/{ticker}/charts-data")
async def get_charts_data(ticker: str):
    """Get data for chart rendering."""
    ticker = validate_ticker(ticker)
    
    data = get_report_data(ticker)
    if not data or not data.get("metrics"):
        raise HTTPException(status_code=404, detail="Metrics data not found")
    
    return data["metrics"]
