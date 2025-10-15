import os
from pathlib import Path
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash as real_flash, session, jsonify, send_from_directory
)
import sqlite3
from werkzeug.utils import secure_filename
from datetime import datetime

# --- Vô hiệu hóa flash mặc định ---
def flash(*args, **kwargs):
    pass

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "static" / "uploads"
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app = Flask(__name__)
app.secret_key = "super_secret_key_green_project"
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)

DATABASE = BASE_DIR / "demo.db"


# ----------------- DB setup -----------------
def get_db():
    conn = sqlite3.connect(str(DATABASE))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Khởi tạo database và tài khoản admin mặc định"""
    with get_db() as conn:
        # Tạo bảng users
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE,
            student_id TEXT,
            address TEXT,
            phone TEXT,
            role TEXT DEFAULT 'user',
            points INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Tạo bảng images
        conn.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            image_path TEXT,
            caption TEXT,
            likes INTEGER DEFAULT 0,
            approved INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """)

        # Kiểm tra có cột points chưa (trường hợp db cũ)
        cols = [r["name"] for r in conn.execute("PRAGMA table_info(users)").fetchall()]
        if "points" not in cols:
            conn.execute("ALTER TABLE users ADD COLUMN points INTEGER DEFAULT 0")
            print("✅ Đã thêm cột points vào bảng users.")

        # Tạo admin mặc định nếu chưa có
        admin = conn.execute("SELECT * FROM users WHERE username='DevModGreen'").fetchone()
        if not admin:
            conn.execute("""
                INSERT INTO users (username, password, email, role, points)
                VALUES ('DevModGreen', 'DevModGreen', 'admin@greencampus.local', 'admin', 0)
            """)
            print("Đã tạo tài khoản admin mặc định: DevModGreen / DevModGreen")

    print("Database sẵn sàng.")


# ----------------- Helper -----------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ----------------- ROUTES -----------------
@app.route("/")
def index():
    with get_db() as conn:
        total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_images = conn.execute("SELECT COUNT(*) FROM images WHERE approved = 1").fetchone()[0]

        user_points = None
        if "user_id" in session:
            row = conn.execute("SELECT points FROM users WHERE id = ?", (session["user_id"],)).fetchone()
            if row:
                user_points = row["points"]

    return render_template(
        "index.html",
        username=session.get("username"),
        user_points=user_points,
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
            flash("Thiếu thông tin bắt buộc!")
            return redirect(url_for("register"))

        try:
            with get_db() as conn:
                conn.execute("""
                    INSERT INTO users (username, password, email, student_id, address, phone, points)
                    VALUES (?, ?, ?, ?, ?, ?, 0)
                """, (username, password, email, student_id, address, phone))
            flash("Đăng ký thành công!")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Username hoặc Email đã tồn tại!")
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
            session["role"] = user["role"]

            if user["role"] == "admin":
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("index"))
        else:
            flash("Sai mật khẩu hoặc tài khoản không tồn tại.")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Đã đăng xuất!")
    return redirect(url_for("index"))


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "user_id" not in session:
        flash("Bạn cần đăng nhập để đăng ảnh.")
        return redirect(url_for("login"))

    if request.method == "POST":
        file = request.files.get("image")
        caption = request.form.get("caption", "").strip()

        if not file or not allowed_file(file.filename):
            flash("File không hợp lệ.")
            return redirect(url_for("upload"))

        filename = secure_filename(f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}")
        save_path = UPLOAD_FOLDER / filename
        file.save(str(save_path))
        rel_path = f"uploads/{filename}"

        with get_db() as conn:
            conn.execute("""
                INSERT INTO images (user_id, image_path, caption, approved)
                VALUES (?, ?, ?, 0)
            """, (session["user_id"], rel_path, caption))

        flash("📨 Ảnh của bạn đã được gửi đến quản trị viên, vui lòng chờ duyệt.")
        return redirect(url_for("upload"))

    with get_db() as conn:
        rows = conn.execute("""
            SELECT images.*, users.username
            FROM images
            JOIN users ON images.user_id = users.id
            WHERE images.approved = 1
            ORDER BY images.created_at DESC
        """).fetchall()

        user_points = conn.execute("""
            SELECT points FROM users WHERE id = ?
        """, (session["user_id"],)).fetchone()["points"]

    return render_template("upload.html", images=rows, username=session.get("username"), user_points=user_points)


