import asyncio
import logging
import os
from pathlib import Path
from core.brain import NovaGravityBrain

# Configure logging to see MCP details
logging.basicConfig(level=logging.INFO)

async def test_claude_integration():
    db_path = "nova26.db"
    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found.")
        return

    print("--- Booting Nova Gravity Brain ---")
    brain = NovaGravityBrain(soul_db_path=db_path)
    await brain.boot()
    
    print("\n--- Testing Claude Code Delegation ---")
    test_prompt = "Create a simple hello_world.py script in the current directory."
    
    # We simulate the process_input but specifically for a delegate_code action
    # Or just call _act directly if we want to bypass reasoning for testing
    decision = {
        "action_type": "delegate_code",
        "required_tool": "claude_code",
        "tool_input": {
            "prompt": test_prompt,
            "workdir": "."
        }
    }
    
    print(f"Sending task to Claude: {test_prompt}")
    try:
        # Give a small delay for MCP connection background task to stabilize
        await asyncio.sleep(2)
        
        result = await brain._act(decision)
        print("\n--- Result from Claude Code ---")
        print(result.get('response'))
        
    except Exception as e:
        print(f"\nError during delegation: {str(e)}")
    finally:
        await brain.hibernate()

if __name__ == "__main__":
    asyncio.run(test_claude_integration())
