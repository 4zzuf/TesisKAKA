import simpy
import random

import trafico

from parametros import (
    ParametrosBateria,
    ParametrosEstacion,
    ParametrosOperacionBus,
    ParametrosEconomicos,
    ParametrosSimulacion,
)


param_bateria = ParametrosBateria()
param_estacion = ParametrosEstacion()
param_operacion = ParametrosOperacionBus()
param_economicos = ParametrosEconomicos()
param_simulacion = ParametrosSimulacion()

# Controla la verbosidad de la simulación
VERBOSE = True

# Función para formatear horas decimales incluyendo el día de simulación
def formato_hora(horas_decimales):
    """Devuelve un string "Día DD hh:mm" para la hora dada."""
    dia = int(horas_decimales // 24) + 1
    horas_totales = horas_decimales % 24
    horas, minutos = divmod(horas_totales * 60, 60)
    return f"Día {dia:02} {int(horas):02}:{int(minutos):02}"

def es_fin_de_semana(tiempo):
    """Determina si la hora de simulación corresponde a fin de semana."""
    dia_semana = int(tiempo // 24) % 7
    return dia_semana >= 5

def calcular_soc_inicial(hora_actual):
    """Calcula el SoC inicial considerando el tráfico."""
    factor = trafico.factor_trafico(hora_actual)
    if factor >= 1.3:
        return random.uniform(10, 20)  # Tráfico muy congestionado
    if factor >= 1.1:
        return random.uniform(20, 30)  # Tráfico moderado
    return random.uniform(30, 40)  # Tráfico ligero


class EstacionIntercambio:
    def __init__(self, env, capacidad_estacion):
        self.env = env
        # "estaciones" representa los puntos donde los autobuses realizan el
        # cambio de batería. Cada cargador se gestiona mediante un proceso
        # independiente, por lo que no se requiere un recurso adicional.
        self.estaciones = simpy.Resource(env, capacity=capacidad_estacion)

        # Inventario de baterías cargadas disponible para los autobuses.
        # Se almacenan como el porcentaje de SoC que tienen, 100% significa
        # una batería completamente cargada.
        self.baterias_reserva = simpy.Store(
            env,
            capacity=param_estacion.total_baterias,
        )

        # Baterías descargadas a la espera de ser cargadas nuevamente.
        self.baterias_descargadas = simpy.Store(
            env,
            capacity=param_estacion.total_baterias,
        )

        # Inicializar los inventarios.
        self.baterias_reserva.items = [100 for _ in range(param_estacion.baterias_iniciales)]
        self.baterias_descargadas.items = [30 for _ in range(param_estacion.total_baterias - param_estacion.baterias_iniciales)]
        # Registrar el momento en que cada batería entra en reserva para medir el
        # tiempo que permanece en espera hasta ser utilizada.
        self._ingreso_reserva = [0.0 for _ in range(param_estacion.baterias_iniciales)]
        self.tiempos_espera_baterias = []
        self.baterias_cargando = 0  # Cantidad de baterías actualmente en carga
        self.tiempo_espera_total = 0  # Tiempo total de espera acumulado
        self.energia_total_cargada = 0  # Energía total consumida para cargar baterías
        self.costo_total_electrico = 0  # Costo total de carga eléctrica
        self.costo_total_gas = 0  # Costo total si se usara gas natural
        self.energia_total_gas = 0  # Energía total consumida si se usara gas
        self.energia_punta_autobuses = 0  # Energía consumida en hora punta por autobuses
        self.energia_fuera_punta_autobuses = 0  # Energía consumida fuera de hora punta por autobuses
        self.energia_punta_electrica = 0  # Energía consumida en hora punta de electricidad
        self.intercambios_realizados = 0  # Cantidad de reemplazos efectuados
        # Historial de intercambios (día, hora, energía)
        self.registro_intercambios = []

        # Costo de cargar las baterías iniciales
        self.cargar_baterias_iniciales()

        # Inicia procesos de carga paralelos para cada cargador
        for _ in range(param_estacion.capacidad_estacion):
            self.env.process(self.cargar_bateria())

    def cargar_baterias_iniciales(self):
        for _ in range(param_estacion.baterias_iniciales):
            hora_actual = 0  # Asumimos que se cargaron antes del inicio de la simulación
            capacidad_carga = param_bateria.capacidad
            if param_economicos.horas_punta[0] <= hora_actual < param_economicos.horas_punta[1]:  # Hora punta eléctrica
                costo_carga = capacidad_carga * param_economicos.costo_punta
            else:  # Hora fuera de punta
                costo_carga = capacidad_carga * param_economicos.costo_normal

            self.energia_total_cargada += capacidad_carga
            self.costo_total_electrico += costo_carga

    def reemplazar_bateria(self, autobuses_id, soc_inicial, hora_actual):
        """Realiza el intercambio asumiendo que hay batería disponible."""
        # Tomar una batería cargada de la reserva y depositar la usada
        # ``soc_inicial`` corresponde al nivel de carga de la batería usada
        # cuando el autobús llega a la estación.
        _ = yield self.baterias_reserva.get()
        ingreso = self._ingreso_reserva.pop(0)
        self.tiempos_espera_baterias.append(self.env.now - ingreso)
        yield self.baterias_descargadas.put(soc_inicial)
        capacidad_requerida = (param_bateria.soc_objetivo - soc_inicial) / 100 * param_bateria.capacidad
        tiempo_reemplazo = 4 / 60  # 4 minutos en horas
        hora_final = self.env.now + tiempo_reemplazo  # Hora después del intercambio
        if VERBOSE:
            print(
                f"Autobús {autobuses_id} reemplaza su batería en {formato_hora(self.env.now)} "
                f"(SoC inicial: {soc_inicial:.2f}%). Hora final: {formato_hora(hora_final)}"
            )
        yield self.env.timeout(tiempo_reemplazo)
        self.intercambios_realizados += 1
        dia_actual = int(self.env.now // 24)
        hora_registro = formato_hora(self.env.now)
        self.registro_intercambios.append((dia_actual, hora_registro, capacidad_requerida))

        # Clasificar consumo de energía según hora punta de autobuses
        if 7 <= hora_actual < 9 or 18 <= hora_actual < 20:
            self.energia_punta_autobuses += capacidad_requerida
        else:
            self.energia_fuera_punta_autobuses += capacidad_requerida

        # Clasificar consumo según hora punta de electricidad
        if param_economicos.horas_punta[0] <= hora_actual < param_economicos.horas_punta[1]:  # Hora punta eléctrica
            self.energia_punta_electrica += capacidad_requerida

        # La estimación de consumo de gas se calcula tras la ruta del autobús

    def cargar_bateria(self):
        """Proceso individual de un cargador."""
        while True:
            # Comprobar cada minuto si hay baterías por cargar
            if len(self.baterias_descargadas.items) == 0:
                yield self.env.timeout(1 / 60)
                continue

            soc_actual = yield self.baterias_descargadas.get()
            self.baterias_cargando += 1

            hora_actual = int(self.env.now % 24)
            capacidad_carga = (
                (param_bateria.soc_objetivo - soc_actual) / 100
            ) * param_bateria.capacidad
            tiempo_carga = param_bateria.tiempo_carga(soc_actual)

            if param_economicos.horas_punta[0] <= hora_actual < param_economicos.horas_punta[1]:
                costo_carga = capacidad_carga * param_economicos.costo_punta
                if VERBOSE:
                    print(
                        f"Se está cargando una batería en hora punta (Hora actual: {hora_actual})"
                    )
            else:
                costo_carga = capacidad_carga * param_economicos.costo_normal
                if VERBOSE:
                    print(
                        f"Se está cargando una batería fuera de hora punta (Hora actual: {hora_actual})"
                    )

            yield self.env.timeout(tiempo_carga)

            self.baterias_cargando -= 1
            yield self.baterias_reserva.put(param_bateria.soc_objetivo)
            self._ingreso_reserva.append(self.env.now)
            self.energia_total_cargada += capacidad_carga
            self.costo_total_electrico += costo_carga


# Procesos para simular la llegada de autobuses
def llegada_autobuses(env, estacion, max_autobuses, tiempo_ruta=4):
    """Genera la llegada inicial de autobuses y crea procesos cíclicos.

    Durante horas pico (7:00-9:00 y 16:00-18:00) los autobuses llegan cada
    6 minutos. El resto del día la frecuencia es de 12 minutos.
    """
    yield env.timeout(5)  # Los autobuses comienzan a llegar a las 5:00 AM
    for autobuses_id in range(1, max_autobuses + 1):
        hora_actual = env.now % 24
        if 7 <= hora_actual < 9 or 16 <= hora_actual < 18:
            intervalo = 0.1  # 6 minutos
        else:
            intervalo = 0.2  # 12 minutos
        yield env.timeout(intervalo)
        hora_actual = int(env.now % 24)
        soc_inicial = calcular_soc_inicial(hora_actual)
        if VERBOSE:
            print(
                f"Autobús {autobuses_id} llega a la estación en {formato_hora(env.now)} "
                f"(Hora actual: {hora_actual}, SoC inicial: {soc_inicial:.2f}%)"
            )
        env.process(proceso_autobus(env, estacion, autobuses_id, soc_inicial, tiempo_ruta))


# Proceso para simular el flujo del autobús
def proceso_autobus(env, estacion, autobuses_id, soc_inicial, tiempo_ruta):
    """Simula un autobús que intercambia baterías y vuelve tras su ruta."""
    hora_actual = int(env.now % 24)
    while True:
        llegada = env.now
        ultimo_aviso = env.now
        while len(estacion.baterias_reserva.items) <= 0:
            if VERBOSE and env.now - ultimo_aviso >= 10 / 60:
                print(
                    f"Autobús {autobuses_id} espera batería desde {formato_hora(llegada)}"
                )
                ultimo_aviso = env.now
            yield env.timeout(1 / 60)

        with estacion.estaciones.request() as req:
            yield req
            tiempo_espera = env.now - llegada
            estacion.tiempo_espera_total += tiempo_espera
            if VERBOSE:
                print(
                    f"Autobús {autobuses_id} entra a la estación en {formato_hora(env.now)} "
                    f"tras esperar {formato_hora(tiempo_espera)}"
                )
            yield env.process(
                estacion.reemplazar_bateria(autobuses_id, soc_inicial, hora_actual)
            )

        # El autobús sale a su ruta y regresa con la batería descargada
        duracion_ruta = tiempo_ruta * 2 if es_fin_de_semana(env.now) else tiempo_ruta
        hora_inicio_ruta = int(env.now % 24)
        factor = trafico.factor_trafico(hora_inicio_ruta)
        yield env.timeout(duracion_ruta)
        # Consumo de gas equivalente durante la ruta ajustado por el tráfico
        energia_gas = param_operacion.consumo_gas_hora * duracion_ruta * factor
        estacion.energia_total_gas += energia_gas
        estacion.costo_total_gas += energia_gas * param_economicos.costo_gas_kwh
        hora_actual = int(env.now % 24)
        soc_inicial = calcular_soc_inicial(hora_actual)
        if VERBOSE:
            print(
                f"Autobús {autobuses_id} regresa a la estación en {formato_hora(env.now)} "
                f"con SoC {soc_inicial:.2f}%"
            )


# Configuración de la simulación
def ejecutar_simulacion(
    max_autobuses=param_simulacion.max_autobuses,
    duracion=param_simulacion.duracion,
    tiempo_ruta=4,
):
    """Ejecuta la simulación y devuelve la estación resultante.

    ``tiempo_ruta`` indica la duración en horas de la ruta de cada autobús
    antes de volver a solicitar un intercambio de batería.
    """
    random.seed(param_simulacion.semilla)
    env = simpy.Environment()
    estacion = EstacionIntercambio(env, param_estacion.capacidad_estacion)

    env.process(
        llegada_autobuses(
            env,
            estacion,
            max_autobuses=max_autobuses,
            tiempo_ruta=tiempo_ruta,
        )
    )
    env.run(until=duracion)
    return estacion


def formatear_resultados(estacion):
    """Devuelve una lista con los textos de los resultados."""
    dias = param_simulacion.dias
    lines = [
        f"Resultados para {dias:.1f} d\u00edas de operaci\u00f3n",
        f"Consumo total de energ\u00eda en hora punta de autobuses: {estacion.energia_punta_autobuses:.2f} kWh",
        f"Consumo total de energ\u00eda fuera de hora punta de autobuses: {estacion.energia_fuera_punta_autobuses:.2f} kWh",
        f"Consumo total de energ\u00eda en hora punta de electricidad: {estacion.energia_punta_electrica:.2f} kWh",
        f"Tiempo total de espera acumulado: {formato_hora(estacion.tiempo_espera_total)}",
        f"Costo total de operaci\u00f3n (el\u00e9ctrico): S/. {estacion.costo_total_electrico:.2f}",
        f"Costo total de operaci\u00f3n (gas natural): S/. {estacion.costo_total_gas:.2f}",
    ]

    if estacion.costo_total_electrico < estacion.costo_total_gas:
        lines.append("Es m\u00e1s barato operar con electricidad.")
    else:
        lines.append("Es m\u00e1s barato operar con gas natural.")

    emisiones_elec = estacion.energia_total_cargada * param_economicos.factor_co2_elec
    emisiones_gas = estacion.energia_total_gas * param_economicos.factor_co2_gas
    ahorro = emisiones_gas - emisiones_elec
    lines.extend([
        f"Emisiones con electricidad: {emisiones_elec:.2f} kg CO2",
        f"Emisiones con gas natural: {emisiones_gas:.2f} kg CO2",
        f"Ahorro de CO2: {ahorro:.2f} kg",
    ])
    return lines


def imprimir_resultados(estacion):
    """Muestra por pantalla los resultados de la simulación."""
    for line in formatear_resultados(estacion):
        print(line)


if __name__ == "__main__":
    estacion = ejecutar_simulacion()
    imprimir_resultados(estacion)


