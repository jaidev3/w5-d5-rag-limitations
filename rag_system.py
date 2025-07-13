"""
RAG System for Chinook Database
This module implements a Retrieval-Augmented Generation system for querying the Chinook database.
"""

import sqlite3
import time
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import json
import os
from datetime import datetime

# Core imports
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

@dataclass
class QueryResult:
    """Structure for query results with timing information"""
    answer: str
    response_time: float
    retrieved_docs: List[str]
    confidence_score: float = 0.0

class ChinookRAGSystem:
    """RAG System for Chinook Database"""
    
    def __init__(self, db_path: str = "Chinook.db", model_name: str = "gpt-4o-mini"):
        self.db_path = db_path
        self.llm = ChatOpenAI(model=model_name, temperature=0.0)
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = None
        self.retriever = None
        self.rag_chain = None
        
        # Initialize the system
        self._setup_rag_system()
    
    def _get_database_schema(self) -> Dict[str, Any]:
        """Extract comprehensive database schema information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        schema_info = {
            "tables": {},
            "relationships": [],
            "sample_data": {}
        }
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            schema_info["tables"][table_name] = {
                "columns": [
                    {
                        "name": col[1],
                        "type": col[2],
                        "not_null": bool(col[3]),
                        "primary_key": bool(col[5])
                    }
                    for col in columns
                ],
                "description": self._generate_table_description(table_name, columns)
            }
            
            # Get foreign keys
            cursor.execute(f"PRAGMA foreign_key_list({table_name})")
            foreign_keys = cursor.fetchall()
            
            for fk in foreign_keys:
                schema_info["relationships"].append({
                    "from_table": table_name,
                    "from_column": fk[3],
                    "to_table": fk[2],
                    "to_column": fk[4]
                })
            
            # Get sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            sample_rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            
            schema_info["sample_data"][table_name] = {
                "columns": column_names,
                "rows": sample_rows
            }
        
        conn.close()
        return schema_info
    
    def _generate_table_description(self, table_name: str, columns: List[Tuple]) -> str:
        """Generate natural language description of table structure"""
        descriptions = {
            "Album": "Contains music albums with titles and artist references",
            "Artist": "Contains music artists and bands",
            "Customer": "Contains customer information including contact details and location",
            "Employee": "Contains employee information including hierarchy and contact details",
            "Genre": "Contains music genres and categories",
            "Invoice": "Contains customer purchase invoices with billing information",
            "InvoiceLine": "Contains individual line items for each invoice",
            "MediaType": "Contains different media formats (MP3, AAC, etc.)",
            "Playlist": "Contains user-created playlists",
            "PlaylistTrack": "Contains tracks associated with playlists",
            "Track": "Contains individual music tracks with metadata"
        }
        
        base_desc = descriptions.get(table_name, f"Contains {table_name.lower()} data")
        
        # Add column information
        column_info = []
        for col in columns:
            col_name, col_type = col[1], col[2]
            if col[5]:  # Primary key
                column_info.append(f"{col_name} (primary key)")
            else:
                column_info.append(col_name)
        
        return f"{base_desc}. Columns: {', '.join(column_info)}"
    
    def _create_knowledge_documents(self, schema_info: Dict[str, Any]) -> List[Document]:
        """Create documents from database schema and sample data"""
        documents = []
        
        # Create documents for each table
        for table_name, table_info in schema_info["tables"].items():
            # Table schema document
            schema_content = f"""
            Table: {table_name}
            Description: {table_info['description']}
            
            Columns:
            """
            
            for col in table_info["columns"]:
                schema_content += f"- {col['name']} ({col['type']})"
                if col['primary_key']:
                    schema_content += " [PRIMARY KEY]"
                if col['not_null']:
                    schema_content += " [NOT NULL]"
                schema_content += "\n"
            
            # Add sample data
            if table_name in schema_info["sample_data"]:
                sample_data = schema_info["sample_data"][table_name]
                schema_content += f"\nSample data:\n"
                for i, row in enumerate(sample_data["rows"][:3]):  # Limit to 3 rows
                    row_data = dict(zip(sample_data["columns"], row))
                    schema_content += f"Row {i+1}: {json.dumps(row_data, default=str)}\n"
            
            documents.append(Document(
                page_content=schema_content,
                metadata={"table": table_name, "type": "schema"}
            ))
        
        # Create relationship documents
        relationship_content = "Database Relationships:\n"
        for rel in schema_info["relationships"]:
            relationship_content += f"- {rel['from_table']}.{rel['from_column']} -> {rel['to_table']}.{rel['to_column']}\n"
        
        documents.append(Document(
            page_content=relationship_content,
            metadata={"type": "relationships"}
        ))
        
        # Create business context documents
        business_contexts = [
            {
                "content": """
                Business Context: Music Store Operations
                
                This database represents a digital music store similar to iTunes or Spotify.
                Key business concepts:
                - Customers purchase music tracks through invoices
                - Tracks belong to albums, which are created by artists
                - Tracks have genres and media types
                - Employees manage customer relationships
                - Customers can create playlists
                
                Common queries involve:
                - Sales analysis by country, customer, or time period
                - Music catalog browsing by artist, album, or genre
                - Customer behavior and purchasing patterns
                - Employee performance metrics
                """,
                "metadata": {"type": "business_context"}
            },
            {
                "content": """
                Query Patterns and Examples:
                
                Sales Analysis:
                - Total sales by country: JOIN Customer and Invoice tables
                - Top customers: SUM Invoice totals by CustomerId
                - Sales trends: GROUP BY date fields in Invoice
                
                Music Catalog:
                - Artist discography: JOIN Artist, Album, Track tables
                - Genre analysis: JOIN Genre, Track tables
                - Album contents: JOIN Album, Track tables
                
                Customer Analysis:
                - Customer demographics: Customer table with geographic grouping
                - Purchase history: JOIN Customer, Invoice, InvoiceLine tables
                - Playlist analysis: JOIN Playlist, PlaylistTrack, Track tables
                """,
                "metadata": {"type": "query_patterns"}
            }
        ]
        
        for context in business_contexts:
            documents.append(Document(
                page_content=context["content"],
                metadata=context["metadata"]
            ))
        
        return documents
    
    def _setup_rag_system(self):
        """Initialize the RAG system with vector store and retrieval chain"""
        # Get database schema
        schema_info = self._get_database_schema()
        
        # Create knowledge documents
        documents = self._create_knowledge_documents(schema_info)
        
        # Split documents if needed
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        
        split_docs = text_splitter.split_documents(documents)
        
        # Create vector store
        self.vector_store = FAISS.from_documents(split_docs, self.embeddings)
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
        
        # Create RAG chain
        self._create_rag_chain()
    
    def _create_rag_chain(self):
        """Create the RAG processing chain"""
        
        # Define the prompt template
        prompt_template = """
        You are a helpful assistant for a music store database. Use the following context to answer the user's question.
        
        Database Context:
        {context}
        
        Question: {question}
        
        Instructions:
        1. Provide a clear, accurate answer based on the database schema and context
        2. If the question requires data that would need a SQL query, explain what tables and columns would be involved
        3. If you cannot answer the question with the provided context, say so clearly
        4. Be specific about table names, column names, and relationships
        5. Provide examples when helpful
        
        Answer:
        """
        
        prompt = ChatPromptTemplate.from_template(prompt_template)
        
        # Create the chain
        self.rag_chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
    
    def query(self, question: str) -> QueryResult:
        """Process a query through the RAG system"""
        start_time = time.time()
        
        # Retrieve relevant documents
        retrieved_docs = self.retriever.get_relevant_documents(question)
        
        # Generate answer
        answer = self.rag_chain.invoke(question)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Extract document content for analysis
        doc_contents = [doc.page_content[:200] + "..." for doc in retrieved_docs]
        
        return QueryResult(
            answer=answer,
            response_time=response_time,
            retrieved_docs=doc_contents,
            confidence_score=self._calculate_confidence_score(question, retrieved_docs)
        )
    
    def _calculate_confidence_score(self, question: str, retrieved_docs: List[Document]) -> float:
        """Calculate a confidence score based on retrieval quality"""
        if not retrieved_docs:
            return 0.0
        
        # Simple confidence scoring based on document relevance
        # In a real system, this would be more sophisticated
        base_score = 0.7
        
        # Check if we have schema information
        has_schema = any("Table:" in doc.page_content for doc in retrieved_docs)
        if has_schema:
            base_score += 0.2
        
        # Check if we have business context
        has_business_context = any("Business Context:" in doc.page_content for doc in retrieved_docs)
        if has_business_context:
            base_score += 0.1
        
        return min(base_score, 1.0)
    
    def get_database_summary(self) -> Dict[str, Any]:
        """Get a summary of the database structure"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        summary = {}
        
        # Get table counts
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            summary[table_name] = count
        
        conn.close()
        return summary

