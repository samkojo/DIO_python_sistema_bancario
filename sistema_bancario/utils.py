from datetime import datetime
import functools
from pathlib import Path

PWD = Path(__file__).parent
LOG_FILE = 'log.txt'

def persiste_log_arquivo(log):
    try:
        with open(PWD / LOG_FILE, 'a') as arquivo:
            arquivo.write(log)
    except IOError as exc:
        print('Falha ao persistir arquivo de log', exc)

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