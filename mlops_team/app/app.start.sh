#!/bin/bash

echo "Starting FastAPI server..."
uvicorn src.main:app --host 0.0.0.0 --port 8000 &

echo "Starting Streamlit server..."
# Streamlit에 외부 접속 허용 옵션 추가!
streamlit run streamlit_app/dashboard.py --server.port 8501 --server.address=0.0.0.0