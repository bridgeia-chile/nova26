import sys
import json

def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        try:
            req = json.loads(line)
            if req.get("method") == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req.get("id"),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "serverInfo": {"name": "dummy", "version": "1.0.0"}
                    }
                }
                print(json.dumps(resp), flush=True)
            elif req.get("method") == "notifications/initialized":
                pass
            else:
                # Echo back any other request for testing
                resp = {
                    "jsonrpc": "2.0",
                    "id": req.get("id"),
                    "result": {"status": "ok"}
                }
                print(json.dumps(resp), flush=True)
        except Exception as e:
            sys.stderr.write(f"Error: {e}\n")
            sys.stderr.flush()

if __name__ == "__main__":
    main()
