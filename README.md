# (DIO) Projeto criando sistema bancario em python

Sistema bancario simples que permite depositar (valor positivo), sacar e imprimir um extrato.
Nessa v1 não será necessário considerar controle de acesso e multiplos usuarios, e moeda única R$.

## Requisitos

- [x] Depositar valor positivo
- [x] Fazer saques de ate R$ 500,00
- [x] Limite de 3 saques por dia
- [x] Caso usuario não tenha saldo, exibir mensagem de falta de saldo
- [x] Imprimir extrato
- [ ] Modularizar projeto
  - [ ] Função saque deve receber os argumentos apenas por nome (keyword only)
    - [ ] Sugestão de entrada: saldo, valor, extrato, limite, numero_saques, limite_saques
    - [ ] Sugestão de retorno: saldo e extrato
  - [ ] Função deposito deve receber os argumentos apenas por posição (positional only)
    - [ ] Sugestão de entrada: saldo, valor, extrato
    - [ ] Sugestão de saida: saldo e extrato
  - [ ] Função extrato deve receber os argumentos por posição e nome (positional only e keyword only)
    - [ ] Sugestão de entrada: saldo (positional) e extrato (nomeado)
- [ ] Adicionar usuario, podendo ter 1 por cpf
  - [ ] Usuário composto por nome, data de nascimento cpf e endereço (string com formato "logradouro, nro - bairro - cidade/sigla estado")
  - [ ] Armazenar somente numeros no cpf
- [ ] Adicionar conta, precisando estar vinculado a um usuario (1 usuario podem ter varias contas)
  - [ ] Conta composto por: agencia, numero da conta e usuario.
  - [ ] Numero da conta é sequencial, iniciando em 1
  - [ ] Numero da agencia é fixo "0001"
- [ ] Para acessar as funcionalidades de deposito, saque e extrato, deve primeiro selecionar qual usuario e depois qual conta

## Como usar

Pode executar via terminal

```bash
python sistema_bancario.py
```

ou via Makefile, podendo configurar variaveis de ambiente copiando `.env.example` para `.env`:

```bash
make run
```
