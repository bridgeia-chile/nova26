-- ===========================================
-- nova26 SOUL DATABASE v1.0
-- ===========================================

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

-- IDENTIDAD CORE
CREATE TABLE IF NOT EXISTS identity (
    id INTEGER PRIMARY KEY DEFAULT 1,
    name TEXT DEFAULT 'nova26',
    version TEXT DEFAULT '1.0.0',
    personality_json TEXT NOT NULL,
    system_prompt TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_boot DATETIME,
    total_boots INTEGER DEFAULT 0,
    owner_id TEXT NOT NULL,
    owner_name TEXT,
    CHECK (id = 1) -- Solo puede haber UNA identidad
);

-- MEMORIA EPISÓDICA (conversaciones y eventos)
CREATE TABLE IF NOT EXISTS episodic_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    role TEXT CHECK(role IN ('user','assistant','system','tool')) NOT NULL,
    content TEXT NOT NULL,
    interface TEXT DEFAULT 'telegram', -- telegram, cli, api
    importance_score REAL DEFAULT 0.5, -- 0.0 a 1.0
    embedding BLOB, -- vector embedding para búsqueda semántica
    metadata_json TEXT,
    archived INTEGER DEFAULT 0
);

-- MEMORIA SEMÁNTICA (conocimiento aprendido y destilado)
CREATE TABLE IF NOT EXISTS semantic_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL, -- 'fact', 'preference', 'skill', 'relationship', 'insight'
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    confidence REAL DEFAULT 0.8, -- 0.0 a 1.0
    source TEXT, -- de dónde aprendió esto
    learned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_accessed DATETIME,
    access_count INTEGER DEFAULT 0,
    reinforcement_score REAL DEFAULT 1.0, -- se refuerza o decae
    UNIQUE(category, key)
);

-- MEMORIA PROCEDIMENTAL (cómo hacer cosas)
CREATE TABLE IF NOT EXISTS procedural_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name TEXT UNIQUE NOT NULL,
    description TEXT,
    steps_json TEXT NOT NULL, -- pasos para completar la tarea
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    avg_duration_ms INTEGER,
    last_executed DATETIME,
    learned_from TEXT, -- 'user_taught', 'self_discovered', 'claude_code'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- HABILIDADES INSTALADAS (para auto-restauración)
CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT UNIQUE NOT NULL,
    skill_type TEXT CHECK(skill_type IN ('python_package','node_package','mcp_server','script','plugin')) NOT NULL,
    install_command TEXT NOT NULL, -- comando exacto para reinstalar
    config_json TEXT, -- configuración de la habilidad
    dependencies_json TEXT, -- dependencias necesarias
    source_url TEXT, -- URL de origen si aplica
    file_content TEXT, -- contenido del script/plugin si es custom
    version TEXT,
    is_active INTEGER DEFAULT 1,
    installed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_verified DATETIME
);

-- HERRAMIENTAS MCP REGISTRADAS
CREATE TABLE IF NOT EXISTS mcp_tools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_name TEXT UNIQUE NOT NULL,
    server_command TEXT NOT NULL, -- comando para iniciar el servidor MCP
    server_args_json TEXT,
    env_vars_json TEXT, -- variables de entorno necesarias (encriptadas)
    schema_json TEXT, -- schema de la herramienta
    is_active INTEGER DEFAULT 1,
    last_health_check DATETIME,
    health_status TEXT DEFAULT 'unknown',
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- CONFIGURACIÓN PERSISTENTE
CREATE TABLE IF NOT EXISTS config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    encrypted INTEGER DEFAULT 0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- TAREAS PROGRAMADAS
CREATE TABLE IF NOT EXISTS scheduled_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name TEXT NOT NULL,
    cron_expression TEXT, -- NULL si es one-shot
    next_run DATETIME,
    last_run DATETIME,
    task_type TEXT CHECK(task_type IN ('reminder','automation','maintenance','custom')),
    payload_json TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- LOG DE EVOLUCIÓN (tracking de aprendizaje)
CREATE TABLE IF NOT EXISTS evolution_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT CHECK(event_type IN (
        'skill_learned','skill_improved','memory_consolidated',
        'personality_adjusted','error_recovered','insight_gained',
        'boot','shutdown','migration','backup_created'
    )) NOT NULL,
    description TEXT NOT NULL,
    details_json TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- SUB-AGENTES DE LA OFICINA
CREATE TABLE IF NOT EXISTS sub_agents (
    id TEXT PRIMARY KEY, -- ej. 'agent-01', 'agent-02'
    name TEXT NOT NULL,
    role TEXT,
    selected_model TEXT DEFAULT 'Llama-3.3-70b',
    status TEXT DEFAULT 'idle',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- USO DE TOKENS POR AGENTE
CREATE TABLE IF NOT EXISTS token_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,
    model TEXT NOT NULL,
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- RELACIONES Y CONTEXTO DE USUARIOS
CREATE TABLE IF NOT EXISTS known_entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT CHECK(entity_type IN ('person','project','tool','concept')) NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    attributes_json TEXT,
    relationship_to_owner TEXT,
    first_mentioned DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_mentioned DATETIME,
    mention_count INTEGER DEFAULT 1,
    UNIQUE(entity_type, name)
);

-- NODOS PEERS (Sincronización P2P)
CREATE TABLE IF NOT EXISTS node_peers (
    peer_url TEXT PRIMARY KEY,
    node_name TEXT,
    last_sync DATETIME DEFAULT '2000-01-01 00:00:00',
    status TEXT DEFAULT 'active'
);

-- ÍNDICES PARA RENDIMIENTO
CREATE INDEX IF NOT EXISTS idx_episodic_session ON episodic_memory(session_id);
CREATE INDEX IF NOT EXISTS idx_episodic_timestamp ON episodic_memory(timestamp);
CREATE INDEX IF NOT EXISTS idx_episodic_importance ON episodic_memory(importance_score);
CREATE INDEX IF NOT EXISTS idx_semantic_category ON semantic_memory(category);
CREATE INDEX IF NOT EXISTS idx_semantic_accessed ON semantic_memory(last_accessed);
CREATE INDEX IF NOT EXISTS idx_evolution_type ON evolution_log(event_type);
CREATE INDEX IF NOT EXISTS idx_scheduled_next ON scheduled_tasks(next_run);

-- VISTAS ÚTILES
CREATE VIEW IF NOT EXISTS v_active_skills AS
SELECT skill_name, skill_type, install_command, version
FROM skills WHERE is_active = 1;

CREATE VIEW IF NOT EXISTS v_recent_memories AS
SELECT role, content, timestamp, importance_score
FROM episodic_memory
WHERE archived = 0
ORDER BY timestamp DESC LIMIT 100;

CREATE VIEW IF NOT EXISTS v_top_knowledge AS
SELECT category, key, value, confidence, access_count
FROM semantic_memory
ORDER BY reinforcement_score DESC LIMIT 50;
