#!/bin/bash

# FastAPI 서버를 백그라운드에서 실행
# uvicorn src.main:app --host 0.0.0.0 --port 8000 &

# # Streamlit 앱을 포그라운드에서 실행
# # 이 프로세스가 컨테이너의 메인 프로세스가 됨
# streamlit run streamlit_app/dashboard.py --server.port 8501


#!/bin/bash

echo "Starting FastAPI server..."
# uvicorn에 --host 0.0.0.0 옵션이 있는지 다시 한번 확인 (이미 잘 되어있음)
uvicorn src.main:app --host 0.0.0.0 --port 8000 &

echo "Starting Streamlit server..."
# Streamlit에 외부 접속 허용 옵션 추가!
streamlit run streamlit_app/dashboard.py --server.port 8501 --server.address=0.0.0.0