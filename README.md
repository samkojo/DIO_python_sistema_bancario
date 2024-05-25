# (DIO) Projeto criando sistema bancario em python

Sistema bancario simples que permite depositar (valor positivo), sacar e imprimir um extrato.
Nessa v1 não será necessário considerar controle de acesso e multiplos usuarios, e moeda única R$.

## Requisitos

- [x] Depositar valor positivo
- [x] Fazer saques de ate R$ 500,00
- [x] Limite de 3 saques por dia
- [x] Caso usuario não tenha saldo, exibir mensagem de falta de saldo
- [x] Imprimir extrato

## Como usar

Pode executar via terminal

```bash
python sistema_bancario.py
```

ou via Makefile, podendo configurar variaveis de ambiente copiando `.env.example` para `.env`:

```bash
make run
```
