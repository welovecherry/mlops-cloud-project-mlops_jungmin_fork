import requests
import os
import json
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
# 이 스크립트(check_kma_api.py)가 mlops_team 폴더 안에 있고,
# .env 파일이 mlops_jungmin_branch_250602 (상위) 폴더에 있다고 가정
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env') # .env 파일 경로 설정
load_dotenv(dotenv_path=dotenv_path)

AUTH_KEY = os.getenv('AUTH_KEY')
KMA_API_URL = 'https://apihub.kma.go.kr/api/typ01/url/kma_sfctm3.php' # 사용자가 제공한 URL

def check_kma_weather_api():
    if not AUTH_KEY:
        print("AUTH_KEY가 .env 파일에 설정되지 않았거나 파일을 찾을 수 없습니다.")
        print(f".env 파일 예상 경로: {dotenv_path}")
        return

    params = {
        'authKey': AUTH_KEY,
        'pageNo': 1,            # 페이지 번호
        'numOfRows': 10,        # 한 페이지 결과 수 (테스트용으로 작게 설정)
        'dataType': 'JSON',     # 응답 데이터 타입 (JSON 또는 XML)
        'stnIds': '159',        # 지점 번호 (159는 부산) - 여러 지점은 콤마로 구분
        # 'schList': 'TMN,TMX', # 예시: 일최저기온, 일최고기온 (필요한 관측 요소 지정 가능)
        # 'schListSub': '',     # 예시: 세부 관측 요소
    }

    try:
        response = requests.get(KMA_API_URL, params=params, timeout=10)
        response.raise_for_status()  # 오류가 발생하면 예외를 발생시킴

        print(f"API 요청 URL: {response.url}") # 실제 요청된 URL 확인
        print(f"응답 상태 코드: {response.status_code}")

        # 응답 내용 확인 (JSON 형식이라고 가정)
        try:
            data = response.json()
            print("--- API 응답 (JSON 파싱) ---")
            # JSON 데이터를 예쁘게 출력
            print(json.dumps(data, indent=4, ensure_ascii=False))

            # 데이터의 시간 간격 확인을 위한 추가 정보 출력 (예시)
            if 'response' in data and 'body' in data['response'] and 'items' in data['response']['body']:
                items = data['response']['body']['items']['item']
                if items and isinstance(items, list) and len(items) > 0:
                    print("\n--- 첫 번째 데이터 항목의 시간 관련 정보 (예상) ---")
                    # API 응답 구조에 따라 'tm', 'obsTime', 'dataTime' 등 시간 필드명이 다를 수 있음
                    # 실제 필드명을 확인하고 수정해야 함
                    first_item = items[0]
                    time_keys = ['tm', 'TM', 'obsTime', 'dataTime', 'dt'] # 예상되는 시간 관련 키
                    for key in time_keys:
                        if key in first_item:
                            print(f"'{key}': {first_item[key]}")
                    if len(items) > 1:
                        second_item = items[1]
                        print("\n--- 두 번째 데이터 항목의 시간 관련 정보 (예상) ---")
                        for key in time_keys:
                            if key in second_item:
                                print(f"'{key}': {second_item[key]}")


        except json.JSONDecodeError:
            print("--- API 응답 (JSON 파싱 실패, 원본 텍스트) ---")
            print(response.text)

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 오류 발생: {http_err}")
        print(f"응답 내용: {response.text if response else '응답 없음'}")
    except requests.exceptions.RequestException as req_err:
        print(f"요청 중 오류 발생: {req_err}")
    except Exception as e:
        print(f"알 수 없는 오류 발생: {e}")

if __name__ == "__main__":
    check_kma_weather_api()