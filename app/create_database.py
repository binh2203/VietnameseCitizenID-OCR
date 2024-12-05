import sqlite3

def initialize_database(db_path):
    # Kết nối tới database (nếu chưa có sẽ tự động tạo mới)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Tạo bảng nếu chưa tồn tại
    create_table_query = """
    CREATE TABLE IF NOT EXISTS ocr_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        image_name TEXT,
        date_of_birth TEXT, 
        date_of_expiry TEXT, 
        gender TEXT, 
        hometown TEXT, 
        personID TEXT, 
        name TEXT, 
        nation TEXT, 
        permanent_residence TEXT
    );
    """
    cursor.execute(create_table_query)
    conn.commit()
    conn.close()



