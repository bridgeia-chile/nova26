# SKILL: GOOGLE WORKSPACE (gog)

Esta habilidad te permite acceder a los servicios de Google Workspace de tu cuenta actual (`aishaclaw2026@gmail.com`): Gmail, Calendar, Drive, Docs y Sheets.

## REGLAS IMPORTANTES:
1. Para usar estos comandos, DEBES usar la herramienta `os_navigation` con el método `execute`.
2. Nunca pidas contraseñas. La autenticación ya se realizó a nivel de sistema.
3. Al enviar correos o crear eventos, verifica primero la información si es un borrador, a menos que el usuario te dé la orden explícita de enviarlo.

## COMANDOS DISPONIBLES (Ejecutar en terminal)

**Nota Base**: Siempre usarás el comando `gog` para interactuar con la Workspace.

### 📧 Gmail
- **Buscar correos**: `gog gmail search "from:alguien@ejemplo.com" --max 10 --account aishaclaw2026@gmail.com`
- **Buscar mensajes específicos (por email individual)**: `gog gmail messages search "in:inbox" --max 5 --account aishaclaw2026@gmail.com`
- **Enviar correo corto**: `gog gmail send --to "destino@ejemplo.com" --subject "Asunto" --body "Cuerpo del mensaje" --account aishaclaw2026@gmail.com`
- **Crear borrador**: `gog gmail drafts create --to "destino@ejemplo.com" --subject "Asunto" --body "Texto" --account aishaclaw2026@gmail.com`
- **Responder correo**: `gog gmail send --to "destino@ejemplo.com" --subject "Re: Asunto" --body "Texto" --reply-to-message-id <msgId> --account aishaclaw2026@gmail.com`

*(Pauta para mensajes largos: si el correo es de varios párrafos, usa heredoc o pásalo a través de varios saltos de línea codificados como `$'Line 1\n\nLine2'`).*

### 📅 Calendar
- **Listar Eventos**: `gog calendar events primary --from "2024-01-01T00:00:00Z" --to "2024-01-31T23:59:59Z" --account aishaclaw2026@gmail.com`
- **Crear Evento**: `gog calendar create primary --summary "Reunión de Equipo" --from "2024-10-15T10:00:00Z" --to "2024-10-15T11:00:00Z" --account aishaclaw2026@gmail.com` 
  *(Nota: las fechas deben estar en formato ISO 8601)*

### 📁 Drive & Docs
- **Buscar Archivo**: `gog drive search "nombre del documento" --max 10 --account aishaclaw2026@gmail.com`
- **Leer Documento (Docs)**: `gog docs cat <docId> --account aishaclaw2026@gmail.com`

### 📊 Sheets
- **Leer Valores**: `gog sheets get <sheetId> "Hoja1!A1:D10" --json --account aishaclaw2026@gmail.com`
- **Actualizar Valores**: `gog sheets update <sheetId> "Hoja1!A1:B2" --values-json '[["Valor","Valor2"],["1","2"]]' --input USER_ENTERED --account aishaclaw2026@gmail.com`
- **Agregar Fila**: `gog sheets append <sheetId> "Hoja1!A:C" --values-json '[["Nuevo","Dato","Final"]]' --insert INSERT_ROWS --account aishaclaw2026@gmail.com`

## COMPORTAMIENTO ESPERADO:
Inmediatamente después de ejecutar estos comandos, procesa el *stdout* o el resultado JSON y dáselo al usuario en un formato agradable y conversacional. No envíes las tramas JSON puras a menos que el usuario lo solicite explícitamente.
