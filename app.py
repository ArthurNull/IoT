from pathlib import Path
import sqlite3

from flask import Flask, render_template

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-change-before-submission"
app.config["DATABASE"] = str(Path(__file__).with_name("featherfield.sqlite"))


def get_db_connection():
    connection = sqlite3.connect(app.config["DATABASE"])
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS leaderboard (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                level INTEGER NOT NULL DEFAULT 1,
                reputation INTEGER NOT NULL DEFAULT 0,
                birds_discovered INTEGER NOT NULL DEFAULT 0,
                coins INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        existing_rows = connection.execute("SELECT COUNT(*) FROM leaderboard").fetchone()[0]
        if existing_rows == 0:
            connection.executemany(
                """
                INSERT INTO leaderboard (username, level, reputation, birds_discovered, coins)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    ("Ranger Sandy", 5, 180, 12, 240),
                    ("Ranger Tim", 4, 145, 9, 190),
                    ("Ranger Ary", 3, 110, 7, 155),
                ],
            )
        connection.commit()


@app.route("/")
def index():
    init_db()
    return render_template("index.html")


@app.route("/leaderboard")
def leaderboard():
    init_db()
    with get_db_connection() as connection:
        rows = connection.execute(
            """
            SELECT username, level, reputation, birds_discovered, coins
            FROM leaderboard
            ORDER BY reputation DESC, level DESC, birds_discovered DESC
            """
        ).fetchall()
    return render_template("leaderboard.html", players=rows)


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
