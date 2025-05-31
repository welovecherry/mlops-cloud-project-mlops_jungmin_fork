import os
import sys
sys.path.append(
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
)
from dotenv import load_dotenv
load_dotenv()
import pandas as pd
from datetime import datetime
import s3fs
from tqdm import tqdm

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("This will be printed in terminal")

S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')

preprocess_version = "v1.0.0"

def get_file_list(s3, prefix):
    """S3에서 특정 prefix에 해당하는 파일 목록을 가져옵니다."""
    files = s3.glob(f"{S3_BUCKET_NAME}/{prefix}/*.parquet")
    return set(f.split('/')[-1] for f in files)  # 파일명만 추출

def create_features() -> None:
    """
    전처리된 날씨 데이터로부터 피처를 생성합니다.
    - 전처리된 파일 중 피처가 생성되지 않은 파일들만 선택
    - 동일한 파일명으로 피처 저장
    """
    s3 = s3fs.S3FileSystem()
    
    # 전처리된 파일과 피처 파일 목록 가져오기
    preprocess_files = get_file_list(s3, f"data/weather/preprocess/{preprocess_version}")
    feature_files = get_file_list(s3, f"data/weather/feature/{preprocess_version}")
    
    # 피처가 생성되지 않은 파일들만 선택
    files_to_process = preprocess_files - feature_files
    
    if not files_to_process:
        print("모든 파일의 피처가 이미 생성되어 있습니다.")
        return
    
    print(f"피처를 생성할 파일 수: {len(files_to_process)}")
    
    for filename in tqdm(files_to_process, desc="피처 생성 중"):
        # 전처리된 데이터 로드
        preprocess_path = f"{S3_BUCKET_NAME}/data/weather/preprocess/{preprocess_version}/{filename}"
        print(f"\n전처리된 데이터 로드 중: {filename}")
        processed_data = pd.read_parquet(preprocess_path, filesystem=s3)

        # 시계열 특성 생성
        features_df = create_time_features(processed_data)
        
        # 변화율 계산
        features_df = calculate_change_rates(features_df)
        
        # 복합 특성 생성
        features_df = create_composite_features(features_df)
        
        # 피처 저장 (동일한 파일명 사용)
        save_path = f"{S3_BUCKET_NAME}/data/weather/feature/{preprocess_version}/{filename}"
        
        try:
            features_df.to_parquet(save_path, index=False, engine='pyarrow', filesystem=s3)
            print(f"피처가 저장되었습니다: {filename}")
        except Exception as e:
            print(f"피처 저장 중 오류 발생 ({filename}): {e}")

def create_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """시계열 특성 생성"""
    return df

def calculate_change_rates(df: pd.DataFrame) -> pd.DataFrame:
    """변화율 계산"""
    numeric_columns = [
        'Temperature', 'WindSpeed', 'RelativeHumidity',
    ]
    #온도 풍속 습도
    for col in numeric_columns:
        if col in df.columns:
            # 1시간 변화율
            df[f'{col}_change_1h'] = df[col].pct_change(periods=1)
            # 3시간 변화율
            df[f'{col}_change_3h'] = df[col].pct_change(periods=3)
            # 6시간 변화율
            df[f'{col}_change_6h'] = df[col].pct_change(periods=6)
    
    return df

def create_composite_features(df: pd.DataFrame) -> pd.DataFrame:
    """복합 특성 생성"""
    # 체감온도 계산 (Wind Chill)
    if 'Temperature' in df.columns and 'WindSpeed' in df.columns:
        df['feels_like_temp'] = 13.12 + 0.6215 * df['Temperature'] - \
                               11.37 * (df['WindSpeed'] ** 0.16) + \
                               0.3965 * df['Temperature'] * (df['WindSpeed'] ** 0.16)
    
    # 습도와 온도의 상호작용
    if 'Temperature' in df.columns and 'RelativeHumidity' in df.columns:
        df['temp_humidity_interaction'] = df['Temperature'] * df['RelativeHumidity']
    
    return df

if __name__ == "__main__":
    create_features()