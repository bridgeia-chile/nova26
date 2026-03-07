"""
Update Manager for Nova26
Check for new commits on GitHub periodically.
"""
import subprocess
import logging
import os

class UpdateManager:
    def __init__(self, repo_path="."):
        self.repo_path = repo_path
        self._cached_status = False

    def check_for_updates(self):
        """
        Runs git fetch and compares local vs remote.
        Returns True if updates are available.
        """
        try:
            # Silence git output
            devnull = open(os.devnull, 'w')
            
            # Fetch remote changes
            subprocess.run(["git", "fetch"], cwd=self.repo_path, stdout=devnull, stderr=devnull, check=True)
            
            # Compare HEAD with origin/main
            local = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.repo_path).strip()
            remote = subprocess.check_output(["git", "rev-parse", "origin/main"], cwd=self.repo_path).strip()
            
            self._cached_status = local != remote
            return self._cached_status
        except Exception as e:
            # Possibly not a git repo or no internet
            logging.debug(f"Update check failed (expected if not in Git): {e}")
            return False

    @property
    def update_available(self):
        return self._cached_status