# Performance testing utilities
class PerformanceTester:
    """Utility class for testing RAG system performance"""
    
    def __init__(self, rag_system: ChinookRAGSystem):
        self.rag_system = rag_system
        self.test_results = []
    
    def run_test_questions(self, questions: List[str]) -> List[Dict[str, Any]]:
        """Run a set of test questions and collect performance metrics"""
        results = []
        
        for i, question in enumerate(questions, 1):
            print(f"Testing question {i}/{len(questions)}: {question[:50]}...")
            
            result = self.rag_system.query(question)
            
            test_result = {
                "question": question,
                "answer": result.answer,
                "response_time": result.response_time,
                "confidence_score": result.confidence_score,
                "retrieved_docs_count": len(result.retrieved_docs),
                "timestamp": datetime.now().isoformat()
            }
            
            results.append(test_result)
            self.test_results.append(test_result)
        
        return results
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary statistics of performance tests"""
        if not self.test_results:
            return {}
        
        response_times = [r["response_time"] for r in self.test_results]
        confidence_scores = [r["confidence_score"] for r in self.test_results]
        
        return {
            "total_questions": len(self.test_results),
            "avg_response_time": sum(response_times) / len(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "avg_confidence": sum(confidence_scores) / len(confidence_scores),
            "min_confidence": min(confidence_scores),
            "max_confidence": max(confidence_scores)
        }

if __name__ == "__main__":
    # Example usage
    rag_system = ChinookRAGSystem()
    
    # Test query
    result = rag_system.query("How many customers are in the database?")
    print(f"Answer: {result.answer}")
    print(f"Response time: {result.response_time:.2f}s")
    print(f"Confidence: {result.confidence_score:.2f}") 