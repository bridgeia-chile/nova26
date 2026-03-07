import sqlite3
import json
import yaml
from pathlib import Path

db_path = "f:/Users/Rosvel Nuñez/Documents/Proyecto BridgeIA/Antigravity Projects/NovaGravity/nova26.db"
yaml_path = "f:/Users/Rosvel Nuñez/Documents/Proyecto BridgeIA/Antigravity Projects/NovaGravity/config/personality.yaml"

with open(yaml_path, 'r', encoding='utf-8') as f:
    personality = yaml.safe_load(f)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get existing prompt
cursor.execute("SELECT system_prompt, personality_json FROM identity WHERE id = 1")
row = cursor.fetchone()

sys_prompt = f"Eres {personality.get('name')}, un agente autónomo de IA.\n\n"
sys_prompt += "RASGOS NUCLEARES:\n"
for trait in personality.get('core_traits', []):
    sys_prompt += f"- {trait}\n"
    
sys_prompt += "\nREGLAS DE COMPORTAMIENTO:\n"
for rule in personality.get('behavioral_rules', []):
    sys_prompt += f"- {rule}\n"

# Update DB
cursor.execute("UPDATE identity SET system_prompt = ?, personality_json = ? WHERE id = 1", (sys_prompt, json.dumps(personality)))
conn.commit()
conn.close()
print("Identity updated with CEO and sub-agent directives.")
