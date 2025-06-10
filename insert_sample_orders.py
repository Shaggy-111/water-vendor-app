import sqlite3
from datetime import datetime

conn = sqlite3.connect('data/orders.db')
cursor = conn.cursor()

# Sample orders
sample_orders = [
    ("vendor1", "1L Bottle", 10, "Pending", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    ("vendor1", "500ml Bottle", 20, "Pending", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    ("vendor2", "2L Bottle", 15, "Pending", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
]

cursor.executemany("INSERT INTO orders (vendor_name, order_type, quantity, status, created_at) VALUES (?, ?, ?, ?, ?)", sample_orders)

conn.commit()
conn.close()
print("Sample orders inserted!")
