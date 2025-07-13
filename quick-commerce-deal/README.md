# Quick Commerce Deals Platform

A comprehensive price comparison platform for quick commerce apps (Blinkit, Zepto, Instamart, BigBasket Now, etc.) with AI-powered natural language query capabilities.

## Features

- **Multi-Platform Price Tracking**: Real-time price monitoring across multiple quick commerce platforms
- **AI-Powered SQL Agent**: Natural language query processing with intelligent table selection
- **Comprehensive Database Schema**: 50+ tables for products, prices, discounts, availability, and platform data
- **Performance Optimization**: Query caching, connection pooling, and optimization strategies
- **Real-time Updates**: Simulated real-time price updates with dummy data
- **Security**: Rate limiting, authentication, and basic security measures
- **Web Interface**: FastAPI-based REST API with web interface

## Architecture

### Database Schema
- **Products**: Categories, subcategories, brands, variants, nutritional info
- **Platforms**: Quick commerce apps, stores, delivery zones
- **Pricing**: Current prices, historical data, discounts, offers
- **Inventory**: Stock levels, availability, delivery times
- **Users**: Customer data, preferences, order history
- **Analytics**: Search patterns, popular products, performance metrics

### SQL Agent
- **Intelligent Query Processing**: LangChain-powered natural language to SQL conversion
- **Multi-Step Query Generation**: Complex query breakdown with validation
- **Table Selection**: Semantic indexing for optimal table selection from 50+ tables
- **Query Optimization**: Automatic query planning and optimization

### Performance Features
- **Semantic Indexing**: Fast table discovery and selection
- **Query Caching**: Redis-based result caching
- **Connection Pooling**: Efficient database connections
- **Pagination**: Statistical sampling for large result sets

## Quick Start

### Prerequisites
- Python 3.8+
- SQLite (included with Python)
- OpenAI API key (for AI features)

### Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd quick-commerce-deal
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   # Create .env file in project root
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   echo "DATABASE_URL=sqlite:///./quick_commerce.db" >> .env
   echo "LOG_LEVEL=INFO" >> .env
   ```

5. **Initialize database**:
   ```bash
   python -m app.database.init_db
   ```

6. **Generate sample data**:
   ```bash
   python -m app.data.generate_sample_data
   ```

### Running the Application

**Option 1: Using the run script (Recommended)**
```bash
python run.py
```

**Option 2: Using uvicorn directly**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Option 3: Using the main module**
```bash
python -m app.main
```

After starting the server, you can access:
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Core Endpoints

#### Health & Status
- `GET /health` - Health check with system status
- `GET /api/v1/metrics` - System metrics and performance data
- `GET /api/v1/stats` - Platform statistics (products, platforms, categories count)

#### AI-Powered Query Processing
- `POST /api/v1/query` - **Main AI endpoint** - Process natural language queries
  ```json
  {
    "query": "Which app has cheapest onions right now?",
    "max_results": 50,
    "use_cache": true,
    "include_metadata": false
  }
  ```

#### Product Management
- `GET /products` - Get products with advanced filtering
  - **Query Parameters**: `name`, `category`, `brand`, `platform`, `min_price`, `max_price`, `discount_min`, `sort_by`, `limit`, `offset`
- `GET /products/{product_id}` - Get specific product details
- `GET /search` - Search products using natural language
  - **Query Parameters**: `q` (search query), `limit`

#### Platform Information
- `GET /platforms` - Get all quick commerce platforms
  - **Query Parameters**: `active_only` (default: true)

#### Deals & Discounts
- `GET /deals` - Get current deals and discounts
  - **Query Parameters**: `min_discount_percentage`, `platform`, `category`, `limit`

#### Price Comparison
- `POST /compare` - Compare prices across platforms
  ```json
  {
    "product_name": "Onions",
    "platforms": ["blinkit", "zepto", "instamart"],
    "include_discounts": true
  }
  ```

#### Popular Products
- `GET /popular` - Get trending/popular products
  - **Query Parameters**: `limit`, `platform`

#### Categories & Brands
- `GET /categories` - Get all product categories
- `GET /brands` - Get all available brands

#### Cache Management
- `POST /api/v1/cache/clear` - Clear query cache

#### AI Assistant Features
- `GET /api/v1/tables/suggest` - Get table suggestions for query optimization
- `GET /api/v1/columns/suggest` - Get column suggestions for query building

### Response Format

All API responses follow this structure:
```json
{
  "success": true,
  "data": [...],
  "message": "Operation completed successfully",
  "execution_time": 0.123,
  "rows_returned": 25,
  "cached": false
}
```

### Rate Limiting
- **Default**: 60 requests per minute per IP
- **Query endpoint**: Configurable rate limiting
- **Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## Sample Queries

### Natural Language Queries (POST /api/v1/query)
```bash
# Find cheapest products
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Which app has cheapest onions right now?"}'

