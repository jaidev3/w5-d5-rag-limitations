import sqlite3
import os

# Paths to the database files
DB_PATHS = {
    'blinkit': os.path.join(os.path.dirname(__file__), '../db/blinkit.db'),
    'zepto': os.path.join(os.path.dirname(__file__), '../db/zepto.db'),
    'instamart': os.path.join(os.path.dirname(__file__), '../db/instamart.db'),
}

# Paste the SQL CREATE TABLE statements for each platform below (remove the # and indentation)
BLINKIT_SCHEMA = '''
CREATE TABLE blinkit_platform_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform_name TEXT NOT NULL DEFAULT 'Blinkit',
    delivery_time_min INTEGER DEFAULT 10,
    delivery_time_max INTEGER DEFAULT 15,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE blinkit_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    parent_id INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES blinkit_categories(id)
);

CREATE TABLE blinkit_stores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    pincode TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE blinkit_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    store_id INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES blinkit_categories(id),
    FOREIGN KEY (store_id) REFERENCES blinkit_stores(id)
);
'''

ZEPTO_SCHEMA = '''
CREATE TABLE zepto_platform_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform_name TEXT NOT NULL DEFAULT 'Zepto',
    delivery_time_min INTEGER DEFAULT 10,
    delivery_time_max INTEGER DEFAULT 10,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE zepto_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    parent_id INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES zepto_categories(id)
);

CREATE TABLE zepto_stores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    pincode TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE zepto_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    store_id INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES zepto_categories(id),
    FOREIGN KEY (store_id) REFERENCES zepto_stores(id)
);

'''

INSTAMART_SCHEMA = '''
CREATE TABLE instamart_platform_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform_name TEXT NOT NULL DEFAULT 'Instamart',
    delivery_time_min INTEGER DEFAULT 15,
    delivery_time_max INTEGER DEFAULT 25,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE instamart_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    parent_id INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES instamart_categories(id)
);

CREATE TABLE instamart_stores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    pincode TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE instamart_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    store_id INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES instamart_categories(id),
    FOREIGN KEY (store_id) REFERENCES instamart_stores(id)
);
'''

SCHEMAS = {
    'blinkit': BLINKIT_SCHEMA,
    'zepto': ZEPTO_SCHEMA,
    'instamart': INSTAMART_SCHEMA,
}

def apply_schema(db_path, schema_sql):
    conn = sqlite3.connect(db_path)
    try:
        with conn:
            conn.executescript(schema_sql)
        print(f"Schema applied to {db_path}")
    except Exception as e:
        print(f"Error applying schema to {db_path}: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    for platform, db_path in DB_PATHS.items():
        schema = SCHEMAS[platform]
        if '-- Paste' in schema:
            print(f"[SKIP] Please paste the {platform} schema SQL statements in the script.")
            continue
        apply_schema(db_path, schema) 