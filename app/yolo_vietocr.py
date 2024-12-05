import sqlite3
from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
from PIL import Image
from ultralytics import YOLO
import os

def save_to_database(db_path, image_name, date_of_birth, date_of_expiry, gender, hometown, personID, name, nation, permanent_residence):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(''' 
    INSERT INTO ocr_results (image_name, date_of_birth, date_of_expiry, gender, hometown, personID, name, nation, permanent_residence)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (image_name, date_of_birth, date_of_expiry, gender, hometown, personID, name, nation, permanent_residence))
    connection.commit()
    connection.close()

def handle_id(result, ocr_data):
    # Cập nhật personID nếu kết quả là số và dài 12 ký tự
    if result.isdigit() and len(result) == 12:
        ocr_data["personID"] = result

def handle_hometown(result, ocr_data):
    # Thêm hometown vào dữ liệu, giới hạn ở 2 lần xuất hiện
    if ocr_data["home_town_count"] < 2:
        if ocr_data["home_town"]:
            ocr_data["home_town"] = f"{ocr_data['home_town']}, {result}"
        else:
            ocr_data["home_town"] = result
        ocr_data["home_town_count"] += 1

def process_image(image_name, db_path):
    # Kiểm tra tệp tồn tại
    image_path = os.path.join("app", image_name)
    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        return

    # Khởi tạo model YOLO và VietOCR
    model = YOLO("models/yolo/yolov10b.pt")
    config = Cfg.load_config_from_name('vgg_transformer')
    config['weights'] = 'models/vietocr/vgg_transformer.pth'
    config['device'] = 'cpu'
    detector = Predictor(config)

    ocr_data = {
        "personID": "",
        "fullName": "",
        "birthday": "",
        "gender": "",
        "nation": "",
        "home_town": "",
        "residence": "",
        "residence_1": "",
        "expiry": "",
        "home_town_count": 0,
    }

    # Handlers cho từng loại nhãn
    handlers = {
        "name": lambda result: ocr_data.update({"fullName": result}),
        "date_of_birth": lambda result: ocr_data.update({"birthday": result}),
        "gender": lambda result: ocr_data.update({"gender": result}),
        "nation": lambda result: ocr_data.update({"nation": result}),
        "hometown": lambda result: handle_hometown(result, ocr_data),
        "permanent_residence": lambda result: ocr_data.update({"residence": result}),
        "permanent_residence_1": lambda result: ocr_data.update({"residence_1": result}),
        "date_of_expiry": lambda result: ocr_data.update({"expiry": result}),
        "id": lambda result: handle_id(result, ocr_data),
    }

    # Xử lý YOLO
    results = model(image_path)
    for result in results:
        orig_img = result.orig_img
        for box in result.boxes:
            x_min, y_min, x_max, y_max = map(int, box.xyxy[0].tolist())
            cropped_img = orig_img[y_min:y_max, x_min:x_max]
            cropped_pil = Image.fromarray(cropped_img)
            predicted_text = detector.predict(cropped_pil)

            label = result.names[int(box.cls)]
            if label in handlers:
                handlers[label](predicted_text)  

    # Lưu kết quả vào CSDL
    permanent_residence = ", ".join(filter(None, [ocr_data["residence"], ocr_data["residence_1"]]))
    save_to_database(
        db_path=db_path,
        image_name=image_name,
        date_of_birth=ocr_data["birthday"],
        date_of_expiry=ocr_data["expiry"],
        gender=ocr_data["gender"],
        hometown=ocr_data["home_town"],
        personID=ocr_data["personID"],
        name=ocr_data["fullName"],
        nation=ocr_data["nation"],
        permanent_residence=permanent_residence
    )
