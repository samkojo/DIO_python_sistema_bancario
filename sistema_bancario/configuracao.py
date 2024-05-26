from decimal import Decimal
from os import environ
from typing import TypedDict

class Configuracao(TypedDict):
    saque_qtd_max_dia: int
    saque_valor_max: Decimal

configuracoes: Configuracao = {
    'saque_qtd_max_dia': int(environ.get('saque_qtd_max_dia', 3)),
    'saque_valor_max': Decimal(environ.get('saque_valor_max', 500)),
}