"""
nova26 - Main Entry Point

Usage:
    python main.py                    # Normal start
    python main.py --soul /path/to.db # Specific soul path
    python main.py restore /path/to.db # Restore on new machine
    python main.py backup             # Create backup
    python main.py cli                # CLI mode
    python main.py setup              # First-time setup
"""

import argparse
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

from core.brain import NovaGravityBrain
from interfaces.telegram_bot import TelegramInterface
from interfaces.cli import CLIInterface
from interfaces.api_server import APIServer

# Load environment logic
load_dotenv()
DEFAULT_SOUL_PATH = os.getenv('SOUL_DB_PATH', str(Path(__file__).parent / "nova26.db"))

async def first_time_setup():
    print("🌌 nova26 - Primera Configuración")
    print("=" * 50)
    print("Por favor configura tus variables en .env y luego ejecuta `python main.py run`")
    # Extended wizard logic goes here
    pass

async def restore_from_soul(soul_path: str):
    print(f"🔄 Restaurando nova26 desde: {soul_path}")
    brain = NovaGravityBrain(soul_db_path=soul_path)
    await brain.restore()
    print("✅ nova26 ha resucitado con todas sus memorias")

async def main():
    parser = argparse.ArgumentParser(description="nova26 - Agente Autónomo de IA")
    parser.add_argument('command', nargs='?', default='run',
                        choices=['run', 'restore', 'backup', 'cli', 'setup', 'status'])
    parser.add_argument('--soul', type=str, default=DEFAULT_SOUL_PATH,
                        help='Ruta al archivo de alma (nova26.db)')
    parser.add_argument('--interface', type=str, default='all',
                        choices=['telegram', 'cli', 'api', 'all'])
    parser.add_argument('--verbose', action='store_true')

    args = parser.parse_args()

    if args.command == 'setup':
        await first_time_setup()
    elif args.command == 'restore':
        await restore_from_soul(args.soul)
    elif args.command == 'backup':
        print(f"🔒 Creando backup de {args.soul}...")
        # Backup logic
    elif args.command == 'run' or args.command == 'cli':
        interface_choice = 'cli' if args.command == 'cli' else args.interface
        
        brain = NovaGravityBrain(soul_db_path=args.soul)
        await brain.boot()

        # Init interfaces
        if interface_choice in ('telegram', 'all'):
            telegram = TelegramInterface(brain)
            await telegram.start()
            
        if interface_choice in ('api', 'all'):
            api = APIServer(brain)
            await api.start()
            
        if interface_choice in ('cli', 'all'):
            cli = CLIInterface(brain)
            await cli.start()
        else:
            # Keeps event loop running if only telegram/api
            while True:
                await asyncio.sleep(3600)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nApagando...")
