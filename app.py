import os
import re
import sqlite3
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error as MySQLError

def create_app() -> Flask:
    load_dotenv()
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY") or os.urandom(24)
    app.config.update(
        DB_BACKEND=os.getenv("DB_BACKEND", "sqlite").lower(),
        MYSQL_HOST=os.getenv("MYSQL_HOST", "127.0.0.1"),
        MYSQL_PORT=int(os.getenv("MYSQL_PORT", "3306")),
        MYSQL_USER=os.getenv("MYSQL_USER", "root"),
        MYSQL_PASSWORD=os.getenv("MYSQL_PASSWORD", ""),
        MYSQL_DATABASE=os.getenv("MYSQL_DATABASE", "test_login"),
)
    # Ensure instance folder exists for SQLite file storage
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except Exception:
        pass
    initialize_database(app)

    @app.get("/")
    def index():
        if session.get("user_id"):
            return redirect(url_for("dashboard"))
        return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = (request.form.get("email") or "").strip().lower()
            password = request.form.get("password") or ""
            if not email or not password:
                flash("Please enter both email and password.", "error")
                return render_template("login.html")
            user = fetch_user_by_email(app, email)
            if not user or not check_password_hash(user["password_hash"], password):
                flash("Invalid email or password.", "error")
                return render_template("login.html")
            session["user_id"] = user["id"]
            session["user_email"] = user["email"]
            session["user_name"] = user.get("full_name")
            flash("Logged in successfully.", "success")
            ensure_demo_deliveries_for_user(app, user["id"])  # seed when empty (dev/demo)
            return redirect(url_for("dashboard"))
        return render_template("login.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            full_name = (request.form.get("full_name") or "").strip()
            email = (request.form.get("email") or "").strip().lower()
            password = request.form.get("password") or ""
            confirm_password = request.form.get("confirm_password") or ""
            error_messages = validate_registration_input(full_name, email, password, confirm_password)
            if error_messages:
                for message in error_messages:
                    flash(message, "error")
                return render_template("register.html", full_name=full_name, email=email)
            existing = fetch_user_by_email(app, email)
            if existing:
                flash("An account with this email already exists.", "error")
                return render_template("register.html", full_name=full_name, email=email)
            success, msg = create_user(app, full_name, email, password)
            if not success:
                flash(msg or "Failed to create user.", "error")
                return render_template("register.html", full_name=full_name, email=email)
            flash("Account created. You can now log in.", "success")
            return redirect(url_for("login"))
        return render_template("register.html")

    @app.get("/hello")
    def hello():
        # Legacy route: redirect to dashboard
        return redirect(url_for("dashboard"))

    @app.get("/dashboard")
    def dashboard():
        if not session.get("user_id"):
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        user_id = session["user_id"]
        counts = fetch_delivery_counts(app, user_id)
        deliveries_for_map = fetch_deliveries_for_map(app, user_id)
        maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
        return render_template(
            "dashboard.html",
            pending_count=counts.get("pending", 0),
            delivered_count=counts.get("delivered", 0),
            deliveries=deliveries_for_map,
            maps_api_key=maps_api_key,
        )

    @app.get("/deliveries")
    def deliveries_page():
        if not session.get("user_id"):
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        user_id = session["user_id"]
        deliveries = fetch_deliveries_list(app, user_id)
        return render_template("deliveries.html", deliveries=deliveries)

    @app.get("/routes")
    def routes_page():
        if not session.get("user_id"):
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        flash("Routes module coming soon.", "success")
        return redirect(url_for("dashboard"))

    @app.get("/settings")
    def settings_page():
        if not session.get("user_id"):
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        flash("Settings module coming soon.", "success")
        return redirect(url_for("dashboard"))

    @app.route("/deliveries/add", methods=["POST"])
    def deliveries_add():
        if not session.get("user_id"):
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        user_id = session["user_id"]
        tracking_number = (request.form.get("tracking_number") or "").strip()
        amount_str = (request.form.get("amount_due") or "").strip()
        try:
            amount_due = int(amount_str)
        except ValueError:
            amount_due = -1
        if not tracking_number or amount_due < 0:
            flash("Please provide a valid tracking number and amount.", "error")
            return redirect(url_for("deliveries_page"))
        ok, msg = add_delivery(app, user_id, tracking_number, amount_due)
        if not ok:
            flash(msg or "Could not add delivery.", "error")
        else:
            flash("Delivery added.", "success")
        return redirect(url_for("deliveries_page"))

    @app.post("/deliveries/status")
    def deliveries_status():
        if not session.get("user_id"):
            return redirect(url_for("login"))
        user_id = session["user_id"]
        delivery_id = int(request.form.get("delivery_id") or 0)
        status = (request.form.get("status") or "").strip()
        ok, msg = update_delivery_status(app, user_id, delivery_id, status)
        if not ok:
            flash(msg or "Could not update status.", "error")
        return redirect(url_for("deliveries_page"))

    @app.post("/deliveries/delete")
    def deliveries_delete():
        if not session.get("user_id"):
            return redirect(url_for("login"))
        user_id = session["user_id"]
        delivery_id = int(request.form.get("delivery_id") or 0)
        ok, msg = soft_delete_delivery(app, user_id, delivery_id)
        if not ok:
            flash(msg or "Could not delete delivery.", "error")
        else:
            flash("Delivery deleted. You can undo it.", "success")
        return redirect(url_for("deliveries_page"))

    @app.post("/deliveries/undo-delete")
    def deliveries_undo_delete():
        if not session.get("user_id"):
            return redirect(url_for("login"))
        user_id = session["user_id"]
        delivery_id = int(request.form.get("delivery_id") or 0)
        ok, msg = undo_delete_delivery(app, user_id, delivery_id)
        if not ok:
            flash(msg or "Could not undo delete.", "error")
        else:
            flash("Deletion reverted.", "success")
        return redirect(url_for("deliveries_page"))

    @app.get("/logout")
    def logout():
        session.clear()
        flash("You have been logged out.", "success")
        return redirect(url_for("login"))

    @app.route("/forgot", methods=["GET", "POST"])
    def forgot_password():
        if request.method == "POST":
            email = (request.form.get("email") or "").strip().lower()
            # Always show generic response to avoid user enumeration
            user = fetch_user_by_email(app, email) if email else None
            if user:
                token, expires_at = create_password_reset_token(app, user["id"])
                reset_url = url_for("reset_password", token=token, _external=True)
                print(f"[RESET] Password reset link for {email}: {reset_url} (expires {expires_at.isoformat()})")
            flash("If that email exists, you'll receive reset instructions.", "success")
            return redirect(url_for("login"))
        return render_template("forgot.html")

    @app.route("/reset/<token>", methods=["GET", "POST"])
    def reset_password(token: str):
        record = fetch_password_reset_by_token(app, token)
        if not record or record.get("used_at") or record["expires_at"] < datetime.now(timezone.utc):
            flash("Invalid or expired reset link.", "error")
            return redirect(url_for("forgot_password"))
        if request.method == "POST":
            password = request.form.get("password") or ""
            confirm_password = request.form.get("confirm_password") or ""
            errors = validate_registration_input("", "test@example.com", password, confirm_password)
            # We ignore email/full_name errors above by passing dummies; filter to password-related only
            errors = [e for e in errors if "Password" in e]
            if errors:
                for msg in errors:
                    flash(msg, "error")
                return render_template("reset_password.html", token=token)
            ok, msg = update_user_password(app, record["user_id"], password)
            if not ok:
                flash(msg or "Could not update password.", "error")
                return render_template("reset_password.html", token=token)
            mark_password_reset_used(app, token)
            flash("Your password has been reset. You can log in now.", "success")
            return redirect(url_for("login"))
        return render_template("reset_password.html", token=token)

    return app

def validate_registration_input(full_name: str, email: str, password: str, confirm_password: str) -> list[str]:
    errors: list[str] = []
    if not email:
        errors.append("Email is required.")
    elif not is_valid_email(email):
        errors.append("Please enter a valid email address.")
    if not password:
        errors.append("Password is required.")
    elif len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if confirm_password != password:
        errors.append("Passwords do not match.")
    if full_name and len(full_name) > 255:
        errors.append("Name is too long.")
    return errors

def is_valid_email(email: str) -> bool:
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return re.match(pattern, email) is not None

def get_db_connection(app: Flask, include_database: bool = True):
    """Return a DB connection for the configured backend."""
    backend = app.config.get("DB_BACKEND", "mysql")
    if backend == "sqlite":
        # Allow overriding SQLite storage path (useful on hosts like Koyeb)
        db_path = os.getenv("SQLITE_PATH") or os.path.join(app.instance_path, "app.db")
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    # default: mysql
    connection_kwargs = {
        "host": app.config["MYSQL_HOST"],
        "port": app.config["MYSQL_PORT"],
        "user": app.config["MYSQL_USER"],
        "password": app.config["MYSQL_PASSWORD"],
        "autocommit": True,
    }
    if include_database:
        connection_kwargs["database"] = app.config["MYSQL_DATABASE"]
    return mysql.connector.connect(**connection_kwargs)

def initialize_database(app: Flask) -> None:
    backend = app.config.get("DB_BACKEND", "mysql")
    if backend == "sqlite":
        try:
            with get_db_connection(app) as conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      email TEXT NOT NULL UNIQUE,
                      full_name TEXT NULL,
                      password_hash TEXT NOT NULL,
                      created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS deliveries (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER NOT NULL,
                      address TEXT NULL,
                      latitude REAL NULL,
                      longitude REAL NULL,
                      status TEXT NOT NULL,
                      tracking_number TEXT NULL,
                      amount_due INT NOT NULL DEFAULT 0,
                      created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                      delivered_at TIMESTAMP NULL,
                      deleted_at TIMESTAMP NULL,
                      FOREIGN KEY(user_id) REFERENCES users(id)
                    )
                    """
                )
                # SQLite simple migrations to add columns if missing
                try:
                    cur.execute("ALTER TABLE deliveries ADD COLUMN tracking_number TEXT")
                except sqlite3.Error:
                    pass
                try:
                    cur.execute("ALTER TABLE deliveries ADD COLUMN amount_due INT NOT NULL DEFAULT 0")
                except sqlite3.Error:
                    pass
                try:
                    cur.execute("ALTER TABLE deliveries ADD COLUMN deleted_at TIMESTAMP NULL")
                except sqlite3.Error:
                    pass
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS password_resets (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER NOT NULL,
                      token TEXT NOT NULL UNIQUE,
                      expires_at TIMESTAMP NOT NULL,
                      used_at TIMESTAMP NULL,
                      created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                      FOREIGN KEY(user_id) REFERENCES users(id)
                    )
                    """
                )
                conn.commit()
        except sqlite3.Error as exc:
            print(f"[INIT] Error initializing SQLite DB: {exc}")
        return

        # mysql path
    database_name = app.config["MYSQL_DATABASE"]
    try:
        with get_db_connection(app, include_database=False) as server_conn:
            with server_conn.cursor() as cur:
                cur.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{database_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
    except MySQLError as exc:
        print(f"[INIT] Warning: Could not ensure database exists: {exc}")
    try:
        with get_db_connection(app, include_database=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                      id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                      email VARCHAR(255) NOT NULL UNIQUE,
                      full_name VARCHAR(255) NULL,
                      password_hash VARCHAR(255) NOT NULL,
                      created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS deliveries (
                      id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                      user_id INT NOT NULL,
                      address VARCHAR(512) NULL,
                      latitude DOUBLE NULL,
                      longitude DOUBLE NULL,
                      status VARCHAR(32) NOT NULL,
                      tracking_number VARCHAR(64) NULL,
                      amount_due INT NOT NULL DEFAULT 0,
                      created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                      delivered_at TIMESTAMP NULL,
                      deleted_at TIMESTAMP NULL,
                      CONSTRAINT fk_deliveries_user FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                    """
                )
                # MySQL migrations to add columns if missing
                try:
                    cur.execute("ALTER TABLE deliveries ADD COLUMN tracking_number VARCHAR(64) NULL")
                except MySQLError:
                    pass
                try:
                    cur.execute("ALTER TABLE deliveries ADD COLUMN amount_due INT NOT NULL DEFAULT 0")
                except MySQLError:
                    pass
                try:
                    cur.execute("ALTER TABLE deliveries ADD COLUMN deleted_at TIMESTAMP NULL")
                except MySQLError:
                    pass
                try:
                    cur.execute("ALTER TABLE deliveries MODIFY COLUMN status VARCHAR(32) NOT NULL")
                except MySQLError:
                    pass
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS password_resets (
                      id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                      user_id INT NOT NULL,
                      token VARCHAR(255) NOT NULL UNIQUE,
                      expires_at TIMESTAMP NOT NULL,
                      used_at TIMESTAMP NULL,
                      created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                      CONSTRAINT fk_resets_user FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                    """
                )
    except MySQLError as exc:
        print(f"[INIT] Error ensuring users table exists: {exc}")

def fetch_user_by_email(app: Flask, email: str) -> Optional[dict]:
    backend = app.config.get("DB_BACKEND", "mysql")
    try:
        if backend == "sqlite":
            with get_db_connection(app) as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT id, email, full_name, password_hash FROM users WHERE email = ?",
                    (email,),
                )
                row = cur.fetchone()
                if not row:
                    return None
                # sqlite3.Row supports mapping interface
                return {k: row[k] for k in ["id", "email", "full_name", "password_hash"]}
        # mysql
        with get_db_connection(app) as conn:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(
                    "SELECT id, email, full_name, password_hash FROM users WHERE email = %s",
                    (email,),
                )
                return cur.fetchone()
    except (MySQLError, sqlite3.Error) as exc:
        print(f"[DB] Error fetching user by email: {exc}")
        return None

def create_user(app: Flask, full_name: str, email: str, password: str) -> Tuple[bool, Optional[str]]:
    backend = app.config.get("DB_BACKEND", "mysql")
    try:
        password_hash = generate_password_hash(password)
        if backend == "sqlite":
            with get_db_connection(app) as conn:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO users (email, full_name, password_hash) VALUES (?, ?, ?)",
                    (email, full_name or None, password_hash),
                )
                conn.commit()
            return True, None
        # mysql
        with get_db_connection(app) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (email, full_name, password_hash) VALUES (%s, %s, %s)",
                    (email, full_name or None, password_hash),
                )
        return True, None
    except (MySQLError, sqlite3.Error) as exc:
        return False, str(exc)

