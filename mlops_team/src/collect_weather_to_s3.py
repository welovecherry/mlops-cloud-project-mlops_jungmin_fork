# import os
# import requests
# import pandas as pd
# import boto3
# from datetime import datetime
# from dotenv import load_dotenv

# # .env에서 API 키와 S3 정보 불러오기
# load_dotenv()
# API_KEY = os.environ["AUTH_KEY"]
# BUCKET_NAME = os.environ["S3_BUCKET_NAME"]
# REGION = os.environ.get("AWS_REGION", "ap-northeast-2")

# # 현재 시간 기준 경로 계산
# now = datetime.now()
# year = f"year={now.year}"
# month = f"month={now.month:02d}"
# day = f"day={now.day:02d}"
# hour = f"hour={now.hour:02d}"

# s3_path = f"data/weather/raw/{year}/{month}/{day}/{hour}/weather.parquet"

# # 날씨 API 호출 (예: OpenWeatherMap)
# city = "Seoul"
# url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
# response = requests.get(url)
# data = response.json()

# # 데이터 파싱 → pandas로 변환
# df = pd.DataFrame([{
#     "datetime": now.isoformat(),
#     "temp": data["main"]["temp"],
#     "humidity": data["main"]["humidity"],
#     "description": data["weather"][0]["description"],
#     "wind_speed": data["wind"]["speed"]
# }])

# # 로컬에 parquet로 저장
# local_file = "/tmp/weather.parquet"
# df.to_parquet(local_file, index=False)

# # S3 업로드
# s3 = boto3.client("s3", region_name=REGION)
# s3.upload_file(local_file, BUCKET_NAME, s3_path)
# print(f"✅ Uploaded to s3://{BUCKET_NAME}/{s3_path}")