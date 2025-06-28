import sqlite3
import os

# Ensure 'data' folder exists
os.makedirs("data", exist_ok=True)

# Connect to database
conn = sqlite3.connect('data/orders.db')
cursor = conn.cursor()

# ------------------- USERS TABLE -------------------
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        location TEXT,
        email TEXT UNIQUE,
        mobile TEXT,
        is_verified INTEGER DEFAULT 0,
        verification_code TEXT,
        role TEXT CHECK(role IN ('admin', 'vendor', 'delivery')) DEFAULT 'vendor',
        id_proof_path TEXT
    )
''')

# Add extra columns to users table if missing
cursor.execute("PRAGMA table_info(users)")
user_columns = [col[1] for col in cursor.fetchall()]

if "is_approved" not in user_columns:
    cursor.execute("ALTER TABLE users ADD COLUMN is_approved INTEGER DEFAULT 0")
    print("✅ 'is_approved' column added.")

if "latitude" not in user_columns:
    cursor.execute("ALTER TABLE users ADD COLUMN latitude REAL")
    print("✅ 'latitude' column added.")

if "longitude" not in user_columns:
    cursor.execute("ALTER TABLE users ADD COLUMN longitude REAL")
    print("✅ 'longitude' column added.")

# ------------------- ORDERS TABLE -------------------
cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor_name TEXT,
        order_type TEXT,
        quantity INTEGER,
        status TEXT,
        created_at TEXT,
        vendor_location TEXT
    )
''')

cursor.execute("PRAGMA table_info(orders)")
order_columns = [col[1] for col in cursor.fetchall()]

if "vehicle_number" not in order_columns:
    cursor.execute("ALTER TABLE orders ADD COLUMN vehicle_number TEXT")
if "delivery_by" not in order_columns:
    cursor.execute("ALTER TABLE orders ADD COLUMN delivery_by TEXT")
if "delivery_photo" not in order_columns:
    cursor.execute("ALTER TABLE orders ADD COLUMN delivery_photo TEXT")
if "delivery_image" not in order_columns:
    cursor.execute("ALTER TABLE orders ADD COLUMN delivery_image TEXT")

print("✅ Orders table columns checked and updated.")

# ------------------- NOTIFICATIONS TABLE -------------------
cursor.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message TEXT,
        timestamp TEXT
    )
''')

# ------------------- LAB REPORTS TABLE -------------------
cursor.execute('''
    CREATE TABLE IF NOT EXISTS lab_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        month TEXT,
        year TEXT,
        report_path TEXT,
        uploaded_at TEXT
    )
''')
print("✅ 'lab_reports' table created.")

# ------------------- DEFAULT ADMIN -------------------
cursor.execute('''
    INSERT OR IGNORE INTO users (
        username, password, location, email, mobile,
        is_verified, role, id_proof_path, is_approved
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', ('admin', 'admin123', 'HeadOffice', 'admin@system.com', '9999999999', 1, 'admin', '', 1))
print("✅ Default admin inserted (if not present).")

# ------------------- Finalize -------------------
conn.commit()
conn.close()
print("✅ Database setup complete.")
