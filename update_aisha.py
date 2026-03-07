import sqlite3
conn = sqlite3.connect('nova26.db')
cursor = conn.cursor()
cursor.execute("UPDATE sub_agents SET name='Aisha' WHERE id='agent-01'")
conn.commit()
conn.close()
print('Agent 01 renamed to Aisha')
