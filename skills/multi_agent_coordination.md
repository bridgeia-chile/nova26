# SKILL: MULTI_AGENT_COORDINATION (Coordinación de Agentes Paralelos)

Esta habilidad te permite coordinar múltiples agentes simultáneamente para ejecutar tareas en paralelo, reduciendo el tiempo total de ejecución y aumentando la productividad del enjambre.

## Contexto
Como agente líder de la oficina de IA, tienes acceso a un dashboard con agentes activos y herramientas para gestionarlos. Esta habilidad sistematiza el proceso de paralelización.

## Proceso de Coordinación Paralela
1. **Identificación de Tareas Paralelizables**:
   - Analiza la tarea principal y descomponla en subtareas independientes o débilmente acopladas.
   - Evalúa si las subtareas pueden ejecutarse concurrentemente por diferentes agentes.
   - Considera dependencias de recursos o datos para evitar conflictos.

2. **Selección y Asignación de Agentes**:
   - Usa el dashboard o la herramienta `agent_manager` para conocer los agentes disponibles y sus capacidades.
   - Asigna cada subtarea al agente más adecuado (ej: tareas de diseño a Nova Design, tareas de código a Claude Code).
   - Proporciona instrucciones claras y contextos específicos a cada agente.

3. **Ejecución Paralela y Supervisión**:
   - Inicia la ejecución concurrente de las subtareas.
   - Monitorea el progreso mediante herramientas como `script_executor` para verificar estados o `agent_manager` para actualizaciones.
   - Interviene si algún agente encuentra errores o bloqueos, reasignando si es necesario.

4. **Consolidación de Resultados**:
   - Recopila los resultados de cada agente una vez completadas las subtareas.
   - Integra los resultados en un entregable coherente.
   - Valida la calidad y consistencia del resultado final.

## Herramientas Clave
- `agent_manager`: Para actualizar perfiles y gestionar agentes.
- `script_executor`: Para lanzar procesos paralelos o scripts de coordinación.
- `skill_manager`: Para crear habilidades específicas de paralelización si es necesario.
- `os_navigation`: Para manejar archivos compartidos entre agentes.
- Delegación a Claude Code (`delegate_code`) para tareas de programación complejas que puedan paralelizarse internamente.

## Ejemplo de Flujo
**Escenario**: Crear una landing page con diseño y backend.
1. **Identificación**: Subtareas: diseño UI (Nova Design), código frontend (Claude Code), lógica backend (Claude Code).
2. **Asignación**: Asignar diseño a Nova Design, frontend y backend a Claude Code (en dos hilos si es posible).
3. **Ejecución**: Iniciar ambos agentes simultáneamente. Supervisar progreso.
4. **Consolidación**: Unir el diseño y el código en una página funcional.

## Reglas de Seguridad
- Nunca paralelices tareas que compartan recursos críticos sin mecanismos de exclusión mutua.
- Verifica que los agentes tengan permisos adecuados para las tareas asignadas.
- Mantén un registro de las asignaciones para auditoría.

## Medición de Éxito
- Reducción del tiempo total de ejecución respecto a la ejecución secuencial.
- Finalización exitosa de todas las subtareas sin bloqueos.
- Calidad del resultado integrado comparable o superior al enfoque secuencial.
