# 📚 StudyFlow — Study Planner Web Application
A complete web application built with Python Flask + MySQL + HTML/CSS/JavaScript.

---

## 📁 Project Structure

```
studyflow/
├── app.py                  ← Flask backend (main file)
├── database.sql            ← MySQL database setup
├── requirements.txt        ← Python packages to install
├── templates/
│   ├── base.html           ← Shared layout (sidebar, topbar)
│   ├── login.html          ← Login page
│   ├── register.html       ← Register page
│   ├── dashboard.html      ← Dashboard page
│   ├── tasks.html          ← Task list page
│   ├── task_form.html      ← Add / Edit task form
│   ├── reminders.html      ← Reminders page
│   └── analytics.html      ← Analytics & charts page
└── static/
    ├── css/
    │   ├── style.css       ← Main stylesheet
    │   └── auth.css        ← Login/Register styles
    └── js/
        └── main.js         ← JavaScript (password toggle, etc.)
```

---

## ⚙️ Setup Instructions (Step by Step)

### Step 1 — Install Python packages
Open your terminal/command prompt inside the project folder and run:
```
pip install -r requirements.txt
```

### Step 2 — Set up MySQL Database
1. Open MySQL (using phpMyAdmin, MySQL Workbench, or terminal)
2. Run the contents of `database.sql` to create the database and tables:
```sql
-- In MySQL terminal:
source database.sql;
-- OR copy-paste the SQL into phpMyAdmin and click "Go"
```

### Step 3 — Configure Database in app.py
Open `app.py` and update these lines with your MySQL details:
```python
app.config['MYSQL_HOST']     = 'localhost'
app.config['MYSQL_USER']     = 'root'       # your MySQL username
app.config['MYSQL_PASSWORD'] = ''           # your MySQL password
app.config['MYSQL_DB']       = 'studyflow'
```

### Step 4 — Run the Application
```
python app.py
```

### Step 5 — Open in Browser
Go to: http://127.0.0.1:5000

---

## ✨ Features

| Feature           | Description                                          |
|-------------------|------------------------------------------------------|
| Register & Login  | Secure accounts with hashed passwords                |
| Dashboard         | Stats, upcoming deadlines, recent tasks              |
| Task Manager      | Add, edit, delete, complete tasks with filters       |
| Categories        | Homework, Assignment, Exam, Report, Project          |
| Priority Levels   | High, Medium, Low with color coding                  |
| Reminders         | Overdue detection, urgency indicators                |
| Analytics         | Charts for categories, priorities, monthly overview  |
| Search & Filter   | Search tasks by name or subject                      |

---

## 🛠️ Technologies Used

- **Backend:** Python, Flask, Flask-MySQLdb
- **Database:** MySQL
- **Frontend:** HTML5, CSS3, JavaScript
- **Charts:** Chart.js
- **Security:** Werkzeug password hashing

---

## 📝 Notes

- Passwords are stored securely using Werkzeug's `generate_password_hash`
- Sessions expire when the browser is closed
- To change the secret key, update `app.secret_key` in `app.py`
