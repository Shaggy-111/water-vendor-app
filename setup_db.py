# setup_db.py
import sqlite3
import os

# Ensure 'data' folder exists
os.makedirs("data", exist_ok=True)

# Connect / create DB
conn = sqlite3.connect("data/orders.db")
cursor = conn.cursor()

# -------------- USERS TABLE --------------
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username        TEXT UNIQUE,
        password        TEXT,
        location        TEXT,
        email           TEXT UNIQUE,
        mobile          TEXT,
        is_verified     INTEGER DEFAULT 0,
        verification_code TEXT,
        role TEXT CHECK(role IN ('admin','customer','delivery')) DEFAULT 'customer',
        id_proof_path   TEXT,
        is_approved     INTEGER DEFAULT 0,
        latitude        REAL,
        longitude       REAL
    )
"""
)

# -------------- ORDERS TABLE --------------
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name     TEXT,
        order_type        TEXT,
        quantity          INTEGER,
        status            TEXT,
        created_at        TEXT,
        customer_location TEXT,
        vehicle_number    TEXT,
        delivery_by       TEXT,
        delivery_photo    TEXT,
        delivery_image    TEXT
    )
"""
)

# -------------- NOTIFICATIONS TABLE --------------
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        message   TEXT,
        timestamp TEXT
    )
"""
)

# -------------- LAB REPORTS TABLE --------------
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS lab_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        month        TEXT,
        year         TEXT,
        report_path  TEXT,
        uploaded_at  TEXT
    )
"""
)

# -------------- DEFAULT ADMIN USER --------------
cursor.execute(
    """
    INSERT OR IGNORE INTO users (
        username, password, location, email, mobile,
        is_verified, role, id_proof_path, is_approved
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""",
    (
        "admin",
        "admin123",
        "HeadOffice",
        "admin@system.com",
        "9999999999",
        1,
        "admin",
        "",
        1,
    ),
)

conn.commit()
conn.close()
print("✅ Database schema ensured and default admin ready.")

conn = sqlite3.connect("data/orders.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(orders)")
columns = [col[1] for col in cursor.fetchall()]
if "empty_bottles_received" not in columns:
    cursor.execute("ALTER TABLE orders ADD COLUMN empty_bottles_received INTEGER DEFAULT 0")
    print("✅ Added 'empty_bottles_received' column.")
else:
    print("ℹ️ Column already exists.")

conn.commit()
conn.close()
