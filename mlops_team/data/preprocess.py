from abc import ABC, abstractmethod
import pandas as pd

class Preprocess(ABC):
    def __init__(self,):
        self.preprocess_version = ''

    @abstractmethod
    def preprocess_data(self):
        """데이터 전처리 메인 메서드"""
        pass

    @abstractmethod
    def load(self):
        """데이터 로드"""
        df = pd.DataFrame()
        return df
    
    @abstractmethod
    def save(self,df):
        """데이터 저장"""
        pass

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """데이터 결측치 처리"""
        return df

    def remove_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """데이터 이상치 제거"""
        return df

    def convert_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """데이터 타입 변환"""

        return df

    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """데이터 정규화"""
        return df
