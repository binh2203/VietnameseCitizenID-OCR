import os
import sqlite3
from flask import Flask, request, render_template, jsonify
import yolo_vietocr
import create_database

# Cấu hình đường dẫn cơ sở dữ liệu
db_path = "database/OCR.db"
create_database.initialize_database(db_path)

# Tạo thư mục lưu tạm nếu chưa tồn tại
UPLOAD_FOLDER = 'app'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 


@app.route('/')
def index():
    return render_template('index.html')


# API: Đếm số lượng ảnh duy nhất
@app.route('/img_index', methods=['GET'])
def get_img_index():
    try:
        query = "SELECT COUNT(DISTINCT image_name) FROM ocr_results"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()
        conn.close()

        return jsonify({'unique_images_count': result[0]})
    except sqlite3.Error as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Unexpected error", "details": str(e)}), 500


# API: Lấy kết quả OCR
@app.route('/results', methods=['GET'])
def get_results():
    try:
        image_name = request.args.get('image_name')

        if image_name:
            query = "SELECT * FROM ocr_results WHERE image_name = ?"
            params = (image_name,)
        else:
            query = "SELECT * FROM ocr_results"
            params = ()

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        results = [
            {
                "image_name": row[1],
                "date_of_birth": row[2],
                "date_of_expiry": row[3],
                "gender": row[4],
                "hometown": row[5],
                "personID": row[6],
                "name": row[7],
                "nation": row[8],
                "permanent_residence": row[9],
            }
            for row in rows
        ]
        return jsonify(results), 200

    except sqlite3.Error as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Unexpected error", "details": str(e)}), 500


# API: Xử lý ảnh bằng YOLO và VietOCR
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Kiểm tra file được gửi
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        image_file = request.files['file']
        if not image_file.filename.endswith(('.png', '.jpg', '.jpeg')):
            return jsonify({'error': 'File type not supported'}), 400

        # Lưu file tạm
        image_name = image_file.filename
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_name)
        image_file.save(image_path)

        # Xử lý file bằng YOLO và VietOCR
        yolo_vietocr.process_image(image_name, db_path)

        os.remove(image_path)
        return '', 204

    except sqlite3.Error as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Unexpected error", "details": str(e)}), 500

@app.route('/favicon.ico')
def favicon():
    return '', 204 

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
