from datetime import datetime
import functools


def log_operacoes(funcao):
    @functools.wraps(funcao)
    def envelope(*args, **kwargs):
        print(f'| LOG INFO | {datetime.now().strftime("%c")} | Operação {funcao.__name__} |')
        return funcao(*args, **kwargs)

    return envelope