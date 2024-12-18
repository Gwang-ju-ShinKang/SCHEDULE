from airflow import DAG
from airflow.providers.mysql.operators.mysql import MySqlOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# 기본 설정
default_args = {
    'owner': 'gwang-ju',
    'depends_on_past': False,
    'start_date': datetime(2024, 6, 17),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG 정의
with DAG(
    'mysql_backup_session_info',
    default_args=default_args,
    description='Backup session_info to ds_session_info using MySQLOperator',
    schedule_interval='0 1 * * *',  # 매일 새벽 1시
    catchup=False,
) as dag:

    source_table = "session_info"
    ods_table = "ds_session_info"

    # 1. ODS 테이블 삭제 후 재생성
    create_ods_table = MySqlOperator(
        task_id='create_ods_table',
        mysql_conn_id='mysql_default',
        sql=f"""
            DROP TABLE IF EXISTS {ods_table};
            CREATE TABLE {ods_table} LIKE {source_table};
        """,
    )

    # 2. ODS 테이블 데이터 삭제
    delete_ods_task = MySqlOperator(
        task_id='delete_ods_table',
        mysql_conn_id='mysql_default',
        sql=f"""
            DELETE FROM {ods_table};
        """,
    )

    # 3. 원천 데이터를 ODS 테이블로 삽입
    insert_data_task = MySqlOperator(
        task_id='insert_into_ods',
        mysql_conn_id='mysql_default',
        sql=f"""
            INSERT INTO {ods_table}
            SELECT * FROM {source_table};
        """,
    )

    # 4. 원천 데이터 수 조회
    get_source_count = MySqlOperator(
        task_id='get_source_count',
        mysql_conn_id='mysql_default',
        sql=f"""
            SELECT COUNT(*) FROM {source_table};
        """,
        do_xcom_push=True,
    )

    # 5. ODS 테이블 데이터 수 조회
    get_ods_count = MySqlOperator(
        task_id='get_ods_count',
        mysql_conn_id='mysql_default',
        sql=f"""
            SELECT COUNT(*) FROM {ods_table};
        """,
        do_xcom_push=True,
    )

    # 6. 데이터 수 비교
    def compare_counts(**kwargs):
        ti = kwargs['ti']
        source_count = ti.xcom_pull(task_ids='get_source_count')[0][0]  # XCom에서 첫 번째 결과를 가져옴
        ods_count = ti.xcom_pull(task_ids='get_ods_count')[0][0]
        if source_count == ods_count:
            print(f"✅ 데이터 일치: 원천({source_count}) == ODS({ods_count})")
        else:
            raise ValueError(f"❌ 데이터 불일치: 원천({source_count}) != ODS({ods_count})")

    compare_task = PythonOperator(
        task_id='compare_counts',
        python_callable=compare_counts,
    )

    # 작업 순서 정의
    create_ods_table >> delete_ods_task >> insert_data_task >> get_source_count >> get_ods_count >> compare_task
