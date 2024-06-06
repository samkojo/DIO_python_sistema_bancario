from datetime import datetime
from decimal import Decimal, InvalidOperation
import re
from typing import Generator, Iterator, List
from sistema_bancario.sistema import Cliente, Conta, ContaIterador, PessoaFisica, SistemaBancario

def _interface_saque(*, funcao_saque, conta: Conta):
    valor = Decimal(input("Informe o valor do saque: R$ "))
    funcao_saque(valor, conta)
    print(f'R$ {valor:.2f} sacado com sucesso!')

def _interface_deposito(funcao_deposito, conta: Conta, /):
    valor = Decimal(input("Informe o valor do depósito: R$ "))
    funcao_deposito(valor, conta)
    print(f'R$ {valor:.2f} depositado com sucesso!')

def _interface_extrato(extrato: Generator, /, *, bobina=40):
    print()
    print('EXTRATO'.center(bobina, '-'))
    [ print(linha_extrato) for linha_extrato in extrato ]
    print(''.center(bobina, '-'))

def _interface_adicionar_cliente(adicionar_cliente):
    cpf = str(input('Insira o CPF: '))
    nome = str(input('Insira o Nome: '))
    data_nascimento = input('Insira a Data de nascimento (DD/MM/AAAA): ')
    endereco = str(input('Insira o Endereço: '))

    cpf = int(re.sub(r'\D', '', cpf))
    data_nascimento = datetime.strptime(data_nascimento, '%d/%m/%Y').date()

    cliente = PessoaFisica(
        cpf=cpf,
        data_nascimento=data_nascimento,
        endereco=endereco,
        nome=nome
    )
    adicionar_cliente(
        cliente
    )
    print('Cliente (Pessoa Fisica) adicionado com sucesso!')

def _interface_escolha_cliente(clientes: List[Cliente]):
    print()

    if len(clientes) == 0:
        raise ValueError('Você ainda não cadastrou clientes')

    if len(clientes) == 1:
        print(f'Selecionado cliente: {clientes[0]}')
        return clientes[0]

    for indice, cliente in enumerate(clientes):
        print(f"{indice+1}. {cliente}")
    
    escolha_cliente = int(input('Escolha um dos clientes acima (digite o numero correspondente): '))
    escolha_cliente -= 1

    if escolha_cliente < 0 or escolha_cliente > len(clientes):
        raise ValueError('Cliente inexistente')
    
    return clientes[escolha_cliente]

def _interface_escolha_conta_cliente(contas: List[Conta]):
    print()

    if len(contas) == 0:
        raise ValueError('Você ainda não cadastrou contas')

    if len(contas) == 1:
        print(f'Selecionado conta: {contas[0]}')
        return contas[0]
    
    for indice, conta in enumerate(contas):
        print(f"{indice+1}. {conta}")
    
    escolha_cliente = int(input('Escolha uma das contas acima (digite o numero correspondente): '))
    escolha_cliente -= 1

    if escolha_cliente < 0 or escolha_cliente > len(contas):
        raise ValueError('Conta inexistente')
    
    return contas[escolha_cliente]

def _interface_adicionar_conta(adicionar_conta, cliente: Cliente):

    conta: Conta = adicionar_conta(cliente)
    print(f'Conta {conta.numero} cadastrada com sucesso!')

def _interface_filtrar_transacao():
    opcao_filtro = ['Todos','Deposito','Saque']

    for indice, opcao in enumerate(opcao_filtro):
        print(f"{indice}. {opcao}")
    
    escolha_filtro = int(input('Escolha uma das opções acima (digite o numero correspondente): '))

    if escolha_filtro < 0 or escolha_filtro >= len(opcao_filtro):
        raise ValueError('Opção inexistente')
    
    return opcao_filtro[escolha_filtro]

def _interface_listar_contas(contas: Iterator):
    print()
    print('Listando todas as contas'.center(50, '-'))
    [ print(conta) for conta in contas ]
    print(''.center(50, '-'))

def interface(sistema_bancario: SistemaBancario):

    menu = """

    [au] Adicionar usuario
    [ac] Adicionar conta
    [d] Depositar
    [s] Sacar
    [e] Extrato
    [lc] Listar contas
    [q] Sair

    => """
    opcao = input(menu)

    try:
        match opcao:
            case "au":
                _interface_adicionar_cliente(sistema_bancario.adicionar_cliente)

            case "ac":
                cliente = _interface_escolha_cliente(sistema_bancario.clientes)
                _interface_adicionar_conta(sistema_bancario.adicionar_conta, cliente)

            case "d":
                cliente = _interface_escolha_cliente(sistema_bancario.clientes)
                conta = _interface_escolha_conta_cliente(cliente.contas)
                _interface_deposito(sistema_bancario.deposito, conta)

            case "s":
                cliente = _interface_escolha_cliente(sistema_bancario.clientes)
                conta = _interface_escolha_conta_cliente(cliente.contas)
                _interface_saque(funcao_saque=sistema_bancario.saque, conta=conta)

            case "e":
                cliente = _interface_escolha_cliente(sistema_bancario.clientes)
                conta = _interface_escolha_conta_cliente(cliente.contas)
                opcao_filtro = _interface_filtrar_transacao()
                _interface_extrato(sistema_bancario.extrato(conta, opcao_filtro), bobina=50)

            case "lc":
                _interface_listar_contas(ContaIterador(sistema_bancario.clientes))

            case "q":
                return False

            case _:
                raise ValueError('Operação inválida!')
    
    except ValueError as erro:
        print(f'Erro: {str(erro)}')
    except InvalidOperation:
        print('Erro: Você inseriu um valor invalido')