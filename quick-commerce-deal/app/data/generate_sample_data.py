"""Sample data generator for the Quick Commerce Deals platform."""

import logging
import random
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any
from faker import Faker

from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.database.models import *
from app.config import settings

logger = logging.getLogger(__name__)
fake = Faker()


class SampleDataGenerator:
    """Generates realistic sample data for all database tables."""
    
    def __init__(self):
        self.db = SessionLocal()
        self.platforms = []
        self.categories = []
        self.brands = []
        self.products = []
        self.users = []
        
        # Indian product names for realism
        self.indian_products = {
            'vegetables': [
                'Onion', 'Potato', 'Tomato', 'Carrot', 'Cabbage', 'Cauliflower',
                'Green Peas', 'Spinach', 'Brinjal', 'Okra', 'Capsicum', 'Ginger',
                'Garlic', 'Green Chili', 'Coriander', 'Mint', 'Cucumber', 'Radish'
            ],
            'fruits': [
                'Apple', 'Banana', 'Orange', 'Mango', 'Grapes', 'Papaya',
                'Pineapple', 'Watermelon', 'Pomegranate', 'Guava', 'Kiwi',
                'Strawberry', 'Lemon', 'Sweet Lime', 'Coconut', 'Dates'
            ],
            'dairy': [
                'Milk', 'Curd', 'Paneer', 'Butter', 'Cheese', 'Ghee',
                'Buttermilk', 'Cream', 'Lassi', 'Yogurt'
            ],
            'grains': [
                'Rice', 'Wheat Flour', 'Basmati Rice', 'Brown Rice', 'Quinoa',
                'Oats', 'Barley', 'Ragi', 'Semolina', 'Besan'
            ],
            'snacks': [
                'Biscuits', 'Chips', 'Namkeen', 'Cookies', 'Crackers',
                'Nuts', 'Popcorn', 'Bhujia', 'Sev', 'Wafers'
            ],
            'beverages': [
                'Tea', 'Coffee', 'Juice', 'Soft Drinks', 'Energy Drinks',
                'Mineral Water', 'Coconut Water', 'Lassi', 'Buttermilk'
            ],
            'spices': [
                'Turmeric', 'Red Chili Powder', 'Cumin', 'Coriander Seeds',
                'Garam Masala', 'Mustard Seeds', 'Fenugreek', 'Cardamom',
                'Cinnamon', 'Cloves', 'Bay Leaves', 'Asafoetida'
            ]
        }
        
        self.platform_names = [
            'Blinkit', 'Zepto', 'Instamart', 'BigBasket Now', 'Dunzo',
            'Grofers', 'Amazon Fresh', 'Flipkart Quick'
        ]
        
        self.brand_names = [
            'Amul', 'Britannia', 'Parle', 'ITC', 'Nestle', 'Tata',
            'Dabur', 'Patanjali', 'Mother Dairy', 'Haldirams',
            'Bikaji', 'MTR', 'Everest', 'MDH', 'Catch', 'Aashirvaad'
        ]
    
    def generate_all_data(self, size: str = "medium"):
        """Generate all sample data."""
        try:
            logger.info(f"Generating {size} sample data...")
            
            # Determine sizes based on parameter
            sizes = {
                "small": {"platforms": 4, "categories": 10, "brands": 10, "products": 100, "users": 50},
                "medium": {"platforms": 6, "categories": 15, "brands": 15, "products": 500, "users": 200},
                "large": {"platforms": 8, "categories": 20, "brands": 20, "products": 1000, "users": 500}
            }
            
            config = sizes.get(size, sizes["medium"])
            
            # Generate in order due to foreign key dependencies
            self.generate_platforms(config["platforms"])
            self.generate_categories(config["categories"])
            self.generate_brands(config["brands"])
            self.generate_products(config["products"])
            self.generate_users(config["users"])
            
            # Generate platform-specific data
            self.generate_platform_stores()
            self.generate_delivery_zones()
            self.generate_platform_products()
            self.generate_prices()
            self.generate_inventory()
            self.generate_discounts()
            self.generate_offers()
            
            # Generate user-related data
            self.generate_user_data()
            self.generate_orders()
            self.generate_reviews()
            
            # Generate analytics data
            self.generate_analytics_data()
            
            # Generate performance monitoring data
            self.generate_monitoring_data()
            
            self.db.commit()
            logger.info("Sample data generation completed successfully!")
            
        except Exception as e:
            logger.error(f"Error generating sample data: {e}")
            self.db.rollback()
            raise
        finally:
            self.db.close()
    
    def generate_platforms(self, count: int):
        """Generate platform data."""
        logger.info(f"Generating {count} platforms...")
        
        for i in range(count):
            platform_name = self.platform_names[i % len(self.platform_names)]
            
            platform = Platform(
                name=platform_name.lower().replace(' ', ''),
                display_name=platform_name,
                logo_url=f"https://example.com/logos/{platform_name.lower().replace(' ', '')}.png",
                website_url=f"https://{platform_name.lower().replace(' ', '')}.com",
                delivery_fee=random.uniform(0, 50),
                min_order_amount=random.uniform(99, 299),
                max_delivery_distance=random.uniform(5, 25),
                is_active=True
            )
            
            self.db.add(platform)
            self.platforms.append(platform)
    
    def generate_categories(self, count: int):
        """Generate category data."""
        logger.info(f"Generating {count} categories...")
        
        category_names = list(self.indian_products.keys())
        additional_categories = [
            'Personal Care', 'Household', 'Baby Care', 'Pet Care',
            'Beauty', 'Health', 'Frozen Foods', 'Bakery'
        ]
        
        all_categories = category_names + additional_categories
        
        for i in range(count):
            cat_name = all_categories[i % len(all_categories)]
            
            category = Category(
                name=cat_name.title(),
                slug=cat_name.lower().replace(' ', '-'),
                description=f"Fresh and quality {cat_name.lower()} products",
                image_url=f"https://example.com/categories/{cat_name.lower().replace(' ', '')}.jpg",
                sort_order=i,
                is_active=True
            )
            
            self.db.add(category)
            self.categories.append(category)
    
    def generate_brands(self, count: int):
        """Generate brand data."""
        logger.info(f"Generating {count} brands...")
        
        for i in range(count):
            brand_name = self.brand_names[i % len(self.brand_names)]
            
            brand = Brand(
                name=brand_name,
                slug=brand_name.lower().replace(' ', '-'),
                description=f"Premium quality products from {brand_name}",
                logo_url=f"https://example.com/brands/{brand_name.lower().replace(' ', '')}.png",
                country_of_origin="India",
                is_active=True
            )
            
            self.db.add(brand)
            self.brands.append(brand)
    
    def generate_products(self, count: int):
        """Generate product data."""
        logger.info(f"Generating {count} products...")
        
        for i in range(count):
            # Choose random category
            category = random.choice(self.categories)
            category_name = category.name.lower()
            
            # Choose product based on category
            if category_name in self.indian_products:
                product_name = random.choice(self.indian_products[category_name])
            else:
                product_name = fake.word().title()
            
            # Add variety to product names
            variants = ['Fresh', 'Organic', 'Premium', 'Regular', 'Local']
            if random.random() < 0.3:
                product_name = f"{random.choice(variants)} {product_name}"
            
            # Add weight/size
            weights = ['1kg', '500g', '250g', '1L', '500ml', '100g', '2kg']
            if random.random() < 0.5:
                product_name = f"{product_name} - {random.choice(weights)}"
            
            product = Product(
                name=product_name,
                slug=product_name.lower().replace(' ', '-').replace('.', ''),
                description=f"High quality {product_name.lower()} sourced from trusted suppliers",
                short_description=f"Fresh {product_name.lower()}",
                category_id=category.id,
                brand_id=random.choice(self.brands).id if random.random() < 0.7 else None,
                sku=f"SKU{i+1:06d}",
                barcode=f"{random.randint(1000000000000, 9999999999999)}",
                product_type="physical",
                is_active=True,
                is_featured=random.random() < 0.1,
                weight=random.uniform(0.1, 5.0),
                weight_unit="kg"
            )
            
            self.db.add(product)
            self.products.append(product)
    
    def generate_users(self, count: int):
        """Generate user data."""
        logger.info(f"Generating {count} users...")
        
        for i in range(count):
            user = User(
                email=fake.email(),
                phone=f"+91{random.randint(7000000000, 9999999999)}",
                password_hash=fake.password(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=70),
                gender=random.choice(['Male', 'Female', 'Other']),
                is_active=True,
                is_verified=random.random() < 0.8,
                created_at=fake.date_time_between(start_date='-2y', end_date='now')
            )
            
            self.db.add(user)
            self.users.append(user)
    
    def generate_platform_stores(self):
        """Generate platform store data."""
        logger.info("Generating platform stores...")
        
        for platform in self.platforms:
            # Generate 2-5 stores per platform
            for i in range(random.randint(2, 5)):
                store = PlatformStore(
                    platform_id=platform.id,
                    store_name=f"{platform.display_name} Store {i+1}",
                    store_code=f"{platform.name.upper()}{i+1:03d}",
                    address=fake.address(),
                    latitude=random.uniform(12.9, 13.1),  # Bangalore coordinates
                    longitude=random.uniform(77.5, 77.7),
                    phone=f"+91{random.randint(7000000000, 9999999999)}",
                    is_active=True,
                    delivery_radius=random.uniform(3, 15)
                )
                
                self.db.add(store)
    
    def generate_delivery_zones(self):
        """Generate delivery zone data."""
        logger.info("Generating delivery zones...")
        
        zones = [
            "Koramangala", "Indiranagar", "Whitefield", "Electronic City",
            "Marathahalli", "BTM Layout", "Jayanagar", "Banashankari"
        ]
        
        for platform in self.platforms:
            for zone_name in zones:
                zone = DeliveryZone(
                    platform_id=platform.id,
                    zone_name=zone_name,
                    zone_code=f"{platform.name.upper()}_{zone_name.upper().replace(' ', '')}",
                    city="Bangalore",
                    state="Karnataka",
                    country="India",
                    delivery_fee=random.uniform(0, 30),
                    min_order_amount=random.uniform(99, 199),
                    estimated_delivery_time=random.randint(15, 60),
                    is_active=True
                )
                
                self.db.add(zone)
    
    def generate_platform_products(self):
        """Generate platform product mappings."""
        logger.info("Generating platform products...")
        
        for product in self.products:
            # Each product is available on 3-6 platforms
            available_platforms = random.sample(self.platforms, random.randint(3, 6))
            
            for platform in available_platforms:
                platform_product = PlatformProduct(
                    platform_id=platform.id,
                    product_id=product.id,
                    platform_product_id=f"{platform.name}_{product.id}",
                    platform_sku=f"{platform.name.upper()}{product.id:06d}",
                    platform_name=product.name,
                    is_available=random.random() < 0.9
                )
                
                self.db.add(platform_product)
    
    def generate_prices(self):
        """Generate price data."""
        logger.info("Generating prices...")
        
        self.db.flush()  # To get platform_product IDs
        
        platform_products = self.db.query(PlatformProduct).all()
        
        for pp in platform_products:
            # Generate base price
            base_price = random.uniform(10, 500)
            
            # Add some variation based on platform
            platform_multiplier = {
                'blinkit': 1.0,
                'zepto': 1.05,
                'instamart': 0.98,
                'bigbasket': 1.02,
                'dunzo': 1.08,
                'grofers': 0.95,
                'amazon': 1.03,
                'flipkart': 1.01
            }
            
            platform_name = pp.platform.name.lower()
            multiplier = platform_multiplier.get(platform_name, 1.0)
            regular_price = base_price * multiplier
            
            # Generate discount (30% chance)
            discount_pct = random.uniform(5, 40) if random.random() < 0.3 else 0
            sale_price = regular_price * (1 - discount_pct / 100)
            
            price = Price(
                platform_product_id=pp.id,
                regular_price=Decimal(str(round(regular_price, 2))),
                sale_price=Decimal(str(round(sale_price, 2))),
                discount_percentage=discount_pct,
                currency="INR",
                is_active=True
            )
            
            self.db.add(price)
            
            # Generate price history
            for days_back in range(1, 30):
                historical_price = base_price * random.uniform(0.9, 1.1)
                history = PriceHistory(
                    platform_product_id=pp.id,
                    price=Decimal(str(round(historical_price, 2))),
                    currency="INR",
                    recorded_at=datetime.now() - timedelta(days=days_back)
                )
                self.db.add(history)
    
    def generate_inventory(self):
        """Generate inventory data."""
        logger.info("Generating inventory...")
        
        self.db.flush()
        platform_products = self.db.query(PlatformProduct).all()
        
        for pp in platform_products:
            inventory = Inventory(
                platform_product_id=pp.id,
                quantity_available=random.randint(0, 100),
                reserved_quantity=random.randint(0, 10),
                reorder_level=random.randint(5, 20),
                max_stock_level=random.randint(50, 200)
            )
            
            self.db.add(inventory)
    
    def generate_discounts(self):
        """Generate discount data."""
        logger.info("Generating discounts...")
        
        discount_types = ['percentage', 'fixed', 'buy_one_get_one']
        
        for platform in self.platforms:
            # Generate 5-15 discounts per platform
            for i in range(random.randint(5, 15)):
                discount_type = random.choice(discount_types)
                
                discount = Discount(
                    platform_id=platform.id,
                    discount_type=discount_type,
                    discount_value=random.uniform(10, 50) if discount_type == 'percentage' else random.uniform(20, 100),
                    min_order_amount=random.uniform(99, 299),
                    max_discount_amount=random.uniform(50, 200),
                    code=f"SAVE{random.randint(10, 99)}" if random.random() < 0.5 else None,
                    title=f"Special {discount_type.title()} Discount",
                    description=f"Get amazing {discount_type} discount on your orders",
                    start_date=datetime.now() - timedelta(days=random.randint(1, 30)),
                    end_date=datetime.now() + timedelta(days=random.randint(1, 30)),
                    is_active=True,
                    usage_limit=random.randint(100, 1000),
                    usage_count=random.randint(0, 50)
                )
                
                self.db.add(discount)
    
    def generate_offers(self):
        """Generate offer data."""
        logger.info("Generating offers...")
        
        offer_types = ['flash_sale', 'combo', 'bulk_discount']
        
        for platform in self.platforms:
            # Generate 3-8 offers per platform
            for i in range(random.randint(3, 8)):
                offer = Offer(
                    platform_id=platform.id,
                    title=f"Special {random.choice(['Flash', 'Mega', 'Super'])} Deal",
                    description=f"Amazing offer on selected products",
                    offer_type=random.choice(offer_types),
                    discount_percentage=random.uniform(10, 50),
                    min_quantity=random.randint(1, 5),
                    max_quantity=random.randint(10, 50),
                    start_date=datetime.now() - timedelta(days=random.randint(1, 10)),
                    end_date=datetime.now() + timedelta(days=random.randint(1, 20)),
                    is_active=True
                )
                
                self.db.add(offer)
    
    def generate_user_data(self):
        """Generate user-related data."""
        logger.info("Generating user data...")
        
        for user in self.users:
            # Generate addresses
            for i in range(random.randint(1, 3)):
                address = UserAddress(
                    user_id=user.id,
                    address_type=random.choice(['home', 'work', 'other']),
                    address_line1=fake.street_address(),
                    city="Bangalore",
                    state="Karnataka",
                    postal_code=fake.postcode(),
                    country="India",
                    is_default=i == 0
                )
                self.db.add(address)
            
            # Generate preferences
            preferences = ['notifications', 'email_updates', 'sms_alerts']
            for pref in preferences:
                user_pref = UserPreference(
                    user_id=user.id,
                    preference_key=pref,
                    preference_value=str(random.choice([True, False]))
                )
                self.db.add(user_pref)
            
            # Generate favorites
            favorite_products = random.sample(self.products, random.randint(3, 10))
            for product in favorite_products:
                favorite = UserFavorite(
                    user_id=user.id,
                    product_id=product.id
                )
                self.db.add(favorite)
    
    def generate_orders(self):
        """Generate order data."""
        logger.info("Generating orders...")
        
        for user in self.users:
            # Generate 1-5 orders per user
            for i in range(random.randint(1, 5)):
                platform = random.choice(self.platforms)
                
                order = Order(
                    user_id=user.id,
                    platform_id=platform.id,
                    order_number=f"ORD{random.randint(100000, 999999)}",
                    status=random.choice(['pending', 'confirmed', 'delivered', 'cancelled']),
                    total_amount=random.uniform(200, 2000),
                    discount_amount=random.uniform(0, 200),
                    delivery_fee=random.uniform(0, 50),
                    tax_amount=random.uniform(10, 100),
                    final_amount=random.uniform(200, 2000),
                    payment_method=random.choice(['card', 'wallet', 'cod']),
                    payment_status=random.choice(['pending', 'completed', 'failed']),
                    created_at=fake.date_time_between(start_date='-1y', end_date='now')
                )
                
                self.db.add(order)
    
    def generate_reviews(self):
        """Generate review data."""
        logger.info("Generating reviews...")
        
        self.db.flush()
        orders = self.db.query(Order).all()
        
        for order in orders:
            # Generate reviews for some orders
            if random.random() < 0.3:
                product = random.choice(self.products)
                
                review = Review(
                    user_id=order.user_id,
                    product_id=product.id,
                    platform_id=order.platform_id,
                    rating=random.randint(1, 5),
                    title=f"Review for {product.name}",
                    comment=fake.text(max_nb_chars=200),
                    is_verified_purchase=True,
                    helpful_count=random.randint(0, 50)
                )
                
                self.db.add(review)
    
    def generate_analytics_data(self):
        """Generate analytics data."""
        logger.info("Generating analytics data...")
        
        # Generate popular products
        for product in random.sample(self.products, min(100, len(self.products))):
            for platform in random.sample(self.platforms, random.randint(1, 3)):
                popular = PopularProduct(
                    product_id=product.id,
                    platform_id=platform.id,
                    view_count=random.randint(10, 1000),
                    search_count=random.randint(5, 200),
                    order_count=random.randint(1, 50),
                    date=datetime.now().date()
                )
                self.db.add(popular)
        
        # Generate search queries
        sample_queries = [
            "cheapest onions", "best deals", "organic vegetables",
            "discount on fruits", "fresh milk", "compare prices"
        ]
        
        for _ in range(200):
            query = SearchQuery(
                user_id=random.choice(self.users).id if random.random() < 0.7 else None,
                query_text=random.choice(sample_queries),
                query_type="natural_language",
                results_count=random.randint(5, 50),
                execution_time=random.uniform(0.1, 2.0),
                was_successful=random.random() < 0.9
            )
            self.db.add(query)
    
    def generate_monitoring_data(self):
        """Generate monitoring and performance data."""
        logger.info("Generating monitoring data...")
        
        # Generate query performance data
        for _ in range(100):
            perf = QueryPerformance(
                query_hash=fake.md5(),
                query_text="SELECT * FROM products WHERE name LIKE '%onion%'",
                execution_time=random.uniform(0.05, 1.0),
                rows_returned=random.randint(1, 100),
                user_id=random.choice(self.users).id if random.random() < 0.8 else None
            )
            self.db.add(perf)
        
        # Generate API usage data
        endpoints = ["/api/v1/products", "/api/v1/deals", "/api/v1/compare", "/api/v1/query"]
        
        for _ in range(500):
            usage = APIUsage(
                user_id=random.choice(self.users).id if random.random() < 0.8 else None,
                endpoint=random.choice(endpoints),
                method=random.choice(["GET", "POST"]),
                response_time=random.uniform(0.1, 2.0),
                response_status=random.choices([200, 404, 500], weights=[0.8, 0.15, 0.05])[0],
                ip_address=fake.ipv4()
            )
            self.db.add(usage)


def generate_all_sample_data(size: str = "medium"):
    """Generate all sample data."""
    generator = SampleDataGenerator()
    generator.generate_all_data(size)


if __name__ == "__main__":
    import sys
    size = sys.argv[1] if len(sys.argv) > 1 else "medium"
    generate_all_sample_data(size) 