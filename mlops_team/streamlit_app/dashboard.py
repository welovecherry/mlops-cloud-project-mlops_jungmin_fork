# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime
# import numpy as np
# import boto3
# from botocore.exceptions import NoCredentialsError
# import os
# from dotenv import load_dotenv
# import sys # 추가

# # 현재 파일(dashboard.py)의 디렉토리(streamlit_app)에서 한 단계 위(mlops_team)의 경로를 가져옴
# project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# # 파이썬이 모듈을 찾는 경로 목록에 이 프로젝트 경로를 추가
# sys.path.append(project_path)
# from common.s3_loader import load_latest_forecast_from_s3  # S3에서 최신 예측 데이터를 로드하는 함수
# from common.recommender import generate_recommendations # 새로 만든 추천 함수 import


# # 페이지 설정
# st.set_page_config(
#     page_title="🌤️ 날씨별 패션 추천",
#     page_icon="👗",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # 커스텀 CSS
# st.markdown("""
# <style>
#     .main-header {
#         text-align: center;
#         padding: 2rem 0;
#         background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
#         color: white;
#         border-radius: 10px;
#         margin-bottom: 2rem;
#     }
#     .weather-card {
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         padding: 1.5rem;
#         border-radius: 15px;
#         color: white;
#         text-align: center;
#         margin-bottom: 1rem;
#     }
#     .temp-display {
#         font-size: 3rem;
#         font-weight: bold;
#         margin: 0.5rem 0;
#     }
#     .clothing-section {
#         background: white;
#         padding: 2rem;
#         border-radius: 15px;
#         box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
#         margin: 2rem 0;
#     }
#     .clothing-category h4 {
#         color: #4a4a4a;
#         font-size: 1.5rem; 
#         font-weight: 600; 
#         margin-bottom: 0.8rem; 
#     }
#     .clothing-item {
#         display: inline-block;
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         color: white;
#         padding: 0.8rem 1.2rem;
#         margin: 0.3rem;
#         border-radius: 25px;
#         font-size: 0.95rem;
#         font-weight: 500;
#         box-shadow: 0 2px 6px rgba(102, 126, 234, 0.3);
#     }
#     .tip-box {
#         # background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         padding: 1.5rem;
#         border-radius: 12px;
#         margin: 1rem 0;
#         border-left: 4px solid #fdcb6e;
#     }
#     .weather-status {
#         font-size: 1.5rem;
#         font-weight: bold;
#         text-align: center;
#         padding: 1rem;
#         border-radius: 10px;
#         margin: 1rem 0;
#     }
#     .activity-tip {
#         background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
#         padding: 1rem;
#         border-radius: 10px;
#         margin: 1rem 0;
#         color: white;
#         font-weight: 500;
#     }
            
#     .temp-cold { background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%); }
#     .temp-cool { background: linear-gradient(135deg, #81ecec 0%, #00cec9 100%); }
#     .temp-mild { background: linear-gradient(135deg, #55a3ff 0%, #003d82 100%); }
#     .temp-warm { background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%); }
#     .temp-hot { background: linear-gradient(135deg, #fd79a8 0%, #e84393 100%); }
# </style>
# """, unsafe_allow_html=True)

# # Streamlit 전용 데이터 로더: 캐싱과 UI 에러 처리를 담당
# # 600초(10분)동안 캐시 유지함. 하지만 refresh 버튼을 누르면 캐시를 지우고 새로고침함.
# @st.cache_data(ttl=600)
# def get_data_for_app():
#     try:
#         df = load_latest_forecast_from_s3()
#         # latest_date = df['datetime'].max().strftime('%Y-%m-%d %H:%M')
#         # st.success(f"✅ S3에서 최신 데이터를 성공적으로 불러왔습니다. (예측 기준 시점: {latest_date})")
#         latest_date = df['datetime'].max().strftime('%Y-%m-%d %H:%M')
#         now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
#         st.success(f"✅ 데이터 동기화 완료! (가져온 시각: {now_str}  / 최종 예측 시점: {latest_date})")
#         return df
#     except Exception as e:
#         st.error(f"데이터 로딩에 실패했습니다: {e}")
#         st.stop()


