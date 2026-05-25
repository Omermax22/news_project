import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "news_secret_key_2026"

# =========================
# Upload folder
# =========================
UPLOAD_FOLDER = "static/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =========================
# Database setup
# =========================
def init_db():

    conn = sqlite3.connect("news.db")
    c = conn.cursor()

    # News table
    c.execute("""
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        image TEXT,
        views INTEGER DEFAULT 0,
        likes INTEGER DEFAULT 0
    )
    """)

    # Users table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)

    # Comments table
    c.execute("""
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        comment TEXT NOT NULL,
        news_id INTEGER NOT NULL
    )
    """)

    conn.commit()
    conn.close()

init_db()

# =========================
# Create admin
# =========================
def create_admin():

    conn = sqlite3.connect("news.db")
    c = conn.cursor()

    try:

        c.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (
                "omer Hassan",
                generate_password_hash("2002omerhassan@omer"),
                "admin"
            )
        )

        conn.commit()

    except:
        pass

    conn.close()

create_admin()

# =========================
# Home page
# =========================
@app.route("/")
def home():

    conn = sqlite3.connect("news.db")
    c = conn.cursor()

    c.execute("SELECT * FROM news ORDER BY id DESC")
    news = c.fetchall()

    conn.close()

    return render_template(
        "home.html",
        news=news
    )

# =========================
# Register
# =========================
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("news.db")
        c = conn.cursor()

        try:

            c.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (
                    username,
                    generate_password_hash(password),
                    "user"
                )
            )

            conn.commit()

        except:
            return "❌ Username already exists"

        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")

# =========================
# Login
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("news.db")
        c = conn.cursor()

        c.execute(
            "SELECT username, password, role FROM users WHERE username=?",
            (username,)
        )

        user = c.fetchone()

        conn.close()

        if user and check_password_hash(user[1], password):

            session["user"] = user[0]
            session["role"] = user[2]

            return redirect(url_for("admin"))

    return render_template("login.html")

# =========================
# Logout
# =========================
@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))

# =========================
# Admin panel
# =========================
@app.route("/secret-admin")
def admin():

    if not session.get("user"):
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return "❌ No Access"

    conn = sqlite3.connect("news.db")
    c = conn.cursor()

    c.execute("SELECT * FROM news ORDER BY id DESC")
    news = c.fetchall()

    c.execute("SELECT COUNT(*) FROM news")
    news_count = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM users")
    users_count = c.fetchone()[0]

    conn.close()

    return render_template(
        "admin.html",
        news=news,
        news_count=news_count,
        users_count=users_count
    )

# =========================
# Add news
# =========================
@app.route("/add", methods=["POST"])
def add_news():

    if session.get("role") != "admin":
        return redirect(url_for("login"))

    title = request.form.get("title")
    content = request.form.get("content")

    image = request.files.get("image")

    image_path = ""

    if image and image.filename != "":

        filename = secure_filename(image.filename)

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        image.save(filepath)

        image_path = filepath

    conn = sqlite3.connect("news.db")
    c = conn.cursor()

    c.execute(
        """
        INSERT INTO news
        (title, content, image, views, likes)
        VALUES (?, ?, ?, ?, ?)
        """,
        (title, content, image_path, 0, 0)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("admin"))

# =========================
# Delete news
# =========================
@app.route("/delete/<int:news_id>")
def delete_news(news_id):

    if session.get("role") != "admin":
        return redirect(url_for("login"))

    conn = sqlite3.connect("news.db")
    c = conn.cursor()

    c.execute(
        "DELETE FROM news WHERE id=?",
        (news_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("admin"))

# =========================
# Edit news
# =========================
@app.route("/edit/<int:news_id>", methods=["GET", "POST"])
def edit_news(news_id):

    if session.get("role") != "admin":
        return redirect(url_for("login"))

    conn = sqlite3.connect("news.db")
    c = conn.cursor()

    if request.method == "POST":

        title = request.form.get("title")
        content = request.form.get("content")

        c.execute(
            "UPDATE news SET title=?, content=? WHERE id=?",
            (title, content, news_id)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("admin"))

    c.execute(
        "SELECT * FROM news WHERE id=?",
        (news_id,)
    )

    news = c.fetchone()

    conn.close()

    return render_template(
        "edit.html",
        news=news
    )

# =========================
# Add comment
# =========================
@app.route("/add-comment/<int:news_id>", methods=["POST"])
def add_comment(news_id):

    if not session.get("user"):
        return redirect(url_for("login"))

    comment = request.form.get("comment")
    username = session.get("user")

    conn = sqlite3.connect("news.db")
    c = conn.cursor()

    c.execute(
        "INSERT INTO comments (username, comment, news_id) VALUES (?, ?, ?)",
        (username, comment, news_id)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("single_news", news_id=news_id))

# =========================
# Like news
# =========================
@app.route("/like/<int:news_id>")
def like_news(news_id):

    conn = sqlite3.connect("news.db")
    c = conn.cursor()

    c.execute(
        "UPDATE news SET likes = likes + 1 WHERE id=?",
        (news_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("single_news", news_id=news_id))

# =========================
# Single news page
# =========================
@app.route("/news/<int:news_id>")
def single_news(news_id):

    conn = sqlite3.connect("news.db")
    c = conn.cursor()

    # زيادة المشاهدات
    c.execute(
        "UPDATE news SET views = views + 1 WHERE id=?",
        (news_id,)
    )

    conn.commit()

    # جلب الخبر
    c.execute(
        "SELECT * FROM news WHERE id=?",
        (news_id,)
    )

    news = c.fetchone()

    # جلب التعليقات
    c.execute(
        """
        SELECT username, comment
        FROM comments
        WHERE news_id=?
        ORDER BY id DESC
        """,
        (news_id,)
    )

    comments = c.fetchall()

    conn.close()

    return render_template(
        "single.html",
        news=news,
        comments=comments
    )

# =========================
# Run server
# =========================
if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
