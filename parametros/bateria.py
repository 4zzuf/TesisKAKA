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
        soc = max(0.0, min(float(soc), 100.0))
        puntos = self.puntos_curva
        for i in range(len(puntos) - 1):
            x0, y0 = puntos[i]
            x1, y1 = puntos[i + 1]
            if soc <= x1:
                # Interpolación lineal entre los puntos
                return y0 + (y1 - y0) * (soc - x0) / (x1 - x0)
        return puntos[-1][1]

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
