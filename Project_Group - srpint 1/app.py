from flask import Flask, request, redirect, url_for, render_template, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "secret_key_demo"   # cần cho flash message
DATABASE = "demo.db"

# Hàm kết nối DB
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Khởi tạo DB (chạy 1 lần khi mới tạo)
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
        )
        """)
    print("✅ Database initialized.")

@app.route("/")
def home():
    return "Trang chủ Green Campus (demo)"

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        student_id = request.form.get("student_id")
        address = request.form.get("address")
        phone = request.form.get("phone")

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
        username = request.form.get("username")
        password = request.form.get("password")

        with get_db() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (username, password)
            ).fetchone()
            if user:
                flash(f"✅ Đăng nhập thành công! Xin chào {user['username']}")
                return redirect(url_for("home"))
            else:
                flash("❌ Sai username hoặc password")
                return redirect(url_for("login"))

    return render_template("login.html")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
