"""
Soul Database Manager
Handles connection and creation of the SQLite DB containing the agent's soul.
"""
import aiosqlite
import os
import json
from pathlib import Path
import datetime

class SoulDB:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.conn = None

    async def connect(self):
        """Connect to the database, creating it and applying schema if missing."""
        db_exists = self.db_path.exists()
        self.conn = await aiosqlite.connect(self.db_path)
        self.conn.row_factory = aiosqlite.Row
        
        if not db_exists:
            await self._apply_schema()
            
    async def _apply_schema(self):
        """Reads schema.sql and applies it to the new database."""
        schema_path = Path(__file__).parent / "schema.sql"
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema not found at {schema_path}")
            
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_script = f.read()
            
        await self.conn.executescript(schema_script)
        await self.conn.commit()

    async def close(self):
        """Close the database connection cleanly."""
        if self.conn:
            await self.conn.close()

    async def log_evolution(self, event_type: str, description: str, details: dict = None):
        """Log significant evolution events."""
        if details is None:
            details = {}
        await self.conn.execute(
            "INSERT INTO evolution_log (event_type, description, details_json) VALUES (?, ?, ?)",
            (event_type, description, json.dumps(details))
        )
        await self.conn.commit()
