import sqlite3

conn = sqlite3.connect("hotspot.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS requests(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    mac TEXT,
    status TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS logs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mac TEXT,
    time TEXT
)
""")

conn.commit()
conn.close()

print("Database created successfully!")