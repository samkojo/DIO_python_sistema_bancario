import csv
from datetime import datetime
from decimal import Decimal
import functools
from pathlib import Path
from typing import List, TypedDict

# from sistema_bancario.sistema import Cliente

PWD = Path(__file__).parent
LOG_FILE = 'log.txt'
CLIENTES_FILE = 'clientes.csv'
CONTAS_FILE = 'contas.csv'

def persiste_log_arquivo(log):
    try:
        with open(PWD / LOG_FILE, 'a') as arquivo:
            arquivo.write(log)
    except IOError as exc:
        print('Falha ao persistir arquivo de log', exc)

class ClientesCsv(TypedDict):
    cpf: str
    nome: str
    data_nascimento: str
    endereco: str

def cabecalho_csv(class_type):
    return list(class_type.__annotations__.keys())

def inicializa_clientes_csv() -> List[ClientesCsv]:
    print('Inicializando arquivo clientes')
    list_clientes: List[ClientesCsv] = []
    try:
        with open(PWD / CLIENTES_FILE, 'r', newline='', encoding='utf-8') as arquivo:
            read = csv.DictReader(arquivo)
            list_clientes = [ClientesCsv(**linha) for linha in read]
    except FileNotFoundError:
        with open(PWD / CLIENTES_FILE, 'w', newline='', encoding='utf-8') as arquivo:
            write = csv.writer(arquivo)
            write.writerow(cabecalho_csv(ClientesCsv))
    return list_clientes

def persiste_cliente_csv(cliente: ClientesCsv):
    try:
        with open(PWD / CLIENTES_FILE, 'a', newline='', encoding='utf-8') as arquivo:
            write = csv.DictWriter(arquivo, cliente.keys())

            if arquivo.tell() == 0:
                write.writeheader()

            write.writerow(cliente)
    except IOError as exc:
        print('Falha ao persistir cliente', exc)

class ContasCsv(TypedDict):
    id_cliente: str
    agencia: str
    numero: int

def inicializa_contas_csv() -> List[ContasCsv]:
    print('Inicializando arquivo contas')
    list_contas: List[ContasCsv] = []
    try:
        with open(PWD / CONTAS_FILE, 'r', newline='', encoding='utf-8') as arquivo:
            read = csv.DictReader(arquivo)
            list_contas = [ContasCsv(**linha) for linha in read]
    except FileNotFoundError:
        with open(PWD / CONTAS_FILE, 'w', newline='', encoding='utf-8') as arquivo:
            write = csv.writer(arquivo)
            write.writerow(cabecalho_csv(ContasCsv))
    return list_contas

def persiste_conta_csv(conta: ContasCsv):
    try:
        with open(PWD / CONTAS_FILE, 'a', newline='', encoding='utf-8') as arquivo:
            write = csv.DictWriter(arquivo, conta.keys())

            if arquivo.tell() == 0:
                write.writeheader()

            write.writerow(conta)
    except IOError as exc:
        print('Falha ao persistir conta', exc)

def log_operacoes(funcao):
    @functools.wraps(funcao)
    def envelope(*args, **kwargs):
        resultado = funcao(*args, **kwargs)

        log = f'| LOG INFO | {datetime.now().strftime("%c")} | Operação {funcao.__name__} |'
        print(log)

        log_file = log + f' executada com argumentos {args} e {kwargs} | Retornou {resultado}|\n'
        persiste_log_arquivo(log_file)

        return resultado

    return envelope