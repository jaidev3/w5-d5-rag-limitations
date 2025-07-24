import sqlite3
import os
from datetime import datetime

# Paths to the database files
DB_PATHS = {
    'blinkit': os.path.join(os.path.dirname(__file__), '../db/blinkit.db'),
    'zepto': os.path.join(os.path.dirname(__file__), '../db/zepto.db'),
    'instamart': os.path.join(os.path.dirname(__file__), '../db/instamart.db'),
}

# Common product names to be used across all platforms
COMMON_PRODUCTS = [
    'Apple',
    'Milk 1L',
    'Chips',
    'Banana',
    'Orange Juice 1L',
    'Shampoo 200ml',
    'Detergent 1kg',
    'Bread',
    'Ice Cream 500ml',
    'Floor Cleaner 1L',
    'Tomato',
    'Cheese 200g',
]

# Sample data for each platform with consistent product names
SAMPLE_DATA = {
    'blinkit': {
        'platform_info': [
            ('Blinkit', 10, 15, datetime.now()),
        ],
        'categories': [
            ('Groceries', None, True, datetime.now()),
            ('Fruits & Vegetables', 1, True, datetime.now()),
            ('Dairy', 1, True, datetime.now()),
            ('Snacks', None, True, datetime.now()),
            ('Beverages', None, True, datetime.now()),
            ('Personal Care', None, True, datetime.now()),
            ('Household Essentials', None, True, datetime.now()),
            ('Bakery', 1, True, datetime.now()),
            ('Frozen Foods', 1, True, datetime.now()),
            ('Cleaning Supplies', 7, True, datetime.now()),
        ],
        'stores': [
            ('Blinkit Store Delhi', 'Delhi', '110001', True, datetime.now()),
            ('Blinkit Store Mumbai', 'Mumbai', '400001', True, datetime.now()),
            ('Blinkit Store Bangalore', 'Bangalore', '560001', True, datetime.now()),
            ('Blinkit Store Chennai', 'Chennai', '600001', True, datetime.now()),
            ('Blinkit Store Pune', 'Pune', '411001', True, datetime.now()),
        ],
        'products': [
            ('Apple', 2, 1, 120.00, 50, True, datetime.now()),
            ('Milk 1L', 3, 1, 60.00, 100, True, datetime.now()),
            ('Chips', 4, 2, 20.00, 200, True, datetime.now()),
            ('Banana', 2, 2, 40.00, 80, True, datetime.now()),
            ('Orange Juice 1L', 5, 3, 100.00, 60, True, datetime.now()),
            ('Shampoo 200ml', 6, 3, 150.00, 40, True, datetime.now()),
            ('Detergent 1kg', 7, 4, 200.00, 30, True, datetime.now()),
            ('Bread', 8, 4, 30.00, 90, True, datetime.now()),
            ('Ice Cream 500ml', 9, 5, 250.00, 20, True, datetime.now()),
            ('Floor Cleaner 1L', 10, 5, 120.00, 50, True, datetime.now()),
            ('Tomato', 2, 1, 30.00, 100, True, datetime.now()),
            ('Cheese 200g', 3, 2, 80.00, 70, True, datetime.now()),
        ],
    },
    'zepto': {
        'platform_info': [
            ('Zepto', 10, 10, datetime.now()),
        ],
        'categories': [
            ('Essentials', None, True, datetime.now()),
            ('Produce', 1, True, datetime.now()),
            ('Beverages', 1, True, datetime.now()),
            ('Bakery', None, True, datetime.now()),
            ('Snacks & Sweets', None, True, datetime.now()),
            ('Dairy & Eggs', 1, True, datetime.now()),
            ('Personal Care', None, True, datetime.now()),
            ('Household', None, True, datetime.now()),
            ('Frozen', 1, True, datetime.now()),
            ('Cleaning', 8, True, datetime.now()),
        ],
        'stores': [
            ('Zepto Hub Bangalore', 'Bangalore', '560001', True, datetime.now()),
            ('Zepto Hub Chennai', 'Chennai', '600001', True, datetime.now()),
            ('Zepto Hub Delhi', 'Delhi', '110001', True, datetime.now()),
            ('Zepto Hub Mumbai', 'Mumbai', '400001', True, datetime.now()),
            ('Zepto Hub Pune', 'Pune', '411001', True, datetime.now()),
        ],
        'products': [
            ('Apple', 2, 1, 85.00, 55, True, datetime.now()),
            ('Milk 1L', 6, 1, 58.00, 110, True, datetime.now()),
            ('Chips', 5, 2, 22.00, 180, True, datetime.now()),
            ('Banana', 2, 2, 45.00, 85, True, datetime.now()),
            ('Orange Juice 1L', 3, 3, 95.00, 65, True, datetime.now()),
            ('Shampoo 200ml', 7, 3, 140.00, 45, True, datetime.now()),
            ('Detergent 1kg', 8, 4, 190.00, 35, True, datetime.now()),
            ('Bread', 4, 4, 32.00, 95, True, datetime.now()),
            ('Ice Cream 500ml', 9, 5, 240.00, 25, True, datetime.now()),
            ('Floor Cleaner 1L', 10, 5, 115.00, 55, True, datetime.now()),
            ('Tomato', 2, 1, 28.00, 110, True, datetime.now()),
            ('Cheese 200g', 6, 2, 75.00, 75, True, datetime.now()),
        ],
    },
    'instamart': {
        'platform_info': [
            ('Instamart', 15, 25, datetime.now()),
        ],
        'categories': [
            ('Daily Needs', None, True, datetime.now()),
            ('Fresh Produce', 1, True, datetime.now()),
            ('Personal Care', 1, True, datetime.now()),
            ('Household', None, True, datetime.now()),
            ('Beverages', None, True, datetime.now()),
            ('Snacks', None, True, datetime.now()),
            ('Dairy', 1, True, datetime.now()),
            ('Bakery & Sweets', None, True, datetime.now()),
            ('Frozen Foods', 1, True, datetime.now()),
            ('Cleaning Supplies', 4, True, datetime.now()),
        ],
        'stores': [
            ('Instamart Store Pune', 'Pune', '411001', True, datetime.now()),
            ('Instamart Store Kolkata', 'Kolkata', '700001', True, datetime.now()),
            ('Instamart Store Delhi', 'Delhi', '110001', True, datetime.now()),
            ('Instamart Store Mumbai', 'Mumbai', '400001', True, datetime.now()),
            ('Instamart Store Bangalore', 'Bangalore', '560001', True, datetime.now()),
        ],
        'products': [
            ('Apple', 2, 1, 90.00, 60, True, datetime.now()),
            ('Milk 1L', 7, 1, 62.00, 95, True, datetime.now()),
            ('Chips', 6, 2, 25.00, 190, True, datetime.now()),
            ('Banana', 2, 2, 50.00, 75, True, datetime.now()),
            ('Orange Juice 1L', 5, 3, 105.00, 70, True, datetime.now()),
            ('Shampoo 200ml', 3, 3, 145.00, 50, True, datetime.now()),
            ('Detergent 1kg', 4, 4, 210.00, 40, True, datetime.now()),
            ('Bread', 8, 4, 35.00, 100, True, datetime.now()),
            ('Ice Cream 500ml', 9, 5, 260.00, 30, True, datetime.now()),
            ('Floor Cleaner 1L', 10, 5, 125.00, 60, True, datetime.now()),
            ('Tomato', 2, 1, 32.00, 120, True, datetime.now()),
            ('Cheese 200g', 7, 2, 85.00, 80, True, datetime.now()),
        ],
    },
}

