import os
from pathlib import Path
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session, jsonify, send_from_directory
)
import sqlite3
from werkzeug.utils import secure_filename
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app = Flask(__name__)
app.secret_key = "secret_key_demo_change_this"
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
DATABASE = BASE_DIR / "demo.db"


# ---------- DB helper ----------
def get_db():
    conn = sqlite3.connect(str(DATABASE))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            student_id TEXT,
            address TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            image_path TEXT,
            caption TEXT,
            likes INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """)
    print("✅ Database ready (users + images).")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------- ROUTES ----------

@app.route("/")
def index():
    with get_db() as conn:
        total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_images = conn.execute("SELECT COUNT(*) FROM images").fetchone()[0]

    return render_template(
        "index.html",
        username=session.get("username"),
        total_users=total_users,
        total_images=total_images
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        email = request.form.get("email", "").strip()
        student_id = request.form.get("student_id", "")
        address = request.form.get("address", "")
        phone = request.form.get("phone", "")

        if not username or not password or not email:
            flash("⚠️ Thiếu thông tin bắt buộc!")
            return redirect(url_for("register"))

        try:
            with get_db() as conn:
                conn.execute("""
                    INSERT INTO users (username, password, email, student_id, address, phone)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (username, password, email, student_id, address, phone))
            flash("✅ Đăng ký thành công! Mời đăng nhập.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("⚠️ Username hoặc Email đã tồn tại!")
            return redirect(url_for("register"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        with get_db() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE username = ? AND password = ?",
                (username, password)
            ).fetchone()

            if user:
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                flash(f"✅ Đăng nhập thành công! Xin chào {user['username']}")
                return redirect(url_for("index"))
            else:
                flash("❌ Sai username hoặc password")
                return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    flash("👋 Đã đăng xuất thành công!")
    return redirect(url_for("index"))


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "user_id" not in session:
        flash("⚠️ Bạn cần đăng nhập để đăng ảnh.")
        return redirect(url_for("login"))

    if request.method == "POST":
        file = request.files.get("image")
        caption = request.form.get("caption", "").strip()

        if not file or not allowed_file(file.filename):
            flash("⚠️ File không hợp lệ. Chọn ảnh png/jpg/jpeg/gif.")
            return redirect(url_for("upload"))

        filename = secure_filename(f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}")
        save_path = UPLOAD_FOLDER / filename
        file.save(str(save_path))
        rel_path = f"uploads/{filename}"

        with get_db() as conn:
            conn.execute(
                "INSERT INTO images (user_id, image_path, caption) VALUES (?, ?, ?)",
                (session["user_id"], rel_path, caption)
            )
        flash("✅ Đăng ảnh thành công!")
        return redirect(url_for("upload"))

    with get_db() as conn:
        rows = conn.execute("""
            SELECT images.*, users.username
            FROM images
            JOIN users ON images.user_id = users.id
            ORDER BY images.created_at DESC
        """).fetchall()

    return render_template("upload.html", images=rows, username=session.get("username"))


@app.route("/like/<int:image_id>", methods=["POST"])
def like_image(image_id):
    if "user_id" not in session:
        return jsonify({"ok": False, "msg": "Unauthorized"}), 401

    with get_db() as conn:
        cur = conn.execute("SELECT likes FROM images WHERE id = ?", (image_id,)).fetchone()
        if not cur:
            return jsonify({"ok": False, "msg": "Image not found"}), 404
        new_likes = cur["likes"] + 1
        conn.execute("UPDATE images SET likes = ? WHERE id = ?", (new_likes, image_id))

    return jsonify({"ok": True, "likes": new_likes})


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ---------- Main ----------
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8080, debug=True)
