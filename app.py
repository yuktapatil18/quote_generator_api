from flask import Flask, render_template, request, redirect
import random
import sqlite3
from datetime import datetime
import requests

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect("quotes.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quote TEXT,
    author TEXT,
    mood TEXT,
    created_at TEXT
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS favorites(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quote TEXT,
    author TEXT,
    mood TEXT
    )""")

    conn.commit()
    conn.close()


init_db()

def get_api_quote():

    try:

        response = requests.get(
            "https://api.quotable.io/random",
            timeout=5
        )

        data = response.json()

        quote = data["content"]
        author = data["author"]

        return quote, author

    except:

        return None, None

@app.route("/")
def home():
    mood = request.args.get("mood", "focused")
    search = request.args.get("search", "")

    quotes = {
        "focused": [
            ("Focus on progress, not perfection.", "Unknown"),
            ("Discipline beats motivation.", "Unknown"),
            ("Stay consistent.", "Unknown")
        ],

        "happy": [
            ("Smile more, worry less.", "Unknown"),
            ("Happiness is contagious.", "Unknown"),
            ("Enjoy the little things.", "Unknown")
        ],

        "success": [
            ("Success is the sum of small efforts.", "Robert Collier"),
            ("Dream big. Start small.", "Unknown"),
            ("Success comes from consistency.", "Unknown")
        ],

        "study": [
            ("Study while others are sleeping.", "Unknown"),
            ("Learning never exhausts the mind.", "Leonardo da Vinci"),
            ("Every expert was once a beginner.", "Unknown")
        ]
    }

    if mood not in quotes:
        mood = "focused"

    quote, author = get_api_quote()
    if quote is None:

        quote,author = random.choice(quotes[mood])

    conn = sqlite3.connect("quotes.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO history
        (quote, author, mood, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            quote,
            author,
            mood,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )

    conn.commit()

    if search:

        cursor.execute("""
        SELECT quote, author
        FROM history
        WHERE quote LIKE ?
        ORDER BY id DESC
        """, ('%' + search + '%',))

    else:

        cursor.execute("""
        SELECT quote, author
        FROM history
        ORDER BY id DESC
        LIMIT 5
        """)

    history_rows = cursor.fetchall()

    cursor.execute("""
    SELECT quote, author
    FROM favorites
    ORDER BY id DESC
    LIMIT 5
    """)

    favorite_rows = cursor.fetchall()

    conn.close()

    history = [f'"{q}" - {a}' for q, a in history_rows]
    favorites = [f'"{q}" - {a}' for q, a in favorite_rows]

    display_mood = mood.capitalize()

    total_quotes = len(quotes[mood])

    return render_template(
        "index.html",
        quote=quote,
        author=author,
        mood=mood,
        display_mood=display_mood,
        total_quotes=total_quotes,
        history=history,
        favorites=favorites,
        search=search
    )


@app.route("/favorite")
def favorite():
    quote = request.args.get("quote")
    author = request.args.get("author")
    mood = request.args.get("mood")

    if not quote or not author:
        return redirect("/")

    conn = sqlite3.connect("quotes.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM favorites
        WHERE quote = ?
        """,
        (quote,)
    )

    existing = cursor.fetchone()

    if not existing:
        cursor.execute(
            """
            INSERT INTO favorites
            (quote, author, mood)
            VALUES (?, ?, ?)
            """,
            (quote, author, mood)
        )
        conn.commit()

    conn.close()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
