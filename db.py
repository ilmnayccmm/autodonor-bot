import sqlite3
from datetime import datetime

DB_NAME = "autodonor.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    # Створюємо таблицю з усіма необхідними полями
    cur.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            service TEXT NOT NULL,
            phone TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_request(user_id: int, username: str, service: str, phone: str):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO requests (user_id, username, service, phone, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, username, service, phone, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_all_requests():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    # Беремо останні 10 заявок для адмін-панелі
    cur.execute("SELECT created_at, service, phone, username FROM requests ORDER BY id DESC LIMIT 10")
    rows = cur.fetchall()
    conn.close()
    return rows