def insert_sample_data(db_path, platform_data, platform):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        with conn:
            # Insert platform info if not exists (since it's one row)
            cursor.executemany(
                f"INSERT OR IGNORE INTO {platform}_platform_info (platform_name, delivery_time_min, delivery_time_max, created_at) VALUES (?, ?, ?, ?)",
                platform_data['platform_info']
            )
            # Insert categories
            cursor.executemany(
                f"INSERT INTO {platform}_categories (name, parent_id, is_active, created_at) VALUES (?, ?, ?, ?)",
                platform_data['categories']
            )
            # Insert stores
            cursor.executemany(
                f"INSERT INTO {platform}_stores (name, city, pincode, is_active, created_at) VALUES (?, ?, ?, ?, ?)",
                platform_data['stores']
            )
            # Insert products
            cursor.executemany(
                f"INSERT INTO {platform}_products (name, category_id, store_id, price, stock, is_active, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                platform_data['products']
            )
        print(f"Sample data with uniform product names inserted into {db_path}")
    except Exception as e:
        print(f"Error inserting sample data into {db_path}: {e}")
    finally:
        conn.close()

def main():
    """Main function to insert sample data into all databases"""
    print("📦 Adding sample data to databases...\n")
    
    for platform, db_path in DB_PATHS.items():
        if platform not in SAMPLE_DATA:
            print(f"[SKIP] No sample data defined for {platform}")
            continue
        print(f"Processing {platform.upper()} database...")
        insert_sample_data(db_path, SAMPLE_DATA[platform], platform)
        print(f"✅ {platform.upper()} database populated successfully!\n")
    
    print("🎉 All databases have been populated with sample data!")

if __name__ == "__main__":
    main()