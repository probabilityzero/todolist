import sqlite3

connection = sqlite3.connect('todo.db')
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    date TEXT NOT NULL
)
''')

connection.commit()
connection.close()