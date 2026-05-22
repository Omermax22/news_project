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
# إضافة خبر + رفع صورة
# =========================
@app.route('/add', methods=['GET', 'POST'])
def add_news():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image_file = request.files['image']

        image_path = None

        if image_file and image_file.filename != "":
            filename = secure_filename(image_file.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image_file.save(path)
            image_path = path

        conn = sqlite3.connect("news.db")
        c = conn.cursor()
        c.execute("INSERT INTO news (title, content, image) VALUES (?, ?, ?)",
                  (title, content, image_path))
        conn.commit()
        conn.close()

        return redirect(url_for('home'))

    return render_template("add.html")

# =========================
# حذف خبر
# =========================
@app.route('/delete/<int:id>')
def delete_news(id):
    conn = sqlite3.connect("news.db")
    c = conn.cursor()
    c.execute("DELETE FROM news WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

# =========================
# تعديل خبر
# =========================
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_news(id):
    conn = sqlite3.connect("news.db")
    c = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        c.execute("UPDATE news SET title=?, content=? WHERE id=?",
                  (title, content, id))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))

    c.execute("SELECT * FROM news WHERE id=?", (id,))
    news = c.fetchone()
    conn.close()

    return render_template("edit.html", news=news)

# =========================
# تشغيل السيرفر
# =========================
if __name__ == "__main__":
    app.run(debug=True)
