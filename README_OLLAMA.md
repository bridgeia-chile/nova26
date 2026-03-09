# Claude Code + Ollama (Super Setup)

Este script automatiza la configuración completa para ejecutar **Claude Code** (la CLI oficial de Anthropic) utilizando modelos locales de **Ollama**. Ahora incluye verificación de hardware y auto-instalación de dependencias.

## Características

-   **Verificación de Hardware**: Detecta RAM y GPU (NVIDIA/AMD) para asegurar un rendimiento óptimo.
-   **Auto-Instalación**: Instala automáticamente **Node.js**, **Ollama** y **Claude Code** si no se encuentran en el sistema (usando `winget` y `npm`).
-   **Gestión de Modelos**: Verifica si el modelo (por defecto `qwen2.5-coder`) está descargado y lo descarga automáticamente si falta.
-   **Configuración Local**: Redirige todo el tráfico de Claude hacia el endpoint local de Ollama de forma segura.

## Requisitos Previos

-   Windows 10/11.
-   Permisos de Administrador (para instalaciones automáticas vía `winget`).
-   Conexión a Internet (solo para la primera configuración o descarga de modelos).

## Cómo usar el script

1.  Abre una terminal de **PowerShell**.
2.  Ejecuta el script:

    ```powershell
    .\run-claude-ollama.ps1
    ```

3.  El script hará todo el trabajo pesado: verificará tu hardware, instalará lo que falte y finalmente iniciará la interfaz de Claude Code.

### Parámetros opcionales

Puedes elegir un modelo específico pasando el parámetro `-Model`:

```powershell
.\run-claude-ollama.ps1 -Model deepseek-coder-v2
```

## ¿Qué instala el script?

Si los componentes no están presentes, el script intentará instalar:
-   **Node.js**: Plataforma necesaria para Claude Code.
-   **Ollama**: El motor para correr modelos de lenguaje locales.
-   **@anthropic-ai/claude-code**: La herramienta de línea de comandos de Claude.

## Notas Técnicas

-   **API Key**: El script establece una clave ficticia (`ollama`), ya que Claude Code la requiere para iniciar, aunque el tráfico sea local.
-   **Endpoint**: Redirige la URL base a `http://localhost:11434/v1`.
-   **GPU**: Si tienes una GPU NVIDIA, Ollama la detectará automáticamente para acelerar las respuestas.
