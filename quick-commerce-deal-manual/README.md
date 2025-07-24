# Quick Commerce SQL Agent

A multi-database SQL agent system that can query and analyze data across three quick commerce platforms: **Blinkit**, **Zepto**, and **Instamart**.

## Features

- 🚀 **Multi-Database Support**: Query across three separate SQLite databases
- 🤖 **Intelligent SQL Agent**: Natural language to SQL conversion using LangChain
- 🔍 **Cross-Platform Analysis**: Compare products, prices, and delivery times across platforms
- 💬 **Interactive Mode**: Chat-like interface for querying data
- 📊 **Comprehensive Data**: Product catalogs, store locations, pricing, and platform information

## Database Schema

Each platform has its own database with the following tables:
- `{platform}_platform_info`: Platform delivery times and information
- `{platform}_categories`: Product categories with hierarchical structure
- `{platform}_stores`: Store locations with city and pincode
- `{platform}_products`: Product catalog with pricing and stock information

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root (you can copy from `env_example.txt`):

```bash
cp env_example.txt .env
```

Edit the `.env` file and add your OpenAI API key:

```
OPENAI_API_KEY=your_actual_openai_api_key_here
```

### 3. Run the Application

```bash
python main.py
```

The application will:
1. Initialize the databases with schema and sample data
2. Set up the LLM and SQL agent
3. Run test queries to verify functionality
4. Start interactive mode for custom queries

## Usage Examples

### Sample Queries

The system can handle various types of queries:

**Product Comparison:**
```
Compare the price of Milk 1L across all three platforms
```

**Store Information:**
```
Which stores are available in Delhi?
```

**Platform Analysis:**
```
Which platform has the fastest delivery time?
```

**Category Exploration:**
```
What products are available in the Dairy category?
```

**Price Analysis:**
```
Show me the top 5 most expensive products across all platforms
```

### Interactive Mode

After running the initial tests, the application enters interactive mode where you can:
- Ask questions in natural language
- Get SQL query results formatted as readable answers
- Compare data across all three platforms
- Explore product catalogs, pricing, and store information

Type `quit`, `exit`, or `q` to exit the interactive mode.

## Project Structure

```
quick-commerce-deal-manual/
├── main.py                     # Main application entry point
├── sql_agent.py               # SQL agent utilities (optional)
├── streamlit_app.py           # Streamlit web interface (optional)
├── requirements.txt           # Python dependencies
├── env_example.txt           # Environment variables template
├── README.md                 # This file
├── db/                       # SQLite database files
│   ├── blinkit.db
│   ├── zepto.db
│   └── instamart.db
└── scripts/                  # Database management scripts
    ├── apply_schema.py       # Apply database schema
    ├── clean_and_apply_schema.py  # Clean and reapply schema
    └── add_data.py          # Populate with sample data
```

## Database Management

### Reset Databases

To clean and reinitialize all databases:

```bash
python scripts/clean_and_apply_schema.py
python scripts/add_data.py
```

### Add More Data

You can modify the sample data in `scripts/add_data.py` and run:

```bash
python scripts/add_data.py
```

## Troubleshooting

### Common Issues

1. **Missing OpenAI API Key**
   - Ensure your `.env` file contains a valid `OPENAI_API_KEY`
   - Check that the API key has sufficient credits

2. **Database Errors**
   - Run the database reset commands above
   - Ensure the `db/` directory exists and is writable

3. **Import Errors**
   - Verify all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version compatibility (3.8+ recommended)

### Debug Mode

For more detailed logging, you can modify the `verbose=True` parameter in the agent creation or add debug prints throughout the code.

## Sample Data

The system includes sample data for:
- **12 common products** across all platforms (Apple, Milk, Chips, etc.)
- **5 stores per platform** in major Indian cities
- **10 product categories** per platform
- **Platform-specific pricing** and delivery times

## Extensions

The system can be extended to:
- Add more platforms or databases
- Include order history and customer data
- Implement real-time data synchronization
- Add web interface using the included Streamlit app
- Integrate with actual platform APIs

## License

This project is for educational and demonstration purposes. 