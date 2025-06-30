import argparse
import matplotlib.pyplot as plt
import modelo
from modelo import (
    param_simulacion,
    param_economicos,
    param_estacion,
    param_operacion,
)
from parametros import ParametrosBateria

TIEMPO_REEMPLAZO = 4 / 60  # Tiempo de intercambio de la batería en horas


def grafico_carga_bateria(block: bool = True):
    """Grafica la curva de potencia de carga según el SoC."""
    bateria = ParametrosBateria()
    soc_vals = list(range(0, 91))
    potencias = [bateria.potencia_carga(s) for s in soc_vals]

    plt.figure(figsize=(8, 4))
    plt.plot(soc_vals, potencias, marker="o")
    plt.xlabel("Estado de carga (%)")
    plt.ylabel("Potencia de carga (kW)")
    plt.title("Curva de carga de la batería")
    plt.grid(True)
    plt.tight_layout()
    plt.show(block=block)


def _costos_para_autobuses(numero_autobuses, tiempo_ruta=4):
    """Devuelve costos y consumos para la cantidad dada de autobuses."""
    anterior = modelo.VERBOSE
    modelo.VERBOSE = False

    cap_ant = param_estacion.capacidad_estacion
    tot_ant = param_estacion.total_baterias
    ini_ant = param_estacion.baterias_iniciales
    param_estacion.actualizar(
        capacidad=max(numero_autobuses, cap_ant),
        total=max(numero_autobuses * 2, tot_ant),
        iniciales=max(numero_autobuses, ini_ant),
    )
    estacion = modelo.ejecutar_simulacion(max_autobuses=numero_autobuses)
    param_estacion.actualizar(capacidad=cap_ant, total=tot_ant, iniciales=ini_ant)

    modelo.VERBOSE = anterior

    factor = 720 / param_simulacion.duracion
    costo_electrico = estacion.costo_total_electrico * factor
    costo_gas = costo_gas_teorico(numero_autobuses, tiempo_ruta) * factor
    energia_punta = estacion.energia_punta_electrica * factor
    energia_fuera = (estacion.energia_total_cargada - estacion.energia_punta_electrica) * factor
    return costo_electrico, costo_gas, energia_punta, energia_fuera


def costo_gas_teorico(numero_autobuses, tiempo_ruta=4):
    """Calcula el costo de operar los autobuses con gas natural."""
    ciclos = param_simulacion.duracion / tiempo_ruta
    energia_total = numero_autobuses * param_operacion.consumo_gas_hora * tiempo_ruta * ciclos
    return energia_total * param_economicos.costo_gas_kwh


def grafico_costos(block: bool = True):
    """Genera los gráficos de costos y consumo eléctrico."""
    max_autos = param_simulacion.max_autobuses
    valores = list(range(1, max_autos + 1))
    resultados = [_costos_para_autobuses(n) for n in valores]
    costos_elec, costos_gas, energias_punta, energias_fuera = zip(*resultados)

    plt.figure(figsize=(8, 4))
    plt.plot(valores, costos_elec, marker="o")
    plt.xlabel("Número de autobuses")
    plt.ylabel("Costo eléctrico (S/.)")
    plt.title("Costo de operación con electricidad")
    plt.grid(True)
    plt.tight_layout()
    plt.show(block=block)

    anterior = modelo.VERBOSE
    modelo.VERBOSE = False
    estacion = modelo.ejecutar_simulacion()
    modelo.VERBOSE = anterior
    costo_e_hora = estacion.costo_total_electrico / param_simulacion.duracion
    costo_g_hora = estacion.costo_total_gas / param_simulacion.duracion

    plt.figure(figsize=(6, 4))
    etiquetas = ["Electricidad/hora", "Gas natural/hora"]
    valores_bar = [costo_e_hora, costo_g_hora]
    plt.bar(etiquetas, valores_bar, color=["tab:blue", "tab:orange"])
    plt.ylabel("Costo (S/./h)")
    plt.title("Costo promedio por hora de operación")
    plt.tight_layout()
    plt.show(block=block)

    plt.figure(figsize=(8, 4))
    plt.plot(valores, costos_elec, marker="o", label="Electricidad")
    plt.plot(valores, costos_gas, marker="s", label="Gas natural")
    plt.xlabel("Número de autobuses")
    plt.ylabel("Costo (S/.)")
    plt.title("Comparación de costos de operación")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show(block=block)

    plt.figure(figsize=(8, 4))
    plt.plot(valores, energias_punta, marker="o", label="Hora punta")
    plt.plot(valores, energias_fuera, marker="s", label="Fuera de punta")
    plt.xlabel("Número de autobuses")
    plt.ylabel("Consumo eléctrico (kWh)")
    plt.title("Consumo en hora punta y fuera de punta")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show(block=block)


def grafico_diarios(block: bool = True):
    """Grafica intercambios y consumo diarios."""
    anterior = modelo.VERBOSE
    modelo.VERBOSE = False
    estacion = modelo.ejecutar_simulacion()
    modelo.VERBOSE = anterior

    dias = param_simulacion.dias
    intercambios = [0] * (dias + 1)
    energia = [0.0] * (dias + 1)
    for dia, _, energia_swap in estacion.registro_intercambios:
        if dia <= dias:
            intercambios[dia] += 1
            energia[dia] += energia_swap

    plt.figure(figsize=(8, 4))
    plt.plot(range(dias + 1), intercambios, marker="o")
    plt.xlabel("Día de operación")
    plt.ylabel("Intercambios de batería")
    plt.title("Intercambios diarios")
    plt.grid(True)
    plt.tight_layout()
    plt.show(block=block)

    plt.figure(figsize=(8, 4))
    plt.plot(range(dias + 1), energia, marker="s", color="tab:orange")
    plt.xlabel("Día de operación")
    plt.ylabel("Energía cargada (kWh)")
    plt.title("Consumo diario de energía")
    plt.grid(True)
    plt.tight_layout()
    plt.show(block=block)


def grafico_emisiones(block: bool = True):
    """Muestra un gráfico comparando emisiones y el ahorro total de CO2."""
    anterior = modelo.VERBOSE
    modelo.VERBOSE = False
    estacion = modelo.ejecutar_simulacion()
    modelo.VERBOSE = anterior

    factor = 720 / param_simulacion.duracion
    emis_elec = (
        estacion.energia_total_cargada * param_economicos.factor_co2_elec * factor / 1000
    )
    emis_gas = (
        estacion.energia_total_gas * param_economicos.factor_co2_gas * factor / 1000
    )
    ahorro = emis_gas - emis_elec

    plt.figure(figsize=(6, 4))
    etiquetas = ["Electricidad", "Gas natural", "Ahorro de CO2"]
    valores = [emis_elec, emis_gas, ahorro]
    plt.bar(etiquetas, valores, color=["tab:blue", "tab:orange", "tab:green"])
    plt.ylabel("Toneladas de CO2 por mes")
    plt.title("Comparación de emisiones mensuales")
    plt.tight_layout()
    plt.show(block=block)


def main():
    parser = argparse.ArgumentParser(
        description="Genera distintos gráficos del modelo de simulación"
    )
    parser.add_argument(
        "grafico",
        choices=["carga", "costos", "diarios", "emisiones"],
        help="Tipo de gráfico a mostrar",
    )
    args = parser.parse_args()

    if args.grafico == "carga":
        grafico_carga_bateria()
    elif args.grafico == "costos":
        grafico_costos()
    elif args.grafico == "diarios":
        grafico_diarios()
    elif args.grafico == "emisiones":
        grafico_emisiones()


if __name__ == "__main__":  # pragma: no cover - ejecución manual
    main()