def fetch_delivery_counts(app: Flask, user_id: int) -> dict:
    backend = app.config.get("DB_BACKEND", "mysql")
    try:
        if backend == "sqlite":
            with get_db_connection(app) as conn:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM deliveries WHERE user_id = ? AND status = 'pending'", (user_id,))
                pending = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM deliveries WHERE user_id = ? AND status = 'delivered'", (user_id,))
                delivered = cur.fetchone()[0]
                return {"pending": pending, "delivered": delivered}
        with get_db_connection(app) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM deliveries WHERE user_id = %s AND status = 'pending'", (user_id,))
                pending = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM deliveries WHERE user_id = %s AND status = 'delivered'", (user_id,))
                delivered = cur.fetchone()[0]
                return {"pending": pending, "delivered": delivered}
    except (MySQLError, sqlite3.Error) as exc:
        print(f"[DB] Error fetching delivery counts: {exc}")
        return {"pending": 0, "delivered": 0}

def fetch_deliveries_for_map(app: Flask, user_id: int) -> list[dict]:
    backend = app.config.get("DB_BACKEND", "mysql")
    try:
        if backend == "sqlite":
            with get_db_connection(app) as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT id, address, latitude, longitude, status FROM deliveries WHERE user_id = ? AND latitude IS NOT NULL AND longitude IS NOT NULL",
                    (user_id,),
                )
                rows = cur.fetchall()
                return [
                    {"id": r[0], "address": r[1], "latitude": r[2], "longitude": r[3], "status": r[4]}
                    for r in rows
                ]
        with get_db_connection(app) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, address, latitude, longitude, status FROM deliveries WHERE user_id = %s AND latitude IS NOT NULL AND longitude IS NOT NULL",
                    (user_id,),
                )
                rows = cur.fetchall()
                return [
                    {"id": r[0], "address": r[1], "latitude": r[2], "longitude": r[3], "status": r[4]}
                    for r in rows
                ]
    except (MySQLError, sqlite3.Error) as exc:
        print(f"[DB] Error fetching deliveries for map: {exc}")
        return []

