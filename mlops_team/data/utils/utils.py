# -*- coding: utf-8 -*-

import os
import random
import requests
import numpy as np
import json
import re
import pandas as pd

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
    df = pd.DataFrame(forecast_list)[['aplYmd','maxTmpr','minTmpr','dayString']]
    date = pd.DataFrame([{"year":i.year,'month':i.month,'day':i.day} for i in pd.to_datetime(df['aplYmd'], format='%Y%m%d')])
    df = pd.concat([date,df],axis=1)
    df.drop(columns=['aplYmd'],inplace=True)
    df.rename(columns={'maxTmpr':'max_temp','minTmpr':'min_temp','dayString':'day_of_week'},inplace=True)
    to_english = {'월':'Monday',
    '화':'Tuesday',
    '수':'Wednesday',
    '목':'Thursday',
    '금':'Friday',
    '토':'Saturday',
    '일':'Sunday',}
    df['day_of_week'] = df['day_of_week'].map(to_english)
    return df
