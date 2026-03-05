import os
import sys
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime


def get_base_path():
    # Support running frozen executable (PyInstaller)
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


base_path = get_base_path()
template_folder = os.path.join(base_path, 'templates')
app = Flask(__name__, template_folder=template_folder)

def get_db_connection():
    db_path = os.path.join(base_path, 'todo.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def root():
    today = datetime.now().strftime("%Y-%m-%d")
    return redirect(url_for("index", date=today))

@app.route('/<date>')
def index(date):
    q = request.args.get('q', '')
    conn = get_db_connection()
    if q:
        pattern = f"%{q}%"
        tasks = conn.execute(
            'SELECT * FROM tasks WHERE date = ? AND (content LIKE ? OR category LIKE ? OR tags LIKE ?) ORDER BY completed ASC, priority ASC, due_time IS NULL, due_time ASC',
            (date, pattern, pattern, pattern)
        ).fetchall()
    else:
        tasks = conn.execute(
            'SELECT * FROM tasks WHERE date = ? ORDER BY completed ASC, priority ASC, due_time IS NULL, due_time ASC',
            (date,)
        ).fetchall()
    totals = conn.execute('SELECT COUNT(*) as total, SUM(completed) as done FROM tasks WHERE date = ?', (date,)).fetchone()
    conn.close()
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        session_title = "Morning Study Session"
    else:
        session_title = "Evening Study Session"
    total = totals['total'] or 0
    done = totals['done'] or 0
    progress = int(done / total * 100) if total else 0
    return render_template('index.html', tasks=tasks, date=date, session_title=session_title, total=total, done=done, progress=progress, query=q)

@app.route('/<date>/add', methods=('GET', 'POST'))
def add(date):
    if request.method != 'POST':
        return redirect(url_for('index', date=date))
    content = request.form.get('content', '').strip()
    if not content:
        return redirect(url_for('index', date=date))
    due_time = request.form.get('due_time') or None
    try:
        priority = int(request.form.get('priority', 2))
    except Exception:
        priority = 2
    category = request.form.get('category') or ''
    notes = request.form.get('notes') or ''
    tags = request.form.get('tags') or ''
    created_at = datetime.now().isoformat()
    conn = get_db_connection()
    conn.execute('INSERT INTO tasks (content, date, created_at, due_time, priority, notes, category, tags) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                 (content, date, created_at, due_time, priority, notes, category, tags))
    conn.commit()
    conn.close()
    return redirect(url_for('index', date=date))

@app.route('/<date>/delete/<int:task_id>', methods=('POST',))
def delete(date, task_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index', date=date))

@app.route('/<date>/toggle/<int:task_id>', methods=('POST',))
def toggle(date, task_id):
    conn = get_db_connection()
    cur = conn.execute('SELECT completed FROM tasks WHERE id = ?', (task_id,)).fetchone()
    if cur is None:
        conn.close()
        return redirect(url_for('index', date=date))
    new = 0 if cur['completed'] else 1
    conn.execute('UPDATE tasks SET completed = ? WHERE id = ?', (new, task_id))
    conn.commit()
    conn.close()
    return redirect(url_for('index', date=date))

@app.route('/<date>/edit/<int:task_id>', methods=('POST',))
def edit(date, task_id):
    content = request.form.get('content', '').strip()
    due_time = request.form.get('due_time') or None
    try:
        priority = int(request.form.get('priority', 2))
    except Exception:
        priority = 2
    category = request.form.get('category') or ''
    notes = request.form.get('notes') or ''
    tags = request.form.get('tags') or ''
    conn = get_db_connection()
    conn.execute('UPDATE tasks SET content = ?, due_time = ?, priority = ?, category = ?, notes = ?, tags = ? WHERE id = ?',
                 (content, due_time, priority, category, notes, tags, task_id))
    conn.commit()
    conn.close()
    return redirect(url_for('index', date=date))


@app.route('/session', methods=('POST',))
def save_session():
    # Accept JSON payload with start,end,duration,type,mode
    data = request.get_json() or {}
    start = data.get('start')
    end = data.get('end')
    duration = int(data.get('duration') or 0)
    s_type = data.get('type') or 'stopwatch'
    mode = data.get('mode') or ''
    # derive date from start timestamp (ISO)
    try:
        d = datetime.fromisoformat(start)
        date = d.strftime('%Y-%m-%d')
    except Exception:
        date = datetime.now().strftime('%Y-%m-%d')
    conn = get_db_connection()
    conn.execute('INSERT INTO sessions (date, start_time, end_time, duration, type, mode) VALUES (?, ?, ?, ?, ?, ?)',
                 (date, start, end, duration, s_type, mode))
    conn.commit()
    conn.close()
    return ('', 204)


def fmt_hms(sec):
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


@app.route('/history')
def history():
    conn = get_db_connection()
    rows = conn.execute('SELECT date, SUM(duration) as total FROM sessions GROUP BY date ORDER BY date DESC').fetchall()
    conn.close()
    summary = []
    for r in rows:
        total = r['total'] or 0
        summary.append({'date': r['date'], 'total': total, 'fmt': fmt_hms(total)})
    return render_template('history.html', summary=summary)


@app.route('/history/<date>')
def history_day(date):
    conn = get_db_connection()
    sessions = conn.execute('SELECT * FROM sessions WHERE date = ? ORDER BY start_time ASC', (date,)).fetchall()
    conn.close()
    sess_list = []
    for s in sessions:
        sess_list.append({
            'id': s['id'], 'start': s['start_time'], 'end': s['end_time'], 'duration': s['duration'], 'type': s['type'], 'mode': s['mode'], 'fmt': fmt_hms(s['duration'])
        })
    total = sum(s['duration'] for s in sess_list)
    return render_template('history_day.html', date=date, sessions=sess_list, total=total, fmt_total=fmt_hms(total))

if __name__ == '__main__':
    app.run(debug=True)