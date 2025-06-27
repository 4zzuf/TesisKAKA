class ParametrosOperacionBus:
    """Parámetros de operación del autobús."""

    def __init__(self, costo_operacion_hora=50, penalizacion_espera=10,
                 consumo_gas_hora=100):
        self.costo_operacion_hora = costo_operacion_hora
        self.penalizacion_espera = penalizacion_espera
        # Energía equivalente que consumiría un autobús a gas por hora
        self.consumo_gas_hora = consumo_gas_hora

    def actualizar(self, costo=None, penalizacion=None, consumo_gas=None):
        """Permite modificar los parámetros de operación."""
        if costo is not None:
            self.costo_operacion_hora = costo
        if penalizacion is not None:
            self.penalizacion_espera = penalizacion
        if consumo_gas is not None:
            self.consumo_gas_hora = consumo_gas
