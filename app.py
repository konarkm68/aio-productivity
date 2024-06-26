import os
import requests

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from icecream import ic

from helpers import apology, login_required

db = SQL("sqlite:///aio-p.db")

# Configure application
app = Flask(__name__)

app.secret_key = "3IkeHwgzG4VbRo1s"

# Custom filter
#app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

def count_tasks_group_by_status(tasks):
    tasks_status_count = {
        "not started": 0,
        "in progress": 0,
        "pending": 0,
        "completed": 0
    }
    for i in tasks:
        if i["status"] == "not started":
            tasks_status_count["not started"] += 1
        elif i["status"] == "in progress":
            tasks_status_count["in progress"] += 1
        elif i["status"] == "pending":
            tasks_status_count["pending"] += 1
        elif i["status"] == "completed":
            tasks_status_count["completed"] += 1
    return tasks_status_count

@app.route("/")
@login_required
def index():
    user = db.execute("SELECT username FROM users WHERE id=?", session.get("user_id"))[0]["username"]

    category = 'future'
    api_url = 'https://api.api-ninjas.com/v1/quotes?category={}'.format(category)
    response = requests.get(api_url, headers={'X-Api-Key': 'JPoUeHK/XTHGgNtjCufFyQ==tn0KdgTRnXFP3mVh'})
    if response.status_code == requests.codes.ok:
        response = response.json()[0]
    else:
        flash("Error:", response.status_code, response.text)

    tasks = db.execute("SELECT * FROM tasks WHERE user_id = ?;", session["user_id"])

    return render_template("index.html", user=user, quote=response["quote"], author=response["author"], tasks=tasks, tasks_status_counter=count_tasks_group_by_status(tasks))


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if (
            not request.form.get("username")
            or not request.form.get("password")
            or not request.form.get("confirmation")
        ):
            return apology("must provide username and password", 400)

        if password != confirmation:
            return apology("passwords must match", 400)
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if not rows:
            hashed_password = generate_password_hash(
                password, method="pbkdf2:sha256", salt_length=16
            )
            db.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)",
                username,
                hashed_password,
            )
            return render_template("register.html", error="Registration Successful!")
        else:
            return apology("username already taken", 400)

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        flash("Logged in!")

        print(session["user_id"])

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route('/tasks', methods=["GET"])
def tasks():
    tasks = db.execute("SELECT * FROM tasks WHERE user_id = ?", session["user_id"])

    return render_template("tasks.html", tasks=tasks, tasks_status_counter=count_tasks_group_by_status(tasks))

@app.route('/add_task', methods=['POST'])
def add_task():
    task = request.form.get("task")
    category = request.form.get("category") or "uncategorized"
    status = request.form.get("status") or "not started"

    db.execute("INSERT INTO tasks (task, category, status, user_id) VALUES (?, ?, ?, ?)", task, category, status, session["user_id"])

    return redirect(url_for('tasks'))

@app.route('/del_task', methods=["POST"])
def del_task():
    ic(request.form.get("task_id"))
    db.execute("DELETE from tasks WHERE id = ? AND user_id = ?", request.form.get("task_id"), session["user_id"])

    return redirect(url_for('tasks'))

@app.route('/edit_task/<int:task_id>', methods=['GET'])
def edit_task_route(task_id):
    task = db.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", task_id, session["user_id"])
    if not task:
        return apology("Task not found", 404)
    return render_template("edit_task.html", task=task[0])

@app.route('/update_task/<int:task_id>', methods=['POST'])
def update_task_route(task_id):
    new_task = request.form.get('task')
    new_status = request.form.get('status')
    db.execute("UPDATE tasks SET task = ?, status = ? WHERE id = ? AND user_id = ?", new_task, new_status, task_id, session["user_id"])
    flash("Task updated successfully!")
    return redirect(url_for('tasks'))

@app.route('/pomodoro')
def pomodoro():
    return render_template('pomodoro.html')


@app.route('/notes', methods=["GET"])
def notes():
    notes = db.execute("SELECT * FROM notes WHERE user_id = ?", session["user_id"])

    return render_template('notes.html', notes=notes)
@app.route('/add_note', methods=["POST"])
def add_note():
    note = request.form.get("note")

    if not note:
        note = "empty"

    category = request.form.get("category") or "uncategorized"

    db.execute("INSERT INTO notes (note, category, user_id) VALUES (?, ?, ?)",
                note, category, session["user_id"])

    return redirect(url_for('notes'))


@app.route('/del_note', methods=["POST"])
def del_note():
    db.execute("DELETE from notes WHERE id = ? AND user_id = ?", request.form.get("note_id"), session["user_id"])

    return redirect(url_for('notes'))

@app.route('/edit_note/<int:note_id>', methods=['GET'])
def edit_note_route(note_id):
    note = db.execute("SELECT * FROM notes WHERE id = ? AND user_id = ?", note_id, session["user_id"])
    if not note:
        return apology("Note not found", 404)
    return render_template("edit_note.html", note=note[0])

@app.route('/update_note/<int:note_id>', methods=['POST'])
def update_note_route(note_id):
    new_note = request.form.get('note')
    db.execute("UPDATE notes SET note = ? WHERE id = ? AND user_id = ?", new_note, note_id, session["user_id"])
    flash("Note updated successfully!")
    return redirect(url_for('notes'))

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Modify User Profile"""

    user = db.execute("""
SELECT * FROM users
WHERE id=?
;""", session.get("user_id"))[0]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        old_pass = request.form.get("old_pass")
        new_pass = request.form.get("new_pass")
        confirmation = request.form.get("confirmation")

        # Generate Password & Confirm Password Hash
        # p_hash = generate_password_hash(password)
        c_hash = generate_password_hash(confirmation)

        # Ensure password was submitted
        if not old_pass or not new_pass or not confirmation:
            return apology("must provide old password and/or new password / confirm new password", 403)

        # Ensure old password is correct
        if not check_password_hash(user["hash"], old_pass):
            return apology("invalid old password", 403)

        if old_pass == new_pass:
            return apology("old password and new password should not match", 400)

        if new_pass != confirmation:
            return apology("new password and confirm new password should match", 400)

        # Query to insert user
        db.execute("""
UPDATE users
SET hash=?
WHERE id=?
;""", c_hash, user["id"])

        flash("Updated Password!")

        return redirect("/")

    return render_template("profile.html", username=user["username"])
