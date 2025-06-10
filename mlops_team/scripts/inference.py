import torch
import pandas as pd
import s3fs
import numpy as np
from datetime import datetime, timedelta


# 예측
def predict(model, device, latest_seq, latest_time, horizon=168):
    model.eval()
    with torch.no_grad():
        inp = torch.tensor(latest_seq, dtype=torch.float32).unsqueeze(0).to(device)  # [1, seq_len, input_size]
        output = model(inp)  # [1, horizon]
        preds = output.cpu().numpy().flatten()

    # 예측 시점 생성
    last_row = latest_time.iloc[-1]
    last_time = datetime(
        year=int(last_row["year"]),
        month=int(last_row["month"]),
        day=int(last_row["day"]),
        hour=int(last_row["hour"])
    )
    future_times = [last_time + timedelta(hours=i + 1) for i in range(horizon)]

    df = pd.DataFrame({
        'year': [t.year for t in future_times],
        'month': [t.month for t in future_times],
        'day': [t.day for t in future_times],
        'hour': [t.hour for t in future_times],
        'day_of_week': [t.strftime('%A') for t in future_times],
        'pred_Temperature': np.round(preds, 1)})
    return df


# S3 저장
def save_predict(pred_df, s3_bucket='mlops-prj', prefix='data/weather/inference/'):
    now = datetime.now().strftime('%Y%m%d_%H%M')
    file_path = f"{prefix}forecast_{now}.parquet"
    full_path = f"s3://{s3_bucket}/{file_path}"

    s3 = s3fs.S3FileSystem()
    pred_df.to_parquet(full_path, index=False, engine='pyarrow', filesystem=s3)
    print(f"예측 결과 저장 완료: {full_path}")
    return full_path


