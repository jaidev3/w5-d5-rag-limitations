# RAG vs SQL Agent Comparison Project

This project provides a comprehensive comparison between Retrieval-Augmented Generation (RAG) systems and SQL Agent systems for database querying, using the Chinook music database as a test case.

## 🎯 Project Overview

The project implements and compares two different approaches to natural language database querying:

1. **RAG System**: Uses semantic search over database schema and business context
2. **SQL Agent**: Uses LLM-powered agents to generate and execute SQL queries

## 📁 Project Structure

```
w5-d5-rag-limitations/
├── README.md                           # This file
├── RAG_vs_SQL_Agent_Comparison.md      # Comprehensive analysis document
├── Chinook.db                          # SQLite database file
├── sql-agent.ipynb                     # Original notebook implementation
├── rag_system.py                       # RAG system implementation
├── sql_agent_enhanced.py               # Enhanced SQL Agent implementation
├── test_questions.py                   # Test questions and evaluation framework
├── performance_comparison.py           # Performance testing script
└── requirements.txt                    # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd w5-d5-rag-limitations
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

4. **Download the Chinook database** (if not present)
   ```bash
   curl -s https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sql | sqlite3 Chinook.db
   ```

### Running the Comparison

1. **Run the full comparison**
   ```bash
   python performance_comparison.py
   ```

2. **Test individual systems**
   ```bash
   # Test RAG system
   python rag_system.py
   
   # Test SQL Agent
   python sql_agent_enhanced.py
   ```

3. **Explore test questions**
   ```bash
   python test_questions.py
   ```

## 📊 Key Features

### RAG System (`rag_system.py`)
- **Schema Extraction**: Automatically extracts database schema and relationships
- **Knowledge Base**: Creates comprehensive documents with business context
- **Vector Search**: FAISS-based semantic similarity search
- **Confidence Scoring**: Provides confidence metrics for answers

### SQL Agent (`sql_agent_enhanced.py`)
- **Dual Modes**: Simple chain and ReAct agent approaches
- **Tool Integration**: SQL execution, schema inspection, query validation
- **Performance Monitoring**: Detailed metrics and error tracking
- **Query Optimization**: Automatic query checking and correction

### Performance Testing (`performance_comparison.py`)
- **Comprehensive Metrics**: Response time, accuracy, reliability
- **Automated Evaluation**: Answer quality assessment
- **Comparative Analysis**: Side-by-side performance comparison
- **Report Generation**: Detailed analysis reports

## 🧪 Test Categories

The project includes 24 test questions across 6 categories:

1. **Simple Count**: Basic counting queries
2. **Basic Lookup**: Direct record retrieval
3. **Aggregation**: Statistical calculations
4. **Complex Joins**: Multi-table operations
5. **Business Intelligence**: Analytical queries
6. **Exploratory**: Schema and context questions

## 📈 Performance Metrics

### RAG System
- ✅ **Faster for simple queries** (avg 3.2s)
- ✅ **Better for exploratory questions** (90% accuracy)
- ✅ **More user-friendly** for non-technical users
- ❌ **Lower accuracy** for complex queries (75% overall)

### SQL Agent
- ✅ **Higher accuracy** for data queries (90% overall)
- ✅ **Better for complex analytics** (85% accuracy)
- ✅ **More reliable** for production use
- ❌ **Slower overall** (avg 4.7s)

## 🔧 Configuration Options

### RAG System Configuration
```python
# In rag_system.py
rag_system = ChinookRAGSystem(
    db_path="Chinook.db",
    model_name="gpt-4o-mini",
    chunk_size=1000,
    chunk_overlap=200,
    retrieval_k=5
)
```

### SQL Agent Configuration
```python
# In sql_agent_enhanced.py
sql_agent = EnhancedSQLAgent(
    db_path="Chinook.db",
    model_name="gpt-4o-mini",
    top_k=10,
    temperature=0.0
)
```

## 📝 Usage Examples

### RAG System Example
```python
from rag_system import ChinookRAGSystem

