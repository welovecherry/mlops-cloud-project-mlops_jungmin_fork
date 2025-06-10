import torch
import argparse
import logging

from .preprocess import Feature_Engineering
from .train import LSTM_Model, TempDataset, LSTMTrainer
from .inference import predict, save_predict

from torch.utils.data import DataLoader
from .train import seed_everything
import numpy as np
# 시드 고정
seed_everything(42)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%H:%M:%S',
    force=True)
logger = logging.getLogger(__name__)


def main(**args):
    HORIZON = 168
    SEQ_LEN = 336
    total_steps = 13
    step = 1

    logger.info(f"[{step}/{total_steps}] Start Pipeline..."); step += 1

    start_year = args.get('start_year', None)
    epochs = args.get('epochs', 20)
    batch_size = args.get('batch_size', 32)
    lr = args.get('lr', 0.0005)
    hidden_size = args.get('hidden_size', 128)
    num_layers = args.get('num_layers', 2)
    dropout = args.get('dropout', 0.3)
    patience = args.get('patience', 5)

    # Preprocessing
    fe = Feature_Engineering()
    logger.info(f"[{step}/{total_steps}] Loading Data from S3..."); step += 1
    df = fe.load_data(start_year=start_year)
    logger.info(f"[{step}/{total_steps}] S3 loading complete. Loaded {df.shape[0]} rows, {df.shape[1]} columns."); step += 1

    logger.info(f"[{step}/{total_steps}] Start Data Preprocessing..."); step += 1
    df = fe.missing_value()
    df = fe.impossible_negative()
    df = fe.feature_selection(target_col='Temperature')
    df = fe.add_feature()

    logger.info(f"[{step}/{total_steps}] Start Feature Engineering..."); step += 1
    train_df, val_df, latest_df = fe.split_data(HORIZON=HORIZON, SEQ_LEN=SEQ_LEN)
    train, val, latest = fe.scaler(train_df, val_df, latest_df)
    train, val, latest, latest_time = fe.encoding(train, val, latest)
    logger.info(f"[{step}/{total_steps}] Data Preprocessing complete."); step += 1
    fe.save_split_data(train, val, latest) # S3 Save
    logger.info(f"[{step}/{total_steps}] Total Features: {train.shape[1]} | Split Datasets Saved to S3"); step += 1

    # DataLoader
    logger.info(f"[{step}/{total_steps}] Creating Data Loaders..."); step += 1
    train_dataset = TempDataset(train, label_col='Temperature', horizon=HORIZON, seq_len=SEQ_LEN)
    val_dataset = TempDataset(val, label_col='Temperature', horizon=HORIZON, seq_len=SEQ_LEN)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    logger.info(f"[{step}/{total_steps}] Data Loaders Ready."); step += 1

    # Model Training
    logger.info(f"[{step}/{total_steps}] Start Model Training..."); step += 1
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    input_size = train.shape[1] - 1
    model = LSTM_Model(input_size=input_size, hidden_size=hidden_size,
                       num_layers=num_layers, output_size=HORIZON, dropout=dropout)
    

    trainer = LSTMTrainer(model, device, lr=lr, input_size=input_size)
    trainer.train(train_loader, val_loader, start_year=start_year,epochs=epochs, batch_size=batch_size, patience=patience)

    logger.info(f"[{step}/{total_steps}] Model Training complete."); step += 1

    # Inference
    logger.info(f"[{step}/{total_steps}] Running Inference..."); step += 1
    latest_seq = latest.drop(columns=['Temperature']).values[-SEQ_LEN:].astype(np.float32)
    pred_df = predict(trainer.model, device, latest_seq, latest_time, horizon=HORIZON)
    save_path = save_predict(pred_df)
    logger.info(f"[{step}/{total_steps}] Inference complete. Predictions saved to: {save_path}"); step += 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start_year", type=int, default=None, help="데이터 수집 시작 연도")
    parser.add_argument("--epochs", type=int, default=15, help="학습 epoch 수")
    parser.add_argument("--batch_size", type=int, default=32, help="배치 사이즈")
    parser.add_argument("--lr", type=float, default=0.001, help="학습률")
    parser.add_argument("--hidden_size", type=int, default=128, help="LSTM hidden size")
    parser.add_argument("--num_layers", type=int, default=2, help="LSTM layer 수")
    parser.add_argument("--dropout", type=float, default=0.3, help="Dropout rate")
    parser.add_argument("--patience", type=int, default=5, help="조기 종료 기준 에폭 수")
    args = parser.parse_args()
    main(
        start_year=args.start_year,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        hidden_size=args.hidden_size,
        num_layers=args.num_layers,
        dropout=args.dropout,
        patience=args.patience
    )
