from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("news.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            image TEXT
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

@app.route('/add', methods=["GET", "POST"])
def add_news():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        image = request.form["image"]

        conn = sqlite3.connect("news.db")
        c = conn.cursor()
        c.execute("INSERT INTO news (title, content, image) VALUES (?, ?, ?)",
                  (title, content, image))
        conn.commit()
        conn.close()
        return redirect("/")

    return render_template("add.html")

@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect("news.db")
    c = conn.cursor()
    c.execute("DELETE FROM news WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route('/edit/<int:id>', methods=["GET","POST"])
def edit(id):
    conn = sqlite3.connect("news.db")
    c = conn.cursor()

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        image = request.form["image"]

        c.execute("UPDATE news SET title=?, content=?, image=? WHERE id=?",
                  (title, content, image, id))
        conn.commit()
        conn.close()
        return redirect("/")

    c.execute("SELECT * FROM news WHERE id=?", (id,))
    news = c.fetchone()
    conn.close()

    return render_template("edit.html", news=news)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
