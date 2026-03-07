# nova26

An autonomous, sovereign, local-first AI agent with a persistent SQLite-based "soul". 

## Features
- **Simple**: Clean architecture, zero bloat, native libraries.
- **Secure**: Sandboxed execution, API keys encrypted in DB, granular permissions.
- **Sovereign**: 100% user-controlled data, entirely local.
- **Efficient**: PicoClaw inspired minimal memory footprint (512MB limit).
- **Portable**: Identity embedded in one portable `nova26.db` SQLite file.
- **Evolutionary**: Re-installs itself, learns, stores memories.

## Setup
Check `.env.example` and set up your local variables. Ensure you have Node JS and NPM installed for plugins.
Run `pip install -r requirements.txt`. 
If booting for the first time, run `python main.py setup`. 
Otherwise, `python main.py run`.

## Docker
Available out of the box via `docker-compose up -d`. Use bounded CPU and Memory containers.
