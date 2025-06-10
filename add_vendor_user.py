import sqlite3

conn = sqlite3.connect('data/orders.db')
cursor = conn.cursor()

# Add vendor user
cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
               ('vendor1', 'vendor123', 'vendor'))

conn.commit()
conn.close()
print("✅ Vendor user created.")
