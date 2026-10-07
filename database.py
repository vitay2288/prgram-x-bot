import sqlite3
from datetime import datetime, date, timedelta
from config import LEVELS

DB = "/data/prgram_x.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance INTEGER DEFAULT 0,
            level TEXT DEFAULT 'Bronze',
            referrer_id INTEGER,
            reg_date TEXT,
            last_bonus TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS referrals (
            user_id INTEGER,
            referrer_id INTEGER
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            channel_link TEXT,
            reward INTEGER,
            max_completions INTEGER,
            completed INTEGER DEFAULT 0,
            created_by INTEGER,
            created_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS user_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            task_id INTEGER,
            completed_at TEXT,
            check_after TEXT,
            status TEXT DEFAULT 'pending',
            UNIQUE(user_id, task_id)
        )
    """)
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def create_user(user_id, username, referrer_id=None):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        INSERT OR IGNORE INTO users (user_id, username, referrer_id, reg_date)
        VALUES (?, ?, ?, ?)
    """, (user_id, username, referrer_id, datetime.now().strftime("%d.%m.%Y")))
    conn.commit()
    conn.close()

def add_balance(user_id, amount):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()
    update_level(user_id)

def update_level(user_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return
    bal = row[0]
    level = "Bronze"
    for name, data in LEVELS.items():
        if bal >= data["threshold"]:
            level = name
    c.execute("UPDATE users SET level = ? WHERE user_id = ?", (level, user_id))
    conn.commit()
    conn.close()

def can_take_bonus(user_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT last_bonus FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if not row or row[0] != str(date.today()):
        return True
    return False

def set_bonus_date(user_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE users SET last_bonus = ? WHERE user_id = ?", (str(date.today()), user_id))
    conn.commit()
    conn.close()

def get_referrer(user_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT referrer_id FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row and row[0] else None

def create_task(task_type, channel_link, reward, max_completions, user_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        INSERT INTO tasks (type, channel_link, reward, max_completions, created_by, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (task_type, channel_link, reward, max_completions, user_id, datetime.now().strftime("%d.%m.%Y")))
    conn.commit()
    conn.close()

def get_available_tasks(user_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        SELECT * FROM tasks 
        WHERE completed < max_completions 
        AND id NOT IN (SELECT task_id FROM user_tasks WHERE user_id = ?)
        LIMIT 10
    """, (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def complete_task(user_id, task_id, reward):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    check_date = (datetime.now() + timedelta(days=7)).strftime("%d.%m.%Y")
    c.execute("""
        INSERT INTO user_tasks (user_id, task_id, completed_at, check_after)
        VALUES (?, ?, ?, ?)
    """, (user_id, task_id, datetime.now().strftime("%d.%m.%Y"), check_date))
    c.execute("UPDATE tasks SET completed = completed + 1 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    add_balance(user_id, reward)
    referrer = get_referrer(user_id)
    if referrer:
        add_balance(referrer, int(reward * 0.09))

def get_pending_checks():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    today = datetime.now().strftime("%d.%m.%Y")
    c.execute("""
        SELECT ut.id, ut.user_id, ut.task_id, t.reward, t.channel_link
        FROM user_tasks ut
        JOIN tasks t ON ut.task_id = t.id
        WHERE ut.status = 'pending' AND ut.check_after <= ?
    """, (today,))
    rows = c.fetchall()
    conn.close()
    return rows

def reject_task(user_task_id, reward):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT user_id FROM user_tasks WHERE id = ?", (user_task_id,))
    row = c.fetchone()
    if row:
        user_id = row[0]
        c.execute("UPDATE user_tasks SET status = 'rejected' WHERE id = ?", (user_task_id,))
        conn.commit()
        conn.close()
        add_balance(user_id, -reward)
    else:
        conn.close()

def confirm_task(user_task_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE user_tasks SET status = 'confirmed' WHERE id = ?", (user_task_id,))
    conn.commit()
    conn.close()
