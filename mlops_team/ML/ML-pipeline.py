import os
import mlflow
import pyarrow.fs as pafs
from clothing_rules import get_cloth_sense
from Preprocessing import Feature_Engineering
from split_data import Data_Split
from train import Tree_Models
from inference import predict
from datetime import datetime

# S3 버킷 및 경로 설정
S3_BUCKET = os.getenv('S3_BUCKET_NAME')
RAW_PREFIX = 'data/weather/raw/'


def main(year=None):
    # 데이터 로드
    fe = Feature_Engineering(is_train=True)
    fe.load_data(prefix=RAW_PREFIX, year=year)

    # 전처리
    fe.missing_value()
    fe.add_feature()
    fe.spearman_test(target_col='Temperature')
    fe.remove_high_corr_target(target_col='Temperature')
    fe.kruskal_test(target_col='Temperature')
    fe.feature_selection(target_col='Temperature')
    
    # 인코딩
    fe.encoding(is_train=True)
    df = fe.df

    # 데이터 분할
    splitter = Data_Split()
    train_df, val_df, test_df = splitter.split_data(df)

    # train 인코딩
    fe_train = Feature_Engineering(train_df)
    fe_train.encoding(is_train=True)
    label_encoders = fe_train.label_encoders
    onehot_encoders = fe_train.onehot_encoders
    feature_cols = fe_train.feature_cols

    # val 인코딩
    fe_val = Feature_Engineering(val_df, feature_cols=feature_cols)
    fe_val.label_encoders = label_encoders
    fe_val.onehot_encoders = onehot_encoders
    fe_val.encoding(is_train=False)

    # test 인코딩
    fe_test = Feature_Engineering(test_df, feature_cols=feature_cols)
    fe_test.label_encoders = label_encoders
    fe_test.onehot_encoders = onehot_encoders
    fe_test.encoding(is_train=False)

    # S3에 저장
    splitter.save_split_data(fe_train.df, fe_val.df, fe_test.df)
    print('S3에 저장 완료')

    # 학습 및 분리
    X_train = fe_train.df.drop(columns=['Temperature'])  
    y_train = fe_train.df['Temperature']
    X_val = fe_val.df.drop(columns=['Temperature'])
    y_val = fe_val.df['Temperature']
    tree_models = Tree_Models(X_train, y_train, X_val, y_val)   
    tree_models.train_models()
    tree_models.evaluate_models()

    # 추론
    best_model_name = tree_models.top_models(1)[0]
    filter_str = f"tags.mlflow.runName = '{best_model_name}'"
    run_df = mlflow.search_runs(filter_string=filter_str, order_by=['metrics.rmse ASC'])
    run_id = run_df.iloc[0].run_id
    model_uri = f"runs:/{run_id}/{best_model_name}_model"
    model = mlflow.sklearn.load_model(model_uri)
    result_df = predict(model, fe_test.df[feature_cols], feature_cols)
    result_df = fe_test.df.copy()
    result_df['pred_temp'] = model.predict(fe_test.df[feature_cols])
    result_df['cloth_rec'] = [get_cloth_sense(temp) for temp in result_df['pred_temp']]
    result_df = result_df[['year', 'month', 'day', 'hour', 'pred_temp', 'cloth_rec']]
    now = datetime.now().strftime('%Y%m%d_%H%M%S')
    s3_path = f"{S3_BUCKET}/inference/test_inference_results_{now}.parquet"
    s3 = pafs.S3FileSystem(region='ap-northeast-2')  # 아시아 태평양 서울(AWS 리전)
    result_df.to_parquet(s3_path, index=False, engine='pyarrow', filesystem=s3)
    print('추론 결과 S3 저장')

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--year', type=int, default=None, help='불러올 연도 (예: 2024)')
    args = parser.parse_args()
    main(year=args.year)
