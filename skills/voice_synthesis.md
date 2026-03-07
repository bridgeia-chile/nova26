# SKILL: VOICE_SYNTHESIS (Síntesis de Voz)
Este skill te permite comunicarte verbalmente a través de audio.

## Capacidades:
1. **Respuesta por Voz**: Si el usuario te pide "háblame" o menciona "audio", genera tu respuesta y el sistema la convertirá automáticamente a voz.
2. **Personalidad Conversacional**: Usa un tono cercano y fluido. Como usas una voz femenina (Victoria/Bella), adapta tus expresiones para sonar natural en español.
3. **Control de Audio**: Puedes usar la herramienta `audio_tools` con el método `speak` si necesitas generar un audio con un texto específico diferente a tu respuesta actual.

## Cuándo usar:
- Cuando el usuario prefiera escuchar a leer.
- Para dar noticias, leer resúmenes largos de forma amena.
- Para practicar idiomas.

## Formato de Herramienta:
```json
{
  "action_type": "use_tool",
  "required_tool": "audio_tools",
  "tool_input": {
    "method": "speak",
    "text": "Texto que quieres que sea locutado",
    "voice_id": "opcional_id_de_voz"
  }
}
```
