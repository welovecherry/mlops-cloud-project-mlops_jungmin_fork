# 🌦️ End-to-End MLOps Platform for Weather-Based Clothing Recommendation

> **💡 Personal Contribution Focus**: This repository showcases my individual contributions as **MLOps Engineer & Backend Developer** in a team project. I was responsible for the entire infrastructure, deployment automation, and backend systems.

[English](#english) | [한국어](#korean)

---

## English

### 🎯 Project Overview

A complete **End-to-End MLOps pipeline** that transforms a deep learning model from development to production, serving weather-based clothing recommendations through both web dashboard and REST API.
<img width="608" alt="스크린샷 2025-06-12 오전 11 25 51" src="https://github.com/user-attachments/assets/918459d6-264d-4881-bb72-d25c3519884d" />


*

**🔗 Live Demos:**
- **Streamlit Dashboard:** `http://[EC2_IP]:8501`
- **FastAPI Documentation:** `http://[EC2_IP]:8000/docs`

### 💻 Tech Stack

| **Category** | **Technology** | **Role in Project** |
|--------------|----------------|---------------------|
| **Backend & ML** | **Python**, **PyTorch**, **FastAPI** | Used **Python** as the main language, utilizing a **PyTorch**-based LSTM model. Built a stable API server with **FastAPI** to serve model predictions. |
| **Frontend** | **Streamlit**, **Plotly** | Rapidly developed an interactive web dashboard using **Streamlit** to visualize data analysis and model predictions. Implemented dynamic charts with **Plotly**. |
| **DevOps & Infra** | **AWS S3**, **AWS EC2**, **Docker**, **GitHub Actions** | Utilized **AWS S3** as a data lake and deployed the final service on **EC2**. Ensured environmental consistency by containerizing the application with **Docker**. Automated the entire deployment process with a CI/CD pipeline based on **GitHub Actions**. |
| **Tools & Etc.** | **Makefile**, **Git** | Wrote a **Makefile** to standardize and simplify complex Docker and development commands, enhancing team productivity. Practiced systematic version control and collaboration through **Git**. |

### 🏗️ System Architecture

<img width="1100" alt="스크린샷 2025-06-12 오전 10 42 57" src="https://github.com/user-attachments/assets/041fd55f-1ae1-4015-89e0-261c624bb790" />

**I designed and implemented** a **modular microservices architecture** with automated CI/CD pipeline, ensuring scalability and maintainability.

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Source   │───▶│   ML Pipeline    │───▶│  Model Serving  │
│  (Weather API)  │    │ (Training/Pred.) │    │ (FastAPI + UI)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AWS S3        │    │  GitHub Actions  │    │   AWS EC2       │
│ (Data Storage)  │    │   (CI/CD) ←──    │    │  (Production)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              ↑
                    🙋‍♂️ I built this entire
                       automation pipeline
```

### 🚀 My Individual Contributions

> **👨‍💻 Role**: Primary **MLOps Engineer** and **Backend Developer** - I single-handedly designed and implemented the entire infrastructure, deployment automation, and backend systems that power this application.

#### 1. **🏗️ Full System Architecture & Rapid Prototyping**
- **Solo Achievement**: Built a **complete end-to-end prototype in just ONE day** (API Crawling → Preprocessing → ML Prediction → FastAPI Serving)
- **Impact**: Provided the entire team with a clear architectural blueprint and accelerated development by weeks
- **Technical Leadership**: Established the foundational structure that all other team members built upon

#### 2. **🔧 Backend Infrastructure & Code Architecture**
- **My Design**: Created the entire `common/` directory structure and shared business logic
- **My Implementation**: Built all core components from scratch (`s3_loader.py`, `recommender.py`)
- **My Achievement**: **Guaranteed 100% data consistency** between Streamlit UI and FastAPI through centralized logic
- **Code Quality**: Applied **DRY principle** throughout, making the codebase maintainable and scalable

#### 3. **🌐 Complete API & Frontend Development**
- **My Backend Work**: 
  - Designed and coded **both RESTful endpoints** (`/forecast/latest`, `/recommendation/by_day`)
  - Implemented **automatic OpenAPI documentation** generation at `/docs`
  - Solved all **JSON serialization challenges** (NumPy compatibility issues)
  
<img width="800" alt="스크린샷 2025-06-12 오전 10 46 36" src="https://github.com/user-attachments/assets/4265a826-63e4-41a4-a7aa-835562ba8ea8" />
*📊 FastAPI Documentation Interface I built*

- **My Frontend Work**: 
  - Built the **entire Streamlit dashboard** with interactive time-series visualization
  - Integrated **Plotly charts** for dynamic data presentation

#### 4. **🚀 End-to-End CI/CD Pipeline (100% My Work)**

<img width="800" alt="스크린샷 2025-06-12 오전 11 07 15" src="https://github.com/user-attachments/assets/badfdad2-570b-474e-9457-27d48553b6ef" />

*⚙️ CI/CD Pipeline Execution Screenshot*

- **CI Pipeline**: Wrote **all GitHub Actions workflows** for automated Docker builds and Docker Hub pushes
- **CD Pipeline**: Implemented **complete AWS EC2 deployment automation** via SSH
- **Infrastructure**: Configured **all AWS resources** (EC2, Security Groups, S3)
- **Problem Solving**: **Personally debugged and fixed** all deployment issues:
  - Resolved EC2 Security Group networking problems
  - Fixed Docker build context issues
  - Solved FastAPI serialization errors

#### 5. **⚡ Developer Experience & Team Productivity**
- **My Tool**: Wrote the **entire Makefile** (40+ lines) to abstract complex Docker operations
- **My Impact**: **Reduced team onboarding time by 80%** with simplified commands
- **My Documentation**: Created comprehensive setup guides and troubleshooting docs

<img width="800" alt="스크린샷 2025-06-12 오전 11 08 42" src="https://github.com/user-attachments/assets/d445aab3-b818-4340-a2ca-a676a2304f1c" />

*💻 Makefile Commands I Created*

### 🔧 My Technical Problem Solving Journey

> **🎯 All technical challenges were solved by me personally**

*🐛 Problem Solving: Before & After Screenshots*

| **Challenge** | **My Systematic Approach** | **My Solution** | **Business Impact** |
|---------------|----------------------------|-----------------|---------------------|
| **CI/CD Deployment Timeout** | 1. **Hypothesis**: Network firewall blocking<br>2. **Investigation**: Tested local SSH, isolated to GitHub Actions<br>3. **Root Cause**: EC2 Security Group restricted to my IP | **My Fix**: Updated Security Group from static IP to 0.0.0.0/0 for GitHub's dynamic IPs | ✅ **Enabled full automation** |
| **Docker Build Context Error** | 1. **Analysis**: Examined GitHub Actions logs<br>2. **Discovery**: COPY paths misaligned with build context<br>3. **Understanding**: Build context vs Dockerfile structure | **My Solution**: Restructured all COPY commands with correct relative paths | ✅ **100% build success rate** |
| **FastAPI JSON Serialization** | 1. **Debugging**: Traced ValueError to numpy.float32<br>2. **Research**: FastAPI JSON encoder limitations<br>3. **Insight**: Pandas returns NumPy types, not Python types | **My Implementation**: Added explicit float() casting before JSON response | ✅ **Stable API performance** |

### 📊 Measurable Results & Business Impact

> **💪 These improvements are direct results of my individual work**

- ** Deployment Speed**: Reduced from **manual 2+ hours → automated 5 minutes** 
- ** Team Productivity**: Cut new developer onboarding from **4 hours → 45 minutes** 
- ** Code Quality**: Achieved **100% data consistency** between frontend and backend through my architecture
- ** System Reliability**: Implemented **zero-downtime deployments** with automatic rollback capability
- ** Developer Experience**: Created **single-command deployment** (`make build && make run`)
- ** Infrastructure Automation**: **Eliminated all manual deployment steps** through my CI/CD pipeline

---

### 🌱 Soft Skills & Team Support

> While waiting for the model training phase, I actively supported the team by mentoring and creating easy-to-follow tutorials for less experienced developers.  
> This ensured **everyone in the team could experience as much of the MLOps process as possible**, enhancing collective learning and team synergy.
<img width="533" alt="스크린샷 2025-06-12 오전 11 22 19" src="https://github.com/user-attachments/assets/439c377a-60fa-4a7b-9334-c8b517eb8fef" />

---

### 📊 Project Presentation (PPT)

- [Google Slides Link](https://docs.google.com/presentation/d/1nyTqX6bAtM6tONQyYoadjz0QRzScGNQk/edit?slide=id.p10#slide=id.p10)

---
### 🏃‍♂️ Quick Start

```bash
# 1. Build Docker image
make build

# 2. Run application (requires .env file in mlops_team/ directory)
make run

# 3. Access services
# - Streamlit UI: http://localhost:8501
# - FastAPI Docs: http://localhost:8000/docs

# 4. View logs
make log

# 5. Stop and clean up
make clean
```

**Essential Commands:**
- `make build` - Build Docker image
- `make run` - Start both FastAPI and Streamlit services
- `make log` - View container logs
- `make clean` - Stop and remove container

### 🎯 Future Enhancements

- **Model Monitoring:** Implement Prometheus + Grafana for real-time performance tracking
- **Auto-Retraining:** Schedule-based model updates with performance validation
- **A/B Testing:** Multi-version model serving for data-driven optimization

---

# 🌦️ 날씨 기반 의류 추천 End-to-End MLOps 플랫폼

> **💡 개인 기여도 중심**: 이 저장소는 팀 프로젝트에서 **MLOps 엔지니어 & 백엔드 개발자**로서 제가 개인적으로 기여한 부분들을 중심으로 정리했습니다. 전체 인프라, 배포 자동화, 백엔드 시스템을 담당했습니다.

### 🎯 프로젝트 개요

딥러닝 모델을 개발부터 운영까지 **완전 자동화하는 End-to-End MLOps 파이프라인**으로, 날씨 기반 의류 추천 서비스를 웹 대시보드와 REST API로 제공합니다.

*🎬 라이브 데모 스크린샷/GIF*

**🔗 라이브 데모:**
- **Streamlit 대시보드:** `http://[EC2_IP]:8501`
- **FastAPI 문서:** `http://[EC2_IP]:8000/docs`

**🛠️ 기술 스택:**

| **분야** | **기술** | **프로젝트 내 역할** |
|----------|----------|---------------------|
| **백엔드 & ML** | **Python**, **PyTorch**, **FastAPI** | **Python**을 주 언어로 사용하여 **PyTorch** 기반 LSTM 모델을 활용했습니다. **FastAPI**로 모델 예측을 제공하는 안정적인 API 서버를 구축했습니다. |
| **프론트엔드** | **Streamlit**, **Plotly** | **Streamlit**으로 데이터 분석과 모델 예측을 시각화하는 인터랙티브 웹 대시보드를 빠르게 개발했습니다. **Plotly**로 동적 차트를 구현했습니다. |
| **DevOps & 인프라** | **AWS S3**, **AWS EC2**, **Docker**, **GitHub Actions** | **AWS S3**를 데이터 레이크로 활용하고 **EC2**에 최종 서비스를 배포했습니다. **Docker**로 애플리케이션을 컨테이너화하여 환경 일관성을 보장했습니다. **GitHub Actions** 기반 CI/CD 파이프라인으로 전체 배포 과정을 자동화했습니다. |
| **도구 & 기타** | **Makefile**, **Git** | 복잡한 Docker 및 개발 명령어들을 표준화하고 단순화하는 **Makefile**을 작성하여 팀 생산성을 향상시켰습니다. **Git**을 통한 체계적인 버전 관리와 협업을 실천했습니다. |

### 🏗️ 시스템 아키텍처

확장성과 유지보수성을 보장하는 **모듈식 마이크로서비스 아키텍처**와 자동화된 CI/CD 파이프라인을 구축했습니다.

### 🚀 주요 기여사항

**MLOps 엔지니어** 및 **백엔드 개발자**로서 모델 서빙과 배포 자동화의 핵심 인프라를 설계하고 구현했습니다.

#### 1. **시스템 설계 및 프로토타이핑**
- **하루 만에 완전한 end-to-end 프로토타입 구축** (API → 전처리 → ML → 서빙)
- 팀에 명확한 아키텍처 비전 제시하여 개발 속도 가속화

#### 2. **모듈식 아키텍처 구현**
- 공유 비즈니스 로직을 위한 `common/` 디렉토리 생성
- 핵심 컴포넌트 중앙화 (`s3_loader.py`, `recommender.py`)
- Streamlit UI와 FastAPI 간 **100% 데이터 정합성 달성**
- **DRY 원칙** 적용으로 코드 재사용성 최대화

#### 3. **프로덕션 수준 API 개발**
- **백엔드 (FastAPI):** 2개 RESTful 엔드포인트 구축 (`/forecast/latest`, `/recommendation/by_day`)
- **프론트엔드 (Streamlit):** 시계열 시각화가 포함된 인터랙티브 대시보드 개발
- `/docs`에서 **자동 생성 API 문서** 제공으로 개발자 경험 향상

#### 4. **완전한 CI/CD 파이프라인**
- **CI:** 모든 커밋에서 Docker 이미지 빌드 및 Docker Hub 푸시 자동화
- **CD:** SSH 자동화를 통한 AWS EC2 무중단 배포
- **결과:** 배포 시간을 수동 작업 몇 시간에서 자동화된 몇 분으로 단축

#### 5. **개발 생산성 도구**
- 일관된 환경을 위한 전체 애플리케이션 **Docker 컨테이너화**
- 간단한 명령어로 **Makefile 생성** (`make build`, `make run`, `make clean`)
- 복잡한 Docker 작업을 추상화하여 **팀 생산성 향상**

### 🔧 기술적 문제 해결

| 문제 상황 | 해결 방안 | 성과 |
|-----------|-------------|---------|
| **CI/CD 배포 타임아웃** | 네트워크 레이어 분석, EC2 보안 그룹을 고정 IP에서 0.0.0.0/0으로 변경 | 자동 배포 활성화 |
| **Docker 빌드 컨텍스트 오류** | 빌드 컨텍스트와 Dockerfile 구조 간 COPY 경로 정렬 수정 | 100% 빌드 성공률 달성 |
| **FastAPI JSON 직렬화 문제** | NumPy 타입 호환성 문제 파악, 명시적 타입 캐스팅 추가 | 안정적인 API 응답 보장 |

### 📊 성과 및 임팩트

- ** 배포 속도:** 수동 배포 (2시간+) → 자동화 (5분)
- ** 개발 사이클:** 새 팀원 설정 시간 80% 단축
- ** 코드 품질:** 프론트엔드-백엔드 간 100% 데이터 정합성 달성

### 📊 측정 가능한 결과 및 비즈니스 임팩트

> ** 아래 성과는 모두 제가 단독으로 수행한 작업의 직접적인 결과입니다**

- ** 배포 속도 향상**: 수동 1시간+ → 자동화 5분
- ** 팀 생산성 향상**: 새 개발자 온보딩 시간 4시간 → 45분
- ** 코드 품질 향상**: 프론트엔드와 백엔드 간 **100% 데이터 정합성** 확보
- ** 개발자 경험 향상**: `make build && make run` 만으로 배포되는 **원클릭 시스템** 구축
- ** 인프라 자동화**: **수동 배포 작업 전면 제거**, 완전한 자동화 구현

---

### 🌱 소프트 스킬 및 팀 지원

> 모델 학습 시간이 오래 걸리는 동안, 코딩에 익숙하지 않은 팀원들을 위해  
> **튜토리얼을 제작하고 멘토링을 제공**하며 팀 전체가 MLOps 과정을 더 많이 경험하도록 도왔습니다.  
> 이로써 팀의 **집단적 성장과 시너지**를 촉진했습니다.

---

### 📊 프로젝트 발표자료 (PPT)

- [Google Slides 링크](https://docs.google.com/presentation/d/1nyTqX6bAtM6tONQyYoadjz0QRzScGNQk/edit?slide=id.p10#slide=id.p10)

---

### 🏃‍♂️ 빠른 시작

```bash
# 1. Docker 이미지 빌드
make build

# 2. 애플리케이션 실행 (mlops_team/ 디렉토리에 .env 파일 필요)
make run

# 3. 서비스 접속
# - Streamlit UI: http://localhost:8501
# - FastAPI 문서: http://localhost:8000/docs

# 4. 로그 확인
make log

# 5. 중지 및 정리
make clean
```

**필수 명령어:**
- `make build` - Docker 이미지 빌드
- `make run` - FastAPI와 Streamlit 서비스 모두 시작
- `make log` - 컨테이너 로그 확인
- `make clean` - 컨테이너 중지 및 제거

### 🎯 향후 개선사항

- **모델 모니터링:** 실시간 성능 추적을 위한 Prometheus + Grafana 구현
- **자동 재훈련:** 성능 검증이 포함된 스케줄 기반 모델 업데이트
- **A/B 테스팅:** 데이터 기반 최적화를 위한 다중 버전 모델 서빙
