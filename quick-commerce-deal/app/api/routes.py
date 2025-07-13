"""API routes for Quick Commerce Deals platform."""

import logging
from typing import List, Dict, Optional, Any
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import text, and_, or_
from pydantic import BaseModel, Field

from app.database.database import get_db
from app.database.models import (
    Product, Platform, Price, Category, Brand, Discount, 
    PlatformProduct, Offer, PopularProduct, Review
)
from app.agents.sql_agent import sql_agent

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for requests/responses
class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category_name: Optional[str]
    brand_name: Optional[str]
    current_price: Optional[float]
    regular_price: Optional[float]
    discount_percentage: Optional[float]
    platform_name: Optional[str]
    is_available: bool = True

class PlatformResponse(BaseModel):
    id: int
    name: str
    display_name: str
    logo_url: Optional[str]
    delivery_fee: Optional[float]
    min_order_amount: Optional[float]
    is_active: bool

class DealResponse(BaseModel):
    id: int
    product_name: str
    platform_name: str
    original_price: Optional[float]
    discounted_price: Optional[float]
    discount_percentage: Optional[float]
    discount_value: Optional[float]
    deal_type: str
    expires_at: Optional[str]

class ComparisonResponse(BaseModel):
    product_name: str
    comparisons: List[Dict[str, Any]]
    best_deal: Optional[Dict[str, Any]]

class PopularProductResponse(BaseModel):
    id: int
    name: str
    view_count: int
    search_count: int
    order_count: int
    category_name: Optional[str]
    current_price: Optional[float]


