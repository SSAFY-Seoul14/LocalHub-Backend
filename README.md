# LocalHub Backend

LocalHub 프로젝트의 FastAPI 기반 백엔드 서버입니다.

지도 좌표와 장소 데이터를 관리하며, SQLite 데이터베이스와 Kakao Maps API, OpenStreetMap API를 연동할 예정입니다.

## 기술 스택

* Python 3.11
* FastAPI
* SQLite
* SQLAlchemy
* HTTPX
* Pydantic Settings

## 프로젝트 구조

```text
LocalHub-Backend/
├── app/
│   └── main.py
├── venv/
├── .gitignore
├── .env
├── .env.example
├── requirements.txt
└── README.md
```

프로젝트가 진행되면서 API, 데이터베이스, 모델, 서비스 폴더를 추가할 예정입니다.

## 개발 환경

* Python 3.11.x
* 현재 기준 개발 버전: Python 3.11.9

Python 버전 확인:

```bash
python --version
```

## 프로젝트 실행 방법

### 1. 저장소 복제

```bash
git clone <GitHub 저장소 주소>
```

저장소 폴더로 이동합니다.

```bash
cd LocalHub-Backend
```

### 2. 가상환경 생성

Windows Git Bash 기준:

```bash
python -m venv venv
```

### 3. 가상환경 활성화

Git Bash:

```bash
source venv/Scripts/activate
```

PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

CMD:

```cmd
venv\Scripts\activate
```

가상환경이 활성화되면 터미널 앞에 `(venv)`가 표시됩니다.

### 4. 패키지 설치

```bash
pip install -r requirements.txt
```

### 5. 환경변수 설정

`.env.example` 파일을 복사하여 `.env` 파일을 생성합니다.

Git Bash:

```bash
cp .env.example .env
```

Windows CMD:

```cmd
copy .env.example .env
```

`.env` 파일에는 실제 API 키와 로컬 환경 설정을 입력합니다.

실제 `.env` 파일은 GitHub에 올리지 않습니다.

### 6. 서버 실행

```bash
fastapi dev app/main.py
```

또는 다음 명령으로 실행할 수 있습니다.

```bash
uvicorn app.main:app --reload
```

### 7. 서버 확인

기본 서버 주소:

```text
http://127.0.0.1:8000
```

Swagger API 문서:

```text
http://127.0.0.1:8000/docs
```

ReDoc API 문서:

```text
http://127.0.0.1:8000/redoc
```

## 가상환경 종료

```bash
deactivate
```

## 패키지 추가 방법

새 패키지를 설치할 때는 반드시 가상환경이 활성화된 상태에서 설치합니다.

```bash
pip install 패키지명
```

설치 후 현재 패키지 버전을 저장합니다.

```bash
pip freeze > requirements.txt
```

패키지를 추가한 팀원은 변경된 `requirements.txt`도 함께 커밋해야 합니다.

## 데이터베이스 계획

SQLite를 사용하여 기존 JSON 장소 데이터를 데이터베이스로 이전할 예정입니다.

예상 작업 순서는 다음과 같습니다.

```text
JSON 데이터 구조 확인
→ SQLite 테이블 설계
→ SQLAlchemy 모델 작성
→ SQLite 데이터베이스 생성
→ JSON 데이터 적재
→ FastAPI 조회 API 구현
```

SQLite 데이터베이스 파일은 각 개발자의 로컬 환경에서 생성하며 GitHub에는 올리지 않습니다.

## 지도 API 계획

다음 외부 서비스를 연동할 예정입니다.

* Kakao Maps Local API
* OpenStreetMap 기반 API
* 필요 시 Nominatim 또는 Overpass API

API 키는 소스 코드에 직접 작성하지 않고 `.env` 파일에서 관리합니다.

## Git 작업 규칙

작업을 시작하기 전에 원격 변경 내용을 가져옵니다.

```bash
git pull origin main
```

기능별 브랜치를 생성합니다.

```bash
git switch -c feature/기능이름
```

예시:

```bash
git switch -c feature/database
git switch -c feature/place-api
git switch -c feature/map-api
```

변경 사항을 저장합니다.

```bash
git add .
git commit -m "feat: 작업 내용"
git push origin 브랜치이름
```

## 커밋 메시지 규칙

```text
feat: 새로운 기능
fix: 버그 수정
docs: 문서 수정
refactor: 코드 구조 개선
test: 테스트 추가 또는 수정
chore: 환경 설정 및 기타 작업
```

예시:

```text
feat: FastAPI 서버 초기 설정
docs: README 실행 방법 추가
chore: requirements 파일 추가
```
