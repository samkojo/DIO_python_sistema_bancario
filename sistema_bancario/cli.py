from decimal import Decimal, InvalidOperation
from sistema_bancario.sistema import SistemaBancario

def interface(sistema_bancario: SistemaBancario):
    menu = """

    [d] Depositar
    [s] Sacar
    [e] Extrato
    [q] Sair

    => """
    opcao = input(menu)

    try:
        match opcao:
            case "d":
                valor = Decimal(input("Informe o valor do depósito: R$ "))
                sistema_bancario.deposito(valor)
                print(f'R$ {valor:.2f} depositado com sucesso!')

            case "s":
                valor = Decimal(input("Informe o valor do saque: R$ "))
                sistema_bancario.saque(valor)
                print(f'R$ {valor:.2f} sacado com sucesso!')

            case "e":
                print()
                print('EXTRATO'.center(40, '-'))
                for transacao in sistema_bancario.extrato():
                    print(f'{transacao["data"].strftime("%c")} {"+" if transacao["valor"].is_signed() else "-"} R${abs(transacao["valor"]):.2f}')
                print(''.center(40, '-'))

            case "q":
                return False

            case _:
                raise ValueError('Operação inválida!')
    
    except ValueError as erro:
        print(f'Erro: {str(erro)}')
    except InvalidOperation:
        print('Erro: Você inseriu um valor invalido')