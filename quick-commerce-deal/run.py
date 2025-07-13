#!/usr/bin/env python3
"""Simple run script for Quick Commerce Deals platform."""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

if __name__ == "__main__":
    import uvicorn
    from app.main import app
    
    print("🚀 Starting Quick Commerce Deals platform...")
    print("📊 Database: SQLite")
    print("🤖 AI-Powered SQL Agent: Ready")
    print("🌐 Web Interface: http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")
    print()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 