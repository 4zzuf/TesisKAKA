import matplotlib.pyplot as plt
from parametros import ParametrosBateria


def main():
    """Grafica la curva de potencia de carga según el SoC."""
    bateria = ParametrosBateria()
    soc_vals = list(range(0, 91))
    potencias = [bateria.potencia_carga(s) for s in soc_vals]

    plt.figure(figsize=(8, 4))
    plt.plot(soc_vals, potencias, marker='o')
    plt.xlabel('Estado de carga (%)')
    plt.ylabel('Potencia de carga (kW)')
    plt.title('Curva de carga de la batería')
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()
