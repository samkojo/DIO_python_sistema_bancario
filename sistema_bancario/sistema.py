from datetime import datetime
from decimal import Decimal
from typing import Dict, List, TypedDict
from sistema_bancario.configuracao import configuracoes

class Transacao(TypedDict):
    data: datetime
    agencia: str
    conta: int
    valor: Decimal

class Usuario(TypedDict):
    cpf: int
    nome: str
    data_nascimento: datetime.date
    endereco: str

class SistemaBancario():
    __usuarios = {}
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
        
    def adicionar_usuario(self, usuario: Usuario):
        resultado = self.__usuarios.setdefault(usuario['cpf'], usuario)

        if (usuario != resultado):
            raise ValueError('Já existe um usuário com mesmo cpf')
