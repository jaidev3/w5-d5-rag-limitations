#!/usr/bin/env python3
"""Setup script for Quick Commerce Deals platform."""

import os
import sys
import logging
import subprocess
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 9):
        logger.error("Python 3.9 or higher is required")
        sys.exit(1)
    logger.info(f"Python version: {sys.version}")

def install_dependencies():
    """Install required Python packages."""
    logger.info("Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        logger.info("Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        sys.exit(1)

def create_directories():
    """Create necessary directories."""
    directories = [
        "static",
        "templates", 
        "logs",
        "data",
        "tests"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.info(f"Created directory: {directory}")

def setup_database():
    """Initialize database and create tables."""
    logger.info("Setting up database...")
    try:
        # Set PYTHONPATH to include the app directory
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.join(os.getcwd(), 'app')
        
        # Create database tables
        subprocess.run([sys.executable, "-m", "app.database.init_db"], 
                      env=env, check=True)
        logger.info("Database tables created successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to create database tables: {e}")
        sys.exit(1)

def generate_sample_data():
    """Generate sample data for testing."""
    logger.info("Generating sample data...")
    try:
        # Set PYTHONPATH to include the app directory
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.join(os.getcwd(), 'app')
        
        # Generate sample data
        subprocess.run([sys.executable, "-m", "app.data.generate_sample_data", "medium"], 
                      env=env, check=True)
        logger.info("Sample data generated successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to generate sample data: {e}")
        logger.warning("Continuing without sample data...")

def create_env_file():
    """Create .env file with default settings."""
    env_content = """# Database Configuration
DATABASE_URL=sqlite:///./quick_commerce.db
DATABASE_ECHO=false

# OpenAI Configuration (optional)
OPENAI_API_KEY=your_openai_api_key_here

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your_secret_key_change_this_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=100

# Application Settings
APP_NAME=Quick Commerce Deals
APP_VERSION=0.1.0
DEBUG=true
LOG_LEVEL=INFO

# Data Generation
GENERATE_SAMPLE_DATA=true
SAMPLE_DATA_SIZE=medium

# Performance
QUERY_CACHE_EXPIRE_SECONDS=300
MAX_QUERY_RESULTS=1000
ENABLE_QUERY_MONITORING=true
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        logger.info("Created .env file with default settings")
    else:
        logger.info(".env file already exists")

def run_tests():
    """Run basic tests to verify setup."""
    logger.info("Running basic tests...")
    try:
        # Test database connection
        from app.database.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM platforms"))
            count = result.scalar()
            logger.info(f"Database connection successful. Found {count} platforms.")
        
        # Test SQL agent initialization
        from app.agents.sql_agent import sql_agent
        if sql_agent:
            logger.info("SQL Agent initialized successfully")
        else:
            logger.warning("SQL Agent not initialized (OpenAI key may be missing)")
        
        logger.info("All tests passed!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        logger.warning("Setup may have issues, but continuing...")

def print_startup_instructions():
    """Print instructions for starting the application."""
    instructions = """
🎉 Setup Complete!

To start the Quick Commerce Deals platform:

1. Activate your virtual environment (if using one):
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate

2. Start the application:
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

3. Open your browser and go to:
   http://localhost:8000

4. Try some example queries:
   - "Which app has cheapest onions right now?"
   - "Show products with 30% discount on Blinkit"
   - "Compare fruit prices between Zepto and Instamart"

5. API Documentation:
   - OpenAPI docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

6. For better AI responses, add your OpenAI API key to .env:
   OPENAI_API_KEY=your_actual_api_key_here

📊 Database Schema:
- 50+ tables for comprehensive data modeling
- Intelligent table selection and query optimization
- Real-time price tracking and comparison

🤖 AI Features:
- Natural language query processing
- Intelligent table selection from 50+ tables
- Multi-step query generation with validation
- Performance optimization and caching

🚀 Ready to explore price comparison with AI!
"""
    
    print(instructions)

def main():
    """Main setup function."""
    logger.info("Starting Quick Commerce Deals platform setup...")
    
    # Check system requirements
    check_python_version()
    
    # Setup steps
    create_directories()
    create_env_file()
    install_dependencies()
    setup_database()
    generate_sample_data()
    run_tests()
    
    # Print completion message
    logger.info("Setup completed successfully!")
    print_startup_instructions()

if __name__ == "__main__":
    main() 