import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import (
    LoginManager, UserMixin, login_user, login_required,
    logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "change-this-secret-key"  # needed for session/flash messages
DB_NAME = "notes.db"

# ---------------------------------------------------------
# DATABASE SETUP
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# ---------------------------------------------------------
# FLASK-LOGIN SETUP
# ---------------------------------------------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access this page."

class User(UserMixin):
    def __init__(self, id, email, name):
        self.id = id
        self.email = email
        self.name = name

@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if row:
        return User(row["id"], row["email"], row["name"])
    return None

# ---------------------------------------------------------
# ROUTES: SIGNUP / LOGIN / LOGOUT
# ---------------------------------------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        name = request.form.get("name", "").strip() or email.split("@")[0]

        conn = get_db()
        existing = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            flash("An account with this email already exists. Please log in.")
            conn.close()
            return redirect(url_for("login"))

        hashed_pw = generate_password_hash(password)
        conn.execute(
            "INSERT INTO users (email, password, name) VALUES (?, ?, ?)",
            (email, hashed_pw, name),
        )
        conn.commit()
        conn.close()
        flash("Account created successfully! Please log in.")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        conn = get_db()
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if row and check_password_hash(row["password"], password):
            user = User(row["id"], row["email"], row["name"])
            login_user(user)
            flash("Logged in successfully!")
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password.")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("login"))

# ---------------------------------------------------------
# ROUTES: HOME + NOTES CRUD
# ---------------------------------------------------------
@app.route("/")
@app.route("/home")
@login_required
def home():
    conn = get_db()
    notes = conn.execute(
        "SELECT * FROM notes WHERE user_id = ? ORDER BY id DESC",
        (current_user.id,),
    ).fetchall()
    conn.close()
    return render_template("home.html", notes=notes, user=current_user)


@app.route("/add_note", methods=["POST"])
@login_required
def add_note():
    title = request.form.get("title", "").strip()
    if title:
        conn = get_db()
        conn.execute(
            "INSERT INTO notes (user_id, title, created_at) VALUES (?, ?, ?)",
            (current_user.id, title, datetime.now().strftime("%b %d, %I:%M %p")),
        )
        conn.commit()
        conn.close()
    else:
        flash("Note cannot be empty.")
    return redirect(url_for("home"))


@app.route("/edit_note/<int:note_id>", methods=["POST"])
@login_required
def edit_note(note_id):
    new_title = request.form.get("title", "").strip()
    conn = get_db()
    note = conn.execute(
        "SELECT * FROM notes WHERE id = ? AND user_id = ?", (note_id, current_user.id)
    ).fetchone()
    if note and new_title:
        conn.execute("UPDATE notes SET title = ? WHERE id = ?", (new_title, note_id))
        conn.commit()
    conn.close()
    return redirect(url_for("home"))


@app.route("/delete_note/<int:note_id>", methods=["POST"])
@login_required
def delete_note(note_id):
    conn = get_db()
    conn.execute(
        "DELETE FROM notes WHERE id = ? AND user_id = ?", (note_id, current_user.id)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("home"))


init_db()

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
