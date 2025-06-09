import pandas as pd
import numpy as np
import os
import time
import mlflow
import mlflow.sklearn
from typing import Dict, List, Tuple
from datetime import datetime
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor, HistGradientBoostingRegressor
from lightgbm import LGBMRegressor
from xgboost import XGBRegressor
from catboost import CatBoostRegressor
import tempfile
import s3fs

MLFLOW_TRACKING_URI = "http://localhost:5001"
MLFLOW_ARTIFACT_LOCATION = "s3://mlops-prj/data/weather/models/"

class Tree_Models:
    def __init__(self, X_train, y_train, X_val, y_val, experiment_name: str = "Weather_Regression"):
        self.X_train = X_train
        self.y_train = y_train
        self.X_val = X_val
        self.y_val = y_val
        self.experiment_name = experiment_name
        self.s3 = s3fs.S3FileSystem()
        
        # MLflow 서버 및 artifact 저장 위치 설정
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        experiment = mlflow.get_experiment_by_name(self.experiment_name)
        if experiment is None:
            mlflow.create_experiment(name=self.experiment_name, artifact_location=MLFLOW_ARTIFACT_LOCATION)
        mlflow.set_experiment(self.experiment_name)
        print(f"MLflow tracking URI: {mlflow.get_tracking_uri()}")
        print(f"Current experiment: {mlflow.get_experiment_by_name(self.experiment_name)}")
        
        # 트리 모델 정의
        tmp_dir = tempfile.mkdtemp()
        self.models = {
            'LightGBM': LGBMRegressor(n_estimators=100, learning_rate=0.1, verbose=-1),
            'XGBoost': XGBRegressor(n_estimators=100, learning_rate=0.1, verbosity=0),
            'CatBoost': CatBoostRegressor(n_estimators=100, learning_rate=0.1, train_dir=tmp_dir, logging_level='Silent'),
            'RandomForest': RandomForestRegressor(n_estimators=100),
            'GradientBoosting': GradientBoostingRegressor(n_estimators=100, learning_rate=0.1),
            'ExtraTrees': ExtraTreesRegressor(n_estimators=100),
            'HistGradientBoosting': HistGradientBoostingRegressor(max_iter=100, learning_rate=0.1)}


    def train_models(self, run_suffix=None, month=None) -> Dict[str, float]:
        X_train, y_train, X_val, y_val = self.X_train, self.y_train, self.X_val, self.y_val
        model_scores = []
        trained_models = {}
        now = datetime.now().strftime('%Y%m%d_%H%M')
        total_models = len(self.models)
        for idx, (name, model) in enumerate(self.models.items(), 1):
            print(f"{idx}/{total_models}: {name} ...")
            run_name = f"{name}_{now}"
            if run_suffix:
                run_name += f"_{run_suffix}"
            start_time = time.time()
            model.fit(X_train, y_train)
            training_time = time.time() - start_time
            preds = model.predict(X_val)
            rmse = mean_squared_error(y_val, preds) ** 0.5
            model_scores.append({'Model': name, 'RMSE': rmse, 'Training_Time': training_time, 'Model_Obj': model, 'RunName': run_name})
            trained_models[name] = model
            with mlflow.start_run(run_name=run_name):
                mlflow.log_param("model_name", name)
                mlflow.log_param("n_estimators", getattr(model, 'n_estimators', None) or getattr(model, 'max_iter', None))
                mlflow.log_metric("rmse", rmse)
                mlflow.log_metric("training_time", training_time)
                mlflow.sklearn.log_model(model, f"{name}_model", input_example=X_val.iloc[:1])
        model_scores = sorted(model_scores, key=lambda x: x['RMSE'])
        top_3 = model_scores[:3]
        self.top_model_names = [item['Model'] for item in top_3]
        self.top_run_names = [item['RunName'] for item in top_3]
        self.trained_models = trained_models
        return {item['Model']: item['Training_Time'] for item in top_3}

    def register_best_model(self, model_registry_name="WeatherProductionModel"):
        # 상위 1개 모델을 운영 Registry에 등록
        best_model = self.top_model_names[0]
        best_run_name = self.top_run_names[0]
        # MLflow에서 해당 run 찾기
        filter_str = f"tags.mlflow.runName = '{best_run_name}'"
        run_df = mlflow.search_runs(filter_string=filter_str, order_by=['metrics.rmse ASC'])
        run_id = run_df.iloc[0].run_id
        model_uri = f"runs:/{run_id}/{best_model}_model"
        result = mlflow.register_model(model_uri=model_uri, name=model_registry_name)
        client = mlflow.tracking.MlflowClient()
        client.transition_model_version_stage(
            name=model_registry_name,
            version=result.version,
            stage="Production")
        return result.version

    def evaluate_models(self) -> pd.DataFrame:
        X_val, y_val = self.X_val, self.y_val
        results = []
        # top_run_names를 사용
        if hasattr(self, 'top_run_names'):
            run_names = self.top_run_names
            model_names = self.top_model_names
        else:
            run_names = [f"{name}_{datetime.now().strftime('%Y%m%d_%H%M')}" for name in self.models.keys()]
            model_names = list(self.models.keys())
        for idx, (name, run_name) in enumerate(zip(model_names, run_names), 1):
            filter_str = f"tags.mlflow.runName = '{run_name}'"
            run_df = mlflow.search_runs(filter_string=filter_str, order_by=['metrics.rmse ASC'])
            if run_df.empty:
                continue
            run_id = run_df.iloc[0].run_id
            model_uri = f"runs:/{run_id}/{name}_model"
            model = mlflow.sklearn.load_model(model_uri)
            preds = model.predict(X_val)
            rmse = mean_squared_error(y_val, preds) ** 0.5
            results.append({
                'Model': name,
                'RMSE': rmse,
                'Training_Time': self.trained_models[name].get_params().get('n_estimators', 0)})
        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values(by='RMSE')
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'eval_result')
        os.makedirs(output_dir, exist_ok=True)
        results_path = os.path.join(output_dir, 'evaluation_results.csv')
        results_df.to_csv(results_path, index=False)
        print(f"\n✅ Evaluation results saved to: {results_path}")
        return results_df

    def top_models(self, n: int = 3) -> List[str]:
        results_df = self.evaluate_models()
        return results_df.head(n)['Model'].tolist()
