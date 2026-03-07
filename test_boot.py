```python
import asyncio
from main import NovaGravityBrain

async def test():
    print("Starting boot test...")
    b = NovaGravityBrain("nova26.db")
    try:
        await b.boot()
        print("Boot Success!")
    except Exception as e:
        print(f"Boot failed: {e}")
    finally:
        await b.db.close()
        print("DB Closed")

if __name__ == "__main__":
    asyncio.run(test())
