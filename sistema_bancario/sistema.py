from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, TypedDict
from sistema_bancario.configuracao import configuracoes


class Cliente:
    def __init__(self, endereco: str):
        self._endereco = endereco
        self._contas: List[Conta] = []

    def realizar_transacao(self, conta: Conta, transacao: Transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta: Conta):
        self._contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, cpf, nome, data_nascimento, endereco):
        super().__init__(endereco)
        self._cpf = cpf
        self._nome = nome
        self._data_nascimento = data_nascimento

class Extrato(TypedDict):
    data: datetime
    valor: Decimal

class Historico:
    def __init__(self) -> None:
        self._extrato: List[Extrato] = []

    @property
    def extrato(self):
        return self._extrato.copy()

    def adicionar_transacao(self, transacao: Transacao):
        extrato: Extrato = {
            'data': datetime.now(),
            'valor': transacao.valor,
        }
        self._extrato.append(extrato)

class Conta:
    def __init__(self, numero: int, cliente: Cliente):
        self._saldo = Decimal(0)
        self._numero = numero
        self._agencia = '0001'
        self._cliente = cliente
        self._historico = Historico()

    @property
    def saldo(self) -> Decimal:
        return self._saldo
    
    @property
    def historico(self) -> Historico:
        return self._historico
    
    @classmethod
    def nova_conta(cls, cliente: Cliente, numero: int) -> Conta:
        return cls(numero, cliente)

    def sacar(self, valor: Decimal) -> bool:
        if valor > self._saldo:
            raise ValueError('Você não tem saldo disponivel para saque!')
        
        self._saldo -= valor
        return True

    def depositar(self, valor: Decimal) -> bool:
        self._saldo += valor
        return True

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, saque_limite_valor=configuracoes['saque_limite_valor'], saque_limite_qtd_dia=configuracoes['saque_limite_qtd_dia']):
        super().__init__(numero, cliente)
        self._saque_limite_valor = saque_limite_valor
        self._saque_limite_qtd_dia = saque_limite_qtd_dia

    def sacar(self, valor: Decimal) -> bool:
        if valor > self._saque_limite_valor:
            raise ValueError(f'Valor maximo de saque R$ {self._saque_limite_valor}')

        qtd_saques_dia = [transacao for transacao in self.historico.extrato 
         if not transacao['valor'].is_signed()
         and transacao['data'] == datetime.now()].count()
        
        if qtd_saques_dia > self._saque_limite_qtd_dia:
            raise ValueError(f'Você ja atingiu limite de {self._saque_limite_qtd_dia} saques no dia!')
        
        return super().sacar(valor)
          

class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @classmethod
    @abstractmethod
    def registrar(self, conta: Conta):
        pass

class Deposito(Transacao):
    def __init__(self, valor: Decimal):
        if valor < 0:
            raise ValueError('Valor do deposito deve ser maior do que zero!')
        self._valor = valor

    def registrar(self, conta: Conta):
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao(self)

class Saque(Transacao):
    def __init__(self, valor: Decimal):
        if valor < 0:
            raise ValueError('Valor do saque deve ser maior do que zero!')
        self._valor = valor

    def registrar(self, conta: Conta):
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao(self)


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

class Conta(TypedDict):
    cpf: int
    agencia: str
    conta: int

class SistemaBancario():
    def __init__(self) -> None:
        self.__usuarios = {}
        self.__contas: List[Conta] = []
        self.__extrato: List[Transacao] = []
        self.__saldo: Decimal = 0
        self.__qtd_saque_dia: int = 0
        self.__ultimo_dia_saque: str = None

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
            raise ValueError('Já existe um usuário com mesmo cpf!')

    def adicionar_conta(self, cpf: int) -> Conta:
        if not self.__usuarios.get(cpf, None):
            raise ValueError('Você não cadastrou esse usuário ainda!')

        numero_conta = 1
        if len(self.__contas):
            numero_conta += self.__contas[-1]['conta']

        conta: Conta = {
                'agencia': '0001',
                'conta': numero_conta,
                'cpf': cpf,
        }
        self.__contas.append(
            conta
        )

        return conta