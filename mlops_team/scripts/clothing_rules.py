def get_cloth_sense(temp: float, sensitivity: str = "normal") -> str:
    """
    temp: 예측된 기온 (float)
    sensitivity: 'cold' (추위를 많이 탐), 'normal' (보통), 'hot' (더위를 많이 탐)
    """
    # 민감도에 따라 체감 온도 보정값 설정
    if sensitivity == "cold":
        adj_temp = temp - 2  # 추위를 많이 타면 체감 온도를 2도 낮게
    elif sensitivity == "hot":
        adj_temp = temp + 2  # 더위를 많이 타면 체감 온도를 2도 높게
    else:
        adj_temp = temp

    if adj_temp >= 25:
        return f"예상 기온({temp:.1f}°C: 반팔과 시원한 옷차림 추천! ☀️"
    elif 20 <= adj_temp < 25:
        return f"예상 기온({temp:.1f}°C: 얇은 긴팔/반팔+가벼운 겉옷 추천 😄"
    elif 15 <= adj_temp < 20:
        return f"예상 기온({temp:.1f}°C: 긴팔+가디건/자켓 추천 🧥"
    elif 10 <= adj_temp < 15:
        return f"예상 기온({temp:.1f}°C: 스웨터/경량 패딩 추천 🌬️"
    else:
        return f"예상 기온({temp:.1f}°C: 두꺼운 외투와 따뜻한 옷차림 필수! 🥶"