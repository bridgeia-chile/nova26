"""
Identity Manager
Manages the core personality and identity records in the soul database.
"""
import json
import yaml
from pathlib import Path
from datetime import datetime

class IdentityManager:
    """Handles the unique instance of the identity."""
    
    def __init__(self, soul_db):
        self.db = soul_db
        self.state = None

    async def load_or_create(self, config_dir: str):
        """Loads identity from DB, or creates it from personality.yaml if new."""
        async with self.db.conn.execute("SELECT * FROM identity WHERE id = 1") as cursor:
            row = await cursor.fetchone()
            
        if not row:
            # Create fresh identity from YAML
            personality_path = Path(config_dir) / "personality.yaml"
            with open(personality_path, "r", encoding="utf-8") as f:
                personality = yaml.safe_load(f)
                
            persona_json = json.dumps(personality)
            sys_prompt = self._build_system_prompt(personality, config_dir)
            
            await self.db.conn.execute(
                """
                INSERT INTO identity (id, name, version, personality_json, system_prompt, owner_id)
                VALUES (1, ?, '1.0.0', ?, ?, 'pending_setup')
                """,
                (personality.get('name', 'nova26'), persona_json, sys_prompt)
            )
            await self.db.conn.commit()
            
            async with self.db.conn.execute("SELECT * FROM identity WHERE id = 1") as cursor:
                row = await cursor.fetchone()
        else:
            # Refresh system prompt with dynamic skills even if already exists
            personality = json.loads(row['personality_json'])
            new_sys_prompt = self._build_system_prompt(personality, config_dir)
            await self.db.conn.execute("UPDATE identity SET system_prompt = ? WHERE id = 1", (new_sys_prompt,))
            await self.db.conn.commit()
            # Reload row
            async with self.db.conn.execute("SELECT * FROM identity WHERE id = 1") as cursor:
                row = await cursor.fetchone()
                
        self.state = dict(row)
        return self.state
        
    async def update_boot_stats(self):
        """Update last_boot timestamp and total_boots count."""
        await self.db.conn.execute(
            """
            UPDATE identity 
            SET last_boot = CURRENT_TIMESTAMP, 
                total_boots = total_boots + 1 
            WHERE id = 1
            """
        )
        await self.db.conn.commit()
        
    def _build_system_prompt(self, personality: dict, config_dir: str) -> str:
        """Constructs the initial base system prompt from the personality dict."""
        sys_prompt = f"Eres {personality.get('name')}, un agente autónomo de IA.\n\n"
        
        sys_prompt += "RASGOS NUCLEARES:\n"
        for trait in personality.get('core_traits', []):
            sys_prompt += f"- {trait}\n"
            
        sys_prompt += "\nREGLAS DE COMPORTAMIENTO:\n"
        for rule in personality.get('behavioral_rules', []):
            sys_prompt += f"- {rule}\n"
            
        # Inject dynamic skills from markdown files
        skills_text = self._load_dynamic_skills(config_dir)
        if skills_text:
            sys_prompt += f"\n\nSKILLS & CAPABILITIES:\n{skills_text}\n"
            
        return sys_prompt

    def _load_dynamic_skills(self, config_dir: str) -> str:
        """Reads .md files from skills/ directory matching config context."""
        skills_path = Path(config_dir).parent / "skills"
        if not skills_path.exists():
            return ""
            
        combined_skills = []
        for md_file in skills_path.glob("*.md"):
            try:
                content = md_file.read_text(encoding='utf-8')
                combined_skills.append(f"### SKILL: {md_file.stem.upper()}\n{content}")
            except Exception:
                continue
                
        return "\n\n".join(combined_skills)
