import pymysql
from datetime import datetime

# MySQL 연결 설정
def get_connection():
    return pymysql.connect(
        host="project-db-cgi.smhrd.com",
        user="cgi_24k_data_p3_3",
        password="smhrd3",
        database="cgi_24k_data_p3_3",
        port=3307,
        charset="utf8mb4"
    )

# 1. 원천 테이블 데이터 수 조회
def get_table_count(table_name):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            query = f"SELECT COUNT(*) FROM {table_name}"
            cursor.execute(query)
            result = cursor.fetchone()[0]
        print(f"[{datetime.now()}] {table_name} 테이블 데이터 수: {result}")
        return result
    except Exception as e:
        print(f"오류 발생 (get_table_count): {e}")
    finally:
        conn.close()

# 2. ODS 테이블 데이터 삭제
def delete_ods_table(table_name):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            query = f"DELETE FROM {table_name}"
            cursor.execute(query)
        conn.commit()
        print(f"[{datetime.now()}] {table_name} 테이블 데이터 삭제 완료")
    except Exception as e:
        print(f"오류 발생 (delete_ods_table): {e}")
    finally:
        conn.close()

# 3. 원천 테이블 데이터를 ODS 테이블로 삽입
def insert_into_ods(source_table, target_table):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            query = f"INSERT INTO {target_table} SELECT * FROM {source_table}"
            cursor.execute(query)
        conn.commit()
        print(f"[{datetime.now()}] {source_table} → {target_table} 데이터 삽입 완료")
    except Exception as e:
        print(f"오류 발생 (insert_into_ods): {e}")
    finally:
        conn.close()

# 4. 원천과 ODS 테이블 데이터 수 비교
def compare_counts(source_count, ods_count):
    if source_count == ods_count:
        print(f"[{datetime.now()}] ✅ 데이터 일치: 원천({source_count}) == ODS({ods_count})")
    else:
        print(f"[{datetime.now()}] ❌ 데이터 불일치: 원천({source_count}) != ODS({ods_count})")

# 5. ODS 테이블 생성
def create_ods_table_if_not_exists(source_table, target_table):
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            query = f"CREATE TABLE IF NOT EXISTS {target_table} LIKE {source_table}"
            cursor.execute(query)
        conn.commit()
        print(f"[{datetime.now()}] {target_table} 테이블 생성 완료")
    except Exception as e:
        print(f"오류 발생 (create_ods_table_if_not_exists): {e}")
    finally:
        conn.close()

# 메인 실행 함수
def main():
    source_table = "session_info"
    ods_table = "ds_session_info"

    # 1. ODS 테이블 존재 확인 및 생성
    create_ods_table_if_not_exists(source_table, ods_table)

    # 2. 원천 데이터 수 조회
    source_count = get_table_count(source_table)

    # 3. ODS 테이블 데이터 삭제
    delete_ods_table(ods_table)

    # 4. 원천 데이터를 ODS 테이블로 삽입
    insert_into_ods(source_table, ods_table)

    # 5. ODS 데이터 수 조회
    ods_count = get_table_count(ods_table)

    # 6. 데이터 수 비교
    compare_counts(source_count, ods_count)

if __name__ == "__main__":
    main()
