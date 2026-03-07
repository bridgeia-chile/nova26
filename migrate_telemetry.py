import sqlite3

db_path = "f:/Users/Rosvel Nuñez/Documents/Proyecto BridgeIA/Antigravity Projects/NovaGravity/nova26.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Read the schema file to execute
schema_path = "f:/Users/Rosvel Nuñez/Documents/Proyecto BridgeIA/Antigravity Projects/NovaGravity/memory/schema.sql"
with open(schema_path, 'r', encoding='utf-8') as f:
    schema_sql = f.read()

cursor.executescript(schema_sql)

# Insert the 9 agents if they don't exist
agents = [
    ("agent-01", "nova26 (Core)", "Líder de la Oficina"),
    ("agent-02", "Nova Research", "Investigación y Análisis"),
    ("agent-03", "Nova Dev", "Desarrollo de Software"),
    ("agent-04", "Nova Data", "Ciencia de Datos"),
    ("agent-05", "Nova Design", "Diseño UI/UX"),
    ("agent-06", "Nova Sec", "Ciberseguridad"),
    ("agent-07", "Nova Ops", "Operaciones y DevOps"),
    ("agent-08", "Nova QA", "Control de Calidad"),
    ("agent-09", "Nova Support", "Soporte Técnico")
]

for agent in agents:
    cursor.execute("""
        INSERT OR IGNORE INTO sub_agents (id, name, role)
        VALUES (?, ?, ?)
    """, agent)

conn.commit()
conn.close()

print("Migration completed: sub_agents and token_usage added, and 9 agents initialized.")