def ensure_demo_deliveries_for_user(app: Flask, user_id: int) -> None:
    """Seed a few demo deliveries for new users if none exist (dev/demo convenience)."""
    backend = app.config.get("DB_BACKEND", "mysql")
    try:
        if backend == "sqlite":
            with get_db_connection(app) as conn:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM deliveries WHERE user_id = ?", (user_id,))
                if cur.fetchone()[0] > 0:
                    return
                data = [
                    (user_id, "123 Market St", 37.7749, -122.4194, "pending"),
                    (user_id, "500 Howard St", 37.7890, -122.3912, "pending"),
                    (user_id, "1 Ferry Building", 37.7955, -122.3937, "delivered"),
                ]
                cur.executemany(
                    "INSERT INTO deliveries (user_id, address, latitude, longitude, status) VALUES (?, ?, ?, ?, ?)",
                    data,
                )
                conn.commit()
            return
        with get_db_connection(app) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM deliveries WHERE user_id = %s", (user_id,))
                if cur.fetchone()[0] > 0:
                    return
                data = [
                    (user_id, "123 Market St", 37.7749, -122.4194, "pending"),
                    (user_id, "500 Howard St", 37.7890, -122.3912, "pending"),
                    (user_id, "1 Ferry Building", 37.7955, -122.3937, "delivered"),
                ]
                cur.executemany(
                    "INSERT INTO deliveries (user_id, address, latitude, longitude, status) VALUES (%s, %s, %s, %s, %s)",
                    data,
                )
    except (MySQLError, sqlite3.Error) as exc:
        print(f"[DB] Error seeding demo deliveries: {exc}")

