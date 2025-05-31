from __future__ import annotations

import pendulum

from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook # S3를 쉽게 쓰게 해주는 도구!

# 1. S3에 업로드할 내용을 정의하는 파이썬 함수
def upload_text_to_s3_callable():
    # S3 버킷 이름과 파일 경로(키) 설정
    bucket_name = "mlops-prj"  # S3 버킷 이름
    file_key = "airflow_tests/hello_from_dag.txt" # S3에 저장될 파일 경로와 이름
    
    # 파일 내용 만들기
    current_time = pendulum.now("Asia/Seoul").to_iso8601_string()
    file_content = f"Hello S3 from Airflow DAG! This file was uploaded at {current_time}."
    
    print(f"Attempting to upload to S3: s3://{bucket_name}/{file_key}")
    print(f"File content: {file_content}")
    
    # Airflow S3Hook을 사용해서 파일 업로드 (Conn Id: 'aws_s3_default' 사용)
    # S3Hook이 1단계에서 만든 Connection 정보를 알아서 사용
    s3_hook = S3Hook(aws_conn_id='aws_s3_default')
    s3_hook.load_string(
        string_data=file_content, # 업로드할 문자열 내용
        key=file_key,             # S3에 저장될 파일 경로/이름
        bucket_name=bucket_name,  # 대상 버킷 이름
        replace=True              # 같은 이름의 파일이 있으면 덮어쓰기
    )
    print(f"Successfully uploaded to s3://{bucket_name}/{file_key}")

# 2. Airflow DAG 정의
with DAG(
    dag_id="s3_upload_test_dag",
    schedule=None, # 수동 실행
    start_date=pendulum.datetime(2024, 5, 30, tz="Asia/Seoul"), # 과거 날짜로
    catchup=False,
    tags=["s3_test", "weather_project_연동테스트"],
) as dag:
    # 파이썬 함수를 실행하는 Task 만들기
    upload_to_s3_task = PythonOperator(
        task_id="upload_simple_text_to_s3",
        python_callable=upload_text_to_s3_callable, # 위에서 만든 함수를 지정
    )

    # Task는 하나뿐이니까 순서 정의는 필요 없음