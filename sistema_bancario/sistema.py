from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Literal, Tuple, TypedDict
from sistema_bancario.configuracao import configuracoes
from sistema_bancario.utils import ClientesCsv, ContasCsv, TransacaoCsv, inicializa_clientes_csv, inicializa_contas_csv, inicializa_transacoes_csv, log_operacoes, persiste_cliente_csv, persiste_conta_csv, persiste_transacao_csv


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
        return transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self._contas.append(conta)
        return conta

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
    
    @property
    def data_nascimento(self):
        return self._data_nascimento
    
    @property
    def endereco(self):
        return self._endereco
    
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

    def adicionar_transacao(self, valor_transacao: Decimal, datahora: datetime = datetime.now()) -> Extrato:
        extrato: Extrato = {
            'data': datahora,
            'valor': valor_transacao,
        }
        self._extrato.append(extrato)
        return extrato

    def transacoes_do_dia(self) -> List[Extrato]:
        return [transacao for transacao in self.extrato
                if transacao['data'].date() == datetime.now().date()]

class Conta:
    def __init__(self, numero: int, cliente: Cliente, saldo: Decimal = Decimal(0)):
        self._saldo = saldo
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
    
    def registrar(self, conta: Conta) -> Extrato:
        if conta.depositar(self.valor):
            return conta.historico.adicionar_transacao(self.valor_transacao)

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
    
    def registrar(self, conta: Conta) -> Extrato:
        if conta.sacar(self.valor):
            return conta.historico.adicionar_transacao(self.valor_transacao)


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


def carrega_clientes(
        clientes: List[ClientesCsv], 
        contas: List[ContasCsv], 
        transacoes: List[TransacaoCsv],
    ) -> Tuple[Dict[str, Cliente], int]:

    print('Carregando clientes, suas contas e transacoes')
    dict_clientes: Dict[str, Cliente] = {}
    for cliente in clientes:
        pessoa = PessoaFisica(
            cpf=cliente['cpf'],
            nome=cliente['nome'],
            data_nascimento=datetime.strptime(cliente['data_nascimento'], '%Y-%m-%d').date(),
            endereco=cliente['endereco'],
        )

        for conta in contas:
            if conta['id_cliente'] != pessoa.id:
                continue

            saldo = sum([
                transacao['valor'] for transacao in transacoes
                if (transacao['cliente_id'] == pessoa.id
                and transacao['conta_agencia'] == conta['agencia']
                and transacao['conta_numero'] == conta['numero'])
            ])
            conta = pessoa.adicionar_conta(ContaCorrente(
                conta['numero'], 
                pessoa, 
                saldo,
            ))

            for transacao in transacoes:
                if (transacao['cliente_id'] != conta.cliente.id
                or transacao['conta_agencia'] != conta.agencia
                or transacao['conta_numero'] != conta.numero):
                    continue
                conta.historico.adicionar_transacao(
                    datahora=datetime.strptime(transacao['datahora'], '%Y-%m-%d %H:%M:%S'),
                    valor_transacao=transacao['valor'],
                )

        dict_clientes.setdefault(cliente['cpf'],pessoa)
    if len(dict_clientes):
        print(f'Carregado(s) {len(dict_clientes)} clientes')

    ultimo_numero_conta = max([conta['numero'] for conta in contas])+1 if len(contas) else 1
    print(ultimo_numero_conta)
    return (dict_clientes, ultimo_numero_conta)

def persiste_cliente(cliente: PessoaFisica):
    persiste_cliente_csv({
        'cpf': cliente.id,
        'nome': cliente.nome,
        'data_nascimento': cliente.data_nascimento.strftime('%Y-%m-%d'),
        'endereco': cliente.endereco,
    })

def persiste_conta(conta: ContaCorrente):
    persiste_conta_csv({
        'id_cliente': conta.cliente.id,
        'agencia': conta.agencia,
        'numero': conta.numero,
    })

def persiste_transacao(conta: Conta, extrato: Extrato):
    persiste_transacao_csv({
        'cliente_id': conta.cliente.id,
        'conta_agencia': conta.agencia,
        'conta_numero': conta.numero,
        'datahora': extrato['data'].strftime('%Y-%m-%d %H:%M:%S'),
        'valor': extrato['valor']
    })

class SistemaBancario():
    VERSAO = '0.6'

    def __init__(self) -> None:
        print(f'Iniciando Sistema Bancario v{self.VERSAO}')
        ContaCorrente.saque_limite_qtd_dia = configuracoes['saque_limite_qtd_dia']
        ContaCorrente.saque_limite_valor = configuracoes['saque_limite_valor']

        self._clientes, self._ultimo_numero_conta = carrega_clientes(
            inicializa_clientes_csv(),
            inicializa_contas_csv(),
            inicializa_transacoes_csv(),
        )
    
    @property
    def clientes(self):
        return list(self._clientes.values())
    
    @log_operacoes
    def adicionar_cliente(self, cliente: Cliente):
        resultado = self._clientes.setdefault(cliente.id, cliente)

        if (cliente != resultado):
            raise ValueError('Já existe um cliente com mesmo cpf!')

        persiste_cliente(resultado)        
        return resultado
    
    @log_operacoes
    def adicionar_conta(self, cliente: Cliente) -> Conta:
        if not self._clientes.get(cliente.id, None):
            raise ValueError('Você não cadastrou esse cliente ainda!')

        conta = ContaCorrente.nova_conta(cliente, self._ultimo_numero_conta)
        cliente.adicionar_conta(conta)

        self._ultimo_numero_conta += 1
        persiste_conta(conta)
        return conta

    @log_operacoes
    def deposito(self, valor: Decimal, cliente: Cliente, conta: Conta):
        transacao = Deposito(valor)
        extrato = cliente.realizar_transacao(conta, transacao)
        persiste_transacao(conta, extrato)

    @log_operacoes
    def saque(self, valor: Decimal, cliente: Cliente, conta: Conta):
        transacao = Saque(valor)
        extrato = cliente.realizar_transacao(conta, transacao)
        persiste_transacao(conta, extrato)

    @log_operacoes
    def extrato(self, conta: Conta, filtrar_operacao: Literal['Deposito','Saque']):
        for transacao in conta.historico.extrato:
            if (filtrar_operacao == 'Deposito' and transacao["valor"].is_signed()) or \
               (filtrar_operacao == 'Saque' and not transacao["valor"].is_signed()):
                continue
            
            yield f'{transacao["data"].strftime("%c")} {"-" if transacao["valor"].is_signed() else "+"} R${abs(transacao["valor"]):.2f}'
        
    def __repr__(self) -> str:
        return f'SistemaBancario v{self.VERSAO}'