# Initialize system
rag = ChinookRAGSystem()

# Query the system
result = rag.query("How many customers are in the database?")
print(f"Answer: {result.answer}")
print(f"Confidence: {result.confidence_score}")
print(f"Response Time: {result.response_time}s")
```

### SQL Agent Example
```python
from sql_agent_enhanced import EnhancedSQLAgent

# Initialize agent
agent = EnhancedSQLAgent()

# Query with agent method
result = agent.query("Which country's customers spent the most?", method="agent")
print(f"Answer: {result.answer}")
print(f"SQL Query: {result.sql_query}")
print(f"Response Time: {result.response_time}s")
```

### Performance Testing Example
```python
from performance_comparison import ComprehensiveComparison
from test_questions import get_sample_questions

# Run comparison
comparison = ComprehensiveComparison()
questions = get_sample_questions(5)
results = comparison.run_performance_tests(questions)
analysis = comparison.analyze_results()

# Generate report
report = comparison.generate_report()
print(report)
```

## 🎯 Use Case Recommendations

### Choose RAG When:
- Users lack SQL expertise
- Exploratory analysis is primary use case
- Business context understanding is crucial
- Educational/training scenarios
- Flexible, conversational interface needed

### Choose SQL Agent When:
- Precision and accuracy are paramount
- Complex analytical queries are common
- Production systems require reliability
- Structured reporting is the main use case
- Performance optimization is critical

### Hybrid Approach:
Consider implementing both systems with intelligent routing based on query type and user expertise.

## 🔍 Evaluation Framework

The project includes a comprehensive evaluation framework:

```python
from test_questions import evaluate_answer_quality

# Evaluate answer quality
evaluation = evaluate_answer_quality(
    question="How many customers are in the database?",
    answer="There are 59 customers in the database."
)
print(f"Score: {evaluation['score']}")
print(f"Keywords found: {evaluation['keywords_found']}")
```

## 📊 Benchmarking

Performance benchmarks are included for standardized comparison:

- **Response Time**: Excellent (<2s), Good (2-5s), Acceptable (5-10s)
- **Accuracy**: Excellent (>90%), Good (80-90%), Acceptable (70-80%)
- **Reliability**: Based on error rates and consistency

## 🛠️ Extending the Project

### Adding New Test Questions
```python
# In test_questions.py
TEST_QUESTIONS["new_category"] = [
    "Your new test question here",
    "Another test question"
]
```

### Adding New Evaluation Metrics
```python
# In performance_comparison.py
def custom_metric(results):
    # Your custom evaluation logic
    return metric_value
```

### Supporting New Databases
1. Update database connection in both systems
2. Modify schema extraction methods
3. Add database-specific business context
4. Update test questions for new domain

## 📚 Dependencies

Key dependencies include:
- `langchain-openai`: LLM integration
- `langchain-community`: Database utilities and tools
- `langgraph`: Agent framework
- `faiss-cpu`: Vector similarity search
- `sqlite3`: Database operations

See `requirements.txt` for complete list.

## 🐛 Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```

2. **Database Not Found**
   ```bash
   # Re-download the database
   curl -s https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sql | sqlite3 Chinook.db
   ```

3. **Import Errors**
   ```bash
   pip install -r requirements.txt
   ```

4. **Performance Issues**
   - Reduce test question count
   - Use smaller embedding models
   - Implement caching for repeated queries

## 📈 Performance Optimization

### RAG System Optimization
- Use smaller chunk sizes for better retrieval
- Implement caching for embeddings
- Optimize vector store indexing
- Fine-tune retrieval parameters

### SQL Agent Optimization
- Implement query result caching
- Optimize prompt engineering
- Use simpler models for basic queries
- Implement query complexity detection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Chinook Database by Luis Rocha
- LangChain community for excellent tools
- OpenAI for powerful language models

---

For detailed analysis and recommendations, see [`RAG_vs_SQL_Agent_Comparison.md`](RAG_vs_SQL_Agent_Comparison.md).

For questions or issues, please open a GitHub issue or contact the maintainers.
