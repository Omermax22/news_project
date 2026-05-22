import os
import sqlite3
from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

@app.route('/')
def home():
    conn = sqlite3.connect("news.db")
    c = conn.cursor()
    c.execute("SELECT * FROM news ORDER BY id DESC")
    news = c.fetchall()
    conn.close()
    return render_template("home.html", news=news)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        image = request.files['image']
        filename = None

        if image and image.filename != "":
            filename = secure_filename(image.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image.save(path)
            filename = "static/uploads/" + filename

        conn = sqlite3.connect("news.db")
        c = conn.cursor()
        c.execute("INSERT INTO news (title, content, image) VALUES (?, ?, ?)",
                  (title, content, filename))
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template("add.html")

if __name__ == "__main__":
    app.run(debug=True)
