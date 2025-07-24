import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_sql_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Step 1: Define connection strings for three SQLite databases
db_names = ["sqlite:///db/blinkit.db", "sqlite:///db/zepto.db", "sqlite:///db/instamart.db"]
db_labels = ["blinkit", "zepto", "instamart"]

# Step 3: Initialize the LLM (using OpenAI as an example; replace with your preferred LLM)
print("Step 2: Initializing LLM...")

# Check if OPENAI_API_KEY is set
if not os.getenv("OPENAI_API_KEY"):
    print("⚠️  Warning: OPENAI_API_KEY not found in environment variables.")
    print("Please set your OpenAI API key in a .env file or environment variable.")
    print("Example .env file content:")
    print("OPENAI_API_KEY=your_api_key_here")
    exit(1)

# Initialize the LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

print("✅ LLM initialized successfully!")

# Step 4: Create the SQLDatabaseToolkit
print("Step 3: Creating SQL Database Toolkits...")

# Create SQLDatabase objects for each database
sql_databases = {}
toolkits = {}

for i, (db_name, label) in enumerate(zip(db_names, db_labels)):
    try:
        # Create SQLDatabase object
        sql_db = SQLDatabase.from_uri(db_name)
        print(f"✅ Created SQLDatabase object for {label} database")
        sql_databases[label] = sql_db
        
        # Create toolkit for this database
        toolkit = SQLDatabaseToolkit(db=sql_db, llm=llm)
        toolkits[label] = toolkit
        
        print(f"✅ Created toolkit for {label} database")
    except Exception as e:
        print(f"❌ Error creating toolkit for {label}: {e}")

# Step 5: Create the SQL agent
print("Step 4: Creating Multi-Database SQL Agent...")

def create_multi_db_agent():
    """Create an agent that can work with multiple databases"""
    
    # Create custom tools for each database
    tools = []
    
    for platform, db in sql_databases.items():
        # Query tool for each database
        def create_query_tool(platform_name, database):
            def query_database(query: str) -> str:
                """Execute SQL query on the specified database"""
                try:
                    result = database.run(query)
                    return f"Results from {platform_name} database:\n{result}"
                except Exception as e:
                    return f"Error querying {platform_name} database: {str(e)}"
            return query_database
        
        query_tool = Tool(
            name=f"query_{platform}_database",
            description=f"Execute SQL queries on the {platform} database. Input should be a valid SQL query string. Use this to query {platform} products, stores, categories, and platform info.",
            func=create_query_tool(platform, db)
        )
        tools.append(query_tool)
        
        # Schema info tool for each database
        def create_schema_tool(platform_name, database):
            def get_schema() -> str:
                """Get database schema information"""
                try:
                    return f"Schema for {platform_name} database:\n{database.get_table_info()}"
                except Exception as e:
                    return f"Error getting schema for {platform_name}: {str(e)}"
            return get_schema
        
        schema_tool = Tool(
            name=f"get_{platform}_schema",
            description=f"Get the database schema and table information for {platform} database. Use this to understand table structure before writing queries.",
            func=create_schema_tool(platform, db)
        )
        tools.append(schema_tool)
    
    # Create a comparison tool
    def compare_across_platforms(product_name: str) -> str:
        """Compare product prices across all platforms"""
        results = []
        for platform, db in sql_databases.items():
            try:
                query = f"SELECT name, price, stock FROM {platform}_products WHERE name LIKE '%{product_name}%' LIMIT 5"
                result = db.run(query)
                results.append(f"{platform.upper()}:\n{result}")
            except Exception as e:
                results.append(f"{platform.upper()}: Error - {str(e)}")
        
        return "\n\n".join(results)
    
    comparison_tool = Tool(
        name="compare_product_prices",
        description="Compare product prices and availability across all three platforms (blinkit, zepto, instamart). Input should be a product name.",
        func=compare_across_platforms
    )
    tools.append(comparison_tool)
    
    # Create the agent with all tools
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.OPENAI_FUNCTIONS,
        verbose=True,
        max_iterations=10,
        early_stopping_method="generate"
    )
    
    return agent

try:
    agent = create_multi_db_agent()
    print("✅ Multi-Database SQL Agent created successfully!")
except Exception as e:
    print(f"❌ Error creating SQL agent: {e}")
    exit(1)

# Step 6: Test the agent with a query
print("Step 5: Testing the agent with sample queries...")

def test_agent():
    """Test the agent with various queries"""
    
    test_queries = [
        "Show me the schema for blinkit database",
        "Compare the price of Apple across all platforms",
        "What is the cheapest price for Milk 1L across all platforms?",
        # "Which platform has the fastest delivery time?",
        # "Show me the top 5 most expensive products across all platforms",
    ]
    
    print("\n🧪 Running test queries...\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"Query {i}: {query}")
        print("-" * 50)
        
        try:
            result = agent.run(query)
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")
        
        print("\n" + "="*70 + "\n")

def interactive_mode():
    """Run the agent in interactive mode"""
    print("\n🚀 Multi-Database SQL Agent is ready! Enter your queries (type 'quit' to exit):")
    print("You can ask questions about products, prices, stores, and delivery times across Blinkit, Zepto, and Instamart.")
    print("\nExample queries:")
    print("- 'Compare prices of Apple across all platforms'")
    print("- 'Which stores are available in Delhi?'")
    print("- 'What are the delivery times for each platform?'")
    print("- 'Show me all products in the Dairy category'")
    print("- 'Find the cheapest Milk 1L across all platforms'")
    print("-" * 70)
    
    while True:
        try:
            user_query = input("\n💬 Your query: ").strip()
            
            if user_query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_query:
                continue
                
            print(f"\n🤔 Processing: {user_query}")
            print("-" * 50)
            
            result = agent.run(user_query)
            print(f"\n✅ Result:\n{result}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    # Run test queries first
    test_agent()
    
    # Then start interactive mode
    interactive_mode()


