# nova26

An autonomous, sovereign, local-first AI agent with a persistent SQLite-based "soul". 

## Features
- **Simple**: Clean architecture, zero bloat, native libraries.
- **Secure**: Sandboxed execution, API keys encrypted in DB, granular permissions.
- **Sovereign**: 100% user-controlled data, entirely local.
- **Efficient**: PicoClaw inspired minimal memory footprint (512MB limit).
- **Portable**: Identity embedded in one portable `nova26.db` SQLite file.
- **Evolutionary**: Re-installs itself, learns, stores memories.

## 🚀 Guía de Instalación y Configuración (Paso a Paso)

Sigue estos pasos para instalar y ejecutar **nova26** en tu entorno local (Windows/Linux/Mac).

### 1. Prerrequisitos
- **Python 3.10+** instalado y agregado al PATH.
- **Node.js y npm** (Requeridos para ejecutar los servidores MCP de Google Stitch y NotebookLM).
- **Git** instalado.

### 2. Clonar el Repositorio e Instalar Dependencias
Abre tu terminal y ejecuta:
```bash
git clone https://github.com/bridgeia-chile/nova26.git
cd nova26
pip install -r requirements.txt
```

### 3. Configurar Variables de Entorno
Copia el archivo de ejemplo y configura tus claves API:
```bash
cp .env.example .env
```
Abre el archivo `.env` y asegúrate de agregar al menos una clave API (Groq, Anthropic u OpenAI).
- Las API Keys se cifran al inyectarse en la base de datos para mayor seguridad.
- Si vas a usar nodos remotos, configura `PEER_NODES`.

### 4. Inicializar la Base de Datos "Soul"
Nova26 utiliza SQLite para almacenar todos sus conocimientos, configuración y estado de agentes.
```bash
# Crea nova26.db, la tabla de agentes, tokens y memoria
python setup_db.py

# (Opcional pero recomendado) Configura el sub-agente de ciberseguridad Nova Sentry
python setup_security.py
```

### 5. Configurar Servidores MCP (Herramientas Externas)
Para que los agentes de diseño e investigación funcionen al 100%, debes registrar las herramientas MCP (Model Context Protocol):

**Para Google Stitch (Diseño UI/UX):**
```bash
python register_stitch.py
```

**Para Google NotebookLM (Gestión de Documentos y Conocimiento):**
```bash
python register_notebooklm.py
```
*Nota: NotebookLM requerirá autenticación con tu cuenta de Google la primera vez que intente ejecutarse.*

### 6. Ejecutar Nova26
Para arrancar el cerebro principal, el dashboard web y las integraciones P2P/Telegram, ejecuta:
```bash
python main.py run --interface all
```

**Acceso al Dashboard:**
Abre en tu navegador `http://localhost:8090` para ver e interactuar con todos tus sub-agentes en tiempo real.
## Docker
Available out of the box via `docker-compose up -d`. Use bounded CPU and Memory containers.