# # 메인 앱
# def main():
#     # 헤더
#     st.markdown("""
#     <div class="main-header">
#         <h1>🌤️ 날씨별 패션 추천</h1>
#         <p>오늘의 날씨에 맞는 완벽한 코디를 추천해드려요!</p>
#     </div>
#     """, unsafe_allow_html=True)
    
#     # 데이터 로드
#     df = get_data_for_app()  # S3에서 데이터 로드

#     # 사이드바 - 날짜 선택 및 설정
#     st.sidebar.header("⚙️ 설정")

#     if st.sidebar.button("🔄 데이터 새로고침"):
#         st.cache_data.clear()  
#         st.rerun()  # 데이터 새로고침 버튼 클릭 시 캐시를 지우고 앱을 다시 실행
    
#     # 날짜 선택
#     st.sidebar.subheader("📅 날짜 선택")
#     available_dates = sorted(df['date'].unique())
#     selected_date = st.sidebar.selectbox(
#         "날짜를 선택하세요:",
#         options=available_dates,
#         format_func=lambda x: x.strftime("%Y년 %m월 %d일")
#     )
    
#     # 온도 단위 선택
#     temp_unit = st.sidebar.radio("🌡️ 온도 단위", ["°C", "°F"])
    
#     # 개인화 설정
#     st.sidebar.subheader("👤 개인 설정")
#     sensitivity = st.sidebar.select_slider(
#         "추위/더위 민감도",
#         options=["매우 추위 탐", "추위 탐", "보통", "더위 탐", "매우 더위 탐"],
#         value="보통"
#     )
    
#     # 선택된 날짜의 데이터 필터링
#     day_data = df[df['date'] == selected_date].copy()
#     day_data = day_data.sort_values('hour')
    
#     # 온도 단위 변환
#     if temp_unit == "°F":
#         day_data['display_temp'] = day_data['pred_Temperature'] * 9/5 + 32
#     else:
#         day_data['display_temp'] = day_data['pred_Temperature']
    
#     # 민감도에 따른 온도 조정
#     temp_adjustment = {
#         "매우 추위 탐": 3,
#         "추위 탐": 1.5,
#         "보통": 0,
#         "더위 탐": -1.5,
#         "매우 더위 탐": -3
#     }
    
#     adjusted_temp = day_data['pred_Temperature'] + temp_adjustment[sensitivity]
#     min_temp = adjusted_temp.min()
#     max_temp = adjusted_temp.max()
#     temp_diff = max_temp - min_temp
#     avg_temp = adjusted_temp.mean()
    
#     # 온도 단위 변환 (표시용)
#     if temp_unit == "°F":
#         min_temp_display = min_temp * 9/5 + 32
#         max_temp_display = max_temp * 9/5 + 32
#         avg_temp_display = avg_temp * 9/5 + 32
#     else:
#         min_temp_display = min_temp
#         max_temp_display = max_temp
#         avg_temp_display = avg_temp
    
#     # 메인 컨텐츠 - 2개 컬럼
#     col1, col2 = st.columns([1, 2])
    
#     # 왼쪽 컬럼 - 날씨 정보
#     with col1:
#         st.markdown(f"""
#         <div class="weather-card">
#             <h3>📅 {selected_date.strftime("%m월 %d일")}</h3>
#             <div class="temp-display">{avg_temp_display:.1f}{temp_unit}</div>
#             <p>평균 기온</p>
#             <hr style="border-color: rgba(255,255,255,0.3);">
#             <p><strong>최고:</strong> {max_temp_display:.1f}{temp_unit}</p>
#             <p><strong>최저:</strong> {min_temp_display:.1f}{temp_unit}</p>
#             <p><strong>일교차:</strong> {temp_diff:.1f}°C</p>
#         </div>
#         """, unsafe_allow_html=True)
    
