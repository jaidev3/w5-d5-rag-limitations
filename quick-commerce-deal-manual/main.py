import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_sql_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Step 1Define connection strings for three SQLite databases
db_names = ["sqlite:///db/blinkit.db", "sqlite:///db/zepto.db", "sqlite:///db/instamart.db"]
db_labels = ["blinkit", "zepto", "instamart"]

# Create engines for each database
engines = [create_engine(db_name) for db_name in db_names]

# Step 2: Create a session for each engine
sessions = [sessionmaker(engine) for engine in engines]

# Step 3: Initialize the LLM (using OpenAI as an example; replace with your preferred LLM)
print("Step 3: Initializing LLM...")

# Check if OPENAI_API_KEY is set
if not os.getenv("OPENAI_API_KEY"):
    print("⚠️  Warning: OPENAI_API_KEY not found in environment variables.")
    print("Please set your OpenAI API key in a .env file or environment variable.")
    print("Example .env file content:")
    print("OPENAI_API_KEY=your_api_key_here")
    exit(1)

# Initialize the LLM
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

print("✅ LLM initialized successfully!")

# Step 4: Create the SQLDatabaseToolkit
print("Step 4: Creating SQL Database Toolkits...")

# Create SQLDatabase objects for each database
sql_databases = []
toolkits = []

for i, (db_name, label) in enumerate(zip(db_names, db_labels)):
    try:
        # Create SQLDatabase object
        sql_db = SQLDatabase.from_uri(db_name)
        sql_databases.append(sql_db)
        
        # Create toolkit for this database
        toolkit = SQLDatabaseToolkit(db=sql_db, llm=llm)
        toolkits.append(toolkit)
        
        print(f"✅ Created toolkit for {label} database")
    except Exception as e:
        print(f"❌ Error creating toolkit for {label}: {e}")

# Step 5: Create the SQL agent
print("Step 5: Creating SQL Agent...")

def create_multi_db_agent():
    """Create an agent that can work with multiple databases"""
    
    # Combine all tools from all toolkits
    all_tools = []
    for i, toolkit in enumerate(toolkits):
        tools = toolkit.get_tools()
        # Rename tools to include database identifier
        for tool in tools:
            tool.name = f"{db_labels[i]}_{tool.name}"
            tool.description = f"[{db_labels[i].upper()} DB] {tool.description}"
        all_tools.extend(tools)
    
    # Create the agent with all tools
    agent = create_sql_agent(
        llm=llm,
        toolkit=toolkits[0],  # Use first toolkit as base
        verbose=True,
        agent_type="openai-tools",
        extra_tools=all_tools[len(toolkits[0].get_tools()):],  # Add tools from other databases
    )
    print(f"all_tools: {all_tools[len(toolkits[0].get_tools()):]}")

    return agent

try:
    agent = create_multi_db_agent()
    print("✅ SQL Agent created successfully!")
except Exception as e:
    print(f"❌ Error creating SQL agent: {e}")
    exit(1)

# Step 6: Test the agent with a query
print("Step 6: Testing the agent with sample queries...")

def test_agent():
    """Test the agent with various queries"""
    
    test_queries = [
        "List all tables in the blinkit database",
        # "What products are available in the Groceries category across all platforms?",
        # "Compare the price of Milk 1L across all three platforms",
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
    print("\n🚀 SQL Agent is ready! Enter your queries (type 'quit' to exit):")
    print("You can ask questions about products, prices, stores, and delivery times across Blinkit, Zepto, and Instamart.")
    print("\nExample queries:")
    print("- 'Compare prices of Apple across all platforms'")
    print("- 'Which stores are available in Delhi?'")
    print("- 'What are the delivery times for each platform?'")
    print("- 'Show me all products in the Dairy category'")
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


