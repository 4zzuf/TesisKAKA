# PrimerRepo

Este repositorio contiene utilidades para simulación.

Las simulaciones por defecto abarcan 500 horas de operación (alrededor de
21 días). Las métricas impresas convierten esa duración a días para facilitar
la interpretación. Por defecto se consideran hasta 20 autobuses en la estación.
La estación cuenta con 21 cargadores y 41 baterías (33 de ellas cargadas al
inicio).

## Gráfico de eficiencia operativa

Ejecuta el script `tiempos_intercambio.py` para visualizar el tiempo de
intercambio promedio de la estación según el número de autobuses. Cada vehículo
efectúa una ruta de cuatro horas y regresa con la batería al 30‑40 % de carga para
un nuevo intercambio. El valor mostrado incluye la espera en cola y el
reemplazo de 4 minutos, expresado en minutos:

```bash
python tiempos_intercambio.py
```
Se abrirá una ventana con la gráfica que relaciona el número de autobuses con
el tiempo promedio de cada intercambio.

## Gráficos de costos y consumos

El script `graficos_costos.py` genera cuatro gráficos:

1. Costo de operación con electricidad según el número de autobuses.
2. Comparación de costos usando electricidad y gas natural.
3. Consumo eléctrico en hora punta y fuera de punta.
4. Costo de operación por hora para ambas tecnologías.

El último gráfico presenta dos barras con el costo promedio por hora al operar
con gas natural frente a electricidad.

Los valores se escalan a un mes de operación para evitar distorsiones cuando
la simulación se ejecuta por 500 horas.

Para que los costos crezcan de forma continua al aumentar la flota,
`graficos_costos.py` amplía temporalmente la capacidad de carga de la estación
según la cantidad de autobuses evaluada. De esta manera no se genera la caída de
costos al pasar de cuatro a cinco vehículos ni la estabilización por encima de
diez.

El costo de operar con gas natural se calcula aparte empleando el consumo
promedio de cada autobús y no depende de los valores de electricidad.

Ejecuta:

```bash
python graficos_costos.py
```

## Ahorro de emisiones

Ejecuta `graficos_emisiones.py` para comparar las emisiones mensuales con
electricidad y gas natural. El gráfico incluye las emisiones de cada tecnología
y una barra adicional con el ahorro total de CO₂:

```bash
python graficos_emisiones.py
```

## Otros gráficos

El script `graficos_diarios.py` muestra la evolución diaria de los
intercambios de batería y del consumo de energía durante el periodo
simulado:

```bash
python graficos_diarios.py
```

## Ejecutar las pruebas

Instala `pytest` y ejecuta las pruebas con:

```bash
pytest
```