#     # 오른쪽 컬럼 - 온도 그래프
#     with col2:
#         st.subheader("📊 시간별 온도 변화")
        
#         # Plotly 그래프 생성
#         fig = go.Figure()
        
#         # 온도 라인 추가
#         fig.add_trace(go.Scatter(
#             x=day_data['hour'],
#             y=day_data['display_temp'],
#             mode='lines+markers',
#             name='온도',
#             line=dict(color='#667eea', width=3),
#             marker=dict(size=8, color='#667eea'),
#             hovertemplate='<b>%{x}시</b><br>온도: %{y:.1f}' + temp_unit + '<extra></extra>',
#             fill='tonexty',
#             fillcolor='rgba(102, 126, 234, 0.1)'
#         ))
        
#         # 최고/최저 온도 포인트 강조
#         max_temp_hour = day_data.loc[day_data['pred_Temperature'].idxmax(), 'hour']
#         min_temp_hour = day_data.loc[day_data['pred_Temperature'].idxmin(), 'hour']
        
#         fig.add_trace(go.Scatter(
#             x=[max_temp_hour],
#             y=[max_temp_display],
#             mode='markers',
#             name='최고기온',
#             marker=dict(size=15, color='red', symbol='triangle-up'),
#             hovertemplate='<b>최고기온</b><br>%{x}시: %{y:.1f}' + temp_unit + '<extra></extra>'
#         ))
        
#         fig.add_trace(go.Scatter(
#             x=[min_temp_hour],
#             y=[min_temp_display],
#             mode='markers',
#             name='최저기온',
#             marker=dict(size=15, color='blue', symbol='triangle-down'),
#             hovertemplate='<b>최저기온</b><br>%{x}시: %{y:.1f}' + temp_unit + '<extra></extra>'
#         ))
        
#         # 그래프 레이아웃 설정
#         fig.update_layout(
#             xaxis_title="시간 (시)",
#             yaxis_title=f"온도 ({temp_unit})",
#             hovermode='x unified',
#             plot_bgcolor='rgba(240,242,246,0.5)',
#             paper_bgcolor='white',
#             font=dict(size=15, color='black'), # 검정색으로 바꿈
#             height=400,
#             margin=dict(l=50, r=50, t=50, b=50),
#             xaxis=dict(
#                 dtick=5,
#                 gridcolor='rgba(200,200,200,0.5)',
#                 range=[-0.5, 23.5],
#                 color='black',  
#                 title_font=dict(color='black'), 
#                 tickfont=dict(color='black')  
#             ),
#             yaxis=dict(
#                 gridcolor='rgba(200,200,200,0.5)',
#                 color ='black',
#                 title_font=dict(color='black'),
#                 tickfont=dict(color='black')
#             )
#         )
        
#         st.plotly_chart(fig, use_container_width=True)
    

#     # style_recommendations, activity_tip = get_recommendations_by_style(avg_temp) 
#     style_recommendations, activity_tip, layering_tip = generate_recommendations(avg_temp, temp_diff)

#     # 2. 스타일 종류들을 탭의 이름으로 사용
#     style_options = ["캐주얼", "비즈니스", "스포티", "페미닌", "미니멀"]
#     tabs = st.tabs([f"👕 {s}" for s in style_options])
    
#     # 3. 각 탭에 내용 채우기
#     for i, tab in enumerate(tabs):
#         with tab:
#             current_style = style_options[i]
#             st.subheader(f"'{current_style}' 스타일 추천")
            
#             recs = style_recommendations.get(current_style, {})
#             if not recs:
#                 st.write("이 스타일에 대한 추천 정보가 아직 없어요. 😢")
#                 continue

#             # 카테고리별로 추천 아이템 표시
#             for category, items in recs.items():
#                 if items: # 아이템이 있을 때만 표시
#                     # 이모지를 사용해서 예쁘게 카테고리 이름 만들기
#                     category_emoji = {"아우터": "🧥", "상의": "👕", "하의": "👖"}.get(category, "✨")
#                     items_html = "".join([f'<div class="clothing-item">{item}</div>' for item in items])
                    
