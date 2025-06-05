from dotenv import load_dotenv
import os
import pandas as pd
import s3fs

# 1. 환경변수 로드
load_dotenv()

# 2. 환경변수 읽기
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# 3. S3 연결
s3 = s3fs.S3FileSystem(key=AWS_ACCESS_KEY_ID, secret=AWS_SECRET_ACCESS_KEY)

# 4. 테스트용 데이터프레임 생성
df = pd.DataFrame({
    "날짜": ["2022-01-21"],
    "기온": [2.5],
    "습도": [65]
})

# 5. 업로드
path = f"{S3_BUCKET_NAME}/data/weather/raw/2022/21/01/data.parquet"
df.to_parquet(path, index=False, engine="pyarrow", filesystem=s3)
print("✅ 업로드 완료:", path)

# 6. 다운로드 확인
df2 = pd.read_parquet(path, filesystem=s3)
print("📄 다운로드한 데이터:")
print(df2)