import sqlite3

def update_agent_role():
    conn = sqlite3.connect('nova26.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE sub_agents SET role='Especialista UI/UX con Google Stitch' WHERE id='agent-05'")
    conn.commit()
    conn.close()
    print("Agent-05 role updated.")

if __name__ == "__main__":
    update_agent_role()
