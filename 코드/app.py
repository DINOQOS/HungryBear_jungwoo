from flask import Flask, render_template, request, redirect
import os
import pymysql
import tensorflow as tf
import keras 
import numpy as np
from PIL import Image
from flask_sqlalchemy import SQLAlchemy    
import urllib.parse
from flask import jsonify

app = Flask(__name__)

# ------------------------------------------------------------------------------------------------------------------------------------
# page 1

@app.route('/')
def test():
    return render_template('test.html')

# ------------------------------------------------------------------------------------------------------------------------------------
# page 2 - DB 연결 및 사용자 정보 입력

@app.route('/test2')
def test2():
    return render_template('test2.html')

# 데이터베이스 연결 (완)
db = pymysql.connect( 
    host="localhost",
    user="root",
    password="****",
    database="hungrybear",
    charset="utf8"
)

# 음식 정보 조회 함수
def get_food_info(food_name):
    cursor = db.cursor(pymysql.cursors.DictCursor)
    query = f"SELECT foodcal FROM food WHERE foodname = '{food_name}'"
    cursor.execute(query)
    result = cursor.fetchone()
    if result:
        return result['foodcal']
    else:
        return None

# 유저 정보
def get_user_info():
    name = request.form.get("name")
    height = float(request.form.get("height"))
    weight = float(request.form.get("weight"))
    age = int(request.form.get("age"))
    gender = request.form.get("gender")
    
    # BMI 계산
    height_m = height / 100  # cm를 m로 변환
    bmi = round(weight / (height_m ** 2), 2)

    # BMR 계산
    if gender == "male":
        bmr = round(66 + (13.75 * weight) + (5 * height) - (6.75 * age), 2)
    elif gender == "female":
        bmr = round(655 + (9.56 * weight) + (1.85 * height) - (4.68 * age), 2)

    
    return name, age, gender, height, weight, bmi, bmr


@app.route('/test2', methods=['GET', 'POST'])

def profile():
    if request.method == 'POST':
        # 사용자 정보 입력 받기
        name, age, gender, height, weight, bmi, bmr = get_user_info()

        # 커서 객체 생성 (완)
        cursor = db.cursor(pymysql.cursors.DictCursor)
        alter_query = "ALTER TABLE customer MODIFY customerID INT AUTO_INCREMENT"

        cursor.execute(alter_query)

        # DB에 유저 정보 삽입
        query = "INSERT INTO customer (name, age, gender, height, weight, bmi, bmr) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (name, age, gender, height, weight, bmi, bmr)

        try:
            cursor.execute(query, values)
            db.commit()
            print("사용자 정보가 성공적으로 저장되었습니다.")
        except Exception as e:
            db.rollback()
            print("사용자 정보 저장 중에 오류가 발생했습니다:", e)

        cursor.close()  # 커서 닫기

        return redirect('/test3')  # 프로필 정보 입력 후 test3 페이지로 리다이렉트

    return render_template('test3.html')

# ------------------------------------------------------------------------------------------------------------------------------------
#누적된 칼로리.

@app.route('/save_food', methods=['POST'])
def save_food():
    data = request.json
    calories = data['calories']
    customer_id = data['customerId']

    # 사용자의 음식 칼로리 누적
    update_query = "UPDATE customer SET food_calories = IFNULL(food_calories, 0) + %s WHERE customerID = %s"
    update_values = (calories, customer_id)
    cursor = db.cursor()
    cursor.execute(update_query, update_values)
    db.commit()

    return jsonify({'message': '음식 칼로리가 성공적으로 누적되었습니다.'})

# ------------------------------------------------------------------------------------------------------------------------------------
#page 3.


upload_folder = 'static/uploads'  # 이미지가 저장될 폴더 경로
app.config['UPLOAD_FOLDER'] = upload_folder

@app.route('/test3', methods=['GET', 'POST'])
def test3():
    # BMI에 따른 메세지 정의
    bmi_messages = {
        'underweight': '저체중입니다! 많이드세요!',
        'normal': '정상체중입니다!',
        'overweight': '과체중입니다! 적절히 관리하세요!',
        'mild_obesity': '경증비만입니다!    관리가 필요합니다!',
        'moderate_obesity': '중등도비만입니다 식단조절과 운동이 필요합니다!',
        'severe_obesity': '고도비만입니다! 전문가의 도움이 필요합니다!'
    }

    # 사용자의 bmi와 bmr 가져오기
    cursor = db.cursor(pymysql.cursors.DictCursor)
    query = "SELECT name, bmi, bmr, IFNULL(food_calories, 0) AS food_calories FROM customer ORDER BY customerID DESC LIMIT 1"
    cursor.execute(query)
    result = cursor.fetchone()

    name = result['name']
    bmi = result['bmi']
    bmr = result['bmr']
    food_calories = result['food_calories']

    predicted_food = None  # predicted_food 변수 초기화
    image = None  # image 변수 초기화
    calories = None  # calories 변수 초기값 설정
    file_path = None  # file_path 변수 초기화

    # 이미지 업로드 처리
    if 'image' in request.files:
        image = request.files['image']
        
        if image.filename != '':
            # 이미지 파일 수 카운트
            file_count = len(os.listdir(upload_folder))
            # 파일 이름 변경
            filename = f"{file_count + 1}.jpg"
            file_path = os.path.join(upload_folder, filename)
            # 파일 저장
            image.save(file_path)
            print("이미지 파일이 성공적으로 저장되었습니다.")

            # 이미지 분류 처리
            model_path = 'C:\\Users\\lily1\\OneDrive\\바탕 화면\\아이와즈_인턴십\\bestmodel_11class.hdf5'
            new_model = tf.keras.models.load_model(model_path)

            class_labels = ['beef_tartare',
                            'chicken_curry',
                            'chocolate_mousse',
                            'french_toast',
                            'fried_rice',
                            'hot_dog',
                            'ice_cream',
                            'lasagna',
                            'oysters',
                            'pizza',
                            'takoyaki']

            def preprocess_image(image):  # 이미지 전처리
                image = image.resize((224, 224))
                image = image.convert('RGB')
                image = np.array(image) / 255.0
                image = np.expand_dims(image, axis=0)
                return image

            def classify_food_photo(image_path):
                image = Image.open(image_path)
                preprocessed_image = preprocess_image(image)

                predictions = new_model.predict(preprocessed_image)
                predicted_class_index = np.argmax(predictions)
                predicted_class = class_labels[predicted_class_index]

                return predicted_class

            predicted_food = classify_food_photo(file_path)
            calories = get_food_info(predicted_food)
            print("Predicted Food:", predicted_food, "의 칼로리", calories)




    return render_template('test3.html', name=name, bmi=bmi, bmr=bmr, file_path=file_path, predicted_food=predicted_food, calories=calories, result=result, bmi_messages=bmi_messages)


  


if __name__ == '__main__':
    app.run(debug=True)
