from __future__ import annotations

import pendulum

from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook # S3Hook 계속 활용!
import pandas as pd
import io # Parquet 파일을 메모리에서 다루기 위해 필요할 수 있음

# S3 Parquet 파일을 읽고 정보를 출력하는 파이썬 함수
def read_s3_parquet_callable():
    # 1. S3 URI에서 버킷 이름과 파일 키(경로) 분리
    s3_uri = "s3://mlops-prj/data/weather/preprocess/v1.0.0/2003.07.05_0000_2025.05.29_1800.parquet" 
    
    # S3 URI를 파싱해서 버킷 이름과 키를 얻는 간단한 방법
    if not s3_uri.startswith("s3://"):
        raise ValueError(f"Invalid S3 URI: {s3_uri}. Must start with s3://")
    
    path_parts = s3_uri.replace("s3://", "").split("/")
    bucket_name = path_parts[0]
    file_key = "/".join(path_parts[1:]) # 파일 경로 전체가 키가 됨
    
    print(f"Attempting to read Parquet file from S3 bucket: {bucket_name}, Key: {file_key}")
    
    try:
        # Airflow S3Hook 사용 (UI에 설정한 'aws_s3_default' Connection 사용)
        s3_hook = S3Hook(aws_conn_id='aws_s3_default')
        
        s3_client = s3_hook.get_conn()
        downloaded_file_path = s3_hook.download_file(
            key=file_key,
            bucket_name=bucket_name,
            local_path="/tmp/" # 컨테이너 내의 임시 폴더
        )
        print(f"File downloaded to: {downloaded_file_path}")
        df = pd.read_parquet(downloaded_file_path)
        
        print("Successfully read the Parquet file from S3! Here's the head:")
        print(df.head())
        print("\nDataFrame Info:")
        df.info()
        print("\nDataFrame Columns:")
        print(list(df.columns)) # 컬럼 이름들 리스트로
        print(f"\nDataFrame shape: {df.shape}")
        
    except Exception as e:
        print(f"ERROR: An error occurred: {e}")
        raise # 에러를 다시 발생시켜서 Airflow UI에서 Task 실패로 표시되도록

with DAG(
    dag_id="s3_parquet_read_dag",
    schedule=None,
    start_date=pendulum.datetime(2024, 5, 30, tz="Asia/Seoul"),
    catchup=False,
    tags=["s3_read", "parquet_test", "weather_project"],
) as dag:
    read_parquet_task = PythonOperator(
        task_id="read_s3_parquet_file",
        python_callable=read_s3_parquet_callable,
    )