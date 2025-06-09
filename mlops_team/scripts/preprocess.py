import pandas as pd
import numpy as np
import warnings
import s3fs
import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from scipy.stats import spearmanr, kruskal
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, RobustScaler
import sklearn
from packaging import version
warnings.filterwarnings('ignore')

# 환경 변수 로드
load_dotenv()

class Feature_Engineering:
    def __init__(self, df=None, is_train=True):
        self.df = df
        self.label_encoders = {}
        self.onehot_encoders = {}
        self.is_train = is_train
        self.s3_bucket = os.getenv("S3_BUCKET_NAME")
        self.s3 = s3fs.S3FileSystem()
    

    def load_data(self, start_year=None, prefix='data/weather/raw'):
        now = datetime.now()
        end_year = now.year
        end_month = now.month

        # 시작연도 설정
        if start_year is None:
            start_year = (now - timedelta(days=365 * 3)).year

        # S3 경로 목록
        months_reduced = [f"s3://{self.s3_bucket}/{prefix}/year={year}/month={str(month).zfill(2)}"
                        for year in range(start_year, end_year + 1)
                        for month in range(1, 13)
                        if not (year == end_year and month > end_month)]

        all_files = []
        for month_path in months_reduced:
            try:
                day_folders = self.s3.ls(month_path)
                for day_folder in day_folders:
                    files = self.s3.glob(f"{day_folder}/*.parquet")
                    all_files.extend(files)
            except FileNotFoundError:
                continue

        df_list = [pd.read_parquet(file, filesystem=self.s3) for file in all_files]
        self.df = pd.concat(df_list, ignore_index=True)
        return self.df


    def missing_value(self):
        for col in self.df.columns:
            if '-' in self.df[col].values:
                self.df[col] = self.df[col].replace('-', 'Other')
        return self.df


    def impossible_negative(self):
        impossible_minus_col = [
            'GustSpeed', 'HourlyRainfall', 'DailyRainfall', 'CumulativeRainfall',
            'RainfallIntensity', 'SnowDepth3Hr', 'DailySnowDepth', 'TotalSnowDepth',
            'LowestCloudHeight', 'SunshineDuration', 'SolarRadiation',
            'WaveHeight', 'MaxWindForce'
        ]
        
        for col in impossible_minus_col:
            if col in self.df.columns:
                self.df[col] = self.df[col].apply(lambda x: 0 if x < 0 else x)
        return self.df
    
    def spearman_test(self, target_col):
        df_num = self.df.select_dtypes(include=['number'])
        features, correlations, p_values = [], [], []

        for col in df_num.columns:
            if col != target_col:
                corr, p = spearmanr(df_num[target_col], df_num[col])
                features.append(col)
                correlations.append(corr)
                p_values.append(p)

        corr_df = pd.DataFrame({
            'Feature': features,
            'Correlation': correlations,
            'P-value': p_values}).sort_values(by='Correlation', ascending=False)
        spearmanr_cols = corr_df[corr_df['P-value'] >= 0.05]['Feature'].tolist()
        return spearmanr_cols


    def kruskal_test(self, target_col, min_group_size=5):
        cat_cols = self.df.select_dtypes(include=['object', 'category']).columns
        results = []

        for col in cat_cols:
            grouped = self.df.groupby(col)[target_col]
            valid_groups = [grp.values for _, grp in grouped if grp.size >= min_group_size]
            if len(valid_groups) >= 2:
                stat, p = kruskal(*valid_groups)
                results.append({'feature': col, 'H-statistic': stat, 'p-value': p})

        kruskal_df = pd.DataFrame(results).sort_values('p-value')
        kruskal_cols = kruskal_df[kruskal_df['p-value'] >= 0.05]['feature'].tolist()
        return kruskal_cols


    def feature_selection(self, target_col):
        spearmanr_cols = self.spearman_test(target_col)
        kruskal_cols = self.kruskal_test(target_col)
        exclude_cols = ['WeatherCode', 'StationID', 'ObservationTime', 'CurrentWeatherCode', 'PastWeatherCode']
        drop_cols = spearmanr_cols + kruskal_cols + exclude_cols

        # 실제 drop 시에도 시계열 + 타겟 변수 제외
        drop_cols = [col for col in drop_cols if col in self.df.columns and col not in ['year', 'month', 'day', 'hour', 'Temperature']]
        self.df.drop(columns=drop_cols, inplace=True)

        order_cols = ['year', 'month', 'day', 'hour', 'Temperature']
        existing = [c for c in order_cols if c in self.df.columns]
        remaining = [c for c in self.df.columns if c not in existing]
        self.df = self.df[existing + remaining]
        return self.df


    def add_feature(self):
        # season
        self.df['season'] = self.df['month'].apply(lambda x:
            'Spring' if 3 <= x <= 5 else
            'Summer' if 6 <= x <= 8 else
            'Fall' if 9 <= x <= 11 else 'Winter')
        
        # time_segment
        self.df['time_segment'] = self.df['hour'].apply(lambda x: 
            'Dawn' if 0 <= x < 6 else
            'Morning' if 6 <= x < 12 else
            'Afternoon' if 12 <= x < 18 else
            'Evening' if 18 <= x < 22 else
            'Night')
        
        # Day (0=Monday ~ 6=Sunday)
        self.df['day_of_week'] = pd.to_datetime(self.df[['year', 'month', 'day']]).dt.dayofweek

        # Hour (0-23)
        max_hour = 23
        self.df['hour_sin'] = np.sin(2 * np.pi * self.df['hour'] / (max_hour + 1))
        self.df['hour_cos'] = np.cos(2 * np.pi * self.df['hour'] / (max_hour + 1))

        # Month (1-12)
        max_month = 12
        self.df['month_sin'] = np.sin(2 * np.pi * (self.df['month'] - 1) / max_month)
        self.df['month_cos'] = np.cos(2 * np.pi * (self.df['month'] - 1) / max_month)

        # Day (1-31)
        max_day = 31
        self.df['day_sin'] = np.sin(2 * np.pi * (self.df['day'] - 1) / max_day)
        self.df['day_cos'] = np.cos(2 * np.pi * (self.df['day'] - 1) / max_day)

        # Day-Week
        self.df['dow_sin'] = np.sin(2 * np.pi * self.df['day_of_week'] / 7)
        self.df['dow_cos'] = np.cos(2 * np.pi * self.df['day_of_week'] / 7)

        return self.df 
    

    def split_data(self, HORIZON=168, SEQ_LEN=336):
        self.df = self.df.sort_values(by=['year', 'month', 'day', 'hour']).reset_index(drop=True)
        val_total_len = SEQ_LEN + HORIZON
        val_df = self.df.iloc[-val_total_len:].copy()
        train_df = self.df.iloc[:-val_total_len].copy()
        latest_input = self.df.iloc[-SEQ_LEN:].copy()
        return train_df, val_df, latest_input


    def scaler(self, train_df, val_df, latest_input):
        train = train_df.copy().drop(columns=['year', 'month', 'day', 'hour'])
        val   = val_df.copy().drop(columns=['year', 'month', 'day', 'hour'])
        latest= latest_input.copy().drop(columns=['year', 'month', 'day', 'hour'])
        num_cols = train.select_dtypes(include=['number']).drop(columns=['Temperature']).columns

        scaler = RobustScaler()
        train[num_cols] = scaler.fit_transform(train[num_cols])
        val[num_cols] = scaler.transform(val[num_cols])
        latest[num_cols] = scaler.transform(latest[num_cols]) 
        return train, val, latest


    def encoding(self, train, val, latest):
        str_cols = train.select_dtypes(include=['object', 'category']).columns.tolist()
        label_cols = []
        onehot_cols = []

        for col in str_cols:
            unique_vals = train[col].nunique()
            if unique_vals <= 10:
                onehot_cols.append(col)
            else:
                label_cols.append(col)
        
        for col in label_cols:
            le = LabelEncoder()
            train[col] = le.fit_transform(train[col])
            self.label_encoders[col] = le

            val[col] = val[col].apply(lambda x: le.transform([x])[0] if x in le.classes_ else -1) # val 처리
            latest[col] = latest[col].apply(lambda x: le.transform([x])[0] if x in le.classes_ else -1) # latest 처리

        for col in onehot_cols:
            if version.parse(sklearn.__version__) >= version.parse("1.2.0"):
                ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
            else:
                ohe = OneHotEncoder(sparse=False, handle_unknown='ignore')
            train_arr = ohe.fit_transform(train[[col]])
            ohe_cols = ohe.get_feature_names_out([col])

            # train 처리
            train_ohe = pd.DataFrame(train_arr, columns=ohe_cols, index=train.index)
            train.drop(columns=[col], inplace=True)
            train = pd.concat([train, train_ohe], axis=1)

            # val 처리
            val_arr = ohe.transform(val[[col]])
            val_ohe = pd.DataFrame(val_arr, columns=ohe_cols, index=val.index)
            val.drop(columns=[col], inplace=True)
            val = pd.concat([val, val_ohe], axis=1)

            # latest_input 처리
            latest_input_arr = ohe.transform(latest[[col]])
            latest_input_ohe = pd.DataFrame(latest_input_arr, columns=ohe_cols, index=latest.index)
            latest.drop(columns=[col], inplace=True)
            latest = pd.concat([latest, latest_input_ohe], axis=1)
            self.onehot_encoders[col] = ohe

        # 컬럼 순서 통일
        val = val[train.columns]
        latest = latest[train.columns]
        return train, val, latest
    

    def save_split_data(self, train, val, latest):
        current_time = datetime.now().strftime('%Y.%m.%d_%H%M')

        # 저장
        train_path = f"{self.s3_bucket}/data/weather/feature/train/train_{current_time}.parquet"
        val_path = f"{self.s3_bucket}/data/weather/feature/val/val_{current_time}.parquet"
        latest_path = f"{self.s3_bucket}/data/weather/feature/latest/latest{current_time}.parquet"

        train.to_parquet(train_path, index=False, engine='pyarrow', filesystem=self.s3)
        val.to_parquet(val_path, index=False, engine='pyarrow', filesystem=self.s3)
        latest.to_parquet(latest_path, index=False, engine='pyarrow', filesystem=self.s3)

        return train_path, val_path, latest_path


 