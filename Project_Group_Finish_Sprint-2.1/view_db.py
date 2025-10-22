import sqlite3

conn = sqlite3.connect("demo.db")
cursor = conn.cursor()

# kiểm tra xem bảng users có tồn tại không
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
table = cursor.fetchone()

if table:
    print("✅ Bảng 'users' tồn tại.")
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

    if rows:
        for row in rows:
            print(row)
    else:
        print("⚠️ Bảng 'users' chưa có dữ liệu.")
else:
    print("❌ Bảng 'users' không tồn tại trong demo.db.")

conn.close()