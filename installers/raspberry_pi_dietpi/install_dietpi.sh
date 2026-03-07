#!/bin/bash
# Nova26 Advanced Installation Script for DietPi / Raspberry Pi 3B+
# Author: BridgeIA
# This script installs dependencies, sets up Nova26, and creates a systemd service.

echo "========================================================"
echo "    🚀 Iniciando Instalación de Nova26 en DietPi..."
echo "========================================================"

# Check if running as root
if [ "$EUID" -ne 0 ]
  then echo "Por favor, corre este script como root (sudo ./install_dietpi.sh)"
  exit
fi

# 1. Update and install dependencies
echo "[1/6] Actualizando paquetes e instalando dependencias (Python, Git)..."
apt-get update -y
apt-get install -y python3 python3-pip python3-venv git jq curl

# 2. Get repository
INSTALL_DIR="/opt/nova26"
if [ ! -d "$INSTALL_DIR" ]; then
    echo "[2/6] Clonando repositorio de Nova26 en $INSTALL_DIR..."
    git clone https://github.com/bridgeia-chile/nova26.git $INSTALL_DIR
else
    echo "[2/6] El directorio $INSTALL_DIR ya existe. Descargando cambios más recientes..."
    cd $INSTALL_DIR
    git pull origin main
fi

cd $INSTALL_DIR

# 3. Setup Virtual Environment
echo "[3/6] Configurando entorno virtual de Python..."
python3 -m venv venv
source venv/bin/activate

# 4. Install Python requirements
echo "[4/6] Instalando dependencias de Python (requirements.txt)..."
pip install --upgrade pip
pip install -r requirements.txt

# 5. Environment Variables & DB Setup
echo "[5/6] Preparando configuración inicial..."
if [ ! -f ".env" ]; then
    echo "GROQ_API_KEY=" > .env
    echo "DEEPSEEK_API_KEY=" >> .env
    echo "GEMINI_API_KEY=" >> .env
    echo "TELEGRAM_BOT_TOKEN=" >> .env
    echo "OWNER_TELEGRAM_ID=" >> .env
    echo "SOUL_DB_PATH=./nova26.db" >> .env
    echo "PEER_NODES=http://[IP_DE_TU_PC]:8090" >> .env
    echo "¡Atención! Se ha creado un archivo '.env' vacío. Deberás rellenarlo."
fi

# Preguntar por el Rol del Agente
echo "--------------------------------------------------------"
echo "  🏷️ Configuración del Agente Principal de Nova26"
echo "--------------------------------------------------------"
read -p "Nombre del Agente (Ej: Aisha): [Aisha] " AGENT_NAME
AGENT_NAME=${AGENT_NAME:-Aisha}

read -p "Cargo/Rol del Agente (Ej: Supervisor, Asistente IA): [Asistente General] " AGENT_ROLE
AGENT_ROLE=${AGENT_ROLE:-Asistente General}

# Script rápido para inyectar este agente en SQLite apenas se corra main.py o check_db.py
cat <<EOF > setup_agent.py
import sqlite3
import os

db_path = './nova26.db'
if not os.path.exists(db_path):
    print("Database not yet initialized. Will be created on first run.")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE sub_agents SET name = ?, role = ? WHERE id = 'agent-01'", ('$AGENT_NAME', '$AGENT_ROLE'))
    if cursor.rowcount == 0:
        cursor.execute("INSERT OR REPLACE INTO sub_agents (id, name, role, status) VALUES ('agent-01', ?, ?, 'online')", ('$AGENT_NAME', '$AGENT_ROLE'))
    conn.commit()
    conn.close()
    print(f"Agente Configurado: {('$AGENT_NAME')} como {('$AGENT_ROLE')}")
EOF

# 6. Setup Systemd Service for 24/7
echo "[6/6] Creando servicio systemd (nova26.service) para ejecución 24/7..."
cat <<EOF > /etc/systemd/system/nova26.service
[Unit]
Description=Nova26 Agent Framework
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python main.py run --interface all
Restart=on-failure
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=nova26

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable nova26.service

echo "========================================================"
echo " ✅ Instalación Inicial Completada Exitosamente!"
echo "========================================================"
echo "Pasos pendientes antes de arrancar:"
echo "1. Edita el archivo de entorno con tus APIs:"
echo "   nano $INSTALL_DIR/.env"
echo "2. Ejecuta el entorno por primera vez para crear la BD y asignar rol:"
echo "   cd $INSTALL_DIR && source venv/bin/activate && python main.py check && python setup_agent.py"
echo "3. Arranca el servicio en segundo plano definitivo:"
echo "   sudo systemctl start nova26.service"
echo ""
echo "Para ver si está corriendo: sudo systemctl status nova26.service"
echo "Para ver los logs diarios: sudo journalctl -u nova26.service -f"
echo "========================================================"
