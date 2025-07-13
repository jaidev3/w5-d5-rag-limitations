"""Comprehensive database models for Quick Commerce Deals platform."""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Date, Text, 
    ForeignKey, Numeric, JSON, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


# ==================== PLATFORM MODELS ====================

class Platform(Base):
    """Quick commerce platforms (Blinkit, Zepto, etc.)"""
    __tablename__ = "platforms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(100), nullable=False)
    logo_url = Column(String(500))
    website_url = Column(String(500))
    app_store_url = Column(String(500))
    play_store_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    api_endpoint = Column(String(500))
    api_key = Column(String(500))
    delivery_fee = Column(Numeric(10, 2))
    min_order_amount = Column(Numeric(10, 2))
    max_delivery_distance = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class PlatformStore(Base):
    """Individual stores within platforms"""
    __tablename__ = "platform_stores"
    
    id = Column(Integer, primary_key=True, index=True)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)
    store_name = Column(String(200), nullable=False)
    store_code = Column(String(100), nullable=False)
    address = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    operating_hours = Column(JSON)
    delivery_radius = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
    
    platform = relationship("Platform", back_populates="stores")


class DeliveryZone(Base):
    """Delivery zones for platforms"""
    __tablename__ = "delivery_zones"
    
    id = Column(Integer, primary_key=True, index=True)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)
    zone_name = Column(String(200), nullable=False)
    zone_code = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False)
    postal_codes = Column(JSON)
    delivery_fee = Column(Numeric(10, 2))
    min_order_amount = Column(Numeric(10, 2))
    estimated_delivery_time = Column(Integer)  # minutes
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    platform = relationship("Platform", back_populates="delivery_zones")


# ==================== PRODUCT MODELS ====================

class Category(Base):
    """Product categories"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True)
    slug = Column(String(200), nullable=False, unique=True)
    description = Column(Text)
    image_url = Column(String(500))
    icon_url = Column(String(500))
    parent_id = Column(Integer, ForeignKey("categories.id"))
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    parent = relationship("Category", remote_side=[id])
    subcategories = relationship("Category", back_populates="parent")


class SubCategory(Base):
    """Product subcategories"""
    __tablename__ = "subcategories"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), nullable=False)
    description = Column(Text)
    image_url = Column(String(500))
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    category = relationship("Category", back_populates="subcategories")


class Brand(Base):
    """Product brands"""
    __tablename__ = "brands"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True)
    slug = Column(String(200), nullable=False, unique=True)
    description = Column(Text)
    logo_url = Column(String(500))
    website_url = Column(String(500))
    country_of_origin = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class Product(Base):
    """Main products table"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), nullable=False)
    slug = Column(String(500), nullable=False, unique=True)
    description = Column(Text)
    short_description = Column(Text)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    subcategory_id = Column(Integer, ForeignKey("subcategories.id"))
    brand_id = Column(Integer, ForeignKey("brands.id"))
    sku = Column(String(100), unique=True)
    barcode = Column(String(100), unique=True)
    product_type = Column(String(50))  # physical, digital, etc.
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    weight = Column(Float)
    weight_unit = Column(String(20))
    dimensions = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    category = relationship("Category", back_populates="products")
    subcategory = relationship("SubCategory", back_populates="products")
    brand = relationship("Brand", back_populates="products")


class ProductVariant(Base):
    """Product variants (size, color, etc.)"""
    __tablename__ = "product_variants"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    variant_name = Column(String(200), nullable=False)
    variant_value = Column(String(200), nullable=False)
    sku = Column(String(100), unique=True)
    additional_price = Column(Numeric(10, 2), default=0)
    weight = Column(Float)
    dimensions = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    product = relationship("Product", back_populates="variants")


class ProductImage(Base):
    """Product images"""
    __tablename__ = "product_images"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    image_url = Column(String(500), nullable=False)
    alt_text = Column(String(200))
    is_primary = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    
    product = relationship("Product", back_populates="images")


