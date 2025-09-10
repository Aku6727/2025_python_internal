import sqlite3

DATABASE = "tickets_r_us_final.db"

try:
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT *FROM movie")
    all_book_results = cursor.fetchall()
    print(all_book_results)
    print("✅ Connection successful")
except sqlite3.Error as e:
    print(f"❌ Connection failed: {e}")
