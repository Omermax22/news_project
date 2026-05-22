import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

# =========================
# إعداد رفع الصور
# =========================
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =========================
# قاعدة البيانات
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
# الصفحة الرئيسية
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
# إضافة خبر
# =========================
@app.route("/add", methods=["POST"])
def add_news():

    title = request.form.get("title")
    content = request.form.get("content")

    image = request.files.get("image")

    image_path = ""

    # حفظ الصورة
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
        "INSERT INTO news (title, content, image) VALUES (?, ?, ?)",
        (title, content, image_path)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("home"))

# =========================
# تشغيل السيرفر
# =========================
if __name__ == "__main__":
    app.run(debug=True)
