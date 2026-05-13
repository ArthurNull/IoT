"""Featherfield Preserve — Flask server (SQLite + SQLAlchemy)."""

from __future__ import annotations

import json
import os
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash

from models import User, UserProgress, db

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FEATHERFIELD_SECRET_KEY", "dev-key-change-for-production")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + str(INSTANCE_DIR / "featherfield.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "login_page"
login_manager.init_app(app)


@login_manager.unauthorized_handler
def unauthorized():
    if request.path.startswith("/api/"):
        return jsonify({"ok": False, "error": "Authentication required."}), 401
    return redirect(url_for("login_page", next=request.url))


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    if not user_id or not user_id.isdigit():
        return None
    return db.session.get(User, int(user_id))


def xp_required_for_level(level: int) -> int:
    return int(75 * (level**1.45))


def level_from_total_xp(total_xp: int) -> int:
    level = 1
    remaining = max(0, int(total_xp))
    while remaining >= xp_required_for_level(level):
        remaining -= xp_required_for_level(level)
        level += 1
    return level


def species_discovered_count(save: dict) -> int:
    coll = save.get("collection") or {}
    return sum(1 for entry in coll.values() if isinstance(entry, dict) and entry.get("discovered"))


def summarize_save_for_community(username: str, save: dict) -> dict:
    xp = int(save.get("xp") or 0)
    return {
        "username": username,
        "level": level_from_total_xp(xp),
        "xp": xp,
        "reputation": int(save.get("reputation") or 0),
        "species_discovered": species_discovered_count(save),
        "total_safe_handles": int(save.get("totalSafeHandles") or 0),
        "total_observations": int(save.get("totalObservations") or 0),
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET"])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    return render_template("login.html")


@app.route("/register", methods=["GET"])
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    return render_template("register.html")


@app.route("/api/session", methods=["GET"])
def api_session():
    if not current_user.is_authenticated:
        return jsonify({"logged_in": False, "username": None})
    return jsonify({"logged_in": True, "username": current_user.username})


@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if len(username) < 3 or len(username) > 80:
        return jsonify({"ok": False, "error": "Username must be 3–80 characters."}), 400
    if len(password) < 6:
        return jsonify({"ok": False, "error": "Password must be at least 6 characters."}), 400

    if User.query.filter(func.lower(User.username) == func.lower(username)).first():
        return jsonify({"ok": False, "error": "That username is already taken."}), 409

    user = User(
        username=username,
        password_hash=generate_password_hash(password),
    )
    db.session.add(user)
    db.session.flush()
    db.session.add(UserProgress(user_id=user.id, save_json="{}"))
    db.session.commit()

    login_user(user)
    return jsonify({"ok": True, "username": user.username})


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    user = User.query.filter(func.lower(User.username) == func.lower(username)).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"ok": False, "error": "Invalid username or password."}), 401

    login_user(user, remember=True)
    return jsonify({"ok": True, "username": user.username})


@app.route("/api/logout", methods=["POST"])
@login_required
def api_logout():
    logout_user()
    return jsonify({"ok": True})


@app.route("/api/save", methods=["GET"])
@login_required
def api_get_save():
    progress = UserProgress.query.filter_by(user_id=current_user.id).first()
    if not progress:
        progress = UserProgress(user_id=current_user.id, save_json="{}")
        db.session.add(progress)
        db.session.commit()

    try:
        payload = json.loads(progress.save_json or "{}")
    except json.JSONDecodeError:
        payload = {}

    return jsonify({"ok": True, "save": payload})


@app.route("/api/save", methods=["PUT"])
@login_required
def api_put_save():
    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return jsonify({"ok": False, "error": "Expected JSON object."}), 400

    progress = UserProgress.query.filter_by(user_id=current_user.id).first()
    if not progress:
        progress = UserProgress(user_id=current_user.id, save_json="{}")
        db.session.add(progress)

    progress.save_json = json.dumps(data)
    db.session.commit()
    return jsonify({"ok": True})


@app.route("/api/community/rangers", methods=["GET"])
def api_community_rangers():
    rows = (
        db.session.query(User, UserProgress)
        .outerjoin(UserProgress, UserProgress.user_id == User.id)
        .order_by(User.username.asc())
        .all()
    )
    out = []
    for user, progress in rows:
        raw = progress.save_json if progress else "{}"
        try:
            save = json.loads(raw or "{}")
        except json.JSONDecodeError:
            save = {}
        if not isinstance(save, dict):
            save = {}
        out.append(summarize_save_for_community(user.username, save))

    out.sort(key=lambda r: (-r["level"], -r["xp"], r["username"].lower()))
    return jsonify({"ok": True, "rangers": out})


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
