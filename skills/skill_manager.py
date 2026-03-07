"""
Skill Manager
Manages self-installation of skills and dependencies upon boot or restoration.
"""
import logging
import asyncio
import json

class SkillManager:
    """Manages skill persistence, restore and discovery."""

    def __init__(self, soul_db):
        self.db = soul_db

    async def audit_skills(self) -> dict:
        """Compara habilidades de la DB con las locales."""
        # For a full implementation we would check site-packages or local paths
        # Given limitations, we outline the audit structure
        async with self.db.conn.execute("SELECT * FROM v_active_skills") as cursor:
            rows = await cursor.fetchall()
            
        active_skills = [dict(row) for row in rows]
        return {
            "installed": [],          # Would be verified externally
            "missing": active_skills, # Assuming all need check on restored
            "broken": []
        }

    async def auto_install_missing(self) -> dict:
        """Autoinstalls missing skills using stored commands."""
        audit = await self.audit_skills()
        results = {"success": [], "failed": []}
        
        for skill in audit["missing"]:
            name = skill['skill_name']
            cmd = skill['install_command']
            logging.info(f"Auto-installing missing skill: {name} via `{cmd}`")
            
            # Simple async execution of install command
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                results["success"].append(name)
                logging.info(f"Successfully installed detail: {name}")
                await self.db.log_evolution('skill_restored', f'Restaurada habilidad {name}')
            else:
                results["failed"].append({"name": name, "error": stderr.decode('utf-8')})
                logging.error(f"Failed to install {name}: {stderr.decode('utf-8')}")
                
        return results

    async def list_md_skills(self) -> list:
        """Lista todas las habilidades basadas en archivos .md."""
        from pathlib import Path
        skills_path = Path(__file__).parent
        return [f.stem for f in skills_path.glob("*.md")]

    async def create_md_skill(self, name: str, content: str) -> bool:
        """Crea un nuevo archivo .md de habilidad."""
        from pathlib import Path
        skills_path = Path(__file__).parent
        file_path = skills_path / f"{name.lower()}.md"
        try:
            file_path.write_text(content, encoding='utf-8')
            await self.db.log_evolution('skill_created', f"Creada habilidad MD: {name}")
            return True
        except Exception as e:
            logging.error(f"Error creando habilidad {name}: {e}")
            return False

    async def register_new_skill(self, skill: dict):
        """Registra una nueva habilidad en el alma."""
        await self.db.conn.execute(
            """
            INSERT INTO skills (skill_name, skill_type, install_command, config_json, dependencies_json, source_url)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                skill.get('name'), 
                skill.get('type'), 
                skill.get('install_command'),
                json.dumps(skill.get('config', {})),
                json.dumps(skill.get('dependencies', [])),
                skill.get('source_url')
            )
        )
        await self.db.conn.commit()
        await self.db.log_evolution('skill_learned', f"Aprendida nueva habilidad: {skill.get('name')}")
