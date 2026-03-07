#!/bin/bash
# Nova26 Auto-Updater Script
# This pulls the latest code from GitHub while preserving local database and .env files.

INSTALL_DIR="/opt/nova26"

echo "========================================================"
echo "    Actualizando Nova26 desde GitHub..."
echo "========================================================"

cd $INSTALL_DIR

# 1. Pull latest code (ignores local uncommitted changes except .env/.db which are in .gitignore)
git pull origin main

# 2. Update python dependencies if requirements.txt changed
source venv/bin/activate
pip install -r requirements.txt

# 3. Restart the service
echo "Reiniciando el servicio de Nova26..."
sudo systemctl restart nova26.service

echo "========================================================"
echo " ✅ Actualización Completada. Nova26 está corriendo la última versión."
echo " Para revisar logs: sudo journalctl -u nova26.service -f"
echo "========================================================"
