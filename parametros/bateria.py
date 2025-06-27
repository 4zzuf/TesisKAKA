class ParametrosBateria:
    """Parámetros relacionados a la batería y curva de carga."""

    def __init__(self, capacidad=300, soc_objetivo=90):
        self.capacidad = capacidad
        # El SoC objetivo se reduce a 90 % por defecto
        self.soc_objetivo = soc_objetivo
        # Coordenadas (SoC, potencia) que definen la curva de carga. Se
        # interpolan linealmente para obtener la potencia en valores
        # intermedios.  Estos puntos siguen el comportamiento solicitado:
        # - 0 a 20 %  : 50 kW → 150 kW
        # - 20 a 55 % : 150 kW → 140 kW
        # - 55 a 80 % : 140 kW → 50 kW
        self.puntos_curva = [
            (0, 50),
            (20, 150),
            (55, 140),
            (80, 50),
        ]

    def actualizar(self, potencia=None, capacidad=None, soc_objetivo=None):
        """Actualiza los valores de la batería según se necesite."""
        if potencia is not None:
            # Mantenido por compatibilidad: no se utiliza directamente
            pass
        if capacidad is not None:
            self.capacidad = capacidad
        if soc_objetivo is not None:
            self.soc_objetivo = soc_objetivo

    def potencia_carga(self, soc):
        """Devuelve la potencia de carga en kW para el SoC dado."""

        soc = max(0, min(soc, 100))
        if soc < 20:
            # De 50 a 150 kW
            return 50 + (soc / 20) * 100
        if soc < 55:
            # De 150 a 140 kW
            return 150 - (soc - 20) * (10 / 35)
        if soc < 80:
            # De 140 a 50 kW
            return 140 - (soc - 55) * (90 / 25)
        return 50

    def tiempo_carga(self, soc_inicial, soc_objetivo=None):
        """Tiempo necesario para cargar desde ``soc_inicial`` hasta el objetivo."""
        objetivo = self.soc_objetivo if soc_objetivo is None else soc_objetivo
        objetivo = min(objetivo, 100)
        soc = max(0, soc_inicial)
        energia_por_pct = self.capacidad / 100
        tiempo = 0.0
        while soc < objetivo:
            sig = min(soc + 1, objetivo)
            potencia = self.potencia_carga(soc)
            energia = (sig - soc) * energia_por_pct
            tiempo += energia / potencia
            soc = sig
        return tiempo
