import sqlite3

def setup_security_db():
    conn = sqlite3.connect('nova26.db')
    cursor = conn.cursor()
    
    # Create security events table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS security_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT,
        severity TEXT,
        details TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Register Nova Sentry if not exists
    cursor.execute('''
    INSERT OR IGNORE INTO sub_agents (id, name, role, selected_model, status)
    VALUES ('agent-06', 'Nova Sentry', 'Oficial de Ciberseguridad', 'Llama-3.3-70b', 'active')
    ''')
    
    conn.commit()
    conn.close()
    print("Security DB infrastructure ready.")

if __name__ == "__main__":
    setup_security_db()
