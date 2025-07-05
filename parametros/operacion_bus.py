class ParametrosOperacionBus:
    """Parámetros de operación del autobús."""

    def __init__(
        self,
        costo_operacion_hora=50,
        penalizacion_espera=10,
        consumo_gas_hora=100,
        velocidad_promedio=30,
        consumo_kwh_km=(0.9, 1.2),
    ):
        self.costo_operacion_hora = costo_operacion_hora
        self.penalizacion_espera = penalizacion_espera
        # Energía equivalente que consumiría un autobús a gas por hora
        self.consumo_gas_hora = consumo_gas_hora
        # Velocidad promedio del autobús en km/h
        self.velocidad_promedio = velocidad_promedio
        # Rango de consumo eléctrico por kilómetro recorrido
        self.consumo_kwh_km = consumo_kwh_km

    def actualizar(
        self,
        costo=None,
        penalizacion=None,
        consumo_gas=None,
        velocidad=None,
        consumo_km=None,
    ):
        """Permite modificar los parámetros de operación."""
        if costo is not None:
            self.costo_operacion_hora = costo
        if penalizacion is not None:
            self.penalizacion_espera = penalizacion
        if consumo_gas is not None:
            self.consumo_gas_hora = consumo_gas
        if velocidad is not None:
            self.velocidad_promedio = velocidad
        if consumo_km is not None:
            self.consumo_kwh_km = consumo_km
