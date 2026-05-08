import sqlite3

conn = sqlite3.connect("mrp.db")
cursor = conn.cursor()

cursor.execute("SELECT id, code, name FROM materials")
print(cursor.fetchall())

conn.close()
