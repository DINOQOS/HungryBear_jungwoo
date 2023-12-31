import pymysql
#추가적으로 변경한 sql문

# 데이터베이스 연결
db = pymysql.connect(
    host="localhost",
    user="root",
    password="****",
    database="hungrybear",
    charset="utf8"
)

try:
    # 데이터베이스 커서 생성
    cursor = db.cursor()

    # 열 추가 쿼리 실행
    sql = "ALTER TABLE customer ADD food_calories INT NULL"
    cursor.execute(sql)

    # 데이터베이스에 변경 사항 저장
    db.commit()

    print("열 추가가 성공적으로 완료되었습니다.")

except Exception as e:
    # 예외가 발생한 경우 롤백 수행
    db.rollback()
    print("열 추가 중 오류가 발생했습니다:", str(e))

finally:
    # 데이터베이스 연결 종료
    db.close()