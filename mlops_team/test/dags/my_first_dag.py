from __future__ import annotations

import pendulum

from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="my_first_weather_dag", # Airflow UI에 표시될 DAG 이름
    schedule=None, # 일단 수동 실행만 가능하도록
    start_date=pendulum.datetime(2024, 5, 29, tz="Asia/Seoul"), # DAG가 언제부터 유효한지 (과거 날짜로)
    catchup=False, # 과거 스케줄 실행 안 함
    tags=["weather_project", "tutorial"], # 검색하기 쉽도록 태그 달기
) as dag:
    # 첫 번째 Task: 간단한 환영 메시지 출력
    task_hello = BashOperator(
        task_id="say_hello", # Task의 고유 ID
        bash_command="echo 'Hello from my first Airflow DAG for MLOps Weather Project!'",
    )

    # 두 번째 Task: 연결된 데이터 폴더 내용 확인
    task_check_data_folder = BashOperator(
        task_id="check_data_folder_in_container",
        bash_command="echo 'Checking /opt/airflow/data folder inside container...' && ls -l /opt/airflow/data",
    )

    # Task 순서 정의: task_hello 다음에 task_check_data_folder 실행
    task_hello >> task_check_data_folder