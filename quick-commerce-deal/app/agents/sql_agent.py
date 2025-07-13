"""Main SQL Agent with LangChain integration for intelligent query processing."""

import logging
import time
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
import json
import hashlib
from datetime import datetime, timedelta

from sqlalchemy import text, inspect
from sqlalchemy.orm import Session
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain_openai import OpenAI
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StdOutCallbackHandler
from langchain.schema import AgentAction, AgentFinish

from app.database.database import engine, get_db
from app.config import settings
from .table_selector import table_selector
from .query_planner import query_planner, QueryPlan, QueryType

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Represents the result of a query execution."""
    success: bool
    data: List[Dict[str, Any]]
    error_message: Optional[str]
    execution_time: float
    rows_returned: int
    query_plan: Optional[QueryPlan]
    generated_sql: Optional[str]
    cached: bool = False


class SQLAgent:
    """Advanced SQL Agent with intelligent query processing capabilities."""
    
    def __init__(self):
        self.db = None
        self.agent = None
        self.toolkit = None
        self.query_cache = {}
        self.performance_metrics = {}
        self._initialize_langchain_components()
    
    def _initialize_langchain_components(self):
        """Initialize LangChain components for SQL agent."""
        try:
            # Create SQLDatabase instance
            self.db = SQLDatabase.from_uri(settings.database_url)
            
            # Create LLM instance
            if settings.openai_api_key:
                llm = OpenAI(
                    temperature=0,
                    openai_api_key=settings.openai_api_key,
                    model_name="gpt-3.5-turbo-instruct"
                )
            else:
                logger.warning("OpenAI API key not provided, using fallback mode")
                llm = None
            
            # Create SQL toolkit
            if llm:
                self.toolkit = SQLDatabaseToolkit(db=self.db, llm=llm)
                
                # Create SQL agent
                self.agent = create_sql_agent(
                    llm=llm,
                    toolkit=self.toolkit,
                    verbose=True,
                    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                    max_iterations=3,
                    max_execution_time=30
                )
            
            logger.info("LangChain SQL Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize LangChain components: {e}")
            self.agent = None
    
    def process_query(self, natural_language_query: str, use_cache: bool = True, 
                     max_results: int = 1000) -> QueryResult:
        """Process a natural language query and return results."""
        start_time = time.time()
        
        try:
            # Generate query hash for caching
            query_hash = self._generate_query_hash(natural_language_query)
            
            # Check cache first
            if use_cache and query_hash in self.query_cache:
                cached_result = self.query_cache[query_hash]
                if not self._is_cache_expired(cached_result):
                    logger.info(f"Cache hit for query: {natural_language_query[:50]}...")
                    cached_result.cached = True
                    return cached_result
            
            # Create query plan
            query_plan = query_planner.create_query_plan(natural_language_query, max_results)
            
            # Validate query plan
            is_valid, validation_errors = query_planner.validate_plan(query_plan)
            if not is_valid:
                return QueryResult(
                    success=False,
                    data=[],
                    error_message=f"Query validation failed: {', '.join(validation_errors)}",
                    execution_time=time.time() - start_time,
                    rows_returned=0,
                    query_plan=query_plan,
                    generated_sql=None
                )
            
            # Generate and execute SQL
            if self.agent:
                result = self._execute_with_langchain(natural_language_query, query_plan)
            else:
                result = self._execute_with_custom_logic(natural_language_query, query_plan)
            
            # Update performance metrics
            execution_time = time.time() - start_time
            self._update_performance_metrics(query_plan, execution_time, result.rows_returned)
            
            # Cache successful results
            if use_cache and result.success:
                result.execution_time = execution_time
                self.query_cache[query_hash] = result
                self._cleanup_cache()
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return QueryResult(
                success=False,
                data=[],
                error_message=str(e),
                execution_time=time.time() - start_time,
                rows_returned=0,
                query_plan=None,
                generated_sql=None
            )
    
    def _execute_with_langchain(self, query: str, query_plan: QueryPlan) -> QueryResult:
        """Execute query using LangChain SQL agent."""
        try:
            # Enhance query with context from query plan
            enhanced_query = self._enhance_query_with_context(query, query_plan)
            
            # Execute with LangChain agent
            response = self.agent.run(enhanced_query)
            
            # Parse LangChain response
            if isinstance(response, str):
                # Try to parse as JSON first
                try:
                    data = json.loads(response)
                    if isinstance(data, list):
                        parsed_data = data
                    else:
                        parsed_data = [data]
                except json.JSONDecodeError:
                    # If not JSON, treat as plain text response
                    parsed_data = [{"response": response}]
            else:
                parsed_data = [{"response": str(response)}]
            
            return QueryResult(
                success=True,
                data=parsed_data,
                error_message=None,
                execution_time=0,  # Will be set by caller
                rows_returned=len(parsed_data),
                query_plan=query_plan,
                generated_sql=None  # LangChain doesn't expose generated SQL easily
            )
            
        except Exception as e:
            logger.error(f"LangChain execution failed: {e}")
            return self._execute_with_custom_logic(query, query_plan)
    
    def _execute_with_custom_logic(self, query: str, query_plan: QueryPlan) -> QueryResult:
        """Execute query using custom SQL generation logic."""
        try:
            # Generate SQL from query plan
            generated_sql = self._generate_sql_from_plan(query, query_plan)
            
            # Execute SQL query
            with next(get_db()) as db:
                result = db.execute(text(generated_sql))
                rows = result.fetchall()
                
                # Convert to list of dictionaries
                if rows:
                    columns = result.keys()
                    data = [dict(zip(columns, row)) for row in rows]
                else:
                    data = []
                
                return QueryResult(
                    success=True,
                    data=data,
                    error_message=None,
                    execution_time=0,  # Will be set by caller
                    rows_returned=len(data),
                    query_plan=query_plan,
                    generated_sql=generated_sql
                )
                
        except Exception as e:
            logger.error(f"Custom SQL execution failed: {e}")
            return QueryResult(
                success=False,
                data=[],
                error_message=str(e),
                execution_time=0,
                rows_returned=0,
                query_plan=query_plan,
                generated_sql=generated_sql if 'generated_sql' in locals() else None
            )
    
    def _generate_sql_from_plan(self, query: str, query_plan: QueryPlan) -> str:
        """Generate SQL query from query plan."""
        try:
            # Build SELECT clause
            select_clause = self._build_select_clause(query, query_plan)
            
            # Build FROM clause
            from_clause = self._build_from_clause(query_plan)
            
            # Build JOIN clauses
            join_clauses = self._build_join_clauses(query_plan)
            
            # Build WHERE clause
            where_clause = self._build_where_clause(query_plan)
            
            # Build ORDER BY clause
            order_by_clause = self._build_order_by_clause(query_plan)
            
            # Build LIMIT clause
            limit_clause = self._build_limit_clause(query_plan)
            
            # Combine all clauses
            sql_parts = [select_clause, from_clause]
            sql_parts.extend(join_clauses)
            if where_clause:
                sql_parts.append(where_clause)
            if order_by_clause:
                sql_parts.append(order_by_clause)
            if limit_clause:
                sql_parts.append(limit_clause)
            
            generated_sql = "\n".join(sql_parts)
            
            logger.debug(f"Generated SQL: {generated_sql}")
            return generated_sql
            
        except Exception as e:
            logger.error(f"Error generating SQL: {e}")
            raise
    
    def _build_select_clause(self, query: str, query_plan: QueryPlan) -> str:
        """Build SELECT clause based on query plan."""
        query_lower = query.lower()
        
        # Determine what to select based on query type
        if query_plan.query_type == QueryType.PRICE_COMPARISON:
            select_fields = [
                "products.name as product_name",
                "platforms.name as platform_name",
                "prices.regular_price",
                "prices.sale_price",
                "prices.discount_percentage"
            ]
        elif query_plan.query_type == QueryType.PRODUCT_SEARCH:
            select_fields = [
                "products.name as product_name",
                "products.description",
                "categories.name as category_name",
                "brands.name as brand_name"
            ]
        elif query_plan.query_type == QueryType.DISCOUNT_INQUIRY:
            select_fields = [
                "products.name as product_name",
                "discounts.discount_type",
                "discounts.discount_value",
                "discounts.discount_percentage",
                "platforms.name as platform_name"
            ]
        elif query_plan.query_type == QueryType.AVAILABILITY_CHECK:
            select_fields = [
                "products.name as product_name",
                "platforms.name as platform_name",
                "inventory.quantity_available",
                "inventory.last_updated"
            ]
        elif query_plan.query_type == QueryType.ANALYTICS:
            select_fields = [
                "products.name as product_name",
                "popular_products.view_count",
                "popular_products.search_count",
                "popular_products.order_count"
            ]
        else:
            # Default selection
            select_fields = [
                "products.name as product_name",
                "prices.sale_price",
                "platforms.name as platform_name"
            ]
        
        # Filter fields based on available tables
        available_fields = []
        for field in select_fields:
            table_name = field.split('.')[0]
            if table_name in query_plan.selected_tables:
                available_fields.append(field)
        
        if not available_fields:
            available_fields = ["*"]
        
        return f"SELECT {', '.join(available_fields)}"
    
    def _build_from_clause(self, query_plan: QueryPlan) -> str:
        """Build FROM clause."""
        # Use the first table as main table
        main_table = query_plan.selected_tables[0]
        return f"FROM {main_table}"
    
    def _build_join_clauses(self, query_plan: QueryPlan) -> List[str]:
        """Build JOIN clauses."""
        joins = []
        
        # Generate JOIN clauses based on join path
        for table1, table2 in query_plan.join_path:
            join_condition = self._get_join_condition(table1, table2)
            if join_condition:
                joins.append(f"LEFT JOIN {table2} ON {join_condition}")
        
        # Add remaining tables not in join path
        joined_tables = {query_plan.selected_tables[0]}  # Main table
        for table1, table2 in query_plan.join_path:
            joined_tables.add(table1)
            joined_tables.add(table2)
        
        for table in query_plan.selected_tables:
            if table not in joined_tables:
                # Find a connection to already joined tables
                for joined_table in joined_tables:
                    join_condition = self._get_join_condition(joined_table, table)
                    if join_condition:
                        joins.append(f"LEFT JOIN {table} ON {join_condition}")
                        joined_tables.add(table)
                        break
        
        return joins
    
    def _get_join_condition(self, table1: str, table2: str) -> Optional[str]:
        """Get join condition between two tables."""
        # Common join patterns
        join_patterns = {
            ('products', 'categories'): 'products.category_id = categories.id',
            ('products', 'brands'): 'products.brand_id = brands.id',
            ('products', 'platform_products'): 'products.id = platform_products.product_id',
            ('platform_products', 'platforms'): 'platform_products.platform_id = platforms.id',
            ('platform_products', 'prices'): 'platform_products.id = prices.platform_product_id',
            ('platform_products', 'inventory'): 'platform_products.id = inventory.platform_product_id',
            ('discounts', 'product_discounts'): 'discounts.id = product_discounts.discount_id',
            ('product_discounts', 'platform_products'): 'product_discounts.platform_product_id = platform_products.id',
            ('offers', 'offer_products'): 'offers.id = offer_products.offer_id',
            ('offer_products', 'platform_products'): 'offer_products.platform_product_id = platform_products.id',
            ('users', 'orders'): 'users.id = orders.user_id',
            ('orders', 'order_items'): 'orders.id = order_items.order_id',
            ('products', 'reviews'): 'products.id = reviews.product_id',
            ('products', 'popular_products'): 'products.id = popular_products.product_id',
            ('products', 'nutritional_info'): 'products.id = nutritional_info.product_id',
            ('categories', 'subcategories'): 'categories.id = subcategories.category_id',
            ('products', 'subcategories'): 'products.subcategory_id = subcategories.id',
            ('platforms', 'discounts'): 'platforms.id = discounts.platform_id',
            ('platforms', 'offers'): 'platforms.id = offers.platform_id',
            ('platforms', 'platform_stores'): 'platforms.id = platform_stores.platform_id',
            ('platforms', 'delivery_zones'): 'platforms.id = delivery_zones.platform_id'
        }
        
        # Try both directions
        key1 = (table1, table2)
        key2 = (table2, table1)
        
        if key1 in join_patterns:
            return join_patterns[key1]
        elif key2 in join_patterns:
            return join_patterns[key2]
        else:
            return None
    
    def _build_where_clause(self, query_plan: QueryPlan) -> Optional[str]:
        """Build WHERE clause."""
        if not query_plan.filter_conditions:
            return None
        
        conditions = []
        for condition in query_plan.filter_conditions:
            # Validate condition references valid tables
            if self._is_valid_condition(condition, query_plan.selected_tables):
                conditions.append(condition)
        
        if conditions:
            return f"WHERE {' AND '.join(conditions)}"
        else:
            return None
    
    def _build_order_by_clause(self, query_plan: QueryPlan) -> Optional[str]:
        """Build ORDER BY clause."""
        if not query_plan.sort_conditions:
            return None
        
        valid_sorts = []
        for sort_condition in query_plan.sort_conditions:
            if self._is_valid_sort(sort_condition, query_plan.selected_tables):
                valid_sorts.append(sort_condition)
        
        if valid_sorts:
            return f"ORDER BY {', '.join(valid_sorts)}"
        else:
            return None
    
    def _build_limit_clause(self, query_plan: QueryPlan) -> Optional[str]:
        """Build LIMIT clause."""
        if query_plan.limit_condition:
            return f"LIMIT {query_plan.limit_condition}"
        else:
            return None
    
    def _is_valid_condition(self, condition: str, tables: List[str]) -> bool:
        """Check if condition references valid tables."""
        # Extract table references from condition
        table_refs = [ref.split('.')[0] for ref in condition.split() if '.' in ref]
        return all(table in tables for table in table_refs)
    
    def _is_valid_sort(self, sort_condition: str, tables: List[str]) -> bool:
        """Check if sort condition references valid tables."""
        # Extract table reference from sort condition
        if '.' in sort_condition:
            table_ref = sort_condition.split('.')[0]
            return table_ref in tables
        return True
    
    def _enhance_query_with_context(self, query: str, query_plan: QueryPlan) -> str:
        """Enhance query with context from query plan."""
        context = f"""
        Query: {query}
        
        Context:
        - Query Type: {query_plan.query_type.value}
        - Selected Tables: {', '.join(query_plan.selected_tables)}
        - Expected Result Count: {query_plan.limit_condition or 'unlimited'}
        
        Please generate and execute an optimized SQL query for this request.
        Focus on the tables mentioned in the context.
        """
        return context
    
    def _generate_query_hash(self, query: str) -> str:
        """Generate hash for query caching."""
        return hashlib.md5(query.lower().encode()).hexdigest()
    
    def _is_cache_expired(self, cached_result: QueryResult) -> bool:
        """Check if cached result is expired."""
        # For now, cache expires after 5 minutes
        cache_duration = timedelta(minutes=5)
        return datetime.now() - cached_result.execution_time > cache_duration
    
    def _cleanup_cache(self):
        """Clean up expired cache entries."""
        if len(self.query_cache) > 1000:  # Limit cache size
            # Remove oldest entries
            oldest_keys = sorted(self.query_cache.keys())[:100]
            for key in oldest_keys:
                del self.query_cache[key]
    
    def _update_performance_metrics(self, query_plan: QueryPlan, execution_time: float, rows_returned: int):
        """Update performance metrics."""
        query_planner.update_performance_stats(query_plan, execution_time, rows_returned)
        
        # Update our own metrics
        plan_type = query_plan.query_type.value
        if plan_type not in self.performance_metrics:
            self.performance_metrics[plan_type] = {
                'total_queries': 0,
                'total_time': 0,
                'avg_time': 0,
                'total_rows': 0,
                'avg_rows': 0
            }
        
        metrics = self.performance_metrics[plan_type]
        metrics['total_queries'] += 1
        metrics['total_time'] += execution_time
        metrics['avg_time'] = metrics['total_time'] / metrics['total_queries']
        metrics['total_rows'] += rows_returned
        metrics['avg_rows'] = metrics['total_rows'] / metrics['total_queries']
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return {
            'query_metrics': self.performance_metrics,
            'cache_stats': {
                'cache_size': len(self.query_cache),
                'cache_hit_rate': self._calculate_cache_hit_rate()
            },
            'table_selector_stats': table_selector.performance_stats
        }
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        # This is a simplified calculation
        # In a real implementation, you'd track hits vs misses
        return 0.0  # Placeholder
    
    def clear_cache(self):
        """Clear query cache."""
        self.query_cache.clear()
        logger.info("Query cache cleared")
    
    def get_table_suggestions(self, query: str) -> List[str]:
        """Get table suggestions for a query."""
        return table_selector.select_tables(query)
    
    def get_column_suggestions(self, query: str) -> List[str]:
        """Get column suggestions for a query."""
        return table_selector.get_column_suggestions(query)


# Global instance
sql_agent = SQLAgent() 