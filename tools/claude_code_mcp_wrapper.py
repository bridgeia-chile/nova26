import subprocess
import sys
import os
import json
import threading
import time

def filter_output():
    # Persistent debug logging with absolute path - use append mode
    log_path = r"F:\Users\Rosvel Nuñez\Documents\Proyecto BridgeIA\Antigravity Projects\NovaGravity\tools\wrapper_debug.log"
    log_file = open(log_path, "a", encoding="utf-8", buffering=1)
    
    def log(msg):
        try:
            log_file.write(f"{time.strftime('%H:%M:%S')} {msg}\n")
            log_file.flush()
        except:
            pass
        try:
            safe_msg = str(msg).encode(sys.stderr.encoding or 'utf-8', errors='replace').decode(sys.stderr.encoding or 'utf-8')
            sys.stderr.write(f"{safe_msg}\n")
            sys.stderr.flush()
        except:
            pass

    log("--- Wrapper Started ---")
    try:
        args = sys.argv[1:]
        log(f"Args: {args}")
        
        env = os.environ.copy()
        log("Env copied")
        
        env["CI"] = "1"
        env["PYTHONUNBUFFERED"] = "1"
        env["TERM"] = "dumb"
        env["NO_COLOR"] = "1"
        env["FORCE_COLOR"] = "0"
        log("Env base keys set")
        
        if not env.get("ANTHROPIC_BASE_URL"):
            env["ANTHROPIC_BASE_URL"] = "http://localhost:11434"
        if not env.get("ANTHROPIC_API_KEY"):
            env["ANTHROPIC_API_KEY"] = "ollama"
        if not env.get("ANTHROPIC_AUTH_TOKEN"):
            env["ANTHROPIC_AUTH_TOKEN"] = "ollama"
        log("Anthropic bridge vars set")
        
        claude_bin_path = os.path.join(os.path.expanduser("~"), ".local", "bin")
        if claude_bin_path not in env.get("PATH", ""):
            env["PATH"] = f"{claude_bin_path};{env.get('PATH', '')}"
        log(f"PATH updated with {claude_bin_path}")
        
        claude_exe = os.path.join(claude_bin_path, "claude.exe")
        log(f"Claude EXE path: {claude_exe}")
        
        model_name = "devstral-2:123b-cloud"
        if "--model" in args:
            idx = args.index("--model")
            if idx + 1 < len(args):
                model_name = args[idx+1]
        log(f"Model name: {model_name}")
            
        # Use direct claude.exe, model is set via environment variable ANTHROPIC_MODEL
        cmd = [claude_exe, "mcp", "serve"]
        log(f"Command constructed: {' '.join(cmd)}")
    except Exception as e:
        log(f"ERROR in setup: {e}")
        sys.exit(1)

    # Start the process with piped IO
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        bufsize=0 # Unbuffered
    )

    def pipe_stdin():
        try:
            while True:
                chunk = sys.stdin.buffer.read(1024)
                if not chunk:
                    break
                process.stdin.write(chunk)
                process.stdin.flush()
        except Exception as e:
            sys.stderr.write(f"DEBUG: stdin pipe error: {e}\n")
        finally:
            if process.stdin:
                process.stdin.close()

    def pipe_stderr():
        try:
            for line in process.stderr:
                decoded = line.decode('utf-8', errors='ignore')
                log(f"DEBUG [stderr]: {decoded.strip()}")
        except Exception as e:
            pass

    # Thread to send proactive 'y\n' to bypass silent prompts
    def proactive_y():
        attempts = 0
        while attempts < 5: # Limit attempts
            time.sleep(5)
            if process.poll() is not None:
                break
            log("DEBUG: Sending proactive 'y\\n' to bypass potential silent prompts")
            try:
                process.stdin.write(b"y\n")
                process.stdin.flush()
                attempts += 1
            except:
                break
    
    threading.Thread(target=proactive_y, daemon=True).start()
    threading.Thread(target=pipe_stdin, daemon=True).start()
    threading.Thread(target=pipe_stderr, daemon=True).start()

    # Filter stdout - binary mode to avoid encoding issues with raw noise
    try:
        pending_data = b""
        while True:
            chunk = process.stdout.read(1)
            if not chunk:
                break
                
            pending_data += chunk
            
            # Use a longer sliding buffer for prompt detection
            decoded_chunk = pending_data.decode('utf-8', errors='ignore')
            
            # Check for various interactive prompts
            prompts = ["?", "Yes    No", "y/n"]
            if any(p in decoded_chunk for p in prompts) and len(decoded_chunk) < 500:
                if "{" not in decoded_chunk: 
                    log(f"DEBUG: Prompt detected: {decoded_chunk.strip()}")
                    process.stdin.write(b"y\n")
                    process.stdin.flush()
                    pending_data = b"" 
                    continue

            if b'\n' in pending_data:
                line_end = pending_data.find(b'\n') + 1
                line = pending_data[:line_end]
                pending_data = pending_data[line_end:]
                
                decoded_line = line.decode('utf-8', errors='ignore').strip()
                
                # Aggressively strip ANSI escape codes
                import re
                ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                clean_line = ansi_escape.sub('', decoded_line).strip()
                
                # Try to find JSON object in the line even if surrounded by noise
                if '{' in clean_line and '}' in clean_line:
                    start = clean_line.find('{')
                    end = clean_line.rfind('}') + 1
                    json_str = clean_line[start:end]
                    try:
                        json.loads(json_str)
                        log(f"DEBUG: JSON detected and passed: {json_str[:100]}...")
                        sys.stdout.buffer.write(json_str.encode('utf-8') + b'\n')
                        sys.stdout.flush()
                        continue
                    except json.JSONDecodeError:
                        pass
                
                if clean_line:
                    log(f"DEBUG [stdout]: {clean_line[:100]}")
                
    except Exception as e:
        log(f"DEBUG: Main loop error: {e}")
    finally:
        log("--- Wrapper Terminating ---")
        process.terminate()
        sys.exit(process.wait())

if __name__ == "__main__":
    filter_output()
