#!/usr/bin/env python
"""Run FastAPI development server."""

import uvicorn
from app.main import app

if __name__ == "__main__":
    print("Starting Financial Reports API...")
    print("Visit http://localhost:8000 for the frontend")
    print("Visit http://localhost:8000/docs for API documentation")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
