from airflow import DAG
from airflow.providers.mysql.operators.mysql import MySqlOperator
from datetime import datetime, timedelta

# 기본 설정
default_args = {
    'owner': 'admin',
    'depends_on_past': False,
    'start_date': datetime(2024, 6, 17),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG 정의
with DAG(
    'daily_data_maintenance',
    default_args=default_args,
    description='Backup and clean data for deepfake analysis',
    schedule_interval='0 1 * * *',  # 매일 새벽 1시
    catchup=False,
) as dag:

    # 1. image_backup_info 데이터를 ds_image_backup_info로 백업
    backup_to_ds_image_backup_info = MySqlOperator(
        task_id='backup_to_ds_image_backup_info',
        mysql_conn_id='mysql_default',
        sql=f"""
            INSERT INTO ds_image_backup_info (deepfake_image_file, deepfake_data, session_idx, model_pred, assent_yn, created_at)
            SELECT deepfake_image_file, deepfake_data, session_idx, model_pred, assent_yn, created_at
            FROM image_backup_info;
        """,
    )

    # 2. upload_info에서 1개월이 지난 데이터 삭제
    delete_old_upload_info = MySqlOperator(
        task_id='delete_old_upload_info',
        mysql_conn_id='mysql_default',
        sql=f"""
            DELETE FROM upload_info
            WHERE created_at < NOW() - INTERVAL 2 MINUTE;
        """,
    )

    # 3. ds_image_backup_info에서 3년이 지난 데이터 삭제
    delete_old_backup_info = MySqlOperator(
        task_id='delete_old_backup_info',
        mysql_conn_id='mysql_default',
        sql=f"""
            DELETE FROM ds_image_backup_info
            WHERE created_at < NOW() - INTERVAL 3 YEAR;
        """,
    )

    # DAG 작업 순서 정의
    backup_to_ds_image_backup_info >> [delete_old_upload_info, delete_old_backup_info]