# Product endpoints
@router.get("/products", response_model=List[ProductResponse])
async def get_products(
    name: Optional[str] = Query(None, description="Product name search"),
    category: Optional[str] = Query(None, description="Category filter"),
    brand: Optional[str] = Query(None, description="Brand filter"),
    platform: Optional[str] = Query(None, description="Platform filter"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    discount_min: Optional[float] = Query(None, description="Minimum discount percentage"),
    sort_by: Optional[str] = Query("name", description="Sort by: name, price, discount"),
    limit: int = Query(50, ge=1, le=1000, description="Number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """Get products with filtering and sorting."""
    try:
        # Build query
        query = db.query(
            Product.id,
            Product.name,
            Product.description,
            Category.name.label("category_name"),
            Brand.name.label("brand_name"),
            Price.sale_price.label("current_price"),
            Price.regular_price,
            Price.discount_percentage,
            Platform.name.label("platform_name"),
            PlatformProduct.is_available
        ).join(
            PlatformProduct, Product.id == PlatformProduct.product_id
        ).join(
            Platform, PlatformProduct.platform_id == Platform.id
        ).join(
            Price, PlatformProduct.id == Price.platform_product_id
        ).outerjoin(
            Category, Product.category_id == Category.id
        ).outerjoin(
            Brand, Product.brand_id == Brand.id
        ).filter(
            Product.is_active == True,
            Price.is_active == True,
            Platform.is_active == True
        )
        
        # Apply filters
        if name:
            query = query.filter(Product.name.ilike(f"%{name}%"))
        
        if category:
            query = query.filter(Category.name.ilike(f"%{category}%"))
        
        if brand:
            query = query.filter(Brand.name.ilike(f"%{brand}%"))
        
        if platform:
            query = query.filter(Platform.name.ilike(f"%{platform}%"))
        
        if min_price is not None:
            query = query.filter(Price.sale_price >= min_price)
        
        if max_price is not None:
            query = query.filter(Price.sale_price <= max_price)
        
        if discount_min is not None:
            query = query.filter(Price.discount_percentage >= discount_min)
        
        # Apply sorting
        if sort_by == "price":
            query = query.order_by(Price.sale_price.asc())
        elif sort_by == "discount":
            query = query.order_by(Price.discount_percentage.desc())
        else:
            query = query.order_by(Product.name.asc())
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        # Execute query
        results = query.all()
        
        # Convert to response format
        products = []
        for result in results:
            products.append(ProductResponse(
                id=result.id,
                name=result.name,
                description=result.description,
                category_name=result.category_name,
                brand_name=result.brand_name,
                current_price=float(result.current_price) if result.current_price else None,
                regular_price=float(result.regular_price) if result.regular_price else None,
                discount_percentage=float(result.discount_percentage) if result.discount_percentage else None,
                platform_name=result.platform_name,
                is_available=result.is_available
            ))
        
        return products
        
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product by ID."""
    try:
        result = db.query(
            Product.id,
            Product.name,
            Product.description,
            Category.name.label("category_name"),
            Brand.name.label("brand_name"),
            Price.sale_price.label("current_price"),
            Price.regular_price,
            Price.discount_percentage,
            Platform.name.label("platform_name"),
            PlatformProduct.is_available
        ).join(
            PlatformProduct, Product.id == PlatformProduct.product_id
        ).join(
            Platform, PlatformProduct.platform_id == Platform.id
        ).join(
            Price, PlatformProduct.id == Price.platform_product_id
        ).outerjoin(
            Category, Product.category_id == Category.id
        ).outerjoin(
            Brand, Product.brand_id == Brand.id
        ).filter(
            Product.id == product_id,
            Product.is_active == True,
            Price.is_active == True
        ).first()
        
        if not result:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return ProductResponse(
            id=result.id,
            name=result.name,
            description=result.description,
            category_name=result.category_name,
            brand_name=result.brand_name,
            current_price=float(result.current_price) if result.current_price else None,
            regular_price=float(result.regular_price) if result.regular_price else None,
            discount_percentage=float(result.discount_percentage) if result.discount_percentage else None,
            platform_name=result.platform_name,
            is_available=result.is_available
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product {product_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Platform endpoints
@router.get("/platforms", response_model=List[PlatformResponse])
async def get_platforms(
    active_only: bool = Query(True, description="Only active platforms"),
    db: Session = Depends(get_db)
):
    """Get all platforms."""
    try:
        query = db.query(Platform)
        
        if active_only:
            query = query.filter(Platform.is_active == True)
        
        platforms = query.all()
        
        return [
            PlatformResponse(
                id=platform.id,
                name=platform.name,
                display_name=platform.display_name,
                logo_url=platform.logo_url,
                delivery_fee=float(platform.delivery_fee) if platform.delivery_fee else None,
                min_order_amount=float(platform.min_order_amount) if platform.min_order_amount else None,
                is_active=platform.is_active
            )
            for platform in platforms
        ]
        
    except Exception as e:
        logger.error(f"Error getting platforms: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Deals endpoints
@router.get("/deals", response_model=List[DealResponse])
async def get_deals(
    min_discount_percentage: Optional[float] = Query(None, description="Minimum discount percentage"),
    platform: Optional[str] = Query(None, description="Platform filter"),
    category: Optional[str] = Query(None, description="Category filter"),
    limit: int = Query(50, ge=1, le=1000, description="Number of results"),
    db: Session = Depends(get_db)
):
    """Get current deals and discounts."""
    try:
        # Query for discount-based deals
        discount_query = db.query(
            Product.name.label("product_name"),
            Platform.name.label("platform_name"),
            Price.regular_price.label("original_price"),
            Price.sale_price.label("discounted_price"),
            Price.discount_percentage,
            Discount.discount_value,
            Discount.discount_type.label("deal_type"),
            Discount.end_date.label("expires_at")
        ).join(
            PlatformProduct, Product.id == PlatformProduct.product_id
        ).join(
            Platform, PlatformProduct.platform_id == Platform.id
        ).join(
            Price, PlatformProduct.id == Price.platform_product_id
        ).join(
            Discount, Platform.id == Discount.platform_id
        ).outerjoin(
            Category, Product.category_id == Category.id
        ).filter(
            Product.is_active == True,
            Price.is_active == True,
            Discount.is_active == True,
            Platform.is_active == True
        )
        
        # Apply filters
        if min_discount_percentage is not None:
            discount_query = discount_query.filter(
                or_(
                    Price.discount_percentage >= min_discount_percentage,
                    Discount.discount_value >= min_discount_percentage
                )
            )
        
        if platform:
            discount_query = discount_query.filter(Platform.name.ilike(f"%{platform}%"))
        
        if category:
            discount_query = discount_query.filter(Category.name.ilike(f"%{category}%"))
        
        # Order by discount percentage
        discount_query = discount_query.order_by(Price.discount_percentage.desc())
        
        # Execute query
        results = discount_query.limit(limit).all()
        
        # Convert to response format
        deals = []
        for result in results:
            deals.append(DealResponse(
                id=len(deals) + 1,  # Simple ID assignment
                product_name=result.product_name,
                platform_name=result.platform_name,
                original_price=float(result.original_price) if result.original_price else None,
                discounted_price=float(result.discounted_price) if result.discounted_price else None,
                discount_percentage=float(result.discount_percentage) if result.discount_percentage else None,
                discount_value=float(result.discount_value) if result.discount_value else None,
                deal_type=result.deal_type or "discount",
                expires_at=result.expires_at.isoformat() if result.expires_at else None
            ))
        
        return deals
        
    except Exception as e:
        logger.error(f"Error getting deals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Price comparison endpoint
@router.post("/compare", response_model=ComparisonResponse)
async def compare_prices(
    product_name: str,
    platforms: Optional[List[str]] = None,
    include_discounts: bool = True,
    db: Session = Depends(get_db)
):
    """Compare prices across platforms for a specific product."""
    try:
        # Build base query
        query = db.query(
            Product.name.label("product_name"),
            Platform.name.label("platform_name"),
            Price.regular_price,
            Price.sale_price,
            Price.discount_percentage,
            PlatformProduct.is_available
        ).join(
            PlatformProduct, Product.id == PlatformProduct.product_id
        ).join(
            Platform, PlatformProduct.platform_id == Platform.id
        ).join(
            Price, PlatformProduct.id == Price.platform_product_id
        ).filter(
            Product.name.ilike(f"%{product_name}%"),
            Product.is_active == True,
            Price.is_active == True,
            Platform.is_active == True
        )
        
        # Filter by platforms if specified
        if platforms:
            query = query.filter(Platform.name.in_(platforms))
        
        # Execute query
        results = query.all()
        
        if not results:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Process results
        comparisons = []
        best_deal = None
        best_price = float('inf')
        
        for result in results:
            price = float(result.sale_price) if result.sale_price else float(result.regular_price)
            
            comparison = {
                "platform_name": result.platform_name,
                "regular_price": float(result.regular_price) if result.regular_price else None,
                "sale_price": float(result.sale_price) if result.sale_price else None,
                "discount_percentage": float(result.discount_percentage) if result.discount_percentage else None,
                "is_available": result.is_available,
                "final_price": price
            }
            
            comparisons.append(comparison)
            
            # Track best deal
            if price < best_price and result.is_available:
                best_price = price
                best_deal = comparison
        
        # Sort by price
        comparisons.sort(key=lambda x: x['final_price'])
        
        return ComparisonResponse(
            product_name=results[0].product_name,
            comparisons=comparisons,
            best_deal=best_deal
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing prices for {product_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Popular products endpoint
@router.get("/popular", response_model=List[PopularProductResponse])
async def get_popular_products(
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    platform: Optional[str] = Query(None, description="Platform filter"),
    db: Session = Depends(get_db)
):
    """Get popular products."""
    try:
        query = db.query(
            Product.id,
            Product.name,
            PopularProduct.view_count,
            PopularProduct.search_count,
            PopularProduct.order_count,
            Category.name.label("category_name"),
            Price.sale_price.label("current_price")
        ).join(
            PopularProduct, Product.id == PopularProduct.product_id
        ).join(
            Platform, PopularProduct.platform_id == Platform.id
        ).outerjoin(
            Category, Product.category_id == Category.id
        ).outerjoin(
            PlatformProduct, and_(
                Product.id == PlatformProduct.product_id,
                PlatformProduct.platform_id == Platform.id
            )
        ).outerjoin(
            Price, PlatformProduct.id == Price.platform_product_id
        ).filter(
            Product.is_active == True,
            Platform.is_active == True
        )
        
        # Filter by platform if specified
        if platform:
            query = query.filter(Platform.name.ilike(f"%{platform}%"))
        
        # Order by popularity
        query = query.order_by(PopularProduct.view_count.desc()).limit(limit)
        
        # Execute query
        results = query.all()
        
        return [
            PopularProductResponse(
                id=result.id,
                name=result.name,
                view_count=result.view_count,
                search_count=result.search_count,
                order_count=result.order_count,
                category_name=result.category_name,
                current_price=float(result.current_price) if result.current_price else None
            )
            for result in results
        ]
        
    except Exception as e:
        logger.error(f"Error getting popular products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Categories endpoint
@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    """Get all product categories."""
    try:
        categories = db.query(Category).filter(Category.is_active == True).all()
        
        return [
            {
                "id": category.id,
                "name": category.name,
                "slug": category.slug,
                "description": category.description,
                "image_url": category.image_url
            }
            for category in categories
        ]
        
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Brands endpoint
@router.get("/brands")
async def get_brands(db: Session = Depends(get_db)):
    """Get all brands."""
    try:
        brands = db.query(Brand).filter(Brand.is_active == True).all()
        
        return [
            {
                "id": brand.id,
                "name": brand.name,
                "slug": brand.slug,
                "description": brand.description,
                "logo_url": brand.logo_url
            }
            for brand in brands
        ]
        
    except Exception as e:
        logger.error(f"Error getting brands: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Search endpoint using natural language
@router.get("/search")
async def search_products(
    q: str = Query(..., description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    db: Session = Depends(get_db)
):
    """Search products using natural language."""
    try:
        # Use SQL agent for natural language search
        result = sql_agent.process_query(
            natural_language_query=f"Find products matching: {q}",
            max_results=limit
        )
        
        if result.success:
            return {
                "success": True,
                "data": result.data,
                "message": "Search completed successfully",
                "execution_time": result.execution_time,
                "rows_returned": result.rows_returned
            }
        else:
            return {
                "success": False,
                "data": [],
                "message": result.error_message,
                "execution_time": result.execution_time,
                "rows_returned": 0
            }
        
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Statistics endpoint
@router.get("/stats")
async def get_statistics(db: Session = Depends(get_db)):
    """Get platform statistics."""
    try:
        # Get basic counts
        total_products = db.query(Product).filter(Product.is_active == True).count()
        total_platforms = db.query(Platform).filter(Platform.is_active == True).count()
        total_categories = db.query(Category).filter(Category.is_active == True).count()
        total_brands = db.query(Brand).filter(Brand.is_active == True).count()
        
        return {
            "total_products": total_products,
            "total_platforms": total_platforms,
            "total_categories": total_categories,
            "total_brands": total_brands,
            "database_tables": 50,  # We have 50+ tables
            "last_updated": "2024-01-01T00:00:00Z"  # Placeholder
        }
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 