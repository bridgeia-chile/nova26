<#
.SYNOPSIS
Instalador y Lanzador Local de Claude Code (con soporte para Ollama) para Nova26
.DESCRIPTION
Este script verifica si Ollama está instalado y en ejecución, y luego asegura que
Claude Code (claude.exe) este disponible localmente. Una vez configurado, lanza
la CLI de Claude Code apuntando a tu instancia local de Ollama.
#>

param (
    [string]$Model = "qwen2.5-coder:14b",
    [string]$WorkspaceDir = "$PSScriptRoot"
)

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  Nova26 - Claude Code Agentic Workflow Setup     " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar Ollama
Write-Host "[*] Comprobando disponibilidad de Ollama..."
try {
    $ollamaVersion = ollama --version 2>$null
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($ollamaVersion)) {
        Write-Host "[!] ERROR: Ollama no esta instalado o no se reconoce el comando 'ollama'." -ForegroundColor Red
        Write-Host "    Instalalo desde https://ollama.com/"
        exit 1
    }
    Write-Host "    [OK] Ollama encontrado: $ollamaVersion" -ForegroundColor Green
} catch {
    Write-Host "[!] ERROR: Ollama no esta disponible en el PATH." -ForegroundColor Red
    exit 1
}

# 2. Descargar instalador de Claude Code de manera local si no existe
$ClaudeInstallPath = "$env:APPDATA\npm\claude.cmd" # Ruta por defecto de npm instalation
$LocalClaudeScript = "$WorkspaceDir\claude_installer.ps1"

if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
    Write-Host "[*] Claude Code no esta instalado. Descargando el instalador oficial de Anthropic..." -ForegroundColor Yellow
    try {
        Invoke-RestMethod -Uri "https://claude.ai/install.ps1" -OutFile $LocalClaudeScript
        Write-Host "    [OK] Instalador descargado en $LocalClaudeScript" -ForegroundColor Green
        
        Write-Host "[*] Instalando Claude Code (esto puede tardar unos segundos)..." -ForegroundColor Yellow
        # Desbloquear archivo de ejecución y correr
        Unblock-File -Path $LocalClaudeScript
        & $LocalClaudeScript
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[!] ERROR al instalar Claude Code. Revisa los mensajes de la consola." -ForegroundColor Red
            exit 1
        }
        Write-Host "    [OK] Instalacion de Claude Code finalizada." -ForegroundColor Green
    } catch {
        Write-Host "[!] ERROR de red o permisos al descargar/ejecutar el instalador de Claude: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "    [OK] Claude Code ya esta instalado en el sistema." -ForegroundColor Green
}

# 3. Configurar Entorno Compatible con Ollama y Lanzar
if ($Model -match "cloud$" -or $Model -match "gpt-oss:120b") {
    Write-Host "[*] Detectado modelo Cloud. Configurando puente hacia API remota (ollama.com)..." -ForegroundColor Yellow
    
    if (-not $env:OLLAMA_API_KEY) {
        Write-Host "[!] ADVERTENCIA: Para los modelos cloud, necesitas estar logeado en ollama (ollama signin) o tener un OLLAMA_API_KEY." -ForegroundColor Magenta
        Write-Host "    Asegurate de haber configurado tu clave en las variables de entorno si usas la API."
    }
    
    $env:ANTHROPIC_AUTH_TOKEN = "ollama"
    $env:ANTHROPIC_BASE_URL = "https://ollama.com"
    # Claude necesita apiKey, pero en el modo cloud real se usa un bearer o la sesión local de ollama.
    # En muchos casos Ollama Cloud acepta tokens genéricos si se usa localhost. En caso de usar la url directa, pasamos la OLLAMA_API_KEY.
    $env:ANTHROPIC_API_KEY = if ($env:OLLAMA_API_KEY) { $env:OLLAMA_API_KEY } else { "ollama" }
    
} else {
    Write-Host "[*] Configurando puente API directo a Ollama Local (localhost:11434)..." -ForegroundColor Yellow
    $env:ANTHROPIC_AUTH_TOKEN = "ollama"
    $env:ANTHROPIC_API_KEY = "ollama"
    $env:ANTHROPIC_BASE_URL = "http://localhost:11434"
}


Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " Inicializando Agente (Modelo: $Model)...         " -ForegroundColor Cyan
Write-Host " Escribe '/exit' o '/clear' dentro de claude.     " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

claude --model $Model

# Si se sale, limpiar
$env:ANTHROPIC_AUTH_TOKEN = $null
$env:ANTHROPIC_API_KEY = $null
$env:ANTHROPIC_BASE_URL = $null

Write-Host "[*] Sesion de Claude Code finalizada." -ForegroundColor Green
exit 0
