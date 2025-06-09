import numpy as np
import torch
import torch.nn as nn
import pandas as pd
import s3fs
import mlflow
import mlflow.pytorch
import getpass
from datetime import datetime
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import mean_squared_error

class TempDataset(Dataset):
    def __init__(self, df, label_col, horizon, seq_len):
        self.seq_len = seq_len
        self.horizon = horizon
        self.X = df.drop(columns=[label_col]).values.astype(np.float32)
        self.y = df[label_col].values.astype(np.float32)
        self.input_len = len(self.X) - seq_len - horizon + 1

    def __len__(self):
        return self.input_len

    def __getitem__(self, idx):
        X_seq = self.X[idx: idx + self.seq_len]
        y_seq = self.y[idx + self.seq_len: idx + self.seq_len + self.horizon]
        return torch.tensor(X_seq), torch.tensor(y_seq)


class LSTM_Model(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size, dropout=0.2):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=dropout)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        lstm_out, _ = self.lstm(x)  # [B, seq_len, H]
        last_out = lstm_out[:, -1, :]  # [B, H]
        output = self.fc(last_out)     # [B, horizon]
        return output

class LSTMTrainer:
    def __init__(self, model, device, lr=0.001, input_size=None):
        self.model = model.to(device)
        self.device = device
        self.criterion = nn.MSELoss()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        self.train_losses = []
        self.val_losses = []
        self.input_size = input_size

    def train(self, train_loader, val_loader, epochs, batch_size, patience=5):
        best_val_loss = float('inf')
        best_rmse = None
        best_train_loss = None
        best_model = None
        wait = 0
        start_time = datetime.now()  

        mlflow.set_tracking_uri("http://mlflow:5001")
        mlflow.set_experiment("LSTM-Weather")
        timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M")
        run_name = f"LSTM_{timestamp}"

        with mlflow.start_run(run_name=run_name): # 학습 전부터 run 시작

            for epoch in range(1, epochs + 1):
                self.model.train()
                train_loss = 0.0
                for X, y in train_loader:
                    X, y = X.to(self.device), y.to(self.device)
                    self.optimizer.zero_grad()
                    pred = self.model(X)
                    loss = self.criterion(pred, y)
                    loss.backward()
                    self.optimizer.step()
                    train_loss += loss.item()
                train_loss /= len(train_loader)

                # Validation
                self.model.eval()
                val_loss = 0.0
                all_preds, all_labels = [], []
                with torch.no_grad():
                    for Xv, yv in val_loader:
                        Xv, yv = Xv.to(self.device), yv.to(self.device)
                        pred = self.model(Xv)
                        loss = self.criterion(pred, yv)
                        val_loss += loss.item()
                        all_preds.extend(pred.cpu().numpy())
                        all_labels.extend(yv.cpu().numpy())
                val_loss /= len(val_loader)
                mse = mean_squared_error(all_labels, all_preds)
                rmse = np.sqrt(mse)

                self.train_losses.append(train_loss)
                self.val_losses.append(val_loss)

                print(f"[Epoch {epoch}] Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | RMSE: {rmse:.4f}")

                # epoch별 로그 기록
                mlflow.log_metric("epoch_train_loss", train_loss, step=epoch)
                mlflow.log_metric("epoch_val_loss", val_loss, step=epoch)
                mlflow.log_metric("epoch_rmse", rmse, step=epoch)

                # Early stopping
                if val_loss < best_val_loss:  # Validation loss 기준으로 가장 좋은 모델 저장
                    best_val_loss = val_loss
                    best_model = self.model.state_dict()
                    best_rmse = rmse
                    best_train_loss = train_loss
                    wait = 0
                else:
                    wait += 1
                    if wait >= patience:
                        print(f"Early stopping triggered at epoch {epoch}.")
                        break

            if best_model is not None:
                self.model.load_state_dict(best_model)

                # Hyperparameters
                mlflow.log_param("hidden_size", self.model.lstm.hidden_size)
                mlflow.log_param("num_layers", self.model.lstm.num_layers)
                mlflow.log_param("dropout", self.model.lstm.dropout)
                mlflow.log_param("learning_rate", self.optimizer.param_groups[0]['lr'])
                mlflow.log_param("epochs", epochs)
                mlflow.log_param("batch_size", batch_size)

                # Best Metrics
                mlflow.log_metric("Best_Train_loss", best_train_loss)
                mlflow.log_metric("Best_Val_loss", best_val_loss)
                mlflow.log_metric("Best_RMSE", best_rmse)

                # Training Time 
                end_time = datetime.now()
                duration_sec = (end_time - start_time).total_seconds()
                duration_str = str(end_time - start_time).split('.')[0]
                mlflow.log_metric("Training_Time", duration_sec)
                mlflow.set_tag("Training_duration", duration_str)
                mlflow.set_tag("Trained_at", end_time.strftime('%Y-%m-%d %H:%M:%S'))
                mlflow.set_tag("training_started_at", start_time.strftime('%Y-%m-%d %H:%M:%S'))  

                # Register model (version-controlled)
                seq_len = 336  # 시퀀스 길이
                input_example = torch.randn(1, seq_len, self.input_size).cpu().numpy()
                mlflow.pytorch.log_model(self.model, artifact_path="model", registered_model_name="LSTM-Weather", input_example=input_example)