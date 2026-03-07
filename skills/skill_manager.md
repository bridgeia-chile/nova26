# SKILL: SKILL_MANAGER (Gestor de Habilidades)
Este skill te permite gestionar tus propias capacidades de forma dinámica.

## Capacidades:
1. **Listar habilidades**: Usa `skill_manager` con el método `list` para ver qué habilidades `.md` y permanentes tienes activas.
2. **Crear nueva habilidad (.md)**: Usa `skill_manager` con el método `create` para escribir una nueva instrucción persistente en tu sistema.
3. **Instalar habilidad (Terminal)**: Usa `skill_manager` con el método `install` para registrar habilidades que requieren instalación por comandos (ej. pip, npm).

## Cuándo usar:
- Cuando el usuario te pida aprender algo nuevo.
- Cuando necesites estructurar un proceso complejo y quieras guardarlo para el futuro.
- Cuando quieras verificar si tienes una herramienta específica instalada.

## Formato de Herramienta:
```json
{
  "action_type": "use_tool",
  "required_tool": "skill_manager",
  "tool_input": {
    "method": "list|create|install",
    "name": "nombre_habilidad", // para create
    "content": "contenido markdown", // para create
    "skill_data": { ... } // para install
  }
}
```
