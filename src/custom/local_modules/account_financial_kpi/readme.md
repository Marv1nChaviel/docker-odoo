## Descripción
Este módulo permite definir y monitorear Indicadores Clave de Desempeño (KPI) financieros utilizando fórmulas personalizadas basadas en saldos de cuentas contables. Proporciona un tablero visual para evaluar rápidamente la salud financiera de la empresa.

## Características Principales
- **Motor de Fórmulas Personalizadas**: Defina KPIs utilizando expresiones Python que pueden acceder al balance de cuentas.
- **Indicadores Visuales**: Sistema de semáforo (Verde, Amarillo, Rojo) para visualizar el estado de cada KPI frente a los objetivos.
- **Tablero de Control**: Vista unificada para monitorear todos los indicadores configurados.

## Uso
1. Vaya a Contabilidad > Informes > KPIs Financieros.
2. Cree un nuevo KPI definiendo:
   - Nombre del indicador.
   - Fórmula de cálculo (ej. `(cajas_y_bancos / pasivo_corriente)`).
   - Umbrales para los estados de alerta (Límite inferior, Objetivo).
3. Monitoree el tablero principal para ver el estado actualizado.

## Dependencias
- `account`
""",