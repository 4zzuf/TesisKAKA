import sys

from PyQt5 import QtWidgets, QtCore
import modelo


class SimulacionWorker(QtCore.QObject):
    """Ejecuta la simulación en un hilo separado."""

    finished = QtCore.pyqtSignal(list)

    def __init__(self, max_autobuses, duracion, tiempo_ruta):
        super().__init__()
        self._max_autobuses = max_autobuses
        self._duracion = duracion
        self._tiempo_ruta = tiempo_ruta

    @QtCore.pyqtSlot()
    def run(self):
        estacion = modelo.ejecutar_simulacion(
            max_autobuses=self._max_autobuses,
            duracion=self._duracion,
            tiempo_ruta=self._tiempo_ruta,
        )

        r = []
        dias = modelo.param_simulacion.dias
        r.append(f"Resultados para {dias:.1f} d\u00edas de operaci\u00f3n")
        r.append(
            f"Consumo total de energ\u00eda en hora punta de autobuses: {estacion.energia_punta_autobuses:.2f} kWh"
        )
        r.append(
            f"Consumo total de energ\u00eda fuera de hora punta de autobuses: {estacion.energia_fuera_punta_autobuses:.2f} kWh"
        )
        r.append(
            f"Consumo total de energ\u00eda en hora punta de electricidad: {estacion.energia_punta_electrica:.2f} kWh"
        )
        r.append(
            f"Tiempo total de espera acumulado: {modelo.formato_hora(estacion.tiempo_espera_total)}"
        )
        r.append(
            f"Costo total de operaci\u00f3n (el\u00e9ctrico): S/. {estacion.costo_total_electrico:.2f}"
        )
        r.append(
            f"Costo total de operaci\u00f3n (gas natural): S/. {estacion.costo_total_gas:.2f}"
        )

        if estacion.costo_total_electrico < estacion.costo_total_gas:
            r.append("Es m\u00e1s barato operar con electricidad.")
        else:
            r.append("Es m\u00e1s barato operar con gas natural.")

        emis_elec = estacion.energia_total_cargada * modelo.param_economicos.factor_co2_elec
        emis_gas = estacion.energia_total_gas * modelo.param_economicos.factor_co2_gas
        ahorro = emis_gas - emis_elec
        r.append(f"Emisiones con electricidad: {emis_elec:.2f} kg CO2")
        r.append(f"Emisiones con gas natural: {emis_gas:.2f} kg CO2")
        r.append(f"Ahorro de CO2: {ahorro:.2f} kg")

        self.finished.emit(r)


class SimulacionWindow(QtWidgets.QWidget):
    """Interfaz principal para ejecutar la simulaci\u00f3n."""

    def __init__(self):
        super().__init__()
        self._thread = None
        self._worker = None
        self._init_ui()

    def _init_ui(self):
        layout = QtWidgets.QFormLayout()

        self.dias = QtWidgets.QSpinBox()
        self.dias.setRange(1, 365)
        self.dias.setValue(modelo.param_simulacion.dias)
        layout.addRow("Duraci\u00f3n (d\u00edas)", self.dias)

        self.autobuses = QtWidgets.QSpinBox()
        self.autobuses.setRange(1, 200)
        self.autobuses.setValue(modelo.param_simulacion.max_autobuses)
        layout.addRow("Max autobuses", self.autobuses)

        self.semilla = QtWidgets.QSpinBox()
        self.semilla.setRange(0, 9999)
        self.semilla.setValue(modelo.param_simulacion.semilla)
        layout.addRow("Semilla", self.semilla)

        self.capacidad = QtWidgets.QSpinBox()
        self.capacidad.setRange(1, 200)
        self.capacidad.setValue(modelo.param_estacion.capacidad_estacion)
        layout.addRow("Capacidad estaci\u00f3n", self.capacidad)

        self.total_baterias = QtWidgets.QSpinBox()
        self.total_baterias.setRange(1, 500)
        self.total_baterias.setValue(modelo.param_estacion.total_baterias)
        layout.addRow("Total bater\u00edas", self.total_baterias)

        self.baterias_iniciales = QtWidgets.QSpinBox()
        self.baterias_iniciales.setRange(0, 500)
        self.baterias_iniciales.setValue(modelo.param_estacion.baterias_iniciales)
        layout.addRow("Bater\u00edas iniciales", self.baterias_iniciales)

        self.tiempo_ruta = QtWidgets.QDoubleSpinBox()
        self.tiempo_ruta.setRange(0.1, 24.0)
        self.tiempo_ruta.setSingleStep(0.5)
        self.tiempo_ruta.setValue(4.0)
        layout.addRow("Tiempo ruta (h)", self.tiempo_ruta)

        self.resultados = QtWidgets.QTextEdit()
        self.resultados.setReadOnly(True)

        self.boton = QtWidgets.QPushButton("Ejecutar simulaci\u00f3n")
        self.boton.clicked.connect(self.run_simulation)

        layout.addRow(self.boton)
        layout.addRow(self.resultados)

        self.setLayout(layout)
        self.setWindowTitle("Simulaci\u00f3n de intercambio de bater\u00edas")

    def run_simulation(self):
        modelo.param_simulacion.actualizar(
            dias=self.dias.value(),
            max_autobuses=self.autobuses.value(),
            semilla=self.semilla.value(),
        )
        modelo.param_estacion.actualizar(
            capacidad=self.capacidad.value(),
            total=self.total_baterias.value(),
            iniciales=self.baterias_iniciales.value(),
        )

        self.boton.setEnabled(False)
        self.resultados.clear()

        self._thread = QtCore.QThread()
        self._worker = SimulacionWorker(
            modelo.param_simulacion.max_autobuses,
            modelo.param_simulacion.duracion,
            self.tiempo_ruta.value(),
        )
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_simulation_finished)
        self._worker.finished.connect(self._thread.quit)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()

    def _on_simulation_finished(self, lines):
        self.resultados.setPlainText("\n".join(lines))
        self.boton.setEnabled(True)
        self._worker.deleteLater()
        self._worker = None
        self._thread = None


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = SimulacionWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":  # pragma: no cover - ejecuci\u00f3n manual
    main()
