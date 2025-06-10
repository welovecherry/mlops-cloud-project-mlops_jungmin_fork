import os
import boto3
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path

# S3에서 가장 최신 예보 Parquet 파일을 찾아 pandas DataFrame으로 반환합니다.
# 실패 시 Exception을 발생시킵니다.
def load_latest_forecast_from_s3():
    # .env 파일 로드 (이 함수를 호출하는 스크립트의 위치를 기준으로 경로 설정)
    env_path = Path(__file__).parent.parent.joinpath('.env')
    load_dotenv(dotenv_path=env_path)

    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    bucket_name = os.getenv("S3_BUCKET_NAME", "mlops-prj")
    prefix = "data/weather/inference/"

    if not all([aws_access_key_id, aws_secret_access_key, bucket_name]):
        raise ValueError("AWS 인증 정보가 .env 파일에 설정되지 않았습니다.")

    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    if 'Contents' not in response:
        raise FileNotFoundError(f"S3 버킷 '{bucket_name}'의 '{prefix}' 폴더에 파일이 없습니다.")

    parquet_files = [obj for obj in response['Contents'] if obj['Key'].endswith('.parquet')]
    if not parquet_files:
        raise FileNotFoundError(f"S3 폴더에 Parquet 파일이 없습니다.")

    latest_file = max(parquet_files, key=lambda obj: obj['LastModified'])
    latest_file_key = latest_file['Key']
    
    s3_path = f"s3://{bucket_name}/{latest_file_key}"
    df = pd.read_parquet(s3_path, storage_options={
        "key": aws_access_key_id,
        "secret": aws_secret_access_key,
    })
    
    #  데이터 전처리 로직 
    df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
    df['date'] = df['datetime'].dt.date
    
    if 'pred_Temperature' not in df.columns:
        raise KeyError("Parquet 파일에 필수 컬럼 'pred_Temperature'가 없습니다.")

    return df.sort_values(by='datetime').reset_index(drop=True)