# ----------------- LIKE API -----------------
@app.route("/like/<int:image_id>", methods=["POST"])
def like_image(image_id):
    if "user_id" not in session:
        return jsonify({"ok": False, "msg": " Bạn cần đăng nhập để like ảnh!"}), 401

    with get_db() as conn:
        img = conn.execute("SELECT likes FROM images WHERE id = ?", (image_id,)).fetchone()
        if not img:
            return jsonify({"ok": False, "msg": "Ảnh không tồn tại!"}), 404

        new_likes = img["likes"] + 1
        conn.execute("UPDATE images SET likes = ? WHERE id = ?", (new_likes, image_id))
        conn.commit()

    return jsonify({"ok": True, "likes": new_likes})


# ----------------- ADMIN -----------------
@app.route("/admin", methods=["GET", "POST"])
def admin_dashboard():
    if "role" not in session or session["role"] != "admin":
        return redirect(url_for("login"))

    count_by_date = None
    selected_date = None

    if request.method == "POST":
        selected_date = request.form.get("selected_date", "").strip()
        if selected_date:
            with get_db() as conn:
                count_by_date = conn.execute("""
                    SELECT COUNT(*) 
                    FROM images 
                    WHERE approved = 1 
                    AND DATE(created_at) = ?
                """, (selected_date,)).fetchone()[0]

    with get_db() as conn:
        total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_images_all = conn.execute("SELECT COUNT(*) FROM images").fetchone()[0]
        total_images_approved = conn.execute("SELECT COUNT(*) FROM images WHERE approved = 1").fetchone()[0]
        users = conn.execute("SELECT username, email, address, phone, role, points FROM users").fetchall()
        pending_images = conn.execute("""
            SELECT images.*, users.username
            FROM images
            JOIN users ON users.id = images.user_id
            WHERE approved = 0
            ORDER BY created_at DESC
        """).fetchall()

    return render_template(
        "admin.html",
        total_users=total_users,
        total_images_all=total_images_all,
        total_images_approved=total_images_approved,
        users=users,
        pending_images=pending_images,
        count_by_date=count_by_date,
        selected_date=selected_date
    )


@app.route("/approve/<int:image_id>", methods=["POST"])
def approve_photo(image_id):
    if "role" not in session or session["role"] != "admin":
        return redirect(url_for("login"))

    with get_db() as conn:
        # Cập nhật trạng thái ảnh
        conn.execute("UPDATE images SET approved = 1 WHERE id = ?", (image_id,))

        # Cộng điểm cho chủ ảnh
        user = conn.execute("SELECT user_id FROM images WHERE id = ?", (image_id,)).fetchone()
        if user:
            conn.execute("""
                UPDATE users SET points = points + 10 WHERE id = ?
            """, (user["user_id"],))

    flash("Ảnh đã được duyệt và người đăng được +10 điểm.")
    return redirect(url_for("admin_dashboard"))


@app.route("/reject/<int:image_id>", methods=["POST"])
def reject_photo(image_id):
    if "role" not in session or session["role"] != "admin":
        return redirect(url_for("login"))

    with get_db() as conn:
        img = conn.execute("SELECT image_path FROM images WHERE id = ?", (image_id,)).fetchone()
        if img:
            try:
                os.remove(BASE_DIR / "static" / img["image_path"])
            except Exception:
                pass
        conn.execute("DELETE FROM images WHERE id = ?", (image_id,))
    flash(" Ảnh đã bị từ chối và xóa.")
    return redirect(url_for("admin_dashboard"))


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# ----------------- Run -----------------
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)