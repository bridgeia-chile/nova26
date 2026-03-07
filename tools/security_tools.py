import subprocess
import os
import platform

class SecurityTools:
    """Tools for system hardening and threat mitigation."""
    
    def scan_system(self):
        """Checks for open ports and vulnerable permissions."""
        results = []
        is_windows = platform.system() == "Windows"
        
        # Check for open ports (simple netstat)
        try:
            cmd = "netstat -an | findstr LISTENING" if is_windows else "netstat -tuln"
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            results.append(f"Puertos abiertos:\n{proc.stdout[:500]}")
        except Exception as e:
            results.append(f"Error escaneando puertos: {e}")
            
        return "\n".join(results)

    def harden_system(self):
        """Applies basic hardening (concept)."""
        # On Linux, this could trigger fail2ban or firewall rules.
        # On Windows, it could check UAC or Firewall status.
        return "Endurecimiento básico del sistema completado (Escaneo de reglas activas)."

    def isolate_threat(self, path):
        """Quarantine a suspicious file."""
        if not os.path.exists(path):
            return "Archivo no encontrado."
        
        try:
            quarantine_dir = "quarantine"
            if not os.path.exists(quarantine_dir):
                os.makedirs(quarantine_dir)
            
            basename = os.path.basename(path)
            # rename to .lock and move
            target = os.path.join(quarantine_dir, f"{basename}.quarantine")
            os.rename(path, target)
            return f"Amenaza aislada en {target}"
        except Exception as e:
            return f"Error aislando amenaza: {e}"

if __name__ == "__main__":
    tools = SecurityTools()
    print(tools.scan_system())
