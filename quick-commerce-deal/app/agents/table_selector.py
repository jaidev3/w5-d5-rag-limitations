"""Intelligent table selector for optimizing query performance."""

import logging
from typing import List, Dict, Set, Optional, Tuple
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
import re
from collections import defaultdict
import json

from app.database.database import engine
from app.config import settings

logger = logging.getLogger(__name__)


class TableSelector:
    """Intelligent table selector for multi-table query optimization."""
    
    def __init__(self):
        self.table_metadata = {}
        self.table_relationships = {}
        self.semantic_mappings = {}
        self.performance_stats = {}
        self._initialize_metadata()
    
    def _initialize_metadata(self):
        """Initialize table metadata and relationships."""
        try:
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            # Build table metadata
            for table in tables:
                columns = inspector.get_columns(table)
                foreign_keys = inspector.get_foreign_keys(table)
                indexes = inspector.get_indexes(table)
                
                self.table_metadata[table] = {
                    'columns': {col['name']: col['type'] for col in columns},
                    'foreign_keys': foreign_keys,
                    'indexes': [idx['name'] for idx in indexes],
                    'primary_key': [col['name'] for col in columns if col.get('primary_key')]
                }
            
            # Build relationship graph
            self._build_relationship_graph()
            
            # Initialize semantic mappings
            self._initialize_semantic_mappings()
            
            logger.info(f"Initialized metadata for {len(tables)} tables")
            
        except Exception as e:
            logger.error(f"Error initializing table metadata: {e}")
    
    def _build_relationship_graph(self):
        """Build a graph of table relationships."""
        self.table_relationships = defaultdict(set)
        
        for table, metadata in self.table_metadata.items():
            for fk in metadata['foreign_keys']:
                referenced_table = fk['referred_table']
                self.table_relationships[table].add(referenced_table)
                self.table_relationships[referenced_table].add(table)
    
    def _initialize_semantic_mappings(self):
        """Initialize semantic mappings for better query understanding."""
        self.semantic_mappings = {
            # Product-related queries
            'product': ['products', 'product_variants', 'product_images', 'product_attributes', 'product_attribute_values'],
            'item': ['products', 'product_variants', 'platform_products'],
            'goods': ['products', 'categories', 'brands'],
            'merchandise': ['products', 'brands', 'categories'],
            
            # Price-related queries
            'price': ['prices', 'price_history', 'platform_products'],
            'cost': ['prices', 'price_history'],
            'amount': ['prices', 'orders', 'order_items'],
            'money': ['prices', 'orders'],
            'rupees': ['prices', 'price_history'],
            'cheap': ['prices', 'discounts', 'offers'],
            'expensive': ['prices', 'price_history'],
            
            # Platform-related queries
            'platform': ['platforms', 'platform_stores', 'platform_products'],
            'app': ['platforms', 'platform_stores'],
            'store': ['platforms', 'platform_stores'],
            'blinkit': ['platforms', 'platform_products', 'prices'],
            'zepto': ['platforms', 'platform_products', 'prices'],
            'instamart': ['platforms', 'platform_products', 'prices'],
            'bigbasket': ['platforms', 'platform_products', 'prices'],
            'dunzo': ['platforms', 'platform_products', 'prices'],
            'grofers': ['platforms', 'platform_products', 'prices'],
            
            # Discount-related queries
            'discount': ['discounts', 'product_discounts', 'prices'],
            'offer': ['offers', 'offer_products', 'discounts'],
            'deal': ['offers', 'discounts', 'product_discounts'],
            'sale': ['offers', 'discounts', 'prices'],
            'promotion': ['offers', 'discounts'],
            
            # Category-related queries
            'category': ['categories', 'subcategories', 'products'],
            'type': ['categories', 'subcategories'],
            'kind': ['categories', 'product_attributes'],
            'brand': ['brands', 'products'],
            'company': ['brands', 'platforms'],
            
            # Inventory-related queries
            'stock': ['inventory', 'stock_movements'],
            'available': ['inventory', 'platform_products'],
            'availability': ['inventory', 'delivery_slots'],
            'quantity': ['inventory', 'order_items'],
            
            # User-related queries
            'user': ['users', 'user_addresses', 'user_preferences'],
            'customer': ['users', 'orders', 'reviews'],
            'account': ['users', 'admin_users'],
            'profile': ['users', 'user_preferences'],
            
            # Order-related queries
            'order': ['orders', 'order_items', 'users'],
            'purchase': ['orders', 'order_items'],
            'buy': ['orders', 'order_items'],
            'cart': ['order_items', 'user_favorites'],
            'checkout': ['orders', 'order_items'],
            
            # Location-related queries
            'location': ['user_addresses', 'delivery_zones', 'platform_stores'],
            'address': ['user_addresses', 'delivery_zones'],
            'delivery': ['delivery_zones', 'delivery_slots', 'orders'],
            'zone': ['delivery_zones', 'platform_stores'],
            
            # Review-related queries
            'review': ['reviews', 'review_images'],
            'rating': ['reviews', 'products'],
            'comment': ['reviews', 'products'],
            'feedback': ['reviews', 'users'],
            
            # Analytics-related queries
            'popular': ['popular_products', 'product_views'],
            'trending': ['popular_products', 'search_queries'],
            'search': ['search_queries', 'products'],
            'view': ['product_views', 'popular_products'],
            'analytics': ['popular_products', 'search_queries', 'product_views'],
            
            # Nutritional queries
            'nutrition': ['nutritional_info', 'products'],
            'healthy': ['nutritional_info', 'product_attributes'],
            'organic': ['product_attributes', 'product_attribute_values'],
            'vegan': ['product_attributes', 'product_attribute_values'],
            'calories': ['nutritional_info', 'products'],
            'protein': ['nutritional_info', 'products'],
            
            # Time-related queries
            'today': ['prices', 'orders', 'product_views'],
            'yesterday': ['price_history', 'orders'],
            'recent': ['price_history', 'orders', 'product_views'],
            'latest': ['prices', 'orders', 'reviews'],
            'current': ['prices', 'inventory', 'offers'],
            'now': ['prices', 'inventory', 'delivery_slots'],
            
            # Comparison queries
            'compare': ['prices', 'platform_products', 'platforms'],
            'difference': ['prices', 'price_history'],
            'versus': ['prices', 'platform_products'],
            'between': ['prices', 'platform_products', 'platforms'],
            'best': ['prices', 'discounts', 'offers'],
            'worst': ['prices', 'reviews'],
            'top': ['popular_products', 'prices'],
            'bottom': ['prices', 'reviews'],
            
            # Specific product categories
            'vegetables': ['products', 'categories'],
            'fruits': ['products', 'categories'],
            'dairy': ['products', 'categories'],
            'meat': ['products', 'categories'],
            'snacks': ['products', 'categories'],
            'beverages': ['products', 'categories'],
            'grocery': ['products', 'categories', 'orders'],
            'food': ['products', 'categories', 'nutritional_info'],
            
            # Specific vegetables/fruits
            'onion': ['products', 'prices', 'platform_products'],
            'potato': ['products', 'prices', 'platform_products'],
            'tomato': ['products', 'prices', 'platform_products'],
            'apple': ['products', 'prices', 'platform_products'],
            'banana': ['products', 'prices', 'platform_products'],
            'milk': ['products', 'prices', 'platform_products'],
            'bread': ['products', 'prices', 'platform_products'],
            'rice': ['products', 'prices', 'platform_products'],
        }
    
    def select_tables(self, query: str, max_tables: int = 10) -> List[str]:
        """Select relevant tables for a given query."""
        try:
            # Normalize query
            query_lower = query.lower()
            
            # Extract relevant tables based on semantic mappings
            relevant_tables = set()
            
            # Check semantic mappings
            for keyword, tables in self.semantic_mappings.items():
                if keyword in query_lower:
                    relevant_tables.update(tables)
            
            # Add relationship-based tables
            expanded_tables = set(relevant_tables)
            for table in relevant_tables:
                if table in self.table_relationships:
                    expanded_tables.update(self.table_relationships[table])
            
            # Score tables based on relevance
            table_scores = self._score_tables(query_lower, expanded_tables)
            
            # Select top tables
            selected_tables = sorted(table_scores.keys(), 
                                   key=lambda x: table_scores[x], 
                                   reverse=True)[:max_tables]
            
            # Ensure essential tables are included
            selected_tables = self._ensure_essential_tables(query_lower, selected_tables)
            
            logger.info(f"Selected {len(selected_tables)} tables for query: {query[:50]}...")
            logger.debug(f"Selected tables: {selected_tables}")
            
            return selected_tables
            
        except Exception as e:
            logger.error(f"Error in table selection: {e}")
            return ['products', 'prices', 'platforms']  # Fallback
    
    def _score_tables(self, query: str, tables: Set[str]) -> Dict[str, float]:
        """Score tables based on query relevance."""
        scores = {}
        
        for table in tables:
            if table not in self.table_metadata:
                continue
                
            score = 0.0
            
            # Table name relevance
            if table in query:
                score += 10.0
            
            # Column name relevance
            for column in self.table_metadata[table]['columns']:
                if column in query:
                    score += 5.0
            
            # Index availability (better performance)
            if self.table_metadata[table]['indexes']:
                score += 2.0
            
            # Foreign key relationships (joinability)
            score += len(self.table_metadata[table]['foreign_keys']) * 1.0
            
            # Performance stats (if available)
            if table in self.performance_stats:
                performance = self.performance_stats[table]
                score += performance.get('query_frequency', 0) * 0.5
                score -= performance.get('avg_query_time', 0) * 0.1
            
            scores[table] = score
        
        return scores
    
    def _ensure_essential_tables(self, query: str, selected_tables: List[str]) -> List[str]:
        """Ensure essential tables are included based on query type."""
        essential_tables = []
        
        # Price comparison queries
        if any(word in query for word in ['price', 'cost', 'cheap', 'expensive', 'compare']):
            essential_tables.extend(['prices', 'platform_products', 'platforms'])
        
        # Product queries
        if any(word in query for word in ['product', 'item', 'goods']):
            essential_tables.extend(['products', 'categories'])
        
        # Platform-specific queries
        if any(platform in query for platform in ['blinkit', 'zepto', 'instamart', 'bigbasket']):
            essential_tables.extend(['platforms', 'platform_products', 'prices'])
        
        # Discount queries
        if any(word in query for word in ['discount', 'offer', 'deal', 'sale']):
            essential_tables.extend(['discounts', 'offers', 'product_discounts'])
        
        # Add essential tables if not already present
        for table in essential_tables:
            if table not in selected_tables and table in self.table_metadata:
                selected_tables.append(table)
        
        return selected_tables
    
    def get_join_path(self, tables: List[str]) -> List[Tuple[str, str]]:
        """Get optimal join path between tables."""
        try:
            if len(tables) <= 1:
                return []
            
            # Build join graph
            join_graph = defaultdict(list)
            for table in tables:
                if table in self.table_metadata:
                    for fk in self.table_metadata[table]['foreign_keys']:
                        ref_table = fk['referred_table']
                        if ref_table in tables:
                            join_graph[table].append((ref_table, fk['constrained_columns'][0], fk['referred_columns'][0]))
            
            # Find optimal join path using minimum spanning tree approach
            joins = []
            connected = {tables[0]}
            
            while len(connected) < len(tables):
                best_join = None
                best_cost = float('inf')
                
                for table in connected:
                    if table in join_graph:
                        for ref_table, local_col, ref_col in join_graph[table]:
                            if ref_table not in connected:
                                cost = self._calculate_join_cost(table, ref_table)
                                if cost < best_cost:
                                    best_cost = cost
                                    best_join = (table, ref_table, local_col, ref_col)
                
                if best_join:
                    table1, table2, col1, col2 = best_join
                    joins.append((table1, table2))
                    connected.add(table2)
                else:
                    # If no direct join found, add remaining tables without explicit joins
                    for table in tables:
                        if table not in connected:
                            connected.add(table)
                            break
            
            return joins
            
        except Exception as e:
            logger.error(f"Error calculating join path: {e}")
            return []
    
    def _calculate_join_cost(self, table1: str, table2: str) -> float:
        """Calculate cost of joining two tables."""
        # Simple cost calculation based on table sizes and indexes
        cost = 1.0
        
        # If either table has performance stats, use them
        if table1 in self.performance_stats:
            cost += self.performance_stats[table1].get('avg_query_time', 0)
        if table2 in self.performance_stats:
            cost += self.performance_stats[table2].get('avg_query_time', 0)
        
        # Prefer tables with indexes
        if (table1 in self.table_metadata and 
            self.table_metadata[table1]['indexes']):
            cost *= 0.8
        if (table2 in self.table_metadata and 
            self.table_metadata[table2]['indexes']):
            cost *= 0.8
        
        return cost
    
    def get_table_info(self, table_name: str) -> Optional[Dict]:
        """Get detailed information about a table."""
        return self.table_metadata.get(table_name)
    
    def update_performance_stats(self, table_name: str, query_time: float):
        """Update performance statistics for a table."""
        if table_name not in self.performance_stats:
            self.performance_stats[table_name] = {
                'query_frequency': 0,
                'total_time': 0,
                'avg_query_time': 0
            }
        
        stats = self.performance_stats[table_name]
        stats['query_frequency'] += 1
        stats['total_time'] += query_time
        stats['avg_query_time'] = stats['total_time'] / stats['query_frequency']
    
    def get_column_suggestions(self, query: str) -> List[str]:
        """Get column suggestions based on query."""
        query_lower = query.lower()
        suggestions = []
        
        # Extract relevant columns from selected tables
        relevant_tables = self.select_tables(query, max_tables=5)
        
        for table in relevant_tables:
            if table in self.table_metadata:
                for column in self.table_metadata[table]['columns']:
                    if any(word in column.lower() for word in query_lower.split()):
                        suggestions.append(f"{table}.{column}")
        
        return suggestions[:20]  # Limit to top 20 suggestions


# Global instance
table_selector = TableSelector() 