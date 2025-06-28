import sqlite3

conn = sqlite3.connect('data/orders.db')
cursor = conn.cursor()

cursor.execute("SELECT username, email, password, role, is_verified, is_approved FROM users")
rows = cursor.fetchall()

print("📋 USERS in DB:")
for row in rows:
    print(row)

conn.close()
