import matplotlib.pyplot as plt
import modelo
from modelo import param_simulacion


def main():
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
    plt.plot(range(dias + 1), intercambios, marker='o')
    plt.xlabel('Día de operación')
    plt.ylabel('Intercambios de batería')
    plt.title('Intercambios diarios')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(8, 4))
    plt.plot(range(dias + 1), energia, marker='s', color='tab:orange')
    plt.xlabel('Día de operación')
    plt.ylabel('Energía cargada (kWh)')
    plt.title('Consumo diario de energía')
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()
