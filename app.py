import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename

app = Flask(__name__)

# =========================
# Secret Key
# =========================
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

    c.execute("""
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        image TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# =========================
# Home page (visitors)
# =========================
@app.route("/")
def home():
    conn = sqlite3.connect("news.db")
    c = conn.cursor()

    c.execute("SELECT * FROM news ORDER BY id DESC")
    news = c.fetchall()

    conn.close()
    return render_template("home.html", news=news)

# =========================
# Login page
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "omer Hassan" and password == "2002omerhassan@omer":
            session["admin"] = True
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
# Admin panel (protected)
# =========================
@app.route("/secret-admin")
def admin():

    if not session.get("admin"):
        return redirect(url_for("login"))

    conn = sqlite3.connect("news.db")
    c = conn.cursor()

    c.execute("SELECT * FROM news ORDER BY id DESC")
    news = c.fetchall()

    conn.close()
    return render_template("admin.html", news=news)

# =========================
# Add news
# =========================
@app.route("/add", methods=["POST"])
def add_news():

    if not session.get("admin"):
        return redirect(url_for("login"))

    title = request.form.get("title")
    content = request.form.get("content")
    image = request.files.get("image")

    image_path = ""

    if image and image.filename != "":
        filename = secure_filename(image.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        image.save(filepath)
        image_path = filepath

    conn = sqlite3.connect("news.db")
    c = conn.cursor()

    c.execute(
        "INSERT INTO news (title, content, image) VALUES (?, ?, ?)",
        (title, content, image_path)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("admin"))

# =========================
# Delete news
# =========================
@app.route("/delete/<int:news_id>")
def delete_news(news_id):

    if not session.get("admin"):
        return redirect(url_for("login"))

    conn = sqlite3.connect("news.db")
    c = conn.cursor()

    c.execute("DELETE FROM news WHERE id=?", (news_id,))

    conn.commit()
    conn.close()

    return redirect(url_for("admin"))

# =========================
# Edit news
# =========================
@app.route("/edit/<int:news_id>", methods=["GET", "POST"])
def edit_news(news_id):

    if not session.get("admin"):
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

    c.execute("SELECT * FROM news WHERE id=?", (news_id,))
    news = c.fetchone()

    conn.close()

    return render_template("edit.html", news=news)

# =========================
# Single news page
# =========================
@app.route("/news/<int:news_id>")
def single_news(news_id):

    conn = sqlite3.connect("news.db")
    c = conn.cursor()

    c.execute("SELECT * FROM news WHERE id=?", (news_id,))
    news = c.fetchone()

    conn.close()

    return render_template("single.html", news=news)

# =========================
# Run server
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
