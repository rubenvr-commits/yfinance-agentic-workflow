"""FastAPI main application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.routes import health, reports
from app.config import DEBUG

app = FastAPI(
    title="Financial Reports API",
    description="API for financial reports and analysis",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(reports.router)

# Serve static files (frontend)
static_dir = Path(__file__).parent.parent / "web"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="web")


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Financial Reports API - Use /docs for API documentation"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=DEBUG)