class ProductAttribute(Base):
    """Product attributes (organic, vegan, etc.)"""
    __tablename__ = "product_attributes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True)
    slug = Column(String(200), nullable=False, unique=True)
    description = Column(Text)
    attribute_type = Column(String(50))  # boolean, text, number, etc.
    is_filterable = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class ProductAttributeValue(Base):
    """Product attribute values"""
    __tablename__ = "product_attribute_values"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    attribute_id = Column(Integer, ForeignKey("product_attributes.id"), nullable=False)
    value = Column(String(500), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    product = relationship("Product", back_populates="attribute_values")
    attribute = relationship("ProductAttribute", back_populates="values")


class NutritionalInfo(Base):
    """Nutritional information for products"""
    __tablename__ = "nutritional_info"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    serving_size = Column(String(100))
    calories = Column(Float)
    protein = Column(Float)
    carbohydrates = Column(Float)
    fat = Column(Float)
    fiber = Column(Float)
    sugar = Column(Float)
    sodium = Column(Float)
    vitamins = Column(JSON)
    minerals = Column(JSON)
    allergens = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())
    
    product = relationship("Product", back_populates="nutritional_info")


# ==================== PRICING MODELS ====================

class PlatformProduct(Base):
    """Products available on specific platforms"""
    __tablename__ = "platform_products"
    
    id = Column(Integer, primary_key=True, index=True)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    platform_product_id = Column(String(200))  # Platform's internal ID
    platform_sku = Column(String(200))
    platform_name = Column(String(500))  # Platform's product name
    platform_url = Column(String(500))
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    platform = relationship("Platform", back_populates="products")
    product = relationship("Product", back_populates="platform_products")
    
    __table_args__ = (UniqueConstraint('platform_id', 'product_id', name='_platform_product_uc'),)


class Price(Base):
    """Current product prices"""
    __tablename__ = "prices"
    
    id = Column(Integer, primary_key=True, index=True)
    platform_product_id = Column(Integer, ForeignKey("platform_products.id"), nullable=False)
    regular_price = Column(Numeric(10, 2), nullable=False)
    sale_price = Column(Numeric(10, 2))
    discount_percentage = Column(Float)
    currency = Column(String(3), default="INR")
    is_active = Column(Boolean, default=True)
    effective_from = Column(DateTime, server_default=func.now())
    effective_to = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    
    platform_product = relationship("PlatformProduct", back_populates="prices")


class PriceHistory(Base):
    """Historical price data"""
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    platform_product_id = Column(Integer, ForeignKey("platform_products.id"), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    sale_price = Column(Numeric(10, 2))
    discount_percentage = Column(Float)
    currency = Column(String(3), default="INR")
    recorded_at = Column(DateTime, server_default=func.now())
    
    platform_product = relationship("PlatformProduct", back_populates="price_history")


class Discount(Base):
    """Discount information"""
    __tablename__ = "discounts"
    
    id = Column(Integer, primary_key=True, index=True)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)
    discount_type = Column(String(50), nullable=False)  # percentage, fixed, buy_one_get_one
    discount_value = Column(Numeric(10, 2), nullable=False)
    min_order_amount = Column(Numeric(10, 2))
    max_discount_amount = Column(Numeric(10, 2))
    code = Column(String(100))
    title = Column(String(200))
    description = Column(Text)
    terms_conditions = Column(Text)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    usage_limit = Column(Integer)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    
    platform = relationship("Platform", back_populates="discounts")


