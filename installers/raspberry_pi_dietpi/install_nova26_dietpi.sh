#!/bin/bash
# NovaGravity (Nova26) Installer for Raspberry Pi 4 (DietPi OS)
# Architecture: ARM64 / Memory: 4GB Recommended

set -e

echo "====================================================="
echo "   Instalador de Nova26 para Raspberry Pi (DietPi)"
echo "====================================================="

# 1. Update system and install base dependencies
echo "[*] Actualizando sistema operativo e instalando dependencias (Python, Git, Curl, Node.js)..."
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install -y python3 python3-pip python3-venv git curl htop screen sqlite3

# 2. Install Node.js (Required for Claude Code)
echo "[*] Instalando Node.js (Requerido para Claude Code)..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 3. Install Ollama (Optional, but recommended for Cloud/Tiny models)
echo "[*] Instalando Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# 4. Install Claude Code
echo "[*] Instalando Claude Code globalmente..."
sudo npm install -g @anthropic-ai/claude-code

# 5. Setup Python Virtual Environment for NovaGravity
echo "[*] Configurando Entorno Virtual de Python..."
cd "$(dirname "$0")/../.." # Assuming this is run from within installers/raspberry_pi_dietpi
PROJECT_ROOT=$(pwd)

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
echo "[*] Instalando dependencias de Python (puede tardar en una Raspberry Pi)..."
# Ensure wheel is installed
pip install wheel
# Install project requirements
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    # Fallback to absolute basics known for this project
    pip install psutil setuptools pynvml uvicorn fastapi python-telegram-bot sqlite3 rich pyyaml
fi

# 6. Initialize Database
echo "[*] Ejecutando migración inicial de la Base de Datos (Telemetría y Agentes)..."
if [ -f "migrate_telemetry.py" ]; then
    python migrate_telemetry.py
fi

# 7. Provide instructions for autostart / usage
echo "====================================================="
echo "¡INSTALACION COMPLETADA EXITOSAMENTE EN DIETPI!"
echo "====================================================="
echo "Notas sobre el hardware (Pi 4 - 4GB RAM):"
echo "  - Los modelos LLM pesados irán MUY lentos, por lo que te"
echo "    recomendamos utilizar la integración de Ollama Cloud"
echo "    o apalancar groq/gemini usando sus respectivas APIs."
echo ""
echo "Para arrancar Nova26:"
echo "  1. Copia tu archivo .env en $PROJECT_ROOT"
echo "  2. cd $PROJECT_ROOT"
echo "  3. source venv/bin/activate"
echo "  4. python main.py API (Para el backend de agentes y UI)"
echo "  5. python main.py CLI (Para interactuar en consola)"
echo "====================================================="
