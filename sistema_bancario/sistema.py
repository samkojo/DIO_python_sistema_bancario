from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Literal, TypedDict
from sistema_bancario.configuracao import configuracoes
from sistema_bancario.utils import log_operacoes


class Cliente:
    def __init__(self, endereco: str):
        self._endereco = endereco
        self._contas: List[Conta] = []
    
    @property
    @abstractmethod
    def id(self):
        pass

    @property
    def contas(self):
        return self._contas.copy()
    
    @property
    @abstractmethod
    def nome(self):
        pass

    def realizar_transacao(self, conta, transacao):
        if len(conta.historico.transacoes_do_dia()) >= configuracoes['transascao_qtd_dia']:
            raise ValueError('Você relealizou o limite máximo de transações por dia')
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self._contas.append(conta)

    def __str__(self) -> str:
        return f'ID: {self.id} - Nome: {self.nome}'

class PessoaFisica(Cliente):
    def __init__(self, cpf: str, nome: str, data_nascimento: datetime.date, endereco: str):
        super().__init__(endereco)
        self._cpf = cpf
        self._nome = nome
        self._data_nascimento = data_nascimento
    
    @property
    def id(self):
        return self._cpf
    
    @property
    def nome(self):
        return self._nome
    
    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: ({self.id})>'

    def __str__(self) -> str:
        return f'CPF: {self.id} - Nome: {self.nome}'

class Extrato(TypedDict):
    data: datetime
    valor: Decimal

class Historico:
    def __init__(self) -> None:
        self._extrato: List[Extrato] = []

    @property
    def extrato(self):
        return self._extrato.copy()

    def adicionar_transacao(self, transacao):
        extrato: Extrato = {
            'data': datetime.now(),
            'valor': transacao.valor_transacao,
        }
        self._extrato.append(extrato)

    def transacoes_do_dia(self) -> List[Extrato]:
        return [transacao for transacao in self.extrato
                if transacao['data'].date() == datetime.now().date()]

class Conta:
    def __init__(self, numero: int, cliente: Cliente):
        self._saldo = Decimal(0)
        self._numero = numero
        self._agencia = '0001'
        self._cliente = cliente
        self._historico = Historico()

    @property
    def numero(self) -> int:
        return self._numero
    
    @property
    def agencia(self) -> str:
        return self._agencia
    
    @property
    def cliente(self) -> Cliente:
        return self._cliente
    
    @property
    def saldo(self) -> Decimal:
        return self._saldo
    
    @property
    def historico(self) -> Historico:
        return self._historico
    
    @classmethod
    def nova_conta(cls, cliente: Cliente, numero: int):
        return cls(numero, cliente)

    def sacar(self, valor: Decimal) -> bool:
        if valor > self._saldo:
            raise ValueError('Você não tem saldo disponivel para saque!')
        
        self._saldo -= valor
        return True

    def depositar(self, valor: Decimal) -> bool:
        self._saldo += valor
        return True
    
    def __str__(self):
        return f'Conta {self.numero}'

class ContaCorrente(Conta):
    saque_limite_valor: Decimal
    saque_limite_qtd_dia: int

    def sacar(self, valor: Decimal) -> bool:
        if valor > self.saque_limite_valor:
            raise ValueError(f'Valor maximo de saque R$ {self.saque_limite_valor}')

        qtd_saques_dia = len(
            [transacao for transacao in self.historico.extrato 
            if transacao['valor'].is_signed()
            and transacao['data'].date() == datetime.now().date()]
        )
        
        if qtd_saques_dia >= self.saque_limite_qtd_dia:
            raise ValueError(f'Você ja atingiu limite de {self.saque_limite_qtd_dia} saques no dia!')
        
        return super().sacar(valor)
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: ('{self.agencia}', '{self.numero}', '{self.cliente.nome}')>"
          

class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @property
    @abstractmethod
    def valor_transacao(self):
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

    @property
    def valor(self):
        return self._valor

    @property
    def valor_transacao(self):
        return self._valor
    
    def registrar(self, conta: Conta):
        if conta.depositar(self.valor):
            conta.historico.adicionar_transacao(self)

class Saque(Transacao):
    def __init__(self, valor: Decimal):
        if valor < 0:
            raise ValueError('Valor do saque deve ser maior do que zero!')
        self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    @property
    def valor_transacao(self):
        return self._valor * -1
    
    def registrar(self, conta: Conta):
        if conta.sacar(self.valor):
            conta.historico.adicionar_transacao(self)


class ContaIterador:
    def __init__(self, clientes: List[Cliente]) -> None:
        self.clientes = clientes
        self.contador_cliente = 0
        self.contador_conta = 0

    def __iter__(self):
        return self
    
    def __next__(self):
        try:
            
            cliente = self.clientes[self.contador_cliente]
            try:
                conta = cliente.contas[self.contador_conta]
                self.contador_conta += 1
                return f'Conta: {conta.numero} - Saldo: {conta.saldo}'
            except IndexError:
                self.contador_cliente += 1
                self.contador_conta = 0
                return self.__next__()
                
        except IndexError:
            raise StopIteration
        
class SistemaBancario():
    versao = '0.6'

    def __init__(self) -> None:
        ContaCorrente.saque_limite_qtd_dia = configuracoes['saque_limite_qtd_dia']
        ContaCorrente.saque_limite_valor = configuracoes['saque_limite_valor']

        self._clientes: Dict[str, Cliente] = {}
        self._ultimo_numero_conta = 1
    
    @property
    def clientes(self):
        return list(self._clientes.values())
    
    @log_operacoes
    def adicionar_cliente(self, cliente: Cliente):
        resultado = self._clientes.setdefault(cliente.id, cliente)

        if (cliente != resultado):
            raise ValueError('Já existe um cliente com mesmo cpf!')
        
        return cliente
    
    @log_operacoes
    def adicionar_conta(self, cliente: Cliente) -> Conta:
        if not self._clientes.get(cliente.id, None):
            raise ValueError('Você não cadastrou esse cliente ainda!')

        conta = ContaCorrente.nova_conta(cliente, self._ultimo_numero_conta)
        cliente.adicionar_conta(conta)

        self._ultimo_numero_conta += 1
        return conta

    @log_operacoes
    def deposito(self, valor: Decimal, cliente: Cliente, conta: Conta):
        transacao = Deposito(valor)
        cliente.realizar_transacao(conta, transacao)

    @log_operacoes
    def saque(self, valor: Decimal, cliente: Cliente, conta: Conta):
        transacao = Saque(valor)
        cliente.realizar_transacao(conta, transacao)

    @log_operacoes
    def extrato(self, conta: Conta, filtrar_operacao: Literal['Deposito','Saque']):
        for transacao in conta.historico.extrato:
            if (filtrar_operacao == 'Deposito' and transacao["valor"].is_signed()) or \
               (filtrar_operacao == 'Saque' and not transacao["valor"].is_signed()):
                continue
            
            yield f'{transacao["data"].strftime("%c")} {"-" if transacao["valor"].is_signed() else "+"} R${abs(transacao["valor"]):.2f}'
        
    def __repr__(self) -> str:
        return f'SistemaBancario v{self.versao}'