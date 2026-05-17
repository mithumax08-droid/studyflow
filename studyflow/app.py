from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql
pymysql.install_as_MySQLdb()
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import date, timedelta
import re
import os

app = Flask(__name__)
app.secret_key = 'studyflow_secret_key_2024'

# ── MySQL Config ──
app.config['MYSQL_HOST']        = os.environ.get('MYSQLHOST', 'localhost')
app.config['MYSQL_USER']        = os.environ.get('MYSQLUSER', 'root')
app.config['MYSQL_PASSWORD']    = os.environ.get('MYSQLPASSWORD', '')
app.config['MYSQL_DB']          = os.environ.get('MYSQLDATABASE', 'studyflow')
app.config['MYSQL_PORT']        = int(os.environ.get('MYSQLPORT', 3306))
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# ── Mail Config ──
app.config['MAIL_SERVER']   = 'smtp.gmail.com'
app.config['MAIL_PORT']     = 587
app.config['MAIL_USE_TLS']  = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_EMAIL')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

mysql = MySQL(app)
mail  = Mail(app)

# ── Helper: login required ──
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ── Helper: days until deadline ──
def days_until(deadline):
    if not deadline:
        return None
    today = date.today()
    if isinstance(deadline, str):
        deadline = date.fromisoformat(deadline)
    return (deadline - today).days

app.jinja_env.globals['days_until'] = days_until
app.jinja_env.globals['today_date'] = lambda: date.today().isoformat()

# ════════════════════════════
#  AUTH
# ════════════════════════════