# Discount-based queries
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Show products with 30%+ discount on Blinkit"}'

# Comparison queries
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Compare fruit prices between Zepto and Instamart"}'

# Budget-based queries
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Find best deals for ₹1000 grocery list"}'
```

### REST API Queries
```bash
# Get products with filters
curl "http://localhost:8000/products?category=fruits&min_price=10&max_price=100&sort_by=price"

# Compare prices
curl -X POST "http://localhost:8000/compare" \
  -H "Content-Type: application/json" \
  -d '{"product_name": "Bananas", "platforms": ["blinkit", "zepto"]}'

# Get deals
curl "http://localhost:8000/deals?min_discount_percentage=20&platform=blinkit"

# Search products
curl "http://localhost:8000/search?q=organic vegetables&limit=10"
```

## Technology Stack

- **Backend**: FastAPI, SQLAlchemy, SQLite
- **AI/ML**: LangChain, OpenAI
- **Caching**: Redis (optional)
- **Authentication**: JWT tokens
- **Rate Limiting**: SlowAPI
- **Data Generation**: Faker, Pandas
- **Testing**: Pytest
- **Documentation**: Swagger/OpenAPI

## Project Structure

```
quick-commerce-deal/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── database.py      # Database connection
│   │   └── init_db.py       # Database initialization
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── sql_agent.py     # Main SQL agent
│   │   ├── query_planner.py # Query planning and optimization
│   │   └── table_selector.py # Intelligent table selection
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py        # API routes
│   ├── data/
│   │   ├── __init__.py
│   │   └── generate_sample_data.py # Sample data generation
│   └── utils/
│       ├── __init__.py
│       └── helpers.py       # Helper functions
├── static/                  # Static files
├── templates/              # HTML templates
├── tests/                  # Test files
├── run.py                  # Application runner
├── requirements.txt        # Dependencies
├── quick_commerce.db       # SQLite database (generated)
└── README.md              # This file
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black app/
```

### Database Operations
```bash
# Reset database
python -m app.database.init_db --reset

# Generate fresh sample data
python -m app.data.generate_sample_data --fresh
```

### Environment Variables
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///./quick_commerce.db
LOG_LEVEL=INFO
RATE_LIMIT_REQUESTS_PER_MINUTE=60
APP_NAME=Quick Commerce Deals
APP_VERSION=1.0.0
```

## Troubleshooting

### Common Issues
1. **Database not found**: Run `python -m app.database.init_db`
2. **No sample data**: Run `python -m app.data.generate_sample_data`
3. **OpenAI API errors**: Check your API key in `.env` file
4. **Port already in use**: Change port in `run.py` or kill existing process

### Logs
Application logs are available in the console output. Adjust log level in `.env`:
```env
LOG_LEVEL=DEBUG  # For detailed logs
LOG_LEVEL=INFO   # For standard logs
LOG_LEVEL=ERROR  # For error logs only
```

## License

MIT License 