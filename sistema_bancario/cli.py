from datetime import datetime
from decimal import Decimal, InvalidOperation
import re
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

def __interface_adiciona_usuario(adicionar_usuario):
    cpf = str(input('Insira o CPF: '))
    nome = str(input('Insira o Nome: '))
    data_nascimento = input('Insira a Data de nascimento (DD/MM/AAAA): ')
    endereco = str(input('Insira o Endereço: '))

    cpf = int(re.sub(r'\D', '', cpf))
    data_nascimento = datetime.strptime(data_nascimento, '%d/%m/%Y').date()

    adicionar_usuario(
        {
            'cpf': cpf,
            'data_nascimento': data_nascimento,
            'endereco': endereco,
            'nome': nome,
        }
    )
    print('Usuário adicionado com sucesso!')

def interface(sistema_bancario: SistemaBancario):

    menu = """

    [d] Depositar
    [s] Sacar
    [e] Extrato
    [au] Adicionar usuario
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

            case "au":
                __interface_adiciona_usuario(sistema_bancario.adicionar_usuario)

            case "q":
                return False

            case _:
                raise ValueError('Operação inválida!')
    
    except ValueError as erro:
        print(f'Erro: {str(erro)}')
    except InvalidOperation:
        print('Erro: Você inseriu um valor invalido')