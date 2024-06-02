from decimal import Decimal
from os import environ
from typing import TypedDict

class Configuracao(TypedDict):
    saque_limite_qtd_dia: int
    saque_limite_valor: Decimal

configuracoes: Configuracao = {
    'saque_limite_qtd_dia': int(environ.get('saque_limite_qtd_dia', 3)),
    'saque_limite_valor': Decimal(environ.get('saque_limite_valor', 500)),
}