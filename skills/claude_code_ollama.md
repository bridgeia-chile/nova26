# SKILL: CLAUDE_CODE_OLLAMA
Esta habilidad te enseña cómo instalar y ejecutar "Claude Code" (herramienta de codificación agéntica de Anthropic) usando los modelos locales proporcionados por Ollama, en lugar de la API de pago.
Cualquier sub-agente de nova26 puede invocar esta configuración si se le delega una tarea usando Claude Code.

# SKILL: CLAUDE_CODE_OLLAMA
Esta habilidad te enseña cómo instalar y ejecutar "Claude Code" (herramienta de codificación agéntica de Anthropic) usando los modelos locales proporcionados por Ollama, en un entorno seguro y validado.
Cualquier sub-agente de nova26 puede invocar esta configuración si se le delega una tarea de programación compleja.

## Ejecución Segura usando el Script Local
A diferencia de configurarlo manualmente o descargarlo desde internet repetidas veces, **nova26 ya cuenta con un script instalador-lazador maestro (`setup_claude_ollama.ps1`)**.

Este script hace todo automáticamente de forma robusta e inteligente:
1. Verifica que Ollama esté instalado y disponible (`ollama --version`).
2. Verifica si Claude Code ya está instalado en el PATH. Si no lo está, lo descarga y lo instala de manera local y silenciosa.
3. Inyecta exactamente las variables de entorno para puentear a Ollama (`ANTHROPIC_API_KEY`, etc).
4. Aplica automáticamente los servidores remotos (`https://ollama.com`) si usas modelos **Cloud**.
5. Lanza el modelo elegido de forma nativa.

### Instrucciones de invocación
Siempre que tú u otro agente deban usar Claude Code, símplemente usa la herramienta del sistema (script execution o terminal) para lanzar el script en la raíz del proyecto.

#### Para Modelos Locales
```powershell
.\setup_claude_ollama.ps1 -Model "qwen2.5-coder:14b"
```

#### Para Modelos Cloud (E.j. gran capacidad)
Asegúrate de tener un ticket validado en consola (`ollama signin`) o una clave API válida configurada como `OLLAMA_API_KEY`.
```powershell
.\setup_claude_ollama.ps1 -Model "gpt-oss:120b-cloud"
```

## Modelos Recomendados para pasar al argumento "-Model"
* **Locales:** `qwen3-coder`, `qwen2.5-coder:14b`, `glm-4.7`, `gpt-oss:20b`
* **Cloud (Sin hardware):** `gpt-oss:120b-cloud`, `llama3-70b-cloud`

**Nota:** 
El agente que invoque este script se quedará "esperando" mientras el prompt de Claude Code captura la interfaz estándar. Trata a Claude como una Sub-Rutina avanzada que leerá el directorio actual por ti.
Si quieres pasar un prompt directamente, puedes usar el stdin u otras flags de claude si el sistema lo necesita.
