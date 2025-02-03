from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('todo.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/<date>')
def index(date):
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks WHERE date = ?', (date,)).fetchall()
    conn.close()

    # Determine the session title based on the current time
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        session_title = "Morning Study Session"
    else:
        session_title = "Evening Study Session"

    return render_template('index.html', tasks=tasks, date=date, session_title=session_title)

@app.route('/<date>/add', methods=('POST',))
def add(date):
    content = request.form['content']
    if content:
        conn = get_db_connection()
        conn.execute('INSERT INTO tasks (content, date) VALUES (?, ?)', (content, date))
        conn.commit()
        conn.close()
    return redirect(url_for('index', date=date))

@app.route('/<date>/delete/<int:task_id>')
def delete(date, task_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index', date=date))

if __name__ == '__main__':
    app.run(debug=True)