"""
Enhanced SQL Agent System for Chinook Database
This module implements an enhanced SQL Agent with performance monitoring and error handling.
"""

import sqlite3
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import create_react_agent
from typing_extensions import TypedDict, Annotated

@dataclass
class SQLQueryResult:
    """Structure for SQL query results with detailed metrics"""
    answer: str
    response_time: float
    sql_query: Optional[str] = None
    query_execution_time: Optional[float] = None
    rows_returned: Optional[int] = None
    error_occurred: bool = False
    error_message: Optional[str] = None
    tool_calls_made: int = 0

class State(TypedDict):
    question: str
    query: str
    result: str
    answer: str

class EnhancedSQLAgent:
    """Enhanced SQL Agent with performance monitoring and error handling"""
    
    def __init__(self, db_path: str = "Chinook.db", model_name: str = "gpt-4o-mini"):
        self.db_path = db_path
        self.model_name = model_name
        self.llm = ChatOpenAI(model=model_name, temperature=0.0)
        
        # Initialize database connection
        self.db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
        
        # Initialize toolkit and agent
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
        self.tools = self.toolkit.get_tools()
        
        # Create both simple chain and agent
        self._setup_simple_chain()
        self._setup_agent()
        
        # Performance tracking
        self.query_history = []
    
    def _setup_simple_chain(self):
        """Setup simple SQL chain for basic queries"""
        system_message = """
        Given an input question, create a syntactically correct {dialect} query to
        run to help find the answer. Unless the user specifies in his question a
        specific number of examples they wish to obtain, always limit your query to
        at most {top_k} results. You can order the results by a relevant column to
        return the most interesting examples in the database.

        Never query for all the columns from a specific table, only ask for the
        few relevant columns given the question.

        Pay attention to use only the column names that you can see in the schema
        description. Be careful to not query for columns that do not exist. Also,
        pay attention to which column is in which table.

        Only use the following tables:
        {table_info}
        """

        user_prompt = "Question: {input}"

        self.query_prompt_template = ChatPromptTemplate(
            [("system", system_message), ("user", user_prompt)]
        )
        
        # Create simple chain components
        self.simple_chain = (
            RunnableLambda(self._write_query) | 
            RunnableLambda(self._execute_query) | 
            RunnableLambda(self._generate_answer)
        )
    
    def _setup_agent(self):
        """Setup the ReAct agent for complex queries"""
        system_message = """
        You are an agent designed to interact with a SQL database.
        Given an input question, create a syntactically correct SQLite query to run,
        then look at the results of the query and return the answer. Unless the user
        specifies a specific number of examples they wish to obtain, always limit your
        query to at most 5 results.

        You can order the results by a relevant column to return the most interesting
        examples in the database. Never query for all the columns from a specific table,
        only ask for the relevant columns given the question.

        You MUST double check your query before executing it. If you get an error while
        executing a query, rewrite the query and try again.

        DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
        database.

        To start you should ALWAYS look at the tables in the database to see what you
        can query. Do NOT skip this step.

        Then you should query the schema of the most relevant tables.
        """
        
        self.agent_executor = create_react_agent(
            self.llm, 
            self.tools, 
            prompt=system_message
        )
    
    def _write_query(self, state: State) -> Dict[str, str]:
        """Generate SQL query from question"""
        prompt = self.query_prompt_template.invoke({
            "dialect": self.db.dialect,
            "top_k": 10,
            "table_info": self.db.get_table_info(),
            "input": state["question"],
        })
        
        class QueryOutput(TypedDict):
            query: Annotated[str, ..., "Syntactically valid SQL query."]
        
        structured_llm = self.llm.with_structured_output(QueryOutput)
        result = structured_llm.invoke(prompt)
        
        return {"question": state["question"], "query": result["query"]}
    
    def _execute_query(self, state: State) -> Dict[str, str]:
        """Execute SQL query and measure performance"""
        start_time = time.time()
        
        try:
            result = self.db.run(state["query"])
            execution_time = time.time() - start_time
            
            return {
                "question": state["question"],
                "query": state["query"],
                "result": result,
                "execution_time": execution_time
            }
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "question": state["question"],
                "query": state["query"],
                "result": f"Error: {str(e)}",
                "execution_time": execution_time
            }
    
    def _generate_answer(self, state: State) -> Dict[str, str]:
        """Generate natural language answer from query results"""
        prompt = (
            "Given the following user question, corresponding SQL query, "
            "and SQL result, answer the user question.\n\n"
            f'Question: {state["question"]}\n'
            f'SQL Query: {state["query"]}\n'
            f'SQL Result: {state["result"]}'
        )
        
        response = self.llm.invoke(prompt)
        return {"answer": response.content}
    
    def query_simple(self, question: str) -> SQLQueryResult:
        """Execute query using simple chain approach"""
        start_time = time.time()
        
        try:
            # Execute the chain
            result = self.simple_chain.invoke({"question": question})
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Extract SQL query and execution time if available
            sql_query = None
            query_execution_time = None
            rows_returned = None
            
            # Try to get additional metrics from the chain execution
            # This is a simplified approach - in practice you'd want more sophisticated tracking
            
            sql_result = SQLQueryResult(
                answer=result["answer"],
                response_time=response_time,
                sql_query=sql_query,
                query_execution_time=query_execution_time,
                rows_returned=rows_returned,
                error_occurred=False,
                tool_calls_made=1  # Simple chain makes one "tool call"
            )
            
            self.query_history.append({
                "question": question,
                "method": "simple_chain",
                "result": sql_result,
                "timestamp": datetime.now().isoformat()
            })
            
            return sql_result
            
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            error_result = SQLQueryResult(
                answer=f"Error occurred: {str(e)}",
                response_time=response_time,
                error_occurred=True,
                error_message=str(e),
                tool_calls_made=0
            )
            
            self.query_history.append({
                "question": question,
                "method": "simple_chain",
                "result": error_result,
                "timestamp": datetime.now().isoformat()
            })
            
            return error_result
    
    def query_agent(self, question: str) -> SQLQueryResult:
        """Execute query using ReAct agent approach"""
        start_time = time.time()
        
        try:
            # Execute the agent
            results = self.agent_executor.invoke(
                {"messages": [HumanMessage(content=question)]}
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Extract the final answer
            final_message = results["messages"][-1]
            answer = final_message.content if hasattr(final_message, 'content') else str(final_message)
            
            # Count tool calls
            tool_calls = sum(1 for msg in results["messages"] if hasattr(msg, 'tool_calls') and msg.tool_calls)
            
            # Try to extract SQL query from the messages
            sql_query = None
            for msg in results["messages"]:
                if hasattr(msg, 'content') and 'SELECT' in str(msg.content):
                    # Simple heuristic to find SQL query
                    content = str(msg.content)
                    if 'SELECT' in content:
                        lines = content.split('\n')
                        for line in lines:
                            if 'SELECT' in line:
                                sql_query = line.strip()
                                break
            
            sql_result = SQLQueryResult(
                answer=answer,
                response_time=response_time,
                sql_query=sql_query,
                error_occurred=False,
                tool_calls_made=tool_calls
            )
            
            self.query_history.append({
                "question": question,
                "method": "agent",
                "result": sql_result,
                "timestamp": datetime.now().isoformat()
            })
            
            return sql_result
            
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            error_result = SQLQueryResult(
                answer=f"Error occurred: {str(e)}",
                response_time=response_time,
                error_occurred=True,
                error_message=str(e),
                tool_calls_made=0
            )
            
            self.query_history.append({
                "question": question,
                "method": "agent",
                "result": error_result,
                "timestamp": datetime.now().isoformat()
            })
            
            return error_result
    
    def query(self, question: str, method: str = "agent") -> SQLQueryResult:
        """Execute query using specified method"""
        if method == "simple":
            return self.query_simple(question)
        elif method == "agent":
            return self.query_agent(question)
        else:
            raise ValueError(f"Unknown method: {method}. Use 'simple' or 'agent'")
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get comprehensive database information"""
        return {
            "dialect": self.db.dialect,
            "tables": self.db.get_usable_table_names(),
            "table_info": self.db.get_table_info(),
            "sample_query": self.db.run("SELECT COUNT(*) as total_tables FROM sqlite_master WHERE type='table'")
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary from query history"""
        if not self.query_history:
            return {}
        
        # Separate by method
        simple_queries = [q for q in self.query_history if q["method"] == "simple_chain"]
        agent_queries = [q for q in self.query_history if q["method"] == "agent"]
        
        def calculate_stats(queries):
            if not queries:
                return {}
            
            response_times = [q["result"].response_time for q in queries]
            errors = [q for q in queries if q["result"].error_occurred]
            tool_calls = [q["result"].tool_calls_made for q in queries]
            
            return {
                "total_queries": len(queries),
                "avg_response_time": sum(response_times) / len(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "error_rate": len(errors) / len(queries),
                "avg_tool_calls": sum(tool_calls) / len(tool_calls) if tool_calls else 0
            }
        
        return {
            "simple_chain": calculate_stats(simple_queries),
            "agent": calculate_stats(agent_queries),
            "total_queries": len(self.query_history)
        }

# Performance testing utilities
class SQLPerformanceTester:
    """Utility class for testing SQL Agent performance"""
    
    def __init__(self, sql_agent: EnhancedSQLAgent):
        self.sql_agent = sql_agent
        self.test_results = []
    
    def run_test_questions(self, questions: List[str], method: str = "agent") -> List[Dict[str, Any]]:
        """Run a set of test questions and collect performance metrics"""
        results = []
        
        for i, question in enumerate(questions, 1):
            print(f"Testing question {i}/{len(questions)} with {method}: {question[:50]}...")
            
            result = self.sql_agent.query(question, method=method)
            
            test_result = {
                "question": question,
                "method": method,
                "answer": result.answer,
                "response_time": result.response_time,
                "sql_query": result.sql_query,
                "error_occurred": result.error_occurred,
                "error_message": result.error_message,
                "tool_calls_made": result.tool_calls_made,
                "timestamp": datetime.now().isoformat()
            }
            
            results.append(test_result)
            self.test_results.append(test_result)
        
        return results
    
    def compare_methods(self, questions: List[str]) -> Dict[str, Any]:
        """Compare performance between simple chain and agent methods"""
        print("Testing with simple chain method...")
        simple_results = self.run_test_questions(questions, method="simple")
        
        print("Testing with agent method...")
        agent_results = self.run_test_questions(questions, method="agent")
        
        def calculate_method_stats(results):
            if not results:
                return {}
            
            response_times = [r["response_time"] for r in results]
            errors = [r for r in results if r["error_occurred"]]
            tool_calls = [r["tool_calls_made"] for r in results]
            
            return {
                "total_queries": len(results),
                "avg_response_time": sum(response_times) / len(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "error_rate": len(errors) / len(results),
                "avg_tool_calls": sum(tool_calls) / len(tool_calls) if tool_calls else 0,
                "successful_queries": len(results) - len(errors)
            }
        
        return {
            "simple_chain": calculate_method_stats(simple_results),
            "agent": calculate_method_stats(agent_results),
            "comparison": {
                "simple_faster": calculate_method_stats(simple_results).get("avg_response_time", float('inf')) < 
                               calculate_method_stats(agent_results).get("avg_response_time", float('inf')),
                "agent_more_reliable": calculate_method_stats(agent_results).get("error_rate", 1) < 
                                      calculate_method_stats(simple_results).get("error_rate", 1)
            }
        }

if __name__ == "__main__":
    # Example usage
    sql_agent = EnhancedSQLAgent()
    
    # Test both methods
    question = "How many customers are there?"
    
    print("Testing simple chain:")
    result_simple = sql_agent.query(question, method="simple")
    print(f"Answer: {result_simple.answer}")
    print(f"Response time: {result_simple.response_time:.2f}s")
    
    print("\nTesting agent:")
    result_agent = sql_agent.query(question, method="agent")
    print(f"Answer: {result_agent.answer}")
    print(f"Response time: {result_agent.response_time:.2f}s")
    
    # Show performance summary
    print("\nPerformance Summary:")
    print(json.dumps(sql_agent.get_performance_summary(), indent=2)) 