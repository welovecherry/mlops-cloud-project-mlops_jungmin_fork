#!/bin/bash

mlflow server --host 0.0.0.0 --port 5001 --backend-store-uri sqlite:///mlflow.db --default-artifact-root s3://mlops-prj/data/weather/model/