#                     st.markdown(f"""
#                     <div class="clothing-category">
#                         <h4>{category_emoji} {category.capitalize()}</h4>
#                         <div>{items_html}</div>
#                     </div>
#                     """, unsafe_allow_html=True)

#     # 일교차 팁은 탭 밖에 공통으로 표시
#     temp_diff = max_temp - min_temp
#     layering_tip = ""
#     if temp_diff >= 10:
#         layering_tip = "🌡️ 일교차가 매우 큽니다! 겉옷을 여러 벌 준비하여 레이어링하세요."
#     elif temp_diff >= 7:
#         layering_tip = "🌡️ 일교차가 큰 편이니 얇은 겉옷을 준비하세요."
    
#     if layering_tip:
#         st.markdown(f"""
#         <div class="tip-box" style="font-size: 20px;">
#             <strong style="font-size: 25px;">💡 레이어링 팁</strong><br>
#             {layering_tip}
#         </div>
#         """, unsafe_allow_html=True)
    
#     if activity_tip:
#         st.markdown(f"""
#         <div class="activity-tip" style="font-size: 20px;">
#             <strong style="font-size: 25px;">🎯 활동 추천</strong><br>
#             {activity_tip}
#         </div>
#         """, unsafe_allow_html=True)
    
#     st.markdown("</div>", unsafe_allow_html=True)
    
#     # 하단 - 상세 정보
#     st.markdown("---")
#     col1, col2 = st.columns(2)
    
#     with col1:
#         st.subheader("📈 온도 통계")
#         max_temp_hour = day_data.loc[day_data['pred_Temperature'].idxmax(), 'hour']
#         min_temp_hour = day_data.loc[day_data['pred_Temperature'].idxmin(), 'hour']
        
#         stats_df = pd.DataFrame({
#             '구분': ['최고기온', '최저기온', '평균기온', '일교차'],
#             '값': [f"{max_temp_display:.1f}{temp_unit}", 
#                   f"{min_temp_display:.1f}{temp_unit}", 
#                   f"{avg_temp_display:.1f}{temp_unit}", 
#                   f"{temp_diff:.1f}°C"],
#             '시간': [f"{max_temp_hour}시", f"{min_temp_hour}시", "-", "-"]
#         })
#         st.dataframe(stats_df, hide_index=True, use_container_width=True)
    
#     with col2:
#         st.subheader("🕐 시간별 상세")
#         detail_df = day_data[['hour', 'display_temp']].copy()
#         detail_df.columns = ['시간', f'온도({temp_unit})']
#         detail_df['시간'] = detail_df['시간'].astype(str) + '시'
#         detail_df[f'온도({temp_unit})'] = detail_df[f'온도({temp_unit})'].round(1)
#         st.dataframe(detail_df, hide_index=True, use_container_width=True, height=300)

# if __name__ == "__main__":
#     main()

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import boto3
from botocore.exceptions import NoCredentialsError
import os
from dotenv import load_dotenv
import sys # 추가

# 현재 파일(dashboard.py)의 디렉토리(streamlit_app)에서 한 단계 위(mlops_team)의 경로를 가져옴
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# 파이썬이 모듈을 찾는 경로 목록에 이 프로젝트 경로를 추가
sys.path.append(project_path)
from common.s3_loader import load_latest_forecast_from_s3  # S3에서 최신 예측 데이터를 로드하는 함수
from common.recommender import generate_recommendations # 새로 만든 추천 함수 import