@app.route('/')
def index():
    return redirect(url_for('dashboard') if 'user_id' in session else url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        if user and check_password_hash(user['password'], password):
            session['user_id']       = user['id']
            session['user_name']     = user['first_name'] + ' ' + user['last_name']
            session['user_fname']    = user['first_name']
            session['user_type']     = user['student_type']
            session['user_initials'] = (user['first_name'][0] + user['last_name'][0]).upper()
            flash('Welcome back, ' + user['first_name'] + '!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid email or password.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        fname    = request.form.get('first_name', '').strip()
        lname    = request.form.get('last_name', '').strip()
        email    = request.form.get('email', '').strip()
        stype    = request.form.get('student_type', 'university')
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        if not fname or not email or not password:
            flash('Please fill all required fields.', 'error')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address.', 'error')
        elif len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
        elif password != confirm:
            flash('Passwords do not match.', 'error')
        else:
            cur = mysql.connection.cursor()
            cur.execute("SELECT id FROM users WHERE email=%s", (email,))
            if cur.fetchone():
                flash('Email already registered.', 'error')
                cur.close()
            else:
                cur.execute(
                    "INSERT INTO users (first_name,last_name,email,password,student_type) VALUES(%s,%s,%s,%s,%s)",
                    (fname, lname, email, generate_password_hash(password), stype)
                )
                mysql.connection.commit()
                cur.close()
                flash('Account created! Please sign in.', 'success')
                return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# ════════════════════════════
#  DASHBOARD
# ════════════════════════════

@app.route('/dashboard')
@login_required
def dashboard():
    uid   = session['user_id']
    today = date.today().isoformat()
    cur   = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) AS v FROM tasks WHERE user_id=%s", (uid,))
    total = cur.fetchone()['v']

    cur.execute("SELECT COUNT(*) AS v FROM tasks WHERE user_id=%s AND status='done'", (uid,))
    done = cur.fetchone()['v']

    cur.execute("SELECT COUNT(*) AS v FROM tasks WHERE user_id=%s AND status!='done' AND deadline < %s", (uid, today))
    overdue = cur.fetchone()['v']

    cur.execute("""SELECT * FROM tasks WHERE user_id=%s AND status!='done'
                   AND deadline>=%s ORDER BY deadline ASC LIMIT 5""", (uid, today))
    upcoming = cur.fetchall()

    cur.execute("SELECT * FROM tasks WHERE user_id=%s ORDER BY created_at DESC LIMIT 6", (uid,))
    recent = cur.fetchall()

    cur.execute("SELECT category, COUNT(*) AS cnt FROM tasks WHERE user_id=%s GROUP BY category", (uid,))
    categories = cur.fetchall()

    cur.close()
    pending = total - done
    pct     = round(done / total * 100) if total else 0

    return render_template('dashboard.html',
        total=total, done=done, pending=pending,
        overdue=overdue, upcoming=upcoming, recent=recent,
        categories=categories, pct=pct, today=today)

# ════════════════════════════
#  TASKS
# ════════════════════════════

@app.route('/tasks')
@login_required
def tasks():
    uid      = session['user_id']
    category = request.args.get('category', 'all')
    search   = request.args.get('search', '').strip()
    cur      = mysql.connection.cursor()
    query    = "SELECT * FROM tasks WHERE user_id=%s"
    params   = [uid]
    if category != 'all':
        query += " AND category=%s"; params.append(category)
    if search:
        query += " AND (name LIKE %s OR subject LIKE %s)"
        params += [f'%{search}%', f'%{search}%']
    query += " ORDER BY FIELD(status,'pending','done'), deadline ASC"
    cur.execute(query, params)
    task_list = cur.fetchall()
    cur.close()
    return render_template('tasks.html', tasks=task_list, category=category, search=search)

@app.route('/tasks/add', methods=['GET', 'POST'])
@login_required
def add_task():
    if request.method == 'POST':
        uid      = session['user_id']
        name     = request.form.get('name', '').strip()
        category = request.form.get('category', 'homework')
        priority = request.form.get('priority', 'medium')
        subject  = request.form.get('subject', '').strip()
        deadline = request.form.get('deadline', '')
        notes    = request.form.get('notes', '').strip()
        if not name or not deadline:
            flash('Task name and deadline are required.', 'error')
            return render_template('task_form.html', task=None)
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO tasks (user_id,name,category,priority,subject,deadline,notes,status) VALUES(%s,%s,%s,%s,%s,%s,%s,'pending')",
            (uid, name, category, priority, subject, deadline, notes)
        )
        mysql.connection.commit()
        cur.close()
        flash('Task added successfully!', 'success')
        return redirect(url_for('tasks'))
    return render_template('task_form.html', task=None)

@app.route('/tasks/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    uid = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tasks WHERE id=%s AND user_id=%s", (task_id, uid))
    task = cur.fetchone()
    if not task:
        flash('Task not found.', 'error')
        return redirect(url_for('tasks'))
    if request.method == 'POST':
        cur.execute("""UPDATE tasks SET name=%s,category=%s,priority=%s,subject=%s,deadline=%s,notes=%s
                       WHERE id=%s AND user_id=%s""",
            (request.form['name'], request.form['category'], request.form['priority'],
             request.form.get('subject',''), request.form['deadline'],
             request.form.get('notes',''), task_id, uid))
        mysql.connection.commit()
        cur.close()
        flash('Task updated!', 'success')
        return redirect(url_for('tasks'))
    cur.close()
    return render_template('task_form.html', task=task)

@app.route('/tasks/toggle/<int:task_id>')
@login_required
def toggle_task(task_id):
    uid = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT status FROM tasks WHERE id=%s AND user_id=%s", (task_id, uid))
    t = cur.fetchone()
    if t:
        new = 'done' if t['status'] == 'pending' else 'pending'
        cur.execute("UPDATE tasks SET status=%s WHERE id=%s", (new, task_id))
        mysql.connection.commit()
    cur.close()
    return redirect(request.referrer or url_for('tasks'))

@app.route('/tasks/delete/<int:task_id>')
@login_required
def delete_task(task_id):
    uid = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM tasks WHERE id=%s AND user_id=%s", (task_id, uid))
    mysql.connection.commit()
    cur.close()
    flash('Task deleted.', 'success')
    return redirect(url_for('tasks'))

# ════════════════════════════
#  REMINDERS
# ════════════════════════════

@app.route('/reminders')
@login_required
def reminders():
    uid   = session['user_id']
    today = date.today().isoformat()
    cur   = mysql.connection.cursor()
    cur.execute("""SELECT * FROM tasks WHERE user_id=%s AND status!='done'
                   ORDER BY deadline ASC""", (uid,))
    task_list = cur.fetchall()
    cur.close()
    return render_template('reminders.html', tasks=task_list, today=today)

# ════════════════════════════
#  ANALYTICS
# ════════════════════════════

@app.route('/analytics')
@login_required
def analytics():
    uid   = session['user_id']
    today = date.today().isoformat()
    cur   = mysql.connection.cursor()

    cur.execute("SELECT category, COUNT(*) AS cnt FROM tasks WHERE user_id=%s GROUP BY category", (uid,))
    cat_data = cur.fetchall()

    cur.execute("SELECT priority, COUNT(*) AS cnt FROM tasks WHERE user_id=%s GROUP BY priority", (uid,))
    pri_data = cur.fetchall()

    cur.execute("""
        SELECT DATE_FORMAT(deadline,'%%b %%Y') AS month,
               COUNT(*) AS total,
               SUM(CASE WHEN status='done' THEN 1 ELSE 0 END) AS completed
        FROM tasks WHERE user_id=%s
        GROUP BY DATE_FORMAT(deadline,'%%Y-%%m'), DATE_FORMAT(deadline,'%%b %%Y')
        ORDER BY MIN(deadline) DESC LIMIT 6
    """, (uid,))
    monthly = list(reversed(cur.fetchall()))

    cur.execute("SELECT COUNT(*) AS v FROM tasks WHERE user_id=%s", (uid,))
    total = cur.fetchone()['v']
    cur.execute("SELECT COUNT(*) AS v FROM tasks WHERE user_id=%s AND status='done'", (uid,))
    done = cur.fetchone()['v']
    cur.execute("SELECT COUNT(*) AS v FROM tasks WHERE user_id=%s AND status!='done' AND deadline<%s", (uid, today))
    overdue = cur.fetchone()['v']

    cur.close()
    pct = round(done / total * 100) if total else 0
    return render_template('analytics.html',
        cat_data=cat_data, pri_data=pri_data, monthly=monthly,
        total=total, done=done, overdue=overdue, pct=pct)

# ════════════════════════════
#  EMAIL REMINDERS
# ════════════════════════════

@app.route('/send-reminders')
def send_reminders():
    try:
        cur = mysql.connection.cursor()
        tomorrow = (date.today() + timedelta(days=1)).isoformat()

        cur.execute("""
            SELECT t.name, t.deadline, t.subject, t.priority,
                   u.email, u.first_name
            FROM tasks t
            JOIN users u ON t.user_id = u.id
            WHERE t.deadline = %s AND t.status = 'pending'
        """, (tomorrow,))

        task_list = cur.fetchall()
        cur.close()

        if not task_list:
            return "No reminders to send today!", 200

        sent = 0
        for task in task_list:
            msg = Message(
                subject=f"⏰ Reminder: {task['name']} is due tomorrow!",
                sender=os.environ.get('MAIL_EMAIL'),
                recipients=[task['email']]
            )
            msg.body = f"""Hi {task['first_name']},

This is a reminder that your task is due tomorrow!

📚 Task: {task['name']}
📅 Deadline: {task['deadline']}
📖 Subject: {task['subject']}
🔴 Priority: {task['priority']}

Login to StudyFlow to complete it:
https://studyflow-production-0cba.up.railway.app

Good luck!
StudyFlow Team
"""
            mail.send(msg)
            sent += 1

        return f"{sent} reminder(s) sent successfully!", 200

    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))