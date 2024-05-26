# (DIO) Projeto criando sistema bancario em python

Sistema bancario simples que permite depositar (valor positivo), sacar e imprimir um extrato.
Nessa v1 não será necessário considerar controle de acesso e multiplos usuarios, e moeda única R$.

## Requisitos

- [x] Depositar valor positivo
- [x] Fazer saques de ate R$ 500,00
- [x] Limite de 3 saques por dia
- [x] Caso usuario não tenha saldo, exibir mensagem de falta de saldo
- [x] Imprimir extrato
- [x] Modularizar projeto
  - [x] Função saque deve receber os argumentos apenas por nome (keyword only)
    - Sugestão de entrada: saldo, valor, extrato, limite, numero_saques, limite_saques
    - Sugestão de retorno: saldo e extrato
  - [x] Função deposito deve receber os argumentos apenas por posição (positional only)
    - Sugestão de entrada: saldo, valor, extrato
    - Sugestão de saida: saldo e extrato
  - [x] Função extrato deve receber os argumentos por posição e nome (positional only e keyword only)
    - Sugestão de entrada: saldo (positional) e extrato (nomeado)
- [x] Adicionar usuario, podendo ter 1 por cpf
  - [x] Usuário composto por nome, data de nascimento, cpf e endereço (string com formato "logradouro, nro - bairro - cidade/sigla estado")
  - [ ] Implementar validações
  - [x] Armazenar somente numeros no cpf
- [ ] Adicionar conta, precisando estar vinculado a um usuario (1 usuario podem ter varias contas)
  - [ ] Conta composto por: agencia, numero da conta e usuario.
  - [ ] Numero da conta é sequencial, iniciando em 1
  - [ ] Numero da agencia é fixo "0001"
- [ ] Para acessar as funcionalidades de deposito, saque e extrato, deve passar que agencia e conta
  - [ ] Para isso primeiro selecionar qual usuario, listas as contas e assim selecionar agencia e conta

## Como usar

Pode executar via terminal

```bash
python -m sistema_bancario
```

ou via Makefile, podendo configurar variaveis de ambiente copiando `.env.example` para `.env`:

```bash
make run
```
