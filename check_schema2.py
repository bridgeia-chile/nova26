import sqlite3

db_path = "nova26.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='sub_agents'")
res = cursor.fetchone()
if res:
    print(res[0])
conn.close()
