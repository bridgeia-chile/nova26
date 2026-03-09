"""
Memory Core
Handles CRUD operations and logic for the memory systems:
- Episodic (conversational logs)
- Semantic (facts, preferences, insights)
- Procedural (how to do tasks)
"""
import json
from datetime import datetime

class MemoryManager:
    """Provides high-level interfaces to all memory types in the SoulDB."""
    
    def __init__(self, soul_db):
        self.db = soul_db

    async def add_episodic(self, session_id: str, role: str, content: str, 
                           interface: str = 'telegram', importance: float = 0.5, 
                           metadata: dict = None, agent_id: str = 'agent-01'):
        """Append a new log to episodic memory."""
        meta_json = json.dumps(metadata) if metadata else None
        await self.db.conn.execute(
            """
            INSERT INTO episodic_memory (session_id, role, content, interface, importance_score, metadata_json, agent_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (session_id, role, content, interface, importance, meta_json, agent_id)
        )
        await self.db.conn.commit()

    async def get_recent_episodic(self, limit: int = 50, agent_id: str = 'agent-01') -> list:
        """Fetch recent conversational context for a specific agent."""
        async with self.db.conn.execute(
            "SELECT * FROM episodic_memory WHERE agent_id = ? ORDER BY timestamp DESC LIMIT ?", 
            (agent_id, limit)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in reversed(rows)] # Chronological order

    async def learn_semantic(self, category: str, key: str, value: str, confidence: float = 0.8, source: str = "user"):
        """Store or update a fact in semantic memory."""
        await self.db.conn.execute(
            """
            INSERT INTO semantic_memory (category, key, value, confidence, source)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(category, key) DO UPDATE SET 
                value = excluded.value,
                confidence = excluded.confidence,
                source = excluded.source,
                learned_at = CURRENT_TIMESTAMP,
                reinforcement_score = reinforcement_score + 0.1
            """,
            (category, key, value, confidence, source)
        )
        await self.db.conn.commit()

    async def search_semantic(self, category: str = None) -> list:
        """Retrieve highest reinforced knowledge. Enhance with embeddings later if needed."""
        query = "SELECT * FROM v_top_knowledge"
        params = ()
        if category:
            query += " WHERE category = ?"
            params = (category,)
            
        async with self.db.conn.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def log_token_usage(self, agent_id: str, model_id: str, prompt_tokens: int, completion_tokens: int):
        """Logs token usage for an agent."""
        query = '''
            INSERT INTO token_usage (agent_id, model, prompt_tokens, completion_tokens)
            VALUES (?, ?, ?, ?)
        '''
        await self.db.conn.execute(query, (agent_id, model_id, prompt_tokens, completion_tokens))
        await self.db.conn.commit()

    async def add_procedural(self, task_name: str, description: str, steps: list, source: str = 'user_taught'):
        """Store a structured multi-step task process."""
        steps_json = json.dumps(steps)
        await self.db.conn.execute(
            """
            INSERT INTO procedural_memory (task_name, description, steps_json, learned_from)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(task_name) DO UPDATE SET
                description = excluded.description,
                steps_json = excluded.steps_json,
                learned_from = excluded.learned_from
            """,
            (task_name, description, steps_json, source)
        )
        await self.db.conn.commit()

    async def get_procedural(self, task_name: str) -> dict:
        """Fetch steps for a procedural task."""
        async with self.db.conn.execute(
            "SELECT * FROM procedural_memory WHERE task_name = ?", (task_name,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None
