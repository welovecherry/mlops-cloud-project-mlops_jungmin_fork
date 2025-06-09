#!/bin/bash

# FastAPI 서버를 백그라운드에서 실행
uvicorn src.main:app --host 0.0.0.0 --port 8000 &

# Streamlit 앱을 포그라운드에서 실행
# 이 프로세스가 컨테이너의 메인 프로세스가 됨
streamlit run streamlit_app/dashboard.py --server.port 8501