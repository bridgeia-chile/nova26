import os
import time
import sqlite3
import logging
import hashlib
from datetime import datetime

class SentryMonitor:
    def __init__(self, soul_path, watch_files=None):
        self.soul_path = soul_path
        self.watch_files = watch_files or ['.env', 'nova26.db']
        self.file_hashes = {}
        self._init_hashes()

    def _init_hashes(self):
        for f in self.watch_files:
            if os.path.exists(f):
                self.file_hashes[f] = self._get_hash(f)

    def _get_hash(self, path):
        try:
            with open(path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except:
            return None

    def check_integrity(self):
        events = []
        for f in self.watch_files:
            if not os.path.exists(f):
                continue
            current_hash = self._get_hash(f)
            if f in self.file_hashes and current_hash != self.file_hashes[f]:
                events.append({
                    "type": "file_integrity_violation",
                    "severity": "CRITICAL",
                    "details": f"Archivo crítico modificado: {f}"
                })
                self.file_hashes[f] = current_hash
        return events

    def log_event(self, event_type, severity, details):
        try:
            conn = sqlite3.connect(self.soul_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO security_events (event_type, severity, details) VALUES (?, ?, ?)",
                (event_type, severity, details)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Sentry error logging event: {e}")
            return False

    async def run_step(self):
        """Executes a single monitoring tick."""
        events = self.check_integrity()
        for e in events:
            self.log_event(e['type'], e['severity'], e['details'])
        return events

if __name__ == "__main__":
    # Test run
    monitor = SentryMonitor('nova26.db')
    print("Sentry monitor initialized. Watching:", monitor.watch_files)
    events = monitor.check_integrity()
    if events:
        print("Initial events:", events)
    else:
        print("System integrity verified.")
