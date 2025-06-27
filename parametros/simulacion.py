class ParametrosSimulacion:
    """Parámetros generales de la simulación."""

    def __init__(self, dias=21, max_autobuses=20, semilla=42):
        # La duración se ingresa en días y se convierte a horas cuando es
        # necesario ejecutar la simulación.
        self.dias = dias
        self.max_autobuses = max_autobuses
        self.semilla = semilla

    @property
    def duracion(self):
        """Duración de la simulación en horas."""
        return self.dias * 24

    def actualizar(self, dias=None, max_autobuses=None, semilla=None):
        """Permite actualizar los parámetros de simulación."""
        if dias is not None:
            self.dias = dias
        if max_autobuses is not None:
            self.max_autobuses = max_autobuses
        if semilla is not None:
            self.semilla = semilla
