import os
import sqlite3
from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename

app = Flask(__name__)

# =========================
# إعداد رفع الصور
# =========================
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# تأكد من وجود المجلد
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
            image TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

# =========================
# الصفحة الرئيسية
# =========================
@app.route('/')
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
@app.route('/add', methods=['GET', 'POST'])
def add_news():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        image_file = request.files['image']
        filename = None

        if image_file and image_file.filename != "":
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image_file.save(image_path)
            filename = image_path

        conn = sqlite3.connect("news.db")
        c = conn.cursor()
        c.execute("INSERT INTO news (title, content, image) VALUES (?, ?, ?)",
                  (title, content, filename))
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template("add.html")

# =========================
# تشغيل التطبيق
# =========================
if __name__ == "__main__":
    app.run(debug=True)
