import pandas as pd
from datetime import datetime
import s3fs
import os
from dotenv import load_dotenv

load_dotenv()

class Data_Split:
    def __init__(self):
        self.s3_bucket = os.getenv("S3_BUCKET_NAME")
        self.s3 = s3fs.S3FileSystem()
        
        
    def split_data(self, df, HORIZON=168, SEQ_LEN=336):
        self.df = self.df.sort_values(by=['year', 'month', 'day', 'hour']).reset_index(drop=True)
        val_total_len = SEQ_LEN + HORIZON
        val_df = self.df.iloc[-val_total_len:].copy()
        train_df = self.df.iloc[:-val_total_len].copy()
        latest_input = self.df.iloc[-SEQ_LEN:].copy()
        return train_df, val_df, latest_input
    

    def save_split_data(self, train_df, val_df, test_df):
        """
        분할된 데이터를 S3에 저장 (train, val, test 각각의 폴더에 저장)
        """
        current_time = datetime.now().strftime('%Y.%m.%d_%H%M')

        # 각 데이터셋을 별도 폴더에 저장
        train_path = f"{self.s3_bucket}/data/weather/feature/train/train_{current_time}.parquet"
        val_path = f"{self.s3_bucket}/data/weather/feature/val/val_{current_time}.parquet"
        test_path = f"{self.s3_bucket}/data/weather/feature/test/test_{current_time}.parquet"

        train_df.to_parquet(train_path, index=False, engine='pyarrow', filesystem=self.s3)
        val_df.to_parquet(val_path, index=False, engine='pyarrow', filesystem=self.s3)
        test_df.to_parquet(test_path, index=False, engine='pyarrow', filesystem=self.s3)

        return train_path, val_path, test_path