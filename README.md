# Telegram Expense Bot

Bot simples para registrar despesas via Telegram e gerar relatórios mensais.

## 1. Criação do Bot no Telegram

1. Abra o Telegram e inicie uma conversa com @BotFather  
2. Envie o comando /newbot  
3. Escolha um nome para o seu bot (ex: ExpenseTrackerBot)  
4. Escolha um username que termine com “bot” (ex: MyExpenseBot)  
5. O BotFather retornará um TOKEN no formato 123456789:ABCdefGhIjKlmNOpQRsTUVwxyz  
6. Copie esse TOKEN para usar na variável de ambiente

## 2. Funcionalidades

- **/add [amount]**  
    Inicia o fluxo de registro de despesa:
    1. Valor (ex: 12.50)  
    2. Categoria (botão inline)  
    3. Data em YYYY-MM-DD ou /skip para hoje  
    4. Nota ou /skip para nenhuma  

- **/report YYYY-MM**  
    Mostra o total por categoria no mês especificado (ex: /report 2025-04)

## 3. Pré-requisitos

- Python 3.8 ou superior  
- Biblioteca python-telegram-bot  
- SQLite (já incluído no Python)  
- TOKEN do seu bot (obtido com o BotFather)

## 4. Instalação

1. Clone o repositório  
      git clone https://github.com/usuario/expense_bot.git  
      cd expense_bot  

2. Crie e ative o ambiente virtual  
      python3 -m venv venv  
      source venv/bin/activate     (Linux/macOS)  
      venv\Scripts\activate        (Windows)  

3. Instale as dependências  
      pip install -r requirements.txt  

4. Defina a variável de ambiente  
      export TELEGRAM_TOKEN="seu_token_aqui"   (Linux/macOS)  
      set TELEGRAM_TOKEN="seu_token_aqui"      (Windows PowerShell)  

## 5. Inicialização do Banco de Dados

O arquivo expenses.db será criado automaticamente na primeira vez que o bot for executado.  
Não há necessidade de comandos manuais adicionais.

## 6. Execução do Bot

Com o ambiente virtual ativado e a variável TELEGRAM_TOKEN definida, execute:  
      python bot.py  

O bot iniciará o polling e aguardará comandos no Telegram.

## 7. Uso no Telegram

### Registrar despesa

- Envie `/add` e siga os passos:  
    1. Valor (ex: 12.50)  
    2. Escolha a categoria  
    3. Data em YYYY-MM-DD ou `/skip`  
    4. Nota ou `/skip`

- Ou envie `/add 12.50` para já pular a etapa de valor.

### Gerar relatório mensal

- Envie `/report 2025-04`  
- O bot retornará a soma por categoria para abril de 2025

---