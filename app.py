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


@app.errorhandler(404)
def not_found(error):
    return apology("The page could not be found. Did you perhaps mistype the URL?", 404)

def count_tasks_group_by_status():
    tasks_status_count_db = db.execute("SELECT status, COUNT(*) FROM tasks WHERE user_id=? GROUP BY status", session.get("user_id"))

    tasks_status_count = {counter['status']: counter['COUNT(*)'] for counter in tasks_status_count_db}

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

    return render_template("index.html", user=user, quote=response["quote"], author=response["author"], tasks=tasks, tasks_status_counter=count_tasks_group_by_status())


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
            return apology("Please provide your username and password and confirmation password and try again.", 403)

        if password != confirmation:
            return apology("Oops! The passwords you entered are different. Please double-check and re-type your password.", 403)
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
            return apology("Whoops! It looks like someone else has already claimed that username. Try picking a unique one.", 400)

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
            return apology("Invalid credentials. Please provide your username and try again.", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Invalid credentials. Please provide your password and try again.", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("Invalid credentials. Please check your username and password and try again.", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        flash("Logged in!")

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
    if ("user_id" not in session.keys()):
        return redirect(url_for("login"))

    tasks = db.execute("SELECT * FROM tasks WHERE user_id = ?", session["user_id"])

    return render_template("tasks.html", tasks=tasks, tasks_status_counter=count_tasks_group_by_status())

@app.route('/add_task', methods=['POST'])
def add_task():
    task = request.form.get("task")
    category = request.form.get("category") or "uncategorized"
    status = request.form.get("status") or "not started"

    db.execute("INSERT INTO tasks (task, status, user_id) VALUES (?, ?, ?)", task, status, session["user_id"])

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
        return apology("The task you're trying to access might have been deleted or moved. Please try searching for it again.", 404)
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
    if ("user_id" not in session.keys()):
        return redirect(url_for("login"))
    return render_template('pomodoro.html')

@app.route('/notes', methods=["GET"])
def notes():
    if ("user_id" not in session.keys()):
        return redirect(url_for("login"))

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
        return apology("Uh oh! Seems like the note you requested isn't available anymore.", 404)
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
    if ("user_id" not in session.keys()):
        return redirect(url_for("login"))

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
            return apology("Current Password: Please enter your current password for verification.\nNew Password: Choose a strong password for your account.\nConfirm New Password: Re-enter your new password to ensure it's correct.", 403)

        # Ensure old password is correct
        if not check_password_hash(user["hash"], old_pass):
            return apology("The current password you entered is incorrect. Please try again.", 400, request.referrer)

        if old_pass == new_pass:
            return apology("To enhance your account security, choose a new password that's different from your current password.", 400, request.referrer)

        if new_pass != confirmation:
            return apology("Your passwords don't match. Please ensure your 'Confirm New Password' field matches your 'New Password'.", 400, request.referrer)

        # Query to insert user
        db.execute("""
UPDATE users
SET hash=?
WHERE id=?
;""", c_hash, user["id"])

        flash("Updated Password!")

        return redirect("/")

    return render_template("profile.html", username=user["username"])
