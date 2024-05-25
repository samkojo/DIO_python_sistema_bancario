from datetime import datetime
from decimal import Decimal, InvalidOperation
from os import environ
from typing import List, TypedDict

class Configuracao(TypedDict):
    saque_qtd_max_dia: int
    saque_valor_max: Decimal

configuracoes: Configuracao = {
    'saque_qtd_max_dia': int(environ.get('saque_qtd_max_dia', 3)),
    'saque_valor_max': Decimal(environ.get('saque_valor_max', 500)),
}

class Transacao(TypedDict):
    data: datetime
    valor: Decimal

class SistemaBancario():
    __extrato: List[Transacao] = []
    __saldo: Decimal = 0
    __qtd_saque_dia: int = 0
    __ultimo_dia_saque: str = None

    def __adiciona_transacao(self, valor: Decimal):
        self.__saldo -= valor
        self.__extrato.append({
            'data': datetime.now(),
            'valor': valor
        })

    def deposito(self, valor: Decimal):
        if valor <= 0:
            raise ValueError('Deposito deve ser maior do que zero!')
        
        self.__adiciona_transacao(valor*-1)

    def __verifica_quantidade_saque(self):
        if datetime.now().isoformat()[:10] != self.__ultimo_dia_saque:
            self.__qtd_saque_dia = 1
            self.__ultimo_dia_saque = datetime.now().isoformat()[:10]
        else:
            self.__qtd_saque_dia += 1
            if self.__qtd_saque_dia > configuracoes['saque_qtd_max_dia']:
                raise ValueError(f'Você ja atingiu limite de {configuracoes["saque_qtd_max_dia"]} saques no dia!')

    def saque(self, valor: Decimal):
        if valor < 0:
            raise ValueError('Você só pode sacar valores positivos!')
        if valor > configuracoes['saque_valor_max']:
            raise ValueError(f'Valor maximo de saque R$ {configuracoes["saque_valor_max"]}')
        if valor > self.__saldo:
            raise ValueError('Você não tem saldo disponivel para saque!')
        
        self.__verifica_quantidade_saque()
        self.__adiciona_transacao(valor)

    def extrato(self):
        return self.__extrato.copy()
        

print('Iniciando sistema bancario')
sistema_bancario = SistemaBancario()

menu = """

[d] Depositar
[s] Sacar
[e] Extrato
[q] Sair

=> """

while True:

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
                break

            case _:
                raise ValueError('Operação inválida!')
    
    except ValueError as erro:
        print(f'Erro: {str(erro)}')
    except InvalidOperation:
        print('Erro: Você inseriu um valor invalido')