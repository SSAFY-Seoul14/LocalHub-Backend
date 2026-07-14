# LocalHub Backend

FastAPI 기반 LocalHub 백엔드 프로젝트입니다.

서울 관광 데이터를 SQLite에 저장하여 장소 검색 및 조회 API를 제공하며,
게시판 CRUD와 Kakao Maps/OpenStreetMap API를 연동합니다.

---

# Tech Stack

- Python 3.11.x
- FastAPI
- SQLAlchemy
- SQLite
- HTTPX
- Pydantic Settings

---

# Project Structure

```
LocalHub-Backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── health.py
│   │       ├── places.py
│   │       ├── posts.py
│   │       └── maps.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── place.py
│   │   └── post.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── place.py
│   │   ├── post.py
│   │   └── map.py
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── place_repository.py
│   │   └── post_repository.py
│   │
│   └── services/
│       ├── __init__.py
│       ├── place_service.py
│       ├── post_service.py
│       ├── kakao_service.py
│       └── osm_service.py
│
├── data/
│   ├── 서울/
│   └── localhub.db
│
├── scripts/
│   └── import_places.py
│
├── tests/
│   ├── test_places.py
│   └── test_posts.py
│
├── (.env)
├── .gitignore
├── requirements.txt
└── README.md
```

---

# Directory Description

| Directory | Description |
|------------|-------------|
| app/api/routes | API Endpoint 정의 |
| app/core | 프로젝트 설정 |
| app/db | SQLite 연결 및 Session 관리 |
| app/models | SQLAlchemy ORM 모델 |
| app/schemas | Request / Response Schema |
| app/repositories | DB 접근 계층 |
| app/services | 비즈니스 로직 |
| data | JSON 데이터 및 SQLite DB |
| scripts | 데이터 적재 스크립트 |
| tests | 테스트 코드 |

---

# Development Environment

| Item | Version |
|------|---------|
| Python | 3.11.x |
| Database | SQLite |
| Framework | FastAPI |

Python 확인

```bash
python --version
```

---

# Installation

## 1. Clone Repository

```bash
git clone <repository-url>
```

```bash
cd LocalHub-Backend
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
```

---

## 3. Activate Virtual Environment

### Git Bash

```bash
source venv/Scripts/activate
```

### PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

---

## 4. Install Packages

```bash
pip install -r requirements.txt
```

---

# Database

JSON 데이터를 SQLite 데이터베이스로 변환합니다.

```
data/
└── 서울/
    ├── 서울_관광지.json
    ├── ...
```

데이터 적재

```bash
python scripts/import_places.py
```

실행 후

```
data/localhub.db
```

가 생성됩니다.

---

# Run Server

```bash
fastapi dev app/main.py
```

또는

```bash
uvicorn app.main:app --reload
```

---

# API Documentation

Swagger

```
http://127.0.0.1:8000/docs
```

ReDoc

```
http://127.0.0.1:8000/redoc
```

---

# Architecture

```
Frontend
      │
      ▼
Router
      │
      ▼
Service
      │
      ▼
Repository
      │
      ▼
SQLite
```

외부 지도 API 사용 시

```
Frontend
      │
      ▼
Router
      │
      ▼
Service
      │
 ┌────┴────┐
 ▼         ▼
SQLite   Kakao / OSM API
```

---

# Data Flow

초기 데이터 적재

```
JSON
    │
    ▼
import_places.py
    │
    ▼
SQLite
```

서비스 실행

```
SQLite
    │
    ▼
Repository
    │
    ▼
Service
    │
    ▼
Router
    │
    ▼
Frontend
```

---

# API Plan

## Health

```
GET /health
```

---

## Places

```
GET /places
GET /places/{id}
GET /places/nearby
GET /places/search
```

---

## Maps

```
GET /maps/reverse-geocode
GET /maps/search
```

---

## Posts

```
GET /posts
GET /posts/{id}

POST /posts

PUT /posts/{id}

DELETE /posts/{id}
```

---

# Git Workflow

최신 코드 가져오기

```bash
git pull origin main
```

브랜치 생성

```bash
git switch -c feature/기능명
```

예시

```bash
git switch -c feature/place-api
git switch -c feature/post-crud
```

작업 완료

```bash
git add .
git commit -m "feat: 장소 조회 API"
git push origin feature/place-api
```

---

# Commit Convention

```
feat
fix
docs
refactor
test
chore
```

예시

```
feat: 게시글 CRUD 구현
feat: 장소 검색 API 구현
fix: SQLite 조회 오류 수정
docs: README 수정
```

---

# Development Roadmap

### Phase 1
- [x] FastAPI 프로젝트 생성
- [x] SQLite 구축
- [x] JSON → SQLite 적재

### Phase 2
- [ ] Place Repository
- [ ] Place API
- [ ] Pagination
- [ ] Keyword Search

### Phase 3
- [ ] Kakao Maps API 연동
- [ ] OpenStreetMap 연동
- [ ] 좌표 기반 주변 장소 검색

### Phase 4
- [ ] 게시판 CRUD
- [ ] 게시글 검색
- [ ] 댓글 기능
- [ ] 이미지 업로드

---

# Data Source

- 한국관광공사 TourAPI 4.0
- 서울 관광 공공데이터