from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.wearher.v1_0_0.feature import create_features
from data.wearher.v1_0_0.preprocess import WeatherPreprocess
from data.wearher.v1_0_0.ingest_raw_wearher import collect_weather_data_with_time

def get_execution_time(**context):
    """실행 시간을 가져오는 함수"""
    execution_date = context['execution_date']
    return execution_date.strftime('%Y%m%d%H%M')

def run_weather_preprocessing():
    WeatherPreprocess()
    return None

default_args = {
    'owner': 'airflow',
    'depends_on_past': True,  # 이전 실행이 성공해야 다음 실행 가능
    'email_on_failure': True,  # 실패 시 이메일 알림
    'email_on_retry': False,
    'retries': 3,  # 실패 시 3번 재시도
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(minutes=30),  # 태스크 타임아웃 설정
}

dag = DAG(
    'weather_data_pipeline',
    default_args=default_args,
    description='날씨 데이터 수집 및 처리 파이프라인 (1시간 간격)',
    schedule_interval='0 * * * *',  # 매 시간 정각에 실행
    start_date=days_ago(1),
    catchup=True,  # 과거 데이터도 수집
    max_active_runs=1,  # 동시 실행 제한
    tags=['weather', 'mlops'],
)

default_args = {
    'owner': 'airflow',
    'retries': 0,
    'start_date': datetime(2025, 5, 31),
}

dag = DAG(
    'wearher_data_pipeline',
    default_args=default_args,
    schedule_interval='* * * * *',  # 매 분마다 실행
    catchup=False,
)

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=3),
}

dag = DAG(
    dag_id='wearher_data_pipeline',
    default_args=default_args,
    description='등록 후 최초 1회 실행 + 이후 1시간 간격 자동 실행',
    schedule_interval='0 * * * *',  # 매 시간 정각
    start_date=days_ago(0),         # 지금부터 시작
    catchup=False,                  # 과거는 실행 안 함
    max_active_runs=1,
    tags=['weather', 'mlops'],
)


# Task 1: 날씨 데이터 수집
collect_weather_data = PythonOperator(
    task_id='collect_weather_data',
    python_callable=collect_weather_data_with_time,
    provide_context=True,  # 컨텍스트 정보 전달
    dag=dag,
)

# Task 3: 데이터 전처리
preprocess_data = PythonOperator(
    task_id='preprocess_weather_data',
    python_callable=run_weather_preprocessing,
    provide_context=True,
    dag=dag,
)

# Task 4: 피처 엔지니어링
create_features_data = PythonOperator(
    task_id='create_weather_features',
    python_callable=create_features,
    provide_context=True,
    dag=dag,
)

# Task 의존성 정의
collect_weather_data >> preprocess_data >> create_features_data 
