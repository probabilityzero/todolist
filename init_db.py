import sqlite3

connection = sqlite3.connect('todo.db')
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    date TEXT NOT NULL
)
""")

cursor.execute("PRAGMA table_info('tasks')")
existing = {row[1] for row in cursor.fetchall()}

defs = {
    'created_at': "TEXT DEFAULT CURRENT_TIMESTAMP",
    'due_time': "TEXT",
    'priority': "INTEGER DEFAULT 2",
    'completed': "INTEGER DEFAULT 0",
    'notes': "TEXT",
    'category': "TEXT",
    'tags': "TEXT",
}

for col, definition in defs.items():
    if col not in existing:
        cursor.execute(f"ALTER TABLE tasks ADD COLUMN {col} {definition}")

cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_date ON tasks(date)')

connection.commit()
connection.close()