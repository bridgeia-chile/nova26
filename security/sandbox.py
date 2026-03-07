"""
Security Layer Sandbox & Permissions
Restrictive execution environment overrides.
"""
import logging

class SecurityManager:
    """Manages permission boundary validations."""
    PERMISSION_LEVELS = {
        'read_only': ['file_read', 'web_search', 'memory_read'],
        'standard': ['file_read', 'file_write', 'web_search',
                     'memory_read', 'memory_write', 'script_run_safe'],
        'elevated': ['file_read', 'file_write', 'file_delete',
                     'web_search', 'memory_read', 'memory_write',
                     'script_run_any', 'system_command', 'mcp_tool_use'],
        'admin': ['*']
    }
    
    def __init__(self, current_level='standard'):
        self.current_level = current_level

    def has_permission(self, required_action: str) -> bool:
        """Check if current operating level allows the action."""
        if '*' in self.PERMISSION_LEVELS[self.current_level]:
            return True
        return required_action in self.PERMISSION_LEVELS[self.current_level]

class Sandbox:
    def __init__(self):
        self.manager = SecurityManager()

    def assert_action_allowed(self, action: str) -> bool:
        """Validates if a targeted action satisfies the security boundaries."""
        allowed = self.manager.has_permission(action)
        if not allowed:
            logging.warning(f"Sandbox blocked unauthorized action: {action}")
        return allowed