class ProductDiscount(Base):
    """Product-specific discounts"""
    __tablename__ = "product_discounts"
    
    id = Column(Integer, primary_key=True, index=True)
    discount_id = Column(Integer, ForeignKey("discounts.id"), nullable=False)
    platform_product_id = Column(Integer, ForeignKey("platform_products.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    discount = relationship("Discount", back_populates="product_discounts")
    platform_product = relationship("PlatformProduct", back_populates="discounts")


class Offer(Base):
    """Special offers and deals"""
    __tablename__ = "offers"
    
    id = Column(Integer, primary_key=True, index=True)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    offer_type = Column(String(50))  # flash_sale, combo, bulk_discount
    discount_percentage = Column(Float)
    discount_amount = Column(Numeric(10, 2))
    min_quantity = Column(Integer)
    max_quantity = Column(Integer)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    image_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
    
    platform = relationship("Platform", back_populates="offers")


class OfferProduct(Base):
    """Products included in offers"""
    __tablename__ = "offer_products"
    
    id = Column(Integer, primary_key=True, index=True)
    offer_id = Column(Integer, ForeignKey("offers.id"), nullable=False)
    platform_product_id = Column(Integer, ForeignKey("platform_products.id"), nullable=False)
    offer_price = Column(Numeric(10, 2))
    created_at = Column(DateTime, server_default=func.now())
    
    offer = relationship("Offer", back_populates="products")
    platform_product = relationship("PlatformProduct", back_populates="offers")


# ==================== INVENTORY MODELS ====================

class Inventory(Base):
    """Inventory levels for products"""
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    platform_product_id = Column(Integer, ForeignKey("platform_products.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("platform_stores.id"))
    quantity_available = Column(Integer, nullable=False)
    reserved_quantity = Column(Integer, default=0)
    reorder_level = Column(Integer, default=10)
    max_stock_level = Column(Integer, default=1000)
    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    platform_product = relationship("PlatformProduct", back_populates="inventory")
    store = relationship("PlatformStore", back_populates="inventory")


class StockMovement(Base):
    """Stock movement history"""
    __tablename__ = "stock_movements"
    
    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey("inventory.id"), nullable=False)
    movement_type = Column(String(50), nullable=False)  # in, out, adjustment
    quantity = Column(Integer, nullable=False)
    reference_id = Column(String(200))  # Order ID, Purchase ID, etc.
    reason = Column(String(200))
    created_at = Column(DateTime, server_default=func.now())
    
    inventory = relationship("Inventory", back_populates="movements")


class DeliverySlot(Base):
    """Available delivery slots"""
    __tablename__ = "delivery_slots"
    
    id = Column(Integer, primary_key=True, index=True)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)
    zone_id = Column(Integer, ForeignKey("delivery_zones.id"), nullable=False)
    slot_date = Column(Date, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    max_orders = Column(Integer, default=50)
    current_orders = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
    delivery_fee = Column(Numeric(10, 2))
    created_at = Column(DateTime, server_default=func.now())
    
    platform = relationship("Platform", back_populates="delivery_slots")
    zone = relationship("DeliveryZone", back_populates="delivery_slots")


# ==================== USER MODELS ====================

class User(Base):
    """User accounts"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), unique=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    date_of_birth = Column(Date)
    gender = Column(String(10))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime)


class UserAddress(Base):
    """User addresses"""
    __tablename__ = "user_addresses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    address_type = Column(String(50), nullable=False)  # home, work, other
    address_line1 = Column(String(255), nullable=False)
    address_line2 = Column(String(255))
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    
    user = relationship("User", back_populates="addresses")


class UserPreference(Base):
    """User preferences"""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    preference_key = Column(String(100), nullable=False)
    preference_value = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())
    
    user = relationship("User", back_populates="preferences")


class UserFavorite(Base):
    """User favorite products"""
    __tablename__ = "user_favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    user = relationship("User", back_populates="favorites")
    product = relationship("Product", back_populates="favorited_by")


# ==================== ORDER MODELS ====================

class Order(Base):
    """Customer orders"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)
    order_number = Column(String(100), unique=True, nullable=False)
    status = Column(String(50), nullable=False)  # pending, confirmed, delivered, cancelled
    total_amount = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0)
    delivery_fee = Column(Numeric(10, 2), default=0)
    tax_amount = Column(Numeric(10, 2), default=0)
    final_amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String(50))
    payment_status = Column(String(50))
    delivery_address = Column(JSON)
    estimated_delivery_time = Column(DateTime)
    actual_delivery_time = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    
    user = relationship("User", back_populates="orders")
    platform = relationship("Platform", back_populates="orders")


class OrderItem(Base):
    """Order items"""
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    platform_product_id = Column(Integer, ForeignKey("platform_products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0)
    total_price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    order = relationship("Order", back_populates="items")
    platform_product = relationship("PlatformProduct", back_populates="order_items")


# ==================== ANALYTICS MODELS ====================

class SearchQuery(Base):
    """User search queries"""
    __tablename__ = "search_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    query_text = Column(String(500), nullable=False)
    query_type = Column(String(50))  # natural_language, filter, etc.
    results_count = Column(Integer)
    execution_time = Column(Float)  # seconds
    was_successful = Column(Boolean, default=True)
    error_message = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    
    user = relationship("User", back_populates="search_queries")


class PopularProduct(Base):
    """Popular products tracking"""
    __tablename__ = "popular_products"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)
    view_count = Column(Integer, default=0)
    search_count = Column(Integer, default=0)
    order_count = Column(Integer, default=0)
    date = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    product = relationship("Product", back_populates="popularity")
    platform = relationship("Platform", back_populates="popular_products")


class PriceAlert(Base):
    """Price alerts set by users"""
    __tablename__ = "price_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    platform_product_id = Column(Integer, ForeignKey("platform_products.id"), nullable=False)
    target_price = Column(Numeric(10, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    notification_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    
    user = relationship("User", back_populates="price_alerts")
    platform_product = relationship("PlatformProduct", back_populates="price_alerts")


class ProductView(Base):
    """Product view tracking"""
    __tablename__ = "product_views"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)
    viewed_at = Column(DateTime, server_default=func.now())
    session_id = Column(String(255))
    ip_address = Column(String(45))
    user_agent = Column(Text)
    
    user = relationship("User", back_populates="product_views")
    product = relationship("Product", back_populates="views")
    platform = relationship("Platform", back_populates="product_views")


class DealAlert(Base):
    """Deal alerts and notifications"""
    __tablename__ = "deal_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    platform_id = Column(Integer, ForeignKey("platforms.id"))
    min_discount_percentage = Column(Float)
    max_price = Column(Numeric(10, 2))
    is_active = Column(Boolean, default=True)
    last_notification_sent = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    
    user = relationship("User", back_populates="deal_alerts")
    product = relationship("Product", back_populates="deal_alerts")
    category = relationship("Category", back_populates="deal_alerts")
    platform = relationship("Platform", back_populates="deal_alerts")


# ==================== REVIEW MODELS ====================

class Review(Base):
    """Product reviews"""
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    platform_id = Column(Integer, ForeignKey("platforms.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    title = Column(String(200))
    comment = Column(Text)
    is_verified_purchase = Column(Boolean, default=False)
    helpful_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    
    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")
    platform = relationship("Platform", back_populates="reviews")


class ReviewImage(Base):
    """Review images"""
    __tablename__ = "review_images"
    
    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=False)
    image_url = Column(String(500), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    review = relationship("Review", back_populates="images")


# ==================== NOTIFICATION MODELS ====================

class Notification(Base):
    """User notifications"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50))  # price_alert, deal_alert, order_update
    is_read = Column(Boolean, default=False)
    data = Column(JSON)  # Additional data
    created_at = Column(DateTime, server_default=func.now())
    
    user = relationship("User", back_populates="notifications")


# ==================== ADMIN MODELS ====================

class AdminUser(Base):
    """Admin users"""
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    role = Column(String(50), nullable=False)  # admin, moderator, analyst
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime)


class SystemLog(Base):
    """System logs"""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    module = Column(String(100))
    function = Column(String(100))
    user_id = Column(Integer, ForeignKey("users.id"))
    admin_id = Column(Integer, ForeignKey("admin_users.id"))
    ip_address = Column(String(45))
    user_agent = Column(Text)
    additional_data = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())


# ==================== CACHE MODELS ====================

class QueryCache(Base):
    """Query result caching"""
    __tablename__ = "query_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    query_hash = Column(String(255), unique=True, nullable=False)
    query_text = Column(Text, nullable=False)
    result_data = Column(JSON)
    execution_time = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)
    hit_count = Column(Integer, default=0)


class SchemaCache(Base):
    """Database schema caching"""
    __tablename__ = "schema_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String(255), nullable=False)
    column_info = Column(JSON, nullable=False)
    relationships = Column(JSON)
    indexes = Column(JSON)
    last_updated = Column(DateTime, server_default=func.now())


# ==================== PERFORMANCE MODELS ====================

class QueryPerformance(Base):
    """Query performance monitoring"""
    __tablename__ = "query_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    query_hash = Column(String(255), nullable=False)
    query_text = Column(Text, nullable=False)
    execution_time = Column(Float, nullable=False)
    rows_returned = Column(Integer)
    tables_used = Column(JSON)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())


class APIUsage(Base):
    """API usage tracking"""
    __tablename__ = "api_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    response_time = Column(Float)
    response_status = Column(Integer)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


# ==================== RELATIONSHIPS ====================

# Platform relationships
Platform.stores = relationship("PlatformStore", back_populates="platform")
Platform.delivery_zones = relationship("DeliveryZone", back_populates="platform")
Platform.products = relationship("PlatformProduct", back_populates="platform")
Platform.discounts = relationship("Discount", back_populates="platform")
Platform.offers = relationship("Offer", back_populates="platform")
Platform.delivery_slots = relationship("DeliverySlot", back_populates="platform")
Platform.orders = relationship("Order", back_populates="platform")
Platform.popular_products = relationship("PopularProduct", back_populates="platform")
Platform.product_views = relationship("ProductView", back_populates="platform")
Platform.deal_alerts = relationship("DealAlert", back_populates="platform")
Platform.reviews = relationship("Review", back_populates="platform")

# Product relationships
Category.products = relationship("Product", back_populates="category")
Category.subcategories = relationship("SubCategory", back_populates="category")
Category.deal_alerts = relationship("DealAlert", back_populates="category")
SubCategory.products = relationship("Product", back_populates="subcategory")
Brand.products = relationship("Product", back_populates="brand")
Product.variants = relationship("ProductVariant", back_populates="product")
Product.images = relationship("ProductImage", back_populates="product")
Product.attribute_values = relationship("ProductAttributeValue", back_populates="product")
Product.nutritional_info = relationship("NutritionalInfo", back_populates="product")
Product.platform_products = relationship("PlatformProduct", back_populates="product")
Product.favorited_by = relationship("UserFavorite", back_populates="product")
Product.popularity = relationship("PopularProduct", back_populates="product")
Product.views = relationship("ProductView", back_populates="product")
Product.deal_alerts = relationship("DealAlert", back_populates="product")
Product.reviews = relationship("Review", back_populates="product")
ProductAttribute.values = relationship("ProductAttributeValue", back_populates="attribute")

# Platform Product relationships
PlatformProduct.prices = relationship("Price", back_populates="platform_product")
PlatformProduct.price_history = relationship("PriceHistory", back_populates="platform_product")
PlatformProduct.discounts = relationship("ProductDiscount", back_populates="platform_product")
PlatformProduct.offers = relationship("OfferProduct", back_populates="platform_product")
PlatformProduct.inventory = relationship("Inventory", back_populates="platform_product")
PlatformProduct.order_items = relationship("OrderItem", back_populates="platform_product")
PlatformProduct.price_alerts = relationship("PriceAlert", back_populates="platform_product")

# User relationships
User.addresses = relationship("UserAddress", back_populates="user")
User.preferences = relationship("UserPreference", back_populates="user")
User.favorites = relationship("UserFavorite", back_populates="user")
User.orders = relationship("Order", back_populates="user")
User.search_queries = relationship("SearchQuery", back_populates="user")
User.price_alerts = relationship("PriceAlert", back_populates="user")
User.product_views = relationship("ProductView", back_populates="user")
User.deal_alerts = relationship("DealAlert", back_populates="user")
User.reviews = relationship("Review", back_populates="user")
User.notifications = relationship("Notification", back_populates="user")

# Order relationships
Order.items = relationship("OrderItem", back_populates="order")

# Other relationships
PlatformStore.inventory = relationship("Inventory", back_populates="store")
DeliveryZone.delivery_slots = relationship("DeliverySlot", back_populates="zone")
Discount.product_discounts = relationship("ProductDiscount", back_populates="discount")
Offer.products = relationship("OfferProduct", back_populates="offer")
Inventory.movements = relationship("StockMovement", back_populates="inventory")
Review.images = relationship("ReviewImage", back_populates="review")


# ==================== INDEXES ====================

# Add indexes for performance
Index('idx_platform_product_platform_id', PlatformProduct.platform_id)
Index('idx_platform_product_product_id', PlatformProduct.product_id)
Index('idx_price_platform_product_id', Price.platform_product_id)
Index('idx_price_history_platform_product_id', PriceHistory.platform_product_id)
Index('idx_price_history_recorded_at', PriceHistory.recorded_at)
Index('idx_inventory_platform_product_id', Inventory.platform_product_id)
Index('idx_product_category_id', Product.category_id)
Index('idx_product_brand_id', Product.brand_id)
Index('idx_product_is_active', Product.is_active)
Index('idx_user_email', User.email)
Index('idx_order_user_id', Order.user_id)
Index('idx_order_platform_id', Order.platform_id)
Index('idx_search_query_user_id', SearchQuery.user_id)
Index('idx_search_query_created_at', SearchQuery.created_at)
Index('idx_product_view_product_id', ProductView.product_id)
Index('idx_product_view_user_id', ProductView.user_id)
Index('idx_product_view_viewed_at', ProductView.viewed_at)
Index('idx_query_cache_query_hash', QueryCache.query_hash)
Index('idx_query_cache_expires_at', QueryCache.expires_at)
Index('idx_query_performance_created_at', QueryPerformance.created_at)
Index('idx_api_usage_user_id', APIUsage.user_id)
Index('idx_api_usage_created_at', APIUsage.created_at) 