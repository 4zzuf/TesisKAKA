# PrimerRepo

Este repositorio contiene utilidades para simulación.

d1xt4j-codex/cambiar-frecuencia-de-salida-de-los-buses
Las simulaciones por defecto abarcan 21 días de operación. Internamente esa
duración se convierte a horas cuando es necesario, pero la entrada y las
métricas se expresan en días para mayor claridad. Por defecto se consideran
hasta 20 autobuses en la estación.
## Instalación

Instala las dependencias con:

```bash

pip install -r requirements.txt
```


main
La estación cuenta con 21 cargadores y 41 baterías (33 de ellas cargadas al
inicio).
Durante los fines de semana la demanda de autobuses se reduce a la mitad,
por lo que cada ruta dura ocho horas en lugar de cuatro. Las horas de entrada
y salida se registran en formato ``hh:mm``.

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

Además, el mismo módulo incluye una función para graficar cuánto tiempo
permanecen las baterías cargadas en la estación antes de ser utilizadas. Para
mostrarla ejecuta:

```bash
python -c "import tiempos_intercambio as t; t.graficar_espera_baterias()"
```

## Gráficos de costos y consumos

El módulo `GraficosModelo.py` genera varias gráficas:

1. Costo de operación con electricidad según el número de autobuses.
2. Comparación de costos usando electricidad y gas natural.
3. Consumo eléctrico en hora punta y fuera de punta.
4. Costo de operación por hora para ambas tecnologías.

El último gráfico presenta dos barras con el costo promedio por hora al operar
con gas natural frente a electricidad.

Los valores se escalan a un mes de operación para evitar distorsiones cuando
la simulación se ejecuta por 21 días.

Para que los costos crezcan de forma continua al aumentar la flota,
`GraficosModelo.py costos` amplía temporalmente la capacidad de carga de la estación
según la cantidad de autobuses evaluada. De esta manera no se genera la caída de
costos al pasar de cuatro a cinco vehículos ni la estabilización por encima de
diez.

El costo de operar con gas natural se calcula aparte empleando el consumo
promedio de cada autobús y no depende de los valores de electricidad. Para
estas simulaciones se considera un uso de 100 kWh por hora, lo que equivale a
unos 200 000 kWh para una flota de veinte vehículos durante 21 días de
operación.

Ejecuta:

```bash
python GraficosModelo.py costos
```

## Ahorro de emisiones

Ejecuta `GraficosModelo.py emisiones` para comparar las emisiones totales del
período con electricidad y gas natural. El gráfico incluye las emisiones de
cada tecnología y una barra adicional con el ahorro total de CO₂:

```bash
python GraficosModelo.py emisiones
```

## Otros gráficos

El módulo `GraficosModelo.py` incluye varias visualizaciones adicionales:

- `diarios`: intercambios y consumo de energía por día.
- `inventario`: baterías cargadas y descargadas disponibles cada hora.
- `cola`: minutos de espera acumulados cada hora.
- `costosdia`: costo eléctrico diario diferenciando laborables y fines de semana.
- `cargadores`: porcentaje de utilización de los cargadores a lo largo del tiempo.


Estas mismas opciones están disponibles en la interfaz gráfica seleccionando el tipo de gráfico en el menú desplegable.

Por ejemplo, para mostrar el inventario de baterías desde la terminal ejecuta:


```bash
python GraficosModelo.py inventario
```

## Simulación desde la línea de comandos

El módulo `cli.py` permite ejecutar la simulación ajustando los parámetros
básicos desde la terminal. Por ejemplo, para simular 30 días con 25 autobuses y
una estación de 30 cargadores:

```bash
python cli.py --dias 30 --max-autobuses 25 --capacidad-estacion 30
```

También es posible cambiar la cantidad total de baterías o la semilla
aleatoria:

```bash
python cli.py --total-baterias 60 --baterias-iniciales 50 --semilla 123
```

## Ejecutar las pruebas

Instala los requisitos y ejecuta las pruebas con:

```bash
pytest
```
