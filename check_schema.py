import sqlite3

def check_schema():
    conn = sqlite3.connect('nova26.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(mcp_tools);")
    columns = cursor.fetchall()
    for col in columns:
        print(col)
    conn.close()

if __name__ == "__main__":
    check_schema()