def fetch_deliveries_list(app: Flask, user_id: int) -> list[dict]:
    backend = app.config.get("DB_BACKEND", "mysql")
    try:
        if backend == "sqlite":
            with get_db_connection(app) as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT id, tracking_number, amount_due, status, address, created_at FROM deliveries WHERE user_id = ? AND deleted_at IS NULL ORDER BY created_at DESC",
                    (user_id,),
                )
                rows = cur.fetchall()
                return [
                    {
                        "id": r[0],
                        "tracking_number": r[1],
                        "amount_due": r[2],
                        "status": r[3],
                        "address": r[4],
                        "created_at": r[5],
                    }
                    for r in rows
                ]
        with get_db_connection(app) as conn:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(
                    "SELECT id, tracking_number, amount_due, status, address, created_at FROM deliveries WHERE user_id = %s AND deleted_at IS NULL ORDER BY created_at DESC",
                    (user_id,),
                )
                return cur.fetchall()
    except (MySQLError, sqlite3.Error) as exc:
        print(f"[DB] Error fetching deliveries list: {exc}")
        return []

def add_delivery(app: Flask, user_id: int, tracking_number: str, amount_due: int) -> tuple[bool, str | None]:
    backend = app.config.get("DB_BACKEND", "mysql")
    try:
        if backend == "sqlite":
            with get_db_connection(app) as conn:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO deliveries (user_id, tracking_number, amount_due, status) VALUES (?, ?, ?, 'pending')",
                    (user_id, tracking_number, amount_due),
                )
                conn.commit()
            return True, None
        with get_db_connection(app) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO deliveries (user_id, tracking_number, amount_due, status) VALUES (%s, %s, %s, 'pending')",
                    (user_id, tracking_number, amount_due),
                )
        return True, None
    except (MySQLError, sqlite3.Error) as exc:
        return False, str(exc)

