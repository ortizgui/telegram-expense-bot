import os
import psycopg2
from psycopg2 import pool

# PostgreSQL connection pool
connection_pool = None


def init_db():
    """Initializes the database and creates tables if they don't exist."""
    global connection_pool
    db_url = os.getenv('DATABASE_URL')

    if connection_pool is None:
        connection_pool = pool.SimpleConnectionPool(1, 10, db_url)

    conn = get_connection()
    try:
        with conn.cursor() as c:
            c.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    amount NUMERIC(10,2) NOT NULL,
                    category TEXT NOT NULL,
                    date DATE NOT NULL,
                    note TEXT
                )
            ''')
        conn.commit()
    finally:
        put_connection(conn)


def get_connection():
    """Gets a connection from the pool, initializing if necessary."""
    if connection_pool is None:
        init_db()
    return connection_pool.getconn()


def put_connection(conn):
    """Returns a connection to the pool."""
    connection_pool.putconn(conn)


def add_expense(user_id, amount, category, date, note):
    """Inserts an expense into the database."""
    conn = get_connection()
    try:
        with conn.cursor() as c:
            c.execute('''
                INSERT INTO expenses (user_id, amount, category, date, note)
                VALUES (%s, %s, %s, %s, %s)
            ''', (user_id, amount, category, date, note))
        conn.commit()
    finally:
        put_connection(conn)


def get_monthly_report(user_id, month):
    """
    Returns a dictionary {category: total} for the month 'YYYY-MM'.
    """
    conn = get_connection()
    try:
        with conn.cursor() as c:
            c.execute('''
                SELECT category, SUM(amount)
                FROM expenses
                WHERE user_id = %s AND to_char(date, 'YYYY-MM') = %s
                GROUP BY category
            ''', (user_id, month))
            rows = c.fetchall()
        return {row[0]: row[1] for row in rows}
    finally:
        put_connection(conn)