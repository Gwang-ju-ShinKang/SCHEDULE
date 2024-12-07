from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from SCHEDULE.lib.util import MySQLOperator, MySQLReturnOperator
from textwrap import dedent

# 기본 인자 설정
default_args = {
    'owner': 'gwang-ju',
    'depends_on_past': False,
    'start_date': datetime(2024, 12, 7),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

DEFAULT_POOL = 'gwang-ju'

# DAG 정의
with (DAG(
        'gwang-ju-sample',
        default_args=default_args,
        description='gwang-ju-sample',
        schedule_interval='0 1 * * *',  # 매일 실행
        tags=['gwang-ju'],
        catchup=False,
) as dag):

    # 1. 소스 카운트
    src_count = MySQLReturnOperator(
        task_id='src_count',
        pool=DEFAULT_POOL,
        priority_weight=1,
        query=f"""
        SELECT COUNT(*) 
        FROM SRC_TABLE
        """,
        do_xcom_push=True,
    )

    # 2. 적재
    insert_ods = MySQLOperator(
        task_id='insert_ods',
        pool=DEFAULT_POOL,
        priority_weight=1,
        query=f"""
            INSERT INTO TABLE ODS_TABLE
            SELECT *
            FROM SRC_TABLE
            """,
        do_xcom_push=True,
    )



    # 3. 적재 카운트
    ods_count = MySQLReturnOperator(
        task_id='ods_count',
        pool=DEFAULT_POOL,
        priority_weight=1,
        query=f"""
                SELECT COUNT(*) 
                FROM ODS_TABLE
                """,
        do_xcom_push=True,
    )

    # 작업 순서 정의
    src_count  >> insert_ods >> ods_count