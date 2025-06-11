# ---------------- 기본 설정 ----------------
IMAGE_NAME = weather-app
CONTAINER_NAME = weather-app-container

AIRFLOW_IMAGE = airflow-img
AIRFLOW_CONTAINER = airflow-container

# ---------------- Weather App (FastAPI + Streamlit) ----------------
# build:
# 	@echo "Building Docker image: $(IMAGE_NAME)..."
# 	docker build -t $(IMAGE_NAME) -f mlops_team/app/Dockerfile.app .

build:
	@echo "Building Docker image: $(IMAGE_NAME)..."
	docker build -t $(IMAGE_NAME) -f mlops_team/app/Dockerfile.app mlops_team

run:
	@echo "Running Docker container: $(CONTAINER_NAME)..."
	-docker rm -f $(CONTAINER_NAME)
	docker run -d -p 8000:8000 -p 8501:8501 --name $(CONTAINER_NAME) --env-file mlops_team/.env $(IMAGE_NAME)
log:
	@echo "Showing logs for container: $(CONTAINER_NAME)..."
	docker logs -f $(CONTAINER_NAME)

stop:
	@echo "Stopping container: $(CONTAINER_NAME)..."
	docker stop $(CONTAINER_NAME)

rm:
	@echo "Removing container: $(CONTAINER_NAME)..."
	docker rm $(CONTAINER_NAME)

clean:
	@echo "Cleaning up Docker resources for $(CONTAINER_NAME)..."
	$(MAKE) stop rm
rebuild:
	@echo "Rebuilding the Docker image and restarting the container..."
	-docker rm -f $(CONTAINER_NAME)
	$(MAKE) build
	$(MAKE) run
restart:
	@echo "Restarting $(CONTAINER_NAME)..."
	$(MAKE) stop rm run

ps:
	@echo "Checking running containers..."
	docker ps

# ---------------- Airflow ----------------
build-airflow:
	@echo "Building Docker image: $(AIRFLOW_IMAGE)..."
	docker build -t $(AIRFLOW_IMAGE) -f mlops_team/Dockerfile.airflow .

run-airflow:
	@echo "Running Airflow container: $(AIRFLOW_CONTAINER)..."
	docker run -d -p 8181:8181 --name $(AIRFLOW_CONTAINER) $(AIRFLOW_IMAGE)

log-airflow:
	@echo "Showing logs for container: $(AIRFLOW_CONTAINER)..."
	docker logs -f $(AIRFLOW_CONTAINER)

stop-airflow:
	@echo "Stopping container: $(AIRFLOW_CONTAINER)..."
	docker stop $(AIRFLOW_CONTAINER)

rm-airflow:
	@echo "Removing container: $(AIRFLOW_CONTAINER)..."
	docker rm $(AIRFLOW_CONTAINER)

clean-airflow:
	@echo "Cleaning up Docker resources for $(AIRFLOW_CONTAINER)..."
	$(MAKE) stop-airflow rm-airflow

rebuild-airflow:
	@echo "Rebuilding and restarting $(AIRFLOW_CONTAINER)..."
	$(MAKE) clean-airflow build-airflow run-airflow

restart-airflow:
	@echo " Restarting $(AIRFLOW_CONTAINER)..."
	$(MAKE) stop-airflow rm-airflow run-airflow

# ---------------- 로컬 개발용 ----------------
dev-api:
	@echo "Starting FastAPI dev server..."
	cd mlops_team && uvicorn src.main:app --reload

dev-streamlit:
	@echo "Starting Streamlit dev server..."
	streamlit run mlops_team/streamlit_app/dashboard.py

# ---------------- MLOps 전체 파이프라인 ----------------
run-pipeline:
	@echo " Running the full MLOps pipeline..."
	python mlops_team/scripts/pipeline.py

# ---------------- 포트 점유 프로세스 종료 ----------------
kill-port:
	@read -p " 종료할 포트 번호를 입력하세요: " port; \
	pid=$$(lsof -ti tcp:$$port); \
	if [ -n "$$pid" ]; then \
		echo "포트 $$port 사용 중인 PID: $$pid, 강제 종료합니다..."; \
		kill -9 $$pid; \
	else \
		echo "포트 $$port 는 사용 중이지 않습니다."; \
	fi

.PHONY: \
	build run log stop rm clean rebuild restart ps \
	build-airflow run-airflow log-airflow stop-airflow rm-airflow clean-airflow rebuild-airflow restart-airflow \
	dev-api dev-streamlit run-pipeline