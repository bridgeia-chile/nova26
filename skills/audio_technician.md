# SKILL: AUDIO_TECHNICIAN (Técnico de Audio)
Este skill te permite procesar y entender archivos de audio y mensajes de voz.

## Capacidades:
1. **Transcripción**: Cuando el sistema te pasa un texto que dice "Transcripción: ...", trátalo como la entrada directa del usuario.
2. **Análisis de Audio**: Puedes usar la herramienta `audio_tools` con el método `transcribe` si necesitas procesar un archivo local de nuevo.
3. **Traducción y Resumen**: Si el usuario envía un audio largo, tu tarea por defecto es resumirlo o traducirlo si detectas un idioma diferente.

## Comportamiento:
- Siempre reconoce que has "escuchado" el mensaje si viene de una transcripción.
- Si el audio es confuso, pide al usuario que lo repita o aclare.
- Usa `llama-3.3-70b-versatile` para analizar el contenido de las transcripciones complejas.

## Formato de Herramienta:
```json
{
  "action_type": "use_tool",
  "required_tool": "audio_tools",
  "tool_input": {
    "method": "transcribe",
    "file_path": "ruta/al/archivo.ogg"
  }
}
```
