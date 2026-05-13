# Featherfield Preserve

A small client–server web game: Flask serves HTML and JSON APIs; the browser runs the game with jQuery (AJAX) and Bootstrap. User accounts and game progress are stored in **SQLite** via **SQLAlchemy**.

## Requirements

- **Python 3.10+** (3.11 is fine)
- pip (usually bundled with Python)

## How to run (local)

1. **Clone the repository** (or download and unzip it), then open a terminal in the project folder:

   ```bash
   cd IoT
   ```

2. **Install dependencies** (once per machine, or after `requirements.txt` changes):

   ```bash
   python3 -m pip install -r requirements.txt
   ```

3. **Start the Flask server:**

   ```bash
   python3 app.py
   ```

4. **Open the app in your browser:**

   [http://127.0.0.1:5000](http://127.0.0.1:5000)

   Use **Register** to create an account, then play. Progress is saved to the server when you are logged in. **Community** shows a public summary for all registered rangers.

5. **Stop the server:** press `Ctrl+C` in the terminal.

## Optional: session secret (not required for local class work)

For a slightly safer local session cookie, you can set an environment variable before starting:

```bash
export FEATHERFIELD_SECRET_KEY="choose-a-long-random-string"
python3 app.py
```

On Windows (Command Prompt):

```cmd
set FEATHERFIELD_SECRET_KEY=choose-a-long-random-string
python3 app.py
```

## Database

The SQLite file is created automatically at **`instance/featherfield.db`** the first time the app runs. It is **not** committed to git (see `.gitignore`). Deleting that file resets all users and saves.

## Project layout

| Path | Role |
|------|------|
| `app.py` | Flask routes, login, APIs, community |
| `models.py` | SQLAlchemy models (`User`, `UserProgress`) |
| `requirements.txt` | Python dependencies |
| `templates/index.html` | Main game + in-game UI |
| `templates/login.html`, `templates/register.html` | Bootstrap auth pages |
| `NEW_flappy_happpy_game_v1.5.html` | Optional standalone copy of the game (open via Flask for full features; `file://` has no server) |

## Allowed stack (assignment)

HTML, CSS, JavaScript, **Bootstrap**, **jQuery**, **Flask** (+ Flask-Login, Flask-SQLAlchemy), **AJAX**, **SQLite** via **SQLAlchemy**.
