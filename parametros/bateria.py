class ParametrosBateria:
    """Parámetros relacionados a la batería y curva de carga."""

    def __init__(self, capacidad=300, soc_objetivo=90):
        self.capacidad = capacidad
        # El SoC objetivo se reduce a 90 % por defecto
        self.soc_objetivo = soc_objetivo

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
        if soc <= 80:
            # Curva suavizada mediante un polinomio cúbico que pasa por los
            # puntos (0,50), (20,150), (55,140) y (80,50)
            a = 5.108225108225208e-04
            b = -0.1344155844155851
            c = 7.483982683982695
            return a * soc ** 3 + b * soc ** 2 + c * soc + 50
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
