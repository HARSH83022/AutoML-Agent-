import sqlite3
import json

# Connect to the memory.db
conn = sqlite3.connect("memory.db")
cursor = conn.cursor()

print("\n📌 Available tables:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())

print("\n📌 Runs table:")
for row in cursor.execute("SELECT * FROM runs;"):
    print(row)

print("\n📌 Events table:")
for row in cursor.execute("SELECT * FROM events;"):
    # Pretty-print JSON payload if possible
    try:
        payload = json.dumps(json.loads(row[3]), indent=2)
    except Exception:
        payload = row[3]
    print(f"ID={row[0]} | run_id={row[1]} | agent={row[2]} | payload={payload} | created_at={row[4]}")

print("\n📌 Artifacts table:")
for row in cursor.execute("SELECT * FROM artifacts;"):
    print(row)

conn.close()
