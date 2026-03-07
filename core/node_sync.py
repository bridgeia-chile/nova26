"""
Node Synchronization Logic for Nova26
Handles exporting and importing of database chunks between P2P Agents
"""
import sqlite3
import logging
import asyncio
import httpx
from datetime import datetime

class NodeSynchronizer:
    def __init__(self, db_path):
        self.db_path = db_path
        
    def _execute_query(self, query, params=(), fetch_all=True):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            if fetch_all:
                result = [dict(row) for row in cursor.fetchall()]
            else:
                conn.commit()
                result = True
            conn.close()
            return result
        except Exception as e:
            logging.error(f"DB Error in Sync: {e}")
            return []

    def export_data(self, since_ts: str) -> dict:
        """Exports memories generated after since_ts."""
        # 1. Episodic Memory
        episodic = self._execute_query(
            "SELECT session_id, timestamp, role, content, interface, importance_score, metadata_json FROM episodic_memory WHERE timestamp > ? ORDER BY timestamp ASC",
            (since_ts,)
        )
        
        # 2. Semantic Memory
        semantic = self._execute_query(
            "SELECT category, key, value, confidence, source, learned_at, last_accessed, access_count, reinforcement_score FROM semantic_memory WHERE learned_at > ? OR last_accessed > ?",
            (since_ts, since_ts)
        )
        
        # 3. Known Entities
        entities = self._execute_query(
            "SELECT entity_type, name, description, attributes_json, relationship_to_owner, first_mentioned, last_mentioned, mention_count FROM known_entities WHERE last_mentioned > ? OR first_mentioned > ?",
            (since_ts, since_ts)
        )
        
        return {
            "episodic": episodic,
            "semantic": semantic,
            "entities": entities,
            "export_time": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }

    def import_data(self, data: dict) -> dict:
        """Merges incoming data into local DB intelligently."""
        stats = {"episodic": 0, "semantic": 0, "entities": 0, "errors": 0}
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 1. Insert Episodic (Ignore precise duplicates by timestamp and content)
            for mem in data.get('episodic', []):
                cursor.execute(
                    "SELECT 1 FROM episodic_memory WHERE timestamp = ? AND content = ?",
                    (mem['timestamp'], mem['content'])
                )
                if not cursor.fetchone():
                    cursor.execute(
                        "INSERT INTO episodic_memory (session_id, timestamp, role, content, interface, importance_score, metadata_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (mem['session_id'], mem['timestamp'], mem['role'], mem['content'], mem['interface'], mem['importance_score'], mem['metadata_json'])
                    )
                    stats["episodic"] += 1
                    
            # 2. Insert or Replace Semantic (Unique: category, key)
            for sm in data.get('semantic', []):
                cursor.execute(
                    "INSERT OR REPLACE INTO semantic_memory (category, key, value, confidence, source, learned_at, last_accessed, access_count, reinforcement_score) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (sm['category'], sm['key'], sm['value'], sm['confidence'], sm['source'], sm['learned_at'], sm['last_accessed'], sm['access_count'], sm['reinforcement_score'])
                )
                stats["semantic"] += 1

            # 3. Insert or Replace Known Entities (Unique: entity_type, name)
            for en in data.get('entities', []):
                cursor.execute(
                    "INSERT OR REPLACE INTO known_entities (entity_type, name, description, attributes_json, relationship_to_owner, first_mentioned, last_mentioned, mention_count) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (en['entity_type'], en['name'], en['description'], en['attributes_json'], en['relationship_to_owner'], en['first_mentioned'], en['last_mentioned'], en['mention_count'])
                )
                stats["entities"] += 1

            conn.commit()
            conn.close()
            logging.info(f"Sync complete. Imported: {stats}")
            return {"status": "success", "stats": stats}
            
        except Exception as e:
            logging.error(f"Error during import: {e}")
            stats["errors"] += 1
            return {"status": "error", "message": str(e), "stats": stats}

    async def pull_from_peer(self, peer_url: str):
        """Fetches new data from a peer and imports it."""
        try:
            # 1. Check last sync time
            res = self._execute_query("SELECT last_sync FROM node_peers WHERE peer_url = ?", (peer_url,))
            since_ts = res[0]['last_sync'] if res else '2000-01-01 00:00:00'
            
            # 2. Fetch data from peer's export endpoint
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(f"{peer_url}/api/v1/sync/export?since_ts={since_ts}")
                resp.raise_for_status()
                payload = resp.json()
            
            # 3. Import data
            if payload.get('status') == 'success':
                import_res = self.import_data(payload.get('data', {}))
                
                # 4. Update last_sync
                if import_res['status'] == 'success':
                    export_time = payload['data'].get('export_time', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
                    self._execute_query(
                        "INSERT OR REPLACE INTO node_peers (peer_url, last_sync, status) VALUES (?, ?, 'active')",
                        (peer_url, export_time), fetch_all=False
                    )
                return import_res
            else:
                return {"status": "error", "message": "Peer returned error payload"}
                
        except Exception as e:
            logging.warning(f"Failed to pull from peer {peer_url}: {e}")
            return {"status": "error", "message": str(e)}

    def get_known_peers(self):
        # We also read PEER_NODES from environment, comma separated
        import os
        env_peers_str = os.getenv("PEER_NODES", "")
        env_peers = [p.strip() for p in env_peers_str.split(',') if p.strip()]
        
        db_peers = self._execute_query("SELECT peer_url FROM node_peers")
        db_peer_urls = [p['peer_url'] for p in db_peers]
        
        # Combine
        all_peers = set(env_peers + db_peer_urls)
        return list(all_peers)
