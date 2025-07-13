"""Main FastAPI application for Quick Commerce Deals platform."""

import logging
import time
from typing import List, Dict, Optional, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database.database import get_db
from app.agents.sql_agent import sql_agent, QueryResult
from app.api.routes import router as api_router

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level))
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered price comparison platform for quick commerce apps",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security
security = HTTPBearer()

# Pydantic models
class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language query")
    max_results: int = Field(default=50, ge=1, le=1000, description="Maximum number of results")
    use_cache: bool = Field(default=True, description="Whether to use cached results")
    include_metadata: bool = Field(default=False, description="Include query metadata in response")

class QueryResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]]
    message: str
    execution_time: float
    rows_returned: int
    cached: bool = False
    query_plan: Optional[Dict[str, Any]] = None
    generated_sql: Optional[str] = None

class ProductSearchRequest(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    platform: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    discount_min: Optional[float] = None
    limit: int = Field(default=50, ge=1, le=1000)

class PriceComparisonRequest(BaseModel):
    product_name: str
    platforms: Optional[List[str]] = None
    include_discounts: bool = True

class DealsRequest(BaseModel):
    min_discount_percentage: Optional[float] = None
    platform: Optional[str] = None
    category: Optional[str] = None
    limit: int = Field(default=50, ge=1, le=1000)

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    database_connected: bool
    agent_initialized: bool

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint serving the main web interface."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Quick Commerce Deals - AI-Powered Price Comparison</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
                line-height: 1.6;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                text-align: center;
                color: white;
                margin-bottom: 40px;
            }
            .header h1 {
                font-size: 3rem;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .header p {
                font-size: 1.2rem;
                opacity: 0.9;
            }
            .search-section {
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }
            .search-box {
                display: flex;
                gap: 15px;
                margin-bottom: 20px;
            }
            .search-input {
                flex: 1;
                padding: 15px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 16px;
                transition: border-color 0.3s;
            }
            .search-input:focus {
                outline: none;
                border-color: #667eea;
            }
            .search-btn {
                padding: 15px 30px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;
                transition: background 0.3s;
            }
            .search-btn:hover {
                background: #5a6fd8;
            }
            .examples {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }
            .example-query {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #667eea;
                cursor: pointer;
                transition: all 0.3s;
            }
            .example-query:hover {
                background: #e9ecef;
                transform: translateY(-2px);
            }
            .results-section {
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                margin-bottom: 30px;
                display: none;
            }
            .loading {
                text-align: center;
                padding: 50px;
                color: #666;
            }
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .result-item {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 15px;
                border-left: 4px solid #28a745;
            }
            .result-item h3 {
                color: #333;
                margin-bottom: 10px;
            }
            .result-item .price {
                font-size: 1.5rem;
                font-weight: bold;
                color: #28a745;
                margin-bottom: 10px;
            }
            .result-item .platform {
                background: #667eea;
                color: white;
                padding: 5px 10px;
                border-radius: 20px;
                font-size: 0.9rem;
                display: inline-block;
                margin-bottom: 10px;
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }
            .feature-card {
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                text-align: center;
            }
            .feature-card h3 {
                color: #667eea;
                margin-bottom: 15px;
            }
            .api-section {
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                margin-top: 30px;
            }
            .api-section h2 {
                color: #333;
                margin-bottom: 20px;
            }
            .api-endpoint {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 15px;
                border-left: 4px solid #667eea;
            }
            .api-endpoint code {
                background: #e9ecef;
                padding: 2px 5px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }
            .footer {
                text-align: center;
                color: white;
                margin-top: 50px;
                opacity: 0.8;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🛒 Quick Commerce Deals</h1>
                <p>AI-Powered Price Comparison Across Multiple Platforms</p>
            </div>
            
            <div class="search-section">
                <h2>Ask anything about prices, products, or deals!</h2>
                <div class="search-box">
                    <input type="text" class="search-input" id="queryInput" placeholder="E.g., Which app has cheapest onions right now?">
                    <button class="search-btn" onclick="searchQuery()">Search</button>
                </div>
                
                <div class="examples">
                    <div class="example-query" onclick="setQuery('Which app has cheapest onions right now?')">
                        🧅 Which app has cheapest onions right now?
                    </div>
                    <div class="example-query" onclick="setQuery('Show products with 30% discount on Blinkit')">
                        🏷️ Show products with 30% discount on Blinkit
                    </div>
                    <div class="example-query" onclick="setQuery('Compare fruit prices between Zepto and Instamart')">
                        🍎 Compare fruit prices between Zepto and Instamart
                    </div>
                    <div class="example-query" onclick="setQuery('Find best deals for ₹1000 grocery list')">
                        🛍️ Find best deals for ₹1000 grocery list
                    </div>
                </div>
            </div>
            
            <div class="results-section" id="resultsSection">
                <h2>Search Results</h2>
                <div id="resultsContent"></div>
            </div>
            
            <div class="features">
                <div class="feature-card">
                    <h3>🤖 AI-Powered Queries</h3>
                    <p>Ask questions in natural language and get intelligent responses using advanced SQL agent technology.</p>
                </div>
                <div class="feature-card">
                    <h3>🔍 Smart Table Selection</h3>
                    <p>Automatically selects optimal tables from 50+ database tables for efficient query processing.</p>
                </div>
                <div class="feature-card">
                    <h3>⚡ Real-Time Pricing</h3>
                    <p>Get up-to-date pricing information across multiple quick commerce platforms.</p>
                </div>
                <div class="feature-card">
                    <h3>🏷️ Deal Discovery</h3>
                    <p>Find the best discounts, offers, and deals automatically across all platforms.</p>
                </div>
            </div>
            
            <div class="api-section">
                <h2>API Endpoints</h2>
                <div class="api-endpoint">
                    <strong>POST /api/v1/query</strong><br>
                    Natural language query processing<br>
                    <code>{"query": "cheapest onions", "max_results": 10}</code>
                </div>
                <div class="api-endpoint">
                    <strong>GET /api/v1/products</strong><br>
                    Product search and filtering<br>
                    <code>?name=onion&platform=blinkit&limit=20</code>
                </div>
                <div class="api-endpoint">
                    <strong>GET /api/v1/deals</strong><br>
                    Current deals and discounts<br>
                    <code>?min_discount_percentage=30&platform=zepto</code>
                </div>
                <div class="api-endpoint">
                    <strong>POST /api/v1/compare</strong><br>
                    Price comparison across platforms<br>
                    <code>{"product_name": "onion", "platforms": ["blinkit", "zepto"]}</code>
                </div>
            </div>
            
            <div class="footer">
                <p>&copy; 2024 Quick Commerce Deals. Powered by AI and advanced query optimization.</p>
            </div>
        </div>
        
        <script>
            function setQuery(query) {
                document.getElementById('queryInput').value = query;
            }
            
            async function searchQuery() {
                const query = document.getElementById('queryInput').value;
                if (!query.trim()) {
                    alert('Please enter a query');
                    return;
                }
                
                const resultsSection = document.getElementById('resultsSection');
                const resultsContent = document.getElementById('resultsContent');
                
                // Show loading
                resultsSection.style.display = 'block';
                resultsContent.innerHTML = `
                    <div class="loading">
                        <div class="spinner"></div>
                        <p>Processing your query...</p>
                    </div>
                `;
                
                try {
                    const response = await fetch('/api/v1/query', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            query: query,
                            max_results: 20,
                            use_cache: true,
                            include_metadata: true
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        displayResults(data);
                    } else {
                        resultsContent.innerHTML = `
                            <div class="result-item" style="border-left-color: #dc3545;">
                                <h3>Error</h3>
                                <p>${data.message}</p>
                            </div>
                        `;
                    }
                } catch (error) {
                    resultsContent.innerHTML = `
                        <div class="result-item" style="border-left-color: #dc3545;">
                            <h3>Error</h3>
                            <p>Failed to process query: ${error.message}</p>
                        </div>
                    `;
                }
            }
            
            function displayResults(data) {
                const resultsContent = document.getElementById('resultsContent');
                
                if (data.data.length === 0) {
                    resultsContent.innerHTML = `
                        <div class="result-item">
                            <h3>No Results Found</h3>
                            <p>Try a different query or check the spelling.</p>
                        </div>
                    `;
                    return;
                }
                
                let html = '';
                
                // Add metadata if available
                if (data.cached) {
                    html += `
                        <div class="result-item" style="border-left-color: #17a2b8;">
                            <h3>ℹ️ Query Information</h3>
                            <p><strong>Cached result:</strong> Yes</p>
                            <p><strong>Execution time:</strong> ${data.execution_time.toFixed(3)}s</p>
                            <p><strong>Results:</strong> ${data.rows_returned} rows</p>
                        </div>
                    `;
                }
                
                // Add results
                data.data.forEach(item => {
                    html += `
                        <div class="result-item">
                            ${item.product_name ? `<h3>${item.product_name}</h3>` : ''}
                            ${item.platform_name ? `<div class="platform">${item.platform_name}</div>` : ''}
                            ${item.sale_price ? `<div class="price">₹${item.sale_price}</div>` : ''}
                            ${item.regular_price && item.sale_price !== item.regular_price ? `<p>Regular Price: ₹${item.regular_price}</p>` : ''}
                            ${item.discount_percentage ? `<p>Discount: ${item.discount_percentage}%</p>` : ''}
                            ${item.category_name ? `<p>Category: ${item.category_name}</p>` : ''}
                            ${item.brand_name ? `<p>Brand: ${item.brand_name}</p>` : ''}
                            ${item.quantity_available ? `<p>Stock: ${item.quantity_available} units</p>` : ''}
                            ${item.view_count ? `<p>Views: ${item.view_count}</p>` : ''}
                            ${item.response ? `<p>${item.response}</p>` : ''}
                        </div>
                    `;
                });
                
                resultsContent.innerHTML = html;
            }
            
            // Allow Enter key to search
            document.getElementById('queryInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    searchQuery();
                }
            });
        </script>
    </body>
    </html>
    """

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Check database connection
        with next(get_db()) as db:
            db.execute("SELECT 1")
        db_connected = True
    except Exception:
        db_connected = False
    
    return HealthResponse(
        status="healthy" if db_connected else "unhealthy",
        timestamp=datetime.now(),
        version=settings.app_version,
        database_connected=db_connected,
        agent_initialized=sql_agent.agent is not None
    )

# Main query endpoint
@app.post("/api/v1/query", response_model=QueryResponse)
@limiter.limit(f"{settings.rate_limit_requests_per_minute}/minute")
async def process_query(
    request: QueryRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Process natural language queries."""
    try:
        start_time = time.time()
        
        # Process query with SQL agent
        result = sql_agent.process_query(
            natural_language_query=request.query,
            use_cache=request.use_cache,
            max_results=request.max_results
        )
        
        # Log query for analytics
        background_tasks.add_task(
            log_query_analytics,
            query=request.query,
            success=result.success,
            execution_time=result.execution_time,
            rows_returned=result.rows_returned
        )
        
        # Prepare response
        response = QueryResponse(
            success=result.success,
            data=result.data,
            message="Query processed successfully" if result.success else result.error_message,
            execution_time=result.execution_time,
            rows_returned=result.rows_returned,
            cached=result.cached
        )
        
        # Include metadata if requested
        if request.include_metadata and result.query_plan:
            response.query_plan = {
                "query_type": result.query_plan.query_type.value,
                "selected_tables": result.query_plan.selected_tables,
                "estimated_cost": result.query_plan.estimated_cost,
                "steps": len(result.query_plan.steps)
            }
            response.generated_sql = result.generated_sql
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Performance metrics endpoint
@app.get("/api/v1/metrics")
async def get_metrics():
    """Get performance metrics."""
    try:
        return sql_agent.get_performance_metrics()
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Clear cache endpoint
@app.post("/api/v1/cache/clear")
async def clear_cache():
    """Clear query cache."""
    try:
        sql_agent.clear_cache()
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Table suggestions endpoint
@app.get("/api/v1/tables/suggest")
async def get_table_suggestions(query: str = Query(..., description="Query to analyze")):
    """Get table suggestions for a query."""
    try:
        suggestions = sql_agent.get_table_suggestions(query)
        return {"suggestions": suggestions}
    except Exception as e:
        logger.error(f"Error getting table suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Column suggestions endpoint
@app.get("/api/v1/columns/suggest")
async def get_column_suggestions(query: str = Query(..., description="Query to analyze")):
    """Get column suggestions for a query."""
    try:
        suggestions = sql_agent.get_column_suggestions(query)
        return {"suggestions": suggestions}
    except Exception as e:
        logger.error(f"Error getting column suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background task for logging
async def log_query_analytics(query: str, success: bool, execution_time: float, rows_returned: int):
    """Log query analytics to database."""
    try:
        with next(get_db()) as db:
            # This would insert into search_queries table
            # For now, just log to console
            logger.info(f"Query logged: {query[:50]}... | Success: {success} | Time: {execution_time:.3f}s | Rows: {rows_returned}")
    except Exception as e:
        logger.error(f"Error logging query analytics: {e}")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": "Endpoint not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"}
    )

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Database URL: {settings.database_url}")
    logger.info(f"Debug mode: {settings.debug}")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info(f"Shutting down {settings.app_name}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.debug) 