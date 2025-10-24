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
    "autocommit": True,  # Tự động commit sau mỗi câu lệnh
}

def get_connection():
    """Tạo và trả về một kết nối mới đến MariaDB."""
    try:
        return mariadb.connect(**DB_CONFIG)
    except mariadb.Error as e:
        print("❌ Lỗi kết nối database:", e)
        raise


def call_sp_save_file(uploader_id, filename, file_type, storage_path, raw_text, summary):
    """Gọi sp_SaveFile_New và lấy file_id qua OUT param (dành cho MariaDB connector)."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        # Gọi procedure mới có OUT param
        cur.execute("CALL sp_SaveFile(?, ?, ?, ?, ?, ?, @out_file_id)", (
            uploader_id, filename, file_type, storage_path, raw_text, summary
        ))
        cur.execute("SELECT @out_file_id")  # Lấy giá trị OUT param
        row = cur.fetchone()
        cur.close()
        conn.close()
        return int(row[0]) if row and row[0] else 0
    except Exception as e:
        try:
            conn.rollback()
        except:
            pass
        raise e
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass


def call_sp_save_question(source_file_id, creator_id, question_text, options_json, answer_letter, status):
    """Gọi sp_SaveQuestion."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("CALL sp_SaveQuestion(?, ?, ?, ?, ?, ?)", (
            source_file_id, creator_id, question_text, options_json, answer_letter, status
        ))
        cur.close()
        conn.close()
    except Exception as e:
        try:
            conn.rollback()
        except:
            pass
        raise e
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass
