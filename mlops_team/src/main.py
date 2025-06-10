from fastapi import FastAPI, HTTPException
from datetime import date
import pandas as pd

# 공통 모듈들을 import!
from common.s3_loader import load_latest_forecast_from_s3
from common.recommender import generate_recommendations

# FastAPI 앱 생성 및 기본 정보 설정
app = FastAPI(
    title="날씨 기반 옷차림 추천 API",
    description="최신 날씨 예보 데이터를 기반으로 옷차림과 활동을 추천합니다.",
    version="1.0.0"
)

# --- API 엔드포인트(기능) 정의 ---

@app.get("/", tags=["기본"])
async def read_root():
    """ API 서버가 잘 켜져있는지 확인하는 기본 엔드포인트 """
    return {"message": "안녕 안녕~ 날씨 기반 옷차림 추천 API에 오신 것을 환영합니다!!!!!!"}


@app.get("/forecast/latest", tags=["날씨 예보"])
async def get_latest_forecast():
    """ S3에서 가장 최신 예보(168시간 = 일주일)를 불러와 JSON 형태로 반환합니다. """
    try:
        df = load_latest_forecast_from_s3()
        # pandas DataFrame을 JSON으로 변환 (orient='records'는 [{}, {}, ...] 형태)
        return df.to_dict(orient="records")
    except Exception as e:
        # 데이터 로딩 중 어떤 에러라도 발생하면, 서버 에러(500)로 처리
        raise HTTPException(status_code=500, detail=f"서버에서 데이터를 불러오는 중 에러가 발생했습니다: {e}")


@app.get("/recommendation/by_day", tags=["옷차림 추천"])
async def get_daily_recommendation(target_date: date):
    """
    특정 날짜(YYYY-MM-DD 형식)를 입력받아 그날의 옷차림과 활동을 추천합니다.
    """
    try:
        df = load_latest_forecast_from_s3()
        
        # 입력받은 날짜에 해당하는 데이터만 필터링
        day_data = df[df['date'] == target_date]

        if day_data.empty:
            # 해당 날짜의 데이터가 예보에 없을 경우, 클라이언트 에러(404)로 처리
            raise HTTPException(status_code=404, detail=f"{target_date}의 예보 데이터가 없습니다.")

        # Streamlit 앱에서 했던 것과 똑같이 평균/최저/최고 기온 계산
        avg_temp = day_data['pred_Temperature'].mean()
        min_temp = day_data['pred_Temperature'].min()
        max_temp = day_data['pred_Temperature'].max()
        temp_diff = max_temp - min_temp
        
        # 공통 추천 모듈 호출
        style_recs, activity_tip, layering_tip = generate_recommendations(avg_temp, temp_diff)
        
        # 깔끔한 JSON 형태로 결과를 정리하여 반환
        return {
            "target_date": target_date,
            "weather_summary": {
                "avg_temp": round(float(avg_temp), 2),      # float()으로 감싸주기
                "min_temp": round(float(min_temp), 2),      # float()으로 감싸주기
                "max_temp": round(float(max_temp), 2),      # float()으로 감싸주기
                "temp_difference": round(float(temp_diff), 2) # float()으로 감싸주기
            },
            "recommendations": {
                "styles": style_recs,
                "activity_tip": activity_tip,
                "layering_tip": layering_tip
            }
        }
    except HTTPException as http_exc:
        # 404 에러는 그대로 다시 발생시킴
        raise http_exc
    except Exception as e:
        # 그 외 모든 에러는 서버 에러(500)로 처리
        raise HTTPException(status_code=500, detail=f"추천을 생성하는 중 서버 에러가 발생했습니다: {e}")
