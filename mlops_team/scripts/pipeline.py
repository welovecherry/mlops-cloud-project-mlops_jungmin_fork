import os
import sys
import logging
from datetime import datetime
from Preprocessing import Feature_Engineering
from train_model import Tree_Models
from dotenv import load_dotenv

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'pipeline_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv(dotenv_path="/mlops_team/.env")

class Pipeline:
    def __init__(self):
        self.fe = Feature_Engineering()
        self.processed_data_path = None
        
    def preprocess(self):
        """전처리 단계 실행"""
        try:
            logger.info("Starting preprocessing pipeline...")
            
            # 데이터 로드 및 전처리
            df = self.fe.load_data_from_s3(None, None, None)
            df = self.fe.missing_value()
            df = self.fe.feature_selection('Temperature')
            df = self.fe.add_season_feature()
            df = self.fe.encoding()
            df = self.fe.target_temp()
            
            # 전처리된 데이터 저장
            self.processed_data_path = self.fe.save_to_s3(df, version='v1.0.0')
            logger.info(f"Preprocessing completed. Data saved at: {self.processed_data_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error during preprocessing: {str(e)}")
            raise
            
    def train(self):
        """학습 단계 실행"""
        try:
            if not self.processed_data_path:
                raise ValueError("No preprocessed data path found.")
                
            logger.info("Starting model training...")
            
            # 모델 학습 및 평가
            tree_models = Tree_Models(self.processed_data_path)
            tree_models.training_times = tree_models.train_models()
            results = tree_models.evaluate_models()
            
            # Top 3 모델 출력
            top_models = tree_models.get_top_models(3)
            logger.info("\nTop 3 Models Selected:")
            for i, model in enumerate(top_models, 1):
                logger.info(f"{i}. {model}")
                
            logger.info("Model training completed successfully.")
            return True
            
        except Exception as e:
            logger.error(f"Error during model training: {str(e)}")
            raise
            
    def run(self):
        """전체 파이프라인 실행"""
        try:
            # 1. 전처리
            if not self.preprocess():
                return False
                
            # 2. 학습
            if not self.train():
                return False
                
            logger.info("Pipeline execution completed successfully.")
            return True
            
        except Exception as e:
            logger.error(f"Error during pipeline execution: {str(e)}")
            return False

def main():
    pipeline = Pipeline()
    success = pipeline.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 