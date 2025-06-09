# -*- coding: utf-8 -*-

import os
import random
import requests
import numpy as np
import json
import re

def init_seed():
    np.random.seed(0)
    random.seed(0)


def project_path():

    return os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)
        ),
        "..",
        ".."
    )



def model_dir(model_name):
    return os.path.join(
        project_path(),
        "models",
        model_name
    )


def auto_increment_run_suffix(name: str, pad=3):
    suffix = name.split("-")[-1]
    next_suffix = str(int(suffix) + 1).zfill(pad)
    return name.replace(suffix, next_suffix)

def get_naver_weather():
    req = requests.get('https://weather.naver.com/today/09140550')
    pattern = r'"domesticWeeklyFcastList"\s*:\s*(\[\{.*?\}\])'
    match = re.search(pattern, req.text, re.DOTALL)
    json_str = match.group(1)
    forecast_list = json.loads(json_str)
    df = pd.DataFrame(forecast_list)

    korean_keys = [
    "지역코드", "시도", "시군구", "읍면동", "예보일", "예보일시",
    "오전날씨코드", "오전날씨", "오전강수확률",
    "오후날씨코드", "오후날씨", "오후강수확률",
    "최저기온", "최고기온", "예보갱신시간", "요일"
    ]
    df.columns = korean_keys
    return df