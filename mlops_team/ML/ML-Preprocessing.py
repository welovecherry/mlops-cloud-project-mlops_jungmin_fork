import pandas as pd
import numpy as np
import warnings
import s3fs
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from scipy.stats import spearmanr, kruskal
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
import sklearn
from packaging import version
warnings.filterwarnings('ignore')

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Feature_Engineering:
    def __init__(self, df=None, is_train=True, feature_cols=None):
        self.df = df
        self.label_encoders = {}
        self.onehot_encoders = {}
        self.is_train = is_train
        self.feature_cols = feature_cols
        logger.info("Feature Engineering pipeline initialized")

    def load_data(self, prefix='data/weather/raw/', year=None, month=None):
        """
        S3에서 연도/월별 parquet 파일을 불러옴
        year=None이면 모든 연도, year=2024 등 특정 연도, month=5 등 특정 월만 불러올 수 있음
        """
        s3_bucket = os.getenv("S3_BUCKET_NAME")
        s3 = s3fs.S3FileSystem()
        def get_all_parquet_files(s3, root_path, year=None, month=None):
            all_files = []
            try:
                year_folders = s3.ls(root_path)
            except Exception as e:
                print(f"폴더 리스트 실패: {root_path}")
                return []
            for folder in year_folders:
                if 'year=' in folder:
                    try:
                        folder_year = int(folder.split('year=')[-1].split('/')[0])
                        if year is not None and folder_year != year:
                            continue
                    except Exception:
                        continue
                else:
                    continue
                # month 필터링 추가
                if month is not None:
                    # month=05, month=5 등 다양한 형태 고려
                    month_folders = [f for f in s3.ls(folder) if 'month=' in f]
                    for m_folder in month_folders:
                        try:
                            folder_month = int(m_folder.split('month=')[-1].split('/')[0])
                            if folder_month != month:
                                continue
                        except Exception:
                            continue
                        stack = [m_folder]
                        while stack:
                            path = stack.pop()
                            if path.endswith('.parquet'):
                                all_files.append(path)
                            else:
                                try:
                                    children = s3.ls(path)
                                    stack.extend(children)
                                except Exception:
                                    pass
                else:
                    stack = [folder]
                    while stack:
                        path = stack.pop()
                        if path.endswith('.parquet'):
                            all_files.append(path)
                        else:
                            try:
                                children = s3.ls(path)
                                stack.extend(children)
                            except Exception:
                                pass
            return all_files

        files = get_all_parquet_files(s3, f"{s3_bucket}/{prefix}", year=year, month=month)
        logger.info(f"{len(files)} parquet files found in S3 (year={year if year else 'ALL'}, month={month if month else 'ALL'}, 재귀 탐색)")

        if self.is_train:
            df_list = []
            for f in files:
                try:
                    df = pd.read_parquet(f, filesystem=s3)
                    if 'month' in df.columns:
                        print(f"{f}: month dtype = {df['month'].dtype}")
                    df_list.append(df)
                except Exception as e:
                    print(f"파일 읽기 실패: {f} | 에러: {e}")
                    continue
            self.df = pd.concat(df_list, ignore_index=True)
            logger.info(f"Merged training data shape: {self.df.shape}")
        else:
            latest_file = sorted(files)[-1]
            self.df = pd.read_parquet(latest_file, filesystem=s3)
            logger.info(f"Inference data loaded from: {latest_file}, shape: {self.df.shape}")

        logger.info(f"Columns: {self.df.columns.tolist()}")

        # 날짜 컬럼 category -> int 변환
        for col in ['year', 'month', 'day', 'hour']:
            if str(self.df[col].dtype) == 'category':
                self.df[col] = self.df[col].astype(int)

        return self.df

    def missing_value(self):
        logger.info("Processing missing values")
        for col in self.df.columns:
            if '-' in self.df[col].values:
                self.df[col] = self.df[col].replace('-', 'Other')
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

        return corr_df[corr_df['P-value'] >= 0.05]['Feature'].tolist()

    def remove_high_corr_target(self, target_col, threshold=0.95, method='spearman'):
        feats = self.df.select_dtypes(include=[np.number]).columns.drop(target_col)
        corr_feats = self.df[feats].corr(method=method).abs()
        corr_target = self.df[feats].corrwith(self.df[target_col], method=method).abs()

        to_drop = set()
        for i, f1 in enumerate(feats):
            for f2 in feats[i+1:]:
                if corr_feats.loc[f1, f2] > threshold:
                    if corr_target[f1] >= corr_target[f2]:
                        to_drop.add(f2)
                    else:
                        to_drop.add(f1)
        return list(to_drop)

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
        return kruskal_df[kruskal_df['p-value'] >= 0.05]['feature'].tolist()

    def feature_selection(self, target_col):
        spearman_over_05 = self.spearman_test(target_col)
        corr_over_95 = self.remove_high_corr_target(target_col)
        kruskal_over_05 = self.kruskal_test(target_col)
        exclude_cols = ['WeatherCode', 'StationID', 'ObservationTime']
        drop_cols = spearman_over_05 + corr_over_95 + kruskal_over_05 + exclude_cols

        # drop_cols에서 시계열 컬럼은 무조건 제외
        for col in ['year', 'month', 'day', 'hour']:
            if col in drop_cols:
                drop_cols.remove(col)

        # 실제 drop 시에도 시계열 컬럼은 제외
        drop_cols = [col for col in drop_cols if col in self.df.columns and col not in ['year', 'month', 'day', 'hour']]
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
        
        return self.df 
    

    def encoding(self, is_train=True):
        label_encoding_cols = []
        onehot_encoding_cols = []
        str_df = self.df.select_dtypes(include=['object', 'category'])    

        for col in str_df.columns:
            if self.df[col].nunique() <= 10:
                onehot_encoding_cols.append(col)
            else:
                label_encoding_cols.append(col)

        # Label Encoding
        for col in label_encoding_cols:
            self.df[col] = self.df[col].astype(str)
            if is_train:
                le = LabelEncoder()
                unique_vals = self.df[col].unique().tolist()
                if 'unseen' not in unique_vals:
                    unique_vals.append('unseen')  # unseen 대응 토큰 추가
                le.fit(unique_vals)
                self.df[col] = le.transform(self.df[col])
                self.label_encoders[col] = le
            else:
                le = self.label_encoders.get(col)
                if le is not None:
                    known_classes = set(le.classes_)
                    self.df[col] = self.df[col].apply(lambda x: x if x in known_classes else 'unseen')
                    self.df[col] = le.transform(self.df[col])

        # One-Hot Encoding
        for col in onehot_encoding_cols:
            if version.parse(sklearn.__version__) >= version.parse("1.2.0"):
                ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
            else:
                ohe = OneHotEncoder(sparse=False, handle_unknown='ignore')

            if is_train:
                ohe_arr = ohe.fit_transform(self.df[[col]])
                self.onehot_encoders[col] = ohe
            else:
                ohe = self.onehot_encoders.get(col)
                if ohe is None:
                    continue
                ohe_arr = ohe.transform(self.df[[col]])

            ohe_cols = ohe.get_feature_names_out([col])
            ohe_df = pd.DataFrame(ohe_arr.astype(int), columns=ohe_cols, index=self.df.index)

            self.df.drop(columns=[col], inplace=True)
            self.df = pd.concat([self.df, ohe_df], axis=1)

        
        # Feature Matching
        if is_train:
            # 열 순서까지 고정 (원래 순서대로 저장)
            self.feature_cols = [col for col in self.df.columns if col != 'Temperature']
        else:
            if self.feature_cols is not None:
                # 누락된 열은 0으로 추가
                for col in self.feature_cols:
                    if col not in self.df.columns:
                        self.df[col] = 0

                # 불필요한 열 제거
                drop_cols = [col for col in self.df.columns if col not in self.feature_cols + ['Temperature']]
                if drop_cols:
                    self.df.drop(columns=drop_cols, inplace=True)

                # 순서 맞추기
                self.df = self.df[self.feature_cols + ['Temperature']]

        return self.df




 