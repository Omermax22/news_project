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

# إنشاء المجلد إذا غير موجود
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
            title TEXT,
            content TEXT,
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
def add():

    if request.method == 'POST':

        title = request.form['title']
        content = request.form['content']

        image = request.files.get('image')

        filename = None

        if image and image.filename != "":

            filename = secure_filename(image.filename)

            image_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )

            image.save(image_path)

            filename = image_path

        conn = sqlite3.connect("news.db")
        c = conn.cursor()

        c.execute(
            "INSERT INTO news (title, content, image) VALUES (?, ?, ?)",
            (title, content, filename)
        )

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template("add.html")

# =========================
# صفحة الخبر
# =========================
@app.route('/news/<int:news_id>')
def single_news(news_id):

    conn = sqlite3.connect("news.db")
    c = conn.cursor()

    c.execute("SELECT * FROM news WHERE id=?", (news_id,))
    news = c.fetchone()

    conn.close()

    return render_template("single.html", news=news)

# =========================
# تشغيل التطبيق
# =========================
if __name__ == "__main__":
    app.run(debug=True)
