#!/bin/bash
# Nova26 Installation Script for DietPi / Raspberry Pi
echo "=========================================="
echo "    Instalando Nova26 en DietPi..."
echo "=========================================="

# 1. Update and install dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git tmux jq

# 2. Setup Virtual Environment
python3 -m venv venv
source venv/bin/activate

# 3. Install Python requirements
# We upgrade pip first as it's highly recommended on ARM
pip install --upgrade pip
pip install -r requirements.txt

echo "=========================================="
echo "Instalación de dependencias completada."
echo "IMPORTANTE:"
echo "1. Debes crear un archivo .env basándote en el que tienes en Windows."
echo "2. Para ejecutar Nova26 de forma persistente usa tmux:"
echo "   tmux new -s nova"
echo "   source venv/bin/activate"
echo "   python main.py run --interface all"
echo "=========================================="
