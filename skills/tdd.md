# SKILL: TDD (Test Driven Development)
La calidad no es negociable. Este skill rige la fase de ejecución.

## El Ciclo Rojo-Verde-Refactor
1. **ROJO**: Escribe un test unitario o de integración para la funcionalidad actual. Ejecútalo y confirma que falla.
2. **VERDE**: Escribe el código mínimo necesario para que el test pase. No más.
3. **REFACTOR**: Mejora el código sin cambiar su comportamiento. Asegúrate de que los tests sigan pasando.
4. **COMMIT**: Guarda tus cambios una vez que el ciclo se complete.

## Reglas de Oro
- **BORRADO**: Si escribes código de producción antes que el test, bórralo y empieza de nuevo.
- **EVIDENCIA**: El éxito no se declara por palabra, se declara por un test pasando en la terminal.
- **ANTIPATRONES**: Evita tests frágiles o que prueben implementación en lugar de comportamiento.
