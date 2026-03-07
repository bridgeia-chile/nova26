import subprocess
import os

def debug_claude():
    env = os.environ.copy()
    claude_bin_path = r"C:\Users\Rosvel Nuñez\.local\bin"
    env["PATH"] = f"{claude_bin_path};{env.get('PATH', '')}"
    env["CI"] = "true"
    env["ANTHROPIC_BASE_URL"] = "http://localhost:11434"
    env["ANTHROPIC_API_KEY"] = "ollama"
    env["ANTHROPIC_AUTH_TOKEN"] = "ollama"

    print(f"--- Debugging Claude CLI at {claude_bin_path} ---")
    
    # Try running claude --help directly
    try:
        print("Running: claude --help")
        res = subprocess.run(["claude", "--help"], env=env, capture_output=True, text=True)
        print(f"STDOUT: {res.stdout[:500]}")
        print(f"STDERR: {res.stderr[:500]}")
        print(f"EXIT CODE: {res.returncode}")
    except Exception as e:
        print(f"ERROR running claude: {e}")

    # Try running via ollama launch
    try:
        print("\nRunning: ollama launch claude --help")
        res = subprocess.run(["ollama", "launch", "claude", "--help"], env=env, capture_output=True, text=True)
        print(f"STDOUT: {res.stdout[:500]}")
        print(f"STDERR: {res.stderr[:500]}")
        print(f"EXIT CODE: {res.returncode}")
    except Exception as e:
        print(f"ERROR running ollama launch: {e}")

if __name__ == "__main__":
    debug_claude()
