import os
import requests

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

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


    #

    return render_template("index.html", user=user, quote=response["quote"], author=response["author"])

@app.route('/to_do', methods=["GET", "POST"])
def to_do():
    tasks = [{"task": "1", "status": "completed"}]
    return render_template('to_do.html', tasks=tasks)

@app.route('/add_task', methods=['POST'])
def add_task():
    task = request.form['task']
    # Add code to store the task in your database or session
    return redirect(url_for('todo'))

@app.route('/pomodoro')
def pomodoro():
    return render_template('pomodoro.html')

@app.route('/note')
def note():
    return render_template('note.html')

@app.route('/quote')
def quote():
    return render_template('quote.html')

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

@app.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():
    """change password"""
    if request.method == "POST":
        username = request.form.get("username")
        oldpassword = request.form.get("oldpassword")
        newpassword = request.form.get("newpassword")

        if not request.form.get("username"):
            return apology("must provide username", 403)

        elif not request.form.get("oldpassword"):
            return apology("must provide password", 403)

        elif not request.form.get("newpassword"):
            return apology("must provide password", 403)

        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("oldpassword")
        ):
            return apology("invalid username and/or password", 403)
        else:
            hashed_password = generate_password_hash(
                newpassword, method="pbkdf2:sha256", salt_length=16
            )
            db.execute(
                "UPDATE users SET hash = ? WHERE username = ?",
                hashed_password,
                username,
            )
            flash("Password changed!")

    return render_template("changepassword.html")

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

