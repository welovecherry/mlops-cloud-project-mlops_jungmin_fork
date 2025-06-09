FROM python:3.9-slim

ENV TZ=Asia/Seoul

RUN apt-get update && \
    apt-get install -y build-essential curl git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 의존성 목록 보고 재료 준비하기
# 'app' 폴더 안에 있는 requirements.txt를 복사해라!
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY app/app.start.sh .
RUN chmod +x ./app.start.sh


COPY src ./src
COPY streamlit_app ./streamlit_app
COPY common ./common
# COPY .env .

# 7. 최종 임무!!
#    - app.start.sh 스크립트를 실행해서 FastAPI와 Streamlit 서버를 동시에 켠다.
CMD ["bash", "app.start.sh"]