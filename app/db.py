# db.py
import mariadb
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "autocommit": False,  # Giữ nguyên False
}

def get_connection():
    """Tạo và trả về một kết nối mới đến MariaDB."""
    try:
        conn = mariadb.connect(**DB_CONFIG)
        # === XÓA SET NAMES KHỎI HÀM NÀY ===
        # Lệnh này sẽ được chuyển vào các hàm 'call_sp'
        return conn
    except mariadb.Error as e:
        print("❌ Lỗi kết nối database:", e)
        raise

def call_sp_save_file(uploader_id, filename, file_type, storage_path, raw_text, summary):
    """Gọi sp_SaveFile, đảm bảo SET NAMES chạy đúng."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        
        # === THÊM SET NAMES VÀO ĐÂY ===
        cur.execute("SET NAMES 'utf8mb4' COLLATE 'utf8mb4_vietnamese_ci'")
        
        # Gọi procedure
        cur.execute("CALL sp_SaveFile(?, ?, ?, ?, ?, ?, @out_file_id)", (
            uploader_id, filename, file_type, storage_path, raw_text, summary
        ))
        # Lấy giá trị OUT param
        cur.execute("SELECT @out_file_id")
        row = cur.fetchone()
        
        conn.commit() # Xác nhận giao dịch
        
        cur.close()
        conn.close()
        return int(row[0]) if row and row[0] else 0
    except Exception as e:
        conn.rollback() # Hoàn tác nếu có lỗi
        raise e
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass

def call_sp_save_question(source_file_id, creator_id, question_text, options_json, answer_letter, status):
    """Gọi sp_SaveQuestion, đảm bảo SET NAMES chạy đúng."""
    conn = get_connection()
    try:
        cur = conn.cursor()

        # === THÊM SET NAMES VÀO ĐÂY ===
        cur.execute("SET NAMES 'utf8mb4' COLLATE 'utf8mb4_vietnamese_ci'")

        cur.execute("CALL sp_SaveQuestion(?, ?, ?, ?, ?, ?)", (
            source_file_id, creator_id, question_text, options_json, answer_letter, status
        ))
        
        conn.commit() # Xác nhận giao dịch
        
        cur.close()
        conn.close()
    except Exception as e:
        conn.rollback() # Hoàn tác nếu có lỗi
        raise e
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass