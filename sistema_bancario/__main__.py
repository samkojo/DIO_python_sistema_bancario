from sistema_bancario.sistema import SistemaBancario
from sistema_bancario.cli import interface

if __name__ == '__main__':
    sistema_bancario = SistemaBancario()

    while interface(sistema_bancario) is not False:
        pass