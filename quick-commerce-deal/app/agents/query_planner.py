"""Advanced query planner for multi-step query generation and optimization."""

import logging
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import re
import time
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session

from app.database.database import engine, get_db
from app.config import settings
from .table_selector import table_selector

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Types of queries the system can handle."""
    PRICE_COMPARISON = "price_comparison"
    PRODUCT_SEARCH = "product_search"
    DISCOUNT_INQUIRY = "discount_inquiry"
    AVAILABILITY_CHECK = "availability_check"
    ANALYTICS = "analytics"
    COMPLEX_MULTI_TABLE = "complex_multi_table"
    SIMPLE_LOOKUP = "simple_lookup"


@dataclass
class QueryPlan:
    """Represents a query execution plan."""
    query_type: QueryType
    selected_tables: List[str]
    join_path: List[Tuple[str, str]]
    filter_conditions: List[str]
    sort_conditions: List[str]
    limit_condition: Optional[int]
    estimated_cost: float
    steps: List[Dict[str, Any]]
    validation_checks: List[str]


class QueryPlanner:
    """Advanced query planner with optimization capabilities."""
    
    def __init__(self):
        self.query_patterns = {}
        self.optimization_rules = {}
        self.performance_cache = {}
        self._initialize_patterns()
        self._initialize_optimization_rules()
    
    def _initialize_patterns(self):
        """Initialize query patterns for different types of queries."""
        self.query_patterns = {
            QueryType.PRICE_COMPARISON: {
                'keywords': ['price', 'cost', 'cheap', 'expensive', 'compare', 'versus', 'between'],
                'required_tables': ['prices', 'platform_products', 'platforms'],
                'common_joins': [
                    ('prices', 'platform_products'),
                    ('platform_products', 'platforms'),
                    ('platform_products', 'products')
                ],
                'typical_filters': ['is_active = true', 'prices.is_active = true'],
                'default_sort': 'prices.sale_price ASC'
            },
            
            QueryType.PRODUCT_SEARCH: {
                'keywords': ['product', 'item', 'goods', 'find', 'search'],
                'required_tables': ['products', 'categories'],
                'common_joins': [
                    ('products', 'categories'),
                    ('products', 'brands'),
                    ('products', 'platform_products')
                ],
                'typical_filters': ['products.is_active = true'],
                'default_sort': 'products.name ASC'
            },
            
            QueryType.DISCOUNT_INQUIRY: {
                'keywords': ['discount', 'offer', 'deal', 'sale', 'promotion'],
                'required_tables': ['discounts', 'offers', 'product_discounts'],
                'common_joins': [
                    ('discounts', 'product_discounts'),
                    ('product_discounts', 'platform_products'),
                    ('offers', 'offer_products')
                ],
                'typical_filters': ['discounts.is_active = true', 'offers.is_active = true'],
                'default_sort': 'discounts.discount_percentage DESC'
            },
            
            QueryType.AVAILABILITY_CHECK: {
                'keywords': ['available', 'stock', 'inventory', 'quantity'],
                'required_tables': ['inventory', 'platform_products'],
                'common_joins': [
                    ('inventory', 'platform_products'),
                    ('platform_products', 'products')
                ],
                'typical_filters': ['inventory.quantity_available > 0'],
                'default_sort': 'inventory.quantity_available DESC'
            },
            
            QueryType.ANALYTICS: {
                'keywords': ['popular', 'trending', 'analytics', 'views', 'top'],
                'required_tables': ['popular_products', 'product_views', 'search_queries'],
                'common_joins': [
                    ('popular_products', 'products'),
                    ('product_views', 'products'),
                    ('search_queries', 'users')
                ],
                'typical_filters': ['popular_products.date >= CURRENT_DATE - INTERVAL 30 DAY'],
                'default_sort': 'popular_products.view_count DESC'
            }
        }
    
    def _initialize_optimization_rules(self):
        """Initialize query optimization rules."""
        self.optimization_rules = {
            'index_usage': {
                'priority': 1,
                'description': 'Prefer indexed columns in WHERE and JOIN clauses',
                'apply': self._optimize_index_usage
            },
            'join_order': {
                'priority': 2,
                'description': 'Optimize join order for better performance',
                'apply': self._optimize_join_order
            },
            'filter_pushdown': {
                'priority': 3,
                'description': 'Push filters down to reduce intermediate result sets',
                'apply': self._optimize_filter_pushdown
            },
            'result_limiting': {
                'priority': 4,
                'description': 'Add appropriate LIMIT clauses for large result sets',
                'apply': self._optimize_result_limiting
            },
            'subquery_optimization': {
                'priority': 5,
                'description': 'Optimize subqueries and CTEs',
                'apply': self._optimize_subqueries
            }
        }
    
    def create_query_plan(self, natural_language_query: str, max_results: int = 1000) -> QueryPlan:
        """Create an optimized query plan from natural language."""
        try:
            start_time = time.time()
            
            # Step 1: Analyze query type
            query_type = self._analyze_query_type(natural_language_query)
            
            # Step 2: Select relevant tables
            selected_tables = table_selector.select_tables(natural_language_query, max_tables=10)
            
            # Step 3: Determine join path
            join_path = table_selector.get_join_path(selected_tables)
            
            # Step 4: Extract filter conditions
            filter_conditions = self._extract_filter_conditions(natural_language_query, selected_tables)
            
            # Step 5: Determine sort conditions
            sort_conditions = self._extract_sort_conditions(natural_language_query, selected_tables)
            
            # Step 6: Set limit condition
            limit_condition = self._determine_limit(natural_language_query, max_results)
            
            # Step 7: Generate execution steps
            steps = self._generate_execution_steps(
                query_type, selected_tables, join_path, filter_conditions, sort_conditions, limit_condition
            )
            
            # Step 8: Add validation checks
            validation_checks = self._generate_validation_checks(selected_tables, filter_conditions)
            
            # Step 9: Estimate cost
            estimated_cost = self._estimate_query_cost(selected_tables, join_path, filter_conditions)
            
            plan = QueryPlan(
                query_type=query_type,
                selected_tables=selected_tables,
                join_path=join_path,
                filter_conditions=filter_conditions,
                sort_conditions=sort_conditions,
                limit_condition=limit_condition,
                estimated_cost=estimated_cost,
                steps=steps,
                validation_checks=validation_checks
            )
            
            # Step 10: Optimize the plan
            optimized_plan = self._optimize_plan(plan)
            
            planning_time = time.time() - start_time
            logger.info(f"Query plan created in {planning_time:.3f}s for: {natural_language_query[:50]}...")
            
            return optimized_plan
            
        except Exception as e:
            logger.error(f"Error creating query plan: {e}")
            # Return fallback plan
            return self._create_fallback_plan(natural_language_query, max_results)
    
    def _analyze_query_type(self, query: str) -> QueryType:
        """Analyze the natural language query to determine its type."""
        query_lower = query.lower()
        
        # Score each query type based on keyword matches
        type_scores = {}
        
        for query_type, pattern in self.query_patterns.items():
            score = 0
            for keyword in pattern['keywords']:
                if keyword in query_lower:
                    score += 1
            
            # Bonus for exact keyword matches
            for keyword in pattern['keywords']:
                if f' {keyword} ' in f' {query_lower} ':
                    score += 0.5
            
            type_scores[query_type] = score
        
        # Return the type with highest score
        if type_scores:
            best_type = max(type_scores, key=type_scores.get)
            if type_scores[best_type] > 0:
                return best_type
        
        # Default to complex multi-table if no clear match
        return QueryType.COMPLEX_MULTI_TABLE
    
    def _extract_filter_conditions(self, query: str, tables: List[str]) -> List[str]:
        """Extract filter conditions from natural language query."""
        conditions = []
        query_lower = query.lower()
        
        # Platform-specific filters
        platform_names = ['blinkit', 'zepto', 'instamart', 'bigbasket', 'dunzo', 'grofers']
        for platform in platform_names:
            if platform in query_lower:
                conditions.append(f"platforms.name ILIKE '%{platform}%'")
        
        # Price-related filters
        price_patterns = [
            (r'under[s]?\s*(\d+)', lambda m: f"prices.sale_price <= {m.group(1)}"),
            (r'above[s]?\s*(\d+)', lambda m: f"prices.sale_price >= {m.group(1)}"),
            (r'less than[s]?\s*(\d+)', lambda m: f"prices.sale_price < {m.group(1)}"),
            (r'more than[s]?\s*(\d+)', lambda m: f"prices.sale_price > {m.group(1)}"),
            (r'between[s]?\s*(\d+)\s*and\s*(\d+)', lambda m: f"prices.sale_price BETWEEN {m.group(1)} AND {m.group(2)}"),
            (r'cheap', lambda m: "prices.sale_price < (SELECT AVG(sale_price) FROM prices)")
        ]
        
        for pattern, condition_func in price_patterns:
            matches = re.finditer(pattern, query_lower)
            for match in matches:
                conditions.append(condition_func(match))
        
        # Discount-related filters
        discount_patterns = [
            (r'(\d+)%\s*off', lambda m: f"discounts.discount_percentage >= {m.group(1)}"),
            (r'(\d+)%\s*discount', lambda m: f"discounts.discount_percentage >= {m.group(1)}"),
            (r'discount', lambda m: "discounts.discount_percentage > 0")
        ]
        
        for pattern, condition_func in discount_patterns:
            matches = re.finditer(pattern, query_lower)
            for match in matches:
                conditions.append(condition_func(match))
        
        # Product-specific filters
        product_patterns = [
            (r'onion', lambda m: "products.name ILIKE '%onion%'"),
            (r'potato', lambda m: "products.name ILIKE '%potato%'"),
            (r'tomato', lambda m: "products.name ILIKE '%tomato%'"),
            (r'apple', lambda m: "products.name ILIKE '%apple%'"),
            (r'banana', lambda m: "products.name ILIKE '%banana%'"),
            (r'milk', lambda m: "products.name ILIKE '%milk%'"),
            (r'bread', lambda m: "products.name ILIKE '%bread%'"),
            (r'rice', lambda m: "products.name ILIKE '%rice%'"),
            (r'fruit', lambda m: "categories.name ILIKE '%fruit%'"),
            (r'vegetable', lambda m: "categories.name ILIKE '%vegetable%'"),
            (r'dairy', lambda m: "categories.name ILIKE '%dairy%'"),
            (r'organic', lambda m: "product_attribute_values.value ILIKE '%organic%'")
        ]
        
        for pattern, condition_func in product_patterns:
            matches = re.finditer(pattern, query_lower)
            for match in matches:
                conditions.append(condition_func(match))
        
        # Time-based filters
        time_patterns = [
            (r'today', lambda m: "DATE(created_at) = CURRENT_DATE"),
            (r'yesterday', lambda m: "DATE(created_at) = CURRENT_DATE - INTERVAL 1 DAY"),
            (r'last week', lambda m: "created_at >= CURRENT_DATE - INTERVAL 7 DAY"),
            (r'last month', lambda m: "created_at >= CURRENT_DATE - INTERVAL 30 DAY"),
            (r'recent', lambda m: "created_at >= CURRENT_DATE - INTERVAL 7 DAY")
        ]
        
        for pattern, condition_func in time_patterns:
            matches = re.finditer(pattern, query_lower)
            for match in matches:
                conditions.append(condition_func(match))
        
        # Add default filters for active records
        if 'products' in tables:
            conditions.append("products.is_active = true")
        if 'prices' in tables:
            conditions.append("prices.is_active = true")
        if 'discounts' in tables:
            conditions.append("discounts.is_active = true")
        if 'offers' in tables:
            conditions.append("offers.is_active = true")
        
        return conditions
    
    def _extract_sort_conditions(self, query: str, tables: List[str]) -> List[str]:
        """Extract sort conditions from natural language query."""
        sort_conditions = []
        query_lower = query.lower()
        
        # Sort patterns
        sort_patterns = [
            (r'cheapest', ["prices.sale_price ASC"]),
            (r'most expensive', ["prices.sale_price DESC"]),
            (r'highest rated', ["reviews.rating DESC"]),
            (r'lowest rated', ["reviews.rating ASC"]),
            (r'newest', ["created_at DESC"]),
            (r'oldest', ["created_at ASC"]),
            (r'popular', ["popular_products.view_count DESC"]),
            (r'best deal', ["discounts.discount_percentage DESC"]),
            (r'alphabetical', ["products.name ASC"]),
            (r'by name', ["products.name ASC"]),
            (r'by price', ["prices.sale_price ASC"]),
            (r'by discount', ["discounts.discount_percentage DESC"])
        ]
        
        for pattern, sort_list in sort_patterns:
            if re.search(pattern, query_lower):
                sort_conditions.extend(sort_list)
                break
        
        # Default sort based on query type
        if not sort_conditions:
            if any(word in query_lower for word in ['price', 'cost', 'cheap']):
                sort_conditions.append("prices.sale_price ASC")
            elif any(word in query_lower for word in ['discount', 'deal', 'offer']):
                sort_conditions.append("discounts.discount_percentage DESC")
            elif any(word in query_lower for word in ['popular', 'trending']):
                sort_conditions.append("popular_products.view_count DESC")
            else:
                sort_conditions.append("products.name ASC")
        
        return sort_conditions
    
    def _determine_limit(self, query: str, max_results: int) -> int:
        """Determine the appropriate limit for the query."""
        query_lower = query.lower()
        
        # Extract explicit numbers
        number_patterns = [
            (r'top\s*(\d+)', lambda m: int(m.group(1))),
            (r'first\s*(\d+)', lambda m: int(m.group(1))),
            (r'show\s*(\d+)', lambda m: int(m.group(1))),
            (r'(\d+)\s*result', lambda m: int(m.group(1))),
            (r'limit\s*(\d+)', lambda m: int(m.group(1)))
        ]
        
        for pattern, extract_func in number_patterns:
            match = re.search(pattern, query_lower)
            if match:
                return min(extract_func(match), max_results)
        
        # Default limits based on query type
        if any(word in query_lower for word in ['all', 'every']):
            return max_results
        elif any(word in query_lower for word in ['few', 'some']):
            return min(10, max_results)
        else:
            return min(50, max_results)
    
    def _generate_execution_steps(self, query_type: QueryType, tables: List[str], 
                                joins: List[Tuple[str, str]], filters: List[str], 
                                sorts: List[str], limit: int) -> List[Dict[str, Any]]:
        """Generate step-by-step execution plan."""
        steps = []
        
        # Step 1: Table selection validation
        steps.append({
            'step': 1,
            'action': 'validate_tables',
            'description': 'Validate selected tables exist and are accessible',
            'tables': tables,
            'validation_required': True
        })
        
        # Step 2: Join validation
        if joins:
            steps.append({
                'step': 2,
                'action': 'validate_joins',
                'description': 'Validate join relationships and foreign keys',
                'joins': joins,
                'validation_required': True
            })
        
        # Step 3: Filter validation
        if filters:
            steps.append({
                'step': 3,
                'action': 'validate_filters',
                'description': 'Validate filter conditions and column references',
                'filters': filters,
                'validation_required': True
            })
        
        # Step 4: Query construction
        steps.append({
            'step': 4,
            'action': 'construct_query',
            'description': 'Construct optimized SQL query',
            'query_type': query_type,
            'validation_required': False
        })
        
        # Step 5: Query execution
        steps.append({
            'step': 5,
            'action': 'execute_query',
            'description': 'Execute query with performance monitoring',
            'timeout': 30,
            'validation_required': False
        })
        
        # Step 6: Result processing
        steps.append({
            'step': 6,
            'action': 'process_results',
            'description': 'Process and format query results',
            'limit': limit,
            'validation_required': False
        })
        
        return steps
    
    def _generate_validation_checks(self, tables: List[str], filters: List[str]) -> List[str]:
        """Generate validation checks for the query plan."""
        checks = []
        
        # Table existence checks
        for table in tables:
            checks.append(f"table_exists:{table}")
        
        # Column reference checks
        for filter_condition in filters:
            # Extract column references from filter
            column_refs = re.findall(r'(\w+\.\w+)', filter_condition)
            for col_ref in column_refs:
                checks.append(f"column_exists:{col_ref}")
        
        # Join relationship checks
        for i, table1 in enumerate(tables):
            for table2 in tables[i+1:]:
                checks.append(f"join_possible:{table1},{table2}")
        
        # Performance checks
        checks.append("query_complexity:acceptable")
        checks.append("estimated_rows:within_limits")
        
        return checks
    
    def _estimate_query_cost(self, tables: List[str], joins: List[Tuple[str, str]], 
                           filters: List[str]) -> float:
        """Estimate the cost of executing the query."""
        base_cost = 1.0
        
        # Cost based on number of tables
        table_cost = len(tables) * 0.5
        
        # Cost based on number of joins
        join_cost = len(joins) * 1.0
        
        # Cost based on filter complexity
        filter_cost = len(filters) * 0.2
        
        # Add costs for complex operations
        complex_operations = ['LIKE', 'ILIKE', 'AVG', 'COUNT', 'GROUP BY', 'ORDER BY']
        complexity_cost = 0
        for filter_condition in filters:
            for op in complex_operations:
                if op in filter_condition.upper():
                    complexity_cost += 0.5
        
        total_cost = base_cost + table_cost + join_cost + filter_cost + complexity_cost
        
        return total_cost
    
    def _optimize_plan(self, plan: QueryPlan) -> QueryPlan:
        """Apply optimization rules to the query plan."""
        optimized_plan = plan
        
        # Apply optimization rules in priority order
        for rule_name, rule_config in sorted(self.optimization_rules.items(), 
                                           key=lambda x: x[1]['priority']):
            try:
                optimized_plan = rule_config['apply'](optimized_plan)
                logger.debug(f"Applied optimization rule: {rule_name}")
            except Exception as e:
                logger.warning(f"Failed to apply optimization rule {rule_name}: {e}")
        
        return optimized_plan
    
    def _optimize_index_usage(self, plan: QueryPlan) -> QueryPlan:
        """Optimize query to use indexes effectively."""
        # This is a placeholder for index optimization logic
        # In a real implementation, this would reorder conditions to use indexed columns first
        return plan
    
    def _optimize_join_order(self, plan: QueryPlan) -> QueryPlan:
        """Optimize join order for better performance."""
        # This is a placeholder for join order optimization
        # In a real implementation, this would reorder joins based on selectivity
        return plan
    
    def _optimize_filter_pushdown(self, plan: QueryPlan) -> QueryPlan:
        """Push filters down to reduce intermediate result sets."""
        # This is a placeholder for filter pushdown optimization
        return plan
    
    def _optimize_result_limiting(self, plan: QueryPlan) -> QueryPlan:
        """Optimize result limiting to prevent large result sets."""
        if plan.limit_condition is None or plan.limit_condition > 1000:
            plan.limit_condition = 1000
        return plan
    
    def _optimize_subqueries(self, plan: QueryPlan) -> QueryPlan:
        """Optimize subqueries and CTEs."""
        # This is a placeholder for subquery optimization
        return plan
    
    def _create_fallback_plan(self, query: str, max_results: int) -> QueryPlan:
        """Create a simple fallback plan when main planning fails."""
        return QueryPlan(
            query_type=QueryType.SIMPLE_LOOKUP,
            selected_tables=['products', 'prices', 'platforms'],
            join_path=[('prices', 'platform_products'), ('platform_products', 'products')],
            filter_conditions=['products.is_active = true', 'prices.is_active = true'],
            sort_conditions=['products.name ASC'],
            limit_condition=min(50, max_results),
            estimated_cost=2.0,
            steps=[
                {
                    'step': 1,
                    'action': 'fallback_query',
                    'description': 'Execute fallback query',
                    'validation_required': False
                }
            ],
            validation_checks=['table_exists:products', 'table_exists:prices']
        )
    
    def validate_plan(self, plan: QueryPlan) -> Tuple[bool, List[str]]:
        """Validate a query plan before execution."""
        errors = []
        
        try:
            # Validate table existence
            inspector = inspect(engine)
            available_tables = inspector.get_table_names()
            
            for table in plan.selected_tables:
                if table not in available_tables:
                    errors.append(f"Table '{table}' does not exist")
            
            # Validate join paths
            for table1, table2 in plan.join_path:
                if table1 not in available_tables:
                    errors.append(f"Join table '{table1}' does not exist")
                if table2 not in available_tables:
                    errors.append(f"Join table '{table2}' does not exist")
            
            # Validate estimated cost
            if plan.estimated_cost > 10.0:
                errors.append(f"Query cost too high: {plan.estimated_cost}")
            
            # Validate result limit
            if plan.limit_condition and plan.limit_condition > 10000:
                errors.append(f"Result limit too high: {plan.limit_condition}")
            
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
        
        return len(errors) == 0, errors
    
    def update_performance_stats(self, plan: QueryPlan, execution_time: float, 
                               rows_returned: int):
        """Update performance statistics for query optimization."""
        plan_key = f"{plan.query_type.value}_{len(plan.selected_tables)}"
        
        if plan_key not in self.performance_cache:
            self.performance_cache[plan_key] = {
                'total_executions': 0,
                'total_time': 0,
                'total_rows': 0,
                'avg_time': 0,
                'avg_rows': 0
            }
        
        stats = self.performance_cache[plan_key]
        stats['total_executions'] += 1
        stats['total_time'] += execution_time
        stats['total_rows'] += rows_returned
        stats['avg_time'] = stats['total_time'] / stats['total_executions']
        stats['avg_rows'] = stats['total_rows'] / stats['total_executions']
        
        # Update table selector performance stats
        for table in plan.selected_tables:
            table_selector.update_performance_stats(table, execution_time / len(plan.selected_tables))


# Global instance
query_planner = QueryPlanner() 