# 페이지 설정
st.set_page_config(
    page_title="🌤️ 날씨별 패션 추천",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .weather-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
    .temp-display {
        font-size: 3rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .clothing-section {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        margin: 2rem 0;
    }
    .clothing-category h4 {
        color: #4a4a4a;
        font-size: 1.5rem; 
        font-weight: 600; 
        margin-bottom: 0.8rem; 
    }
    .clothing-item {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.8rem 1.2rem;
        margin: 0.3rem;
        border-radius: 25px;
        font-size: 0.95rem;
        font-weight: 500;
        box-shadow: 0 2px 6px rgba(102, 126, 234, 0.3);
    }
    .tip-box {
        # background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid #fdcb6e;
    }
    .weather-status {
        font-size: 1.5rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .activity-tip {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: white;
        font-weight: 500;
    }
            
    .temp-cold { background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%); }
    .temp-cool { background: linear-gradient(135deg, #81ecec 0%, #00cec9 100%); }
    .temp-mild { background: linear-gradient(135deg, #55a3ff 0%, #003d82 100%); }
    .temp-warm { background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%); }
    .temp-hot { background: linear-gradient(135deg, #fd79a8 0%, #e84393 100%); }
</style>
""", unsafe_allow_html=True)

# .env 파일에서 환경 변수 로드
# load_dotenv(dotenv_path="mlops_team/.env")
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

# S3에서 최신 예측 데이터를 로드하는 함수
@st.cache_data(ttl=600) # 10분 주기는 그대로 두되, 수동 버튼을 추가할 것
def load_data_from_s3():
    # .env 파일에서 AWS 정보 불러오기
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    bucket_name = os.getenv("S3_BUCKET_NAME", "mlops-prj")
    
    PREFIX = "data/weather/inference/"

    # 키 값이 제대로 로드 되었는지 확인
    if not all([aws_access_key_id, aws_secret_access_key, bucket_name]):
        st.error(".env 파일에 AWS 관련 환경변수가 설정되지 않았습니다.")
        st.stop()

    try:
        df = load_latest_forecast_from_s3()
        # latest_date = df['datetime'].max().strftime('%Y-%m-%d %H:%M')
        # st.success(f"✅ S3에서 최신 데이터를 성공적으로 불러왔습니다. (예측 기준 시점: {latest_date})")
        latest_date = df['datetime'].max().strftime('%Y-%m-%d %H:%M')
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
        st.success(f"✅ 데이터 동기화 완료! (가져온 시각: {now_str}  / 최종 예측 시점: {latest_date})")
        return df
    except Exception as e:
        st.error(f"데이터 로딩에 실패했습니다: {e}")
        st.stop()


# 메인 앱
def main():
    # 헤더
    st.markdown("""
    <div class="main-header">
        <h1>🌤️ 날씨별 패션 추천</h1>
        <p>오늘의 날씨에 맞는 완벽한 코디를 추천해드려요!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 데이터 로드
    df = get_data_for_app()  # S3에서 데이터 로드

    # 사이드바 - 날짜 선택 및 설정
    st.sidebar.header("⚙️ 설정")

    if st.sidebar.button("🔄 데이터 새로고침"):
        st.cache_data.clear()  
        st.rerun()  # 데이터 새로고침 버튼 클릭 시 캐시를 지우고 앱을 다시 실행
    
    # 날짜 선택
    st.sidebar.subheader("📅 날짜 선택")
    available_dates = sorted(df['date'].unique())
    selected_date = st.sidebar.selectbox(
        "날짜를 선택하세요:",
        options=available_dates,
        format_func=lambda x: x.strftime("%Y년 %m월 %d일")
    )
    
    # 온도 단위 선택
    temp_unit = st.sidebar.radio("🌡️ 온도 단위", ["°C", "°F"])
    
    # 개인화 설정
    st.sidebar.subheader("👤 개인 설정")
    sensitivity = st.sidebar.select_slider(
        "추위/더위 민감도",
        options=["매우 추위 탐", "추위 탐", "보통", "더위 탐", "매우 더위 탐"],
        value="보통"
    )
    
    # 선택된 날짜의 데이터 필터링
    day_data = df[df['date'] == selected_date].copy()
    day_data = day_data.sort_values('hour')
    
    # 온도 단위 변환
    if temp_unit == "°F":
        day_data['display_temp'] = day_data['pred_Temperature'] * 9/5 + 32
    else:
        day_data['display_temp'] = day_data['pred_Temperature']
    
    # 민감도에 따른 온도 조정
    temp_adjustment = {
        "매우 추위 탐": 3,
        "추위 탐": 1.5,
        "보통": 0,
        "더위 탐": -1.5,
        "매우 더위 탐": -3
    }
    
    adjusted_temp = day_data['pred_Temperature'] + temp_adjustment[sensitivity]
    min_temp = adjusted_temp.min()
    max_temp = adjusted_temp.max()
    temp_diff = max_temp - min_temp
    avg_temp = adjusted_temp.mean()
    
    # 온도 단위 변환 (표시용)
    if temp_unit == "°F":
        min_temp_display = min_temp * 9/5 + 32
        max_temp_display = max_temp * 9/5 + 32
        avg_temp_display = avg_temp * 9/5 + 32
    else:
        min_temp_display = min_temp
        max_temp_display = max_temp
        avg_temp_display = avg_temp
    
    # 메인 컨텐츠 - 2개 컬럼
    col1, col2 = st.columns([1, 2])
    
    # 왼쪽 컬럼 - 날씨 정보
    with col1:
        st.markdown(f"""
        <div class="weather-card">
            <h3>📅 {selected_date.strftime("%m월 %d일")}</h3>
            <div class="temp-display">{avg_temp_display:.1f}{temp_unit}</div>
            <p>평균 기온</p>
            <hr style="border-color: rgba(255,255,255,0.3);">
            <p><strong>최고:</strong> {max_temp_display:.1f}{temp_unit}</p>
            <p><strong>최저:</strong> {min_temp_display:.1f}{temp_unit}</p>
            <p><strong>일교차:</strong> {temp_diff:.1f}°C</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 오른쪽 컬럼 - 온도 그래프
    with col2:
        st.subheader("📊 시간별 온도 변화")
        
        # Plotly 그래프 생성
        fig = go.Figure()
        
        # 온도 라인 추가
        fig.add_trace(go.Scatter(
            x=day_data['hour'],
            y=day_data['display_temp'],
            mode='lines+markers',
            name='온도',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8, color='#667eea'),
            hovertemplate='<b>%{x}시</b><br>온도: %{y:.1f}' + temp_unit + '<extra></extra>',
            fill='tonexty',
            fillcolor='rgba(102, 126, 234, 0.1)'
        ))
        
        # 최고/최저 온도 포인트 강조
        max_temp_hour = day_data.loc[day_data['pred_Temperature'].idxmax(), 'hour']
        min_temp_hour = day_data.loc[day_data['pred_Temperature'].idxmin(), 'hour']
        
        fig.add_trace(go.Scatter(
            x=[max_temp_hour],
            y=[max_temp_display],
            mode='markers',
            name='최고기온',
            marker=dict(size=15, color='red', symbol='triangle-up'),
            hovertemplate='<b>최고기온</b><br>%{x}시: %{y:.1f}' + temp_unit + '<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=[min_temp_hour],
            y=[min_temp_display],
            mode='markers',
            name='최저기온',
            marker=dict(size=15, color='blue', symbol='triangle-down'),
            hovertemplate='<b>최저기온</b><br>%{x}시: %{y:.1f}' + temp_unit + '<extra></extra>'
        ))
        
        # 그래프 레이아웃 설정
        fig.update_layout(
            hovermode='x unified',
            plot_bgcolor='rgba(240,242,246,0.5)',
            paper_bgcolor='white',
            font=dict(size=15, color='black'),  # 전체 폰트 설정
            height=400,
            margin=dict(l=50, r=50, t=50, b=50),
            xaxis=dict(
                dtick=5,
                gridcolor='rgba(200,200,200,0.5)',
                range=[-0.5, 23.5],
                color='black',
                title=dict(  # x축 타이틀 수정
                    text="시간 (시)",
                    font=dict(color='black')
                ),
                tickfont=dict(color='black')
            ),
            yaxis=dict(
                gridcolor='rgba(200,200,200,0.5)',
                color='black',
                title=dict(  # y축 타이틀 수정
                    text=f"온도 ({temp_unit})",
                    font=dict(color='black')
                ),
                tickfont=dict(color='black')
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    

    # style_recommendations, activity_tip = get_recommendations_by_style(avg_temp) 
    style_recommendations, activity_tip, layering_tip = generate_recommendations(avg_temp, temp_diff)

    # 2. 스타일 종류들을 탭의 이름으로 사용
    style_options = ["캐주얼", "비즈니스", "스포티", "페미닌", "미니멀"]
    tabs = st.tabs([f"👕 {s}" for s in style_options])
    
    # 3. 각 탭에 내용 채우기
    for i, tab in enumerate(tabs):
        with tab:
            current_style = style_options[i]
            st.subheader(f"'{current_style}' 스타일 추천")
            
            recs = style_recommendations.get(current_style, {})
            if not recs:
                st.write("이 스타일에 대한 추천 정보가 아직 없어요. 😢")
                continue

            # 카테고리별로 추천 아이템 표시
            for category, items in recs.items():
                if items: # 아이템이 있을 때만 표시
                    # 이모지를 사용해서 예쁘게 카테고리 이름 만들기
                    category_emoji = {"아우터": "🧥", "상의": "👕", "하의": "👖"}.get(category, "✨")
                    items_html = "".join([f'<div class="clothing-item">{item}</div>' for item in items])
                    
                    st.markdown(f"""
                    <div class="clothing-category">
                        <h4>{category_emoji} {category.capitalize()}</h4>
                        <div>{items_html}</div>
                    </div>
                    """, unsafe_allow_html=True)

    # 일교차 팁은 탭 밖에 공통으로 표시
    temp_diff = max_temp - min_temp
    layering_tip = ""
    if temp_diff >= 10:
        layering_tip = "🌡️ 일교차가 매우 큽니다! 겉옷을 여러 벌 준비하여 레이어링하세요."
    elif temp_diff >= 7:
        layering_tip = "🌡️ 일교차가 큰 편이니 얇은 겉옷을 준비하세요."
    
    if layering_tip:
        st.markdown(f"""
        <div class="tip-box" style="font-size: 20px;">
            <strong style="font-size: 25px;">💡 레이어링 팁</strong><br>
            {layering_tip}
        </div>
        """, unsafe_allow_html=True)
    
    if activity_tip:
        st.markdown(f"""
        <div class="activity-tip" style="font-size: 20px;">
            <strong style="font-size: 25px;">🎯 활동 추천</strong><br>
            {activity_tip}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 하단 - 상세 정보
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 온도 통계")
        max_temp_hour = day_data.loc[day_data['pred_Temperature'].idxmax(), 'hour']
        min_temp_hour = day_data.loc[day_data['pred_Temperature'].idxmin(), 'hour']
        
        stats_df = pd.DataFrame({
            '구분': ['최고기온', '최저기온', '평균기온', '일교차'],
            '값': [f"{max_temp_display:.1f}{temp_unit}", 
                  f"{min_temp_display:.1f}{temp_unit}", 
                  f"{avg_temp_display:.1f}{temp_unit}", 
                  f"{temp_diff:.1f}°C"],
            '시간': [f"{max_temp_hour}시", f"{min_temp_hour}시", "-", "-"]
        })
        st.dataframe(stats_df, hide_index=True, use_container_width=True)
    
    with col2:
        st.subheader("🕐 시간별 상세")
        detail_df = day_data[['hour', 'display_temp']].copy()
        detail_df.columns = ['시간', f'온도({temp_unit})']
        detail_df['시간'] = detail_df['시간'].astype(str) + '시'
        detail_df[f'온도({temp_unit})'] = detail_df[f'온도({temp_unit})'].round(1)
        st.dataframe(detail_df, hide_index=True, use_container_width=True, height=300)

if __name__ == "__main__":
    main()  