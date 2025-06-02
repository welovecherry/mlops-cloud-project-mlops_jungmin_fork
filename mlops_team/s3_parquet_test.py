import pandas as pd
import boto3
from dotenv import load_dotenv
import os
from io import BytesIO # Parquet 파일을 메모리 내에서 다루기 위해 필요

load_dotenv()

# .env 파일에서 S3 버킷 이름 가져오기
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

def create_sample_dataframe():
    """샘플 Pandas DataFrame을 생성합니다."""
    data = {
        'timestamp': pd.to_datetime(['2025-06-02 10:00:00', '2025-06-02 10:05:00', '2025-06-02 10:10:00']),
        'temperature': [25.5, 25.7, 25.6],
        'humidity': [60, 61, 60.5],
        'location': ['Busan', 'Busan', 'Busan']
    }
    df = pd.DataFrame(data)
    return df

def upload_to_s3(df, bucket_name, s3_key):
    """DataFrame을 Parquet 형식으로 S3에 업로드합니다."""
    try:
        # DataFrame을 Parquet 형식의 바이트 스트림으로 변환
        parquet_buffer = BytesIO()
        df.to_parquet(parquet_buffer, engine='pyarrow', index=False)
        parquet_buffer.seek(0) # 버퍼의 시작으로 포인터 이동

        # Boto3 S3 클라이언트 생성
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )

        # S3에 파일 업로드
        s3_client.put_object(Bucket=bucket_name, Key=s3_key, Body=parquet_buffer.getvalue())
        print(f"파일이 성공적으로 S3에 업로드되었습니다: s3://{bucket_name}/{s3_key}")
    except Exception as e:
        print(f"S3 업로드 중 오류 발생: {e}")

def read_from_s3(bucket_name, s3_key):
    """S3에서 Parquet 파일을 읽어 DataFrame으로 반환합니다."""
    try:
        # Boto3 S3 클라이언트 생성
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )

        # S3에서 파일 객체 가져오기
        response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
        file_content = response['Body'].read()

        # Parquet 바이트 스트림에서 DataFrame 읽기
        parquet_buffer = BytesIO(file_content)
        df = pd.read_parquet(parquet_buffer, engine='pyarrow')
        print(f"S3에서 파일을 성공적으로 읽었습니다: s3://{bucket_name}/{s3_key}")
        return df
    except Exception as e:
        print(f"S3 읽기 중 오류 발생: {e}")
        return None

if __name__ == "__main__":
    if not S3_BUCKET_NAME:
        print("S3_BUCKET_NAME 환경 변수가 설정되지 않았습니다. .env 파일을 확인하세요.")
    else:
        # 1. 테스트용 DataFrame 생성
        sample_df = create_sample_dataframe()
        print("--- 생성된 샘플 DataFrame ---")
        print(sample_df)
        print("-" * 30)

        # 2. S3에 업로드할 테스트 경로 설정
        # 실제 운영 경로와 구분되는 테스트용 경로를 사용.
        # 예: data/weather/test/hourly/YYYY/MM/DD/HH/test_data.parquet
        test_s3_key_upload = "data/weather/test/hourly/2025/06/02/13/test_upload.parquet"
        
        # 3. DataFrame을 S3에 Parquet으로 업로드 테스트
        print(f"\n--- S3에 업로드 테스트 (버킷: {S3_BUCKET_NAME}, 키: {test_s3_key_upload}) ---")
        upload_to_s3(sample_df, S3_BUCKET_NAME, test_s3_key_upload)
        print("-" * 30)

        # 4. S3에서 Parquet 파일 읽기 테스트 (방금 업로드한 파일)
        print(f"\n--- S3에서 읽기 테스트 (버킷: {S3_BUCKET_NAME}, 키: {test_s3_key_upload}) ---")
        retrieved_df = read_from_s3(S3_BUCKET_NAME, test_s3_key_upload)
        if retrieved_df is not None:
            print("\n--- S3에서 읽어온 DataFrame ---")
            print(retrieved_df)
            print("-" * 30)

        # 5. 기존에 저장된 일별 데이터 읽기 테스트 (경로를 정확히 지정해야 함)
        # 예시: 기존 데이터가 2025년 5월 1일에 있다고 가정
        existing_daily_data_key = "data/weather/raw/year=2025/month=05/day=01/data.parquet"
        print(f"\n--- 기존 일별 데이터 읽기 테스트 (버킷: {S3_BUCKET_NAME}, 키: {existing_daily_data_key}) ---")
        existing_df = read_from_s3(S3_BUCKET_NAME, existing_daily_data_key)
        if existing_df is not None:
            print("\n--- S3에서 읽어온 기존 일별 DataFrame ---")
            print(existing_df.head()) # 너무 크면 일부만 출력
            print(f"기존 데이터 총 {len(existing_df)} 행")
            print("-" * 30)
        else:
            print(f"기존 일별 데이터를 찾을 수 없거나 읽는 데 실패했습니다. 경로를 확인하세요: s3://{S3_BUCKET_NAME}/{existing_daily_data_key}")