def update_delivery_status(app: Flask, user_id: int, delivery_id: int, status: str) -> tuple[bool, str | None]:
    if status not in ("pending", "delivered", "not_located"):
        return False, "Invalid status"
    backend = app.config.get("DB_BACKEND", "mysql")
    try:
        if backend == "sqlite":
            with get_db_connection(app) as conn:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE deliveries SET status = ? WHERE id = ? AND user_id = ?",
                    (status, delivery_id, user_id),
                )
                conn.commit()
            return True, None
        with get_db_connection(app) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE deliveries SET status = %s WHERE id = %s AND user_id = %s",
                    (status, delivery_id, user_id),
                )
        return True, None
    except (MySQLError, sqlite3.Error) as exc:
        return False, str(exc)

def soft_delete_delivery(app: Flask, user_id: int, delivery_id: int) -> tuple[bool, str | None]:
    backend = app.config.get("DB_BACKEND", "mysql")
    try:
        now = datetime.now(timezone.utc).isoformat()
        if backend == "sqlite":
            with get_db_connection(app) as conn:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE deliveries SET deleted_at = ? WHERE id = ? AND user_id = ?",
                    (now, delivery_id, user_id),
                )
                conn.commit()
            return True, None
        with get_db_connection(app) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE deliveries SET deleted_at = %s WHERE id = %s AND user_id = %s",
                    (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), delivery_id, user_id),
                )
        return True, None
    except (MySQLError, sqlite3.Error) as exc:
        return False, str(exc)

def undo_delete_delivery(app: Flask, user_id: int, delivery_id: int) -> tuple[bool, str | None]:
    backend = app.config.get("DB_BACKEND", "mysql")
    try:
        if backend == "sqlite":
            with get_db_connection(app) as conn:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE deliveries SET deleted_at = NULL WHERE id = ? AND user_id = ?",
                    (delivery_id, user_id),
                )
                conn.commit()
            return True, None
        with get_db_connection(app) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE deliveries SET deleted_at = NULL WHERE id = %s AND user_id = %s",
                    (delivery_id, user_id),
                )
        return True, None
    except (MySQLError, sqlite3.Error) as exc:
        return False, str(exc)

def update_user_password(app: Flask, user_id: int, new_password: str) -> Tuple[bool, Optional[str]]:
    backend = app.config.get("DB_BACKEND", "mysql")
    try:
        password_hash = generate_password_hash(new_password)
        if backend == "sqlite":
            with get_db_connection(app) as conn:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE users SET password_hash = ? WHERE id = ?",
                    (password_hash, user_id),
                )
                conn.commit()
            return True, None
        with get_db_connection(app) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET password_hash = %s WHERE id = %s",
                    (password_hash, user_id),
                )
        return True, None
    except (MySQLError, sqlite3.Error) as exc:
        return False, str(exc)

def create_password_reset_token(app: Flask, user_id: int) -> Tuple[str, datetime]:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    backend = app.config.get("DB_BACKEND", "mysql")
    if backend == "sqlite":
        with get_db_connection(app) as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO password_resets (user_id, token, expires_at) VALUES (?, ?, ?)",
                (user_id, token, expires_at.isoformat()),
            )
            conn.commit()
        return token, expires_at
    with get_db_connection(app) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO password_resets (user_id, token, expires_at) VALUES (%s, %s, %s)",
                (user_id, token, expires_at.strftime("%Y-%m-%d %H:%M:%S")),
            )
    return token, expires_at

def fetch_password_reset_by_token(app: Flask, token: str) -> Optional[dict]:
    backend = app.config.get("DB_BACKEND", "mysql")
    try:
        if backend == "sqlite":
            with get_db_connection(app) as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT id, user_id, token, expires_at, used_at, created_at FROM password_resets WHERE token = ?",
                    (token,),
                )
                row = cur.fetchone()
                if not row:
                    return None
                result = {k: row[k] for k in ["id", "user_id", "token", "expires_at", "used_at", "created_at"]}
                # Normalize timestamps to aware datetime
                result["expires_at"] = _parse_sqlite_timestamp(result["expires_at"])  # type: ignore
                result["used_at"] = _parse_sqlite_timestamp(result["used_at"]) if result["used_at"] else None  # type: ignore
                return result
        with get_db_connection(app) as conn:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(
                    "SELECT id, user_id, token, expires_at, used_at, created_at FROM password_resets WHERE token = %s",
                    (token,),
                )
                row = cur.fetchone()
                if not row:
                    return None
                # MySQL returns naive datetime; make it aware in UTC
                row["expires_at"] = row["expires_at"].replace(tzinfo=timezone.utc)
                row["used_at"] = row["used_at"].replace(tzinfo=timezone.utc) if row["used_at"] else None
                return row
    except (MySQLError, sqlite3.Error) as exc:
        print(f"[DB] Error fetching reset token: {exc}")
        return None

def mark_password_reset_used(app: Flask, token: str) -> None:
    backend = app.config.get("DB_BACKEND", "mysql")
    used_at_str = datetime.now(timezone.utc)
    if backend == "sqlite":
        with get_db_connection(app) as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE password_resets SET used_at = ? WHERE token = ?",
                (used_at_str.isoformat(), token),
            )
            conn.commit()
        return
    with get_db_connection(app) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE password_resets SET used_at = %s WHERE token = %s",
                (used_at_str.strftime("%Y-%m-%d %H:%M:%S"), token),
            )

def _parse_sqlite_timestamp(value: str) -> datetime:
    try:
        # isoformat stored
        return datetime.fromisoformat(value).astimezone(timezone.utc)
    except Exception:
        # fallback common sqlite formats
        try:
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        except Exception:
            return datetime.now(timezone.utc)

if __name__ == "__main__":
    app = create_app()
    app.run(host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")), debug=True)
