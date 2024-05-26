from decimal import Decimal, InvalidOperation
from sistema_bancario.sistema import SistemaBancario

def __interface_saque(*, funcao_saque):
    valor = Decimal(input("Informe o valor do saque: R$ "))
    funcao_saque(valor)
    print(f'R$ {valor:.2f} sacado com sucesso!')

def __interface_deposito(funcao_deposito,/):
    valor = Decimal(input("Informe o valor do depósito: R$ "))
    funcao_deposito(valor)
    print(f'R$ {valor:.2f} depositado com sucesso!')

def __interface_extrato(extrato, /, *, bobina=40):
    print()
    print('EXTRATO'.center(bobina, '-'))
    for transacao in extrato:
        print(f'{transacao["data"].strftime("%c")} {"+" if transacao["valor"].is_signed() else "-"} R${abs(transacao["valor"]):.2f}')
    print(''.center(bobina, '-'))

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
                __interface_deposito(sistema_bancario.deposito)

            case "s":
                __interface_saque(funcao_saque=sistema_bancario.saque)

            case "e":
                __interface_extrato(sistema_bancario.extrato(), bobina=50)

            case "q":
                return False

            case _:
                raise ValueError('Operação inválida!')
    
    except ValueError as erro:
        print(f'Erro: {str(erro)}')
    except InvalidOperation:
        print('Erro: Você inseriu um valor invalido')