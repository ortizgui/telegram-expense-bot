import sqlite3

DB_PATH = 'expenses.db'

def init_db():
    """Inicializa o banco e cria tabela se não existir."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            note TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_expense(user_id, amount, category, date, note):
    """Insere uma despesa no banco."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO expenses (user_id, amount, category, date, note)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, amount, category, date, note))
    conn.commit()
    conn.close()

def get_monthly_report(user_id, month):
    """
    Retorna um dicionário {categoria: total} para o mês 'YYYY-MM'.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT category, SUM(amount) 
        FROM expenses
        WHERE user_id = ? AND strftime('%Y-%m', date) = ?
        GROUP BY category
    ''', (user_id, month))
    rows = c.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}