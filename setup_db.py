import sqlite3
import os

# ✅ Make sure the folder exists
if not os.path.exists("data"):
    os.makedirs("data")

# ✅ Connect fresh to the DB
conn = sqlite3.connect('data/orders.db')
cursor = conn.cursor()

# ✅ Drop table if already exists (to remove old structure)
cursor.execute("DROP TABLE IF EXISTS users")

# ✅ Recreate users table with location column
cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        location TEXT,
        email TEXT,
        is_verified INTEGER DEFAULT 0,
        verification_code TEXT,
        role TEXT CHECK(role IN ('admin', 'vendor'))
    )
''')
# ✅ Create orders table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor_name TEXT,
        order_type TEXT,
        quantity INTEGER,
        status TEXT,
        created_at TEXT
    )
''')

# ✅ Insert admin user
cursor.execute("INSERT OR IGNORE INTO users (username, password, location, role) VALUES (?, ?, ?, ?)",
               ('admin', 'admin123', 'HQ', 'admin'))

conn.commit()
conn.close()

print("✅ Database and both tables recreated successfully.")
