FROM python:3.9-slim

ENV TZ=Asia/Seoul

RUN apt-get update && \
    apt-get install -y build-essential curl git tzdata && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 의존성 목록 복사
COPY mlops_team/app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 실행 스크립트 복사 및 권한 부여
COPY mlops_team/app/app.start.sh .
RUN chmod +x ./app.start.sh

# 모든 소스 코드 폴더들을 각각 복사
COPY mlops_team/src ./src
COPY mlops_team/streamlit_app ./streamlit_app
COPY mlops_team/common ./common


# 최종 실행 명령어
CMD ["bash", "app.start.sh"]