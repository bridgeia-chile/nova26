import subprocess
import os
import time
import sys
import json

def debug_mcp():
    env = os.environ.copy()
    claude_bin_path = r"C:\Users\Rosvel Nuñez\.local\bin"
    env["PATH"] = f"{claude_bin_path};{env.get('PATH', '')}"
    env["CI"] = "true"
    env["PYTHONUNBUFFERED"] = "1"
    env["ANTHROPIC_BASE_URL"] = "http://localhost:11434"
    env["ANTHROPIC_API_KEY"] = "ollama"
    env["ANTHROPIC_AUTH_TOKEN"] = "ollama"

    # First, verify version
    print("Running: claude --version")
    subprocess.run([r"C:\Users\Rosvel Nuñez\.local\bin\claude.exe", "--version"], env=env)

    # The command we want to verify - try local model via ollama launch
    cmd = ["ollama", "launch", "claude", "--model", "qwen2.5-coder:3b", "--", "mcp", "serve"]
    
    print(f"--- Running: {' '.join(cmd)} ---")
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        env=env,
        text=True,
        bufsize=1
    )

    # Send MCP initialize request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "NovaGravity-Debug", "version": "1.0"}
        }
    }
    process.stdin.write(json.dumps(init_request) + "\n")
    process.stdin.flush()
    print(f"Sent initialize request: {json.dumps(init_request)}")

    # Monitor output for 30 seconds
    start_time = time.time()
    try:
        while time.time() - start_time < 30:
            line = process.stdout.readline()
            if line:
                print(f"STDOUT: {line.strip()}")
            
            # Check stderr for noise
            # We don't want to block, so we use a non-blocking check if possible
            # But in this debug script, we just want to see if ANYTHING happens
            time.sleep(0.1)
            
            # Check if process died
            if process.poll() is not None:
                print(f"Process exited with code {process.returncode}")
                break
                
        if process.poll() is None:
            print("Process still running after 30s. Terminating...")
            process.terminate()
            
        stderr_rem = process.stderr.read()
        if stderr_rem:
            print(f"STDERR (remaining): {stderr_rem}")
            
    except KeyboardInterrupt:
        process.terminate()

if __name__ == "__main__":
    debug_mcp()
