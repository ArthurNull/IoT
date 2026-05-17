# Featherfield Preserve

A Flask-wrapped version of the Featherfield Preserve browser game.

This conversion keeps the game frontend split into normal Flask folders:

```text
app.py
requirements.txt
templates/index.html
static/css/style.css
static/js/game.js
tests/test_routes.py
```

## How to run

```bash
pip install -r requirements.txt
python app.py
```

Open this address in your browser:

```text
http://127.0.0.1:5000
```

## How to run tests

```bash
pytest
```

## Notes

This version serves the latest single-file game through Flask. The current login screen is still frontend-only. Real database-backed signup, login/logout, saved progress, and a leaderboard should be added next for the project requirements.
