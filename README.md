# 이우성 AI 스카우팅 비서

**2025 KBO 경기별 타격 기록을 기반으로 한 시계열 데이터 관리·통계·생성형 AI 질의응답 웹 애플리케이션**

> 학습·과제 제출용 시제품입니다. AI 답변은 전문 스카우팅 평가가 아니며, 제공된 Firestore 요약 통계 밖의 사실은 검증이 필요합니다.

## 바로가기

| 항목 | URL |
| --- | --- |
| 웹사이트 (Vercel) | https://lee-woosung-ai-scout-iota.vercel.app |
| 백엔드 API (Render) | https://lee-woosung-ai-scout.onrender.com |
| API 문서 (FastAPI Swagger) | https://lee-woosung-ai-scout.onrender.com/docs |
| GitHub 코드 | https://github.com/soyeon74/lee-woosung-ai-scout |

## 주요 기능

1. **시계열 데이터**: Firestore `data` 컬렉션에서 날짜·안타 수·메모를 읽고 최신순 목록으로 표시합니다.
2. **CRUD**: 관리자 인증 후 `POST`, `PUT`, `DELETE`로 기록을 추가·수정·삭제합니다.
3. **자동 통계**: 경기 수, 안타 합계, 경기당 평균 안타, 최고·최저 안타, 최근 10경기와 이전 10경기의 추세를 계산합니다.
4. **GPT 채팅**: 질문과 함께 *현재 Firestore에서 계산한 요약 정보*를 모델에 전달하여 답변을 생성합니다.
5. **대화 영속 저장**: 질문·답변을 Firestore `conversations` 컬렉션에 저장하고 목록·상세 조회·삭제 API를 제공합니다.
6. **웹 인터페이스**: HTML/CSS/JavaScript로 통계, 채팅, 대화 기록, 데이터 관리 화면을 구현했습니다.
7. **탭 세션 인증 편의**: 관리자 키 인증 성공 후 `sessionStorage`에 현재 탭 한정으로 보관하고 새로고침하면 복원합니다. '키 지우기'로 삭제할 수 있습니다.

## 데이터와 실제 점검 결과

2026-11-07 사용자 실행 검증 기준:

| 지표 | 검증값 |
| --- | ---: |
| 경기 기록 | **105건** |
| 총 안타 | **75안타** |
| 경기당 평균 안타 | 약 **0.714** |
| 기간 | **2025-03-22 ~ 2025-10-04** |
| 최근 10경기 경기당 평균 안타 | **0.7** |
| 이전 10경기 경기당 평균 안타 | **0.6** |
| 최근 추세 | **증가** |

- `value`는 경기별 **안타 수(H)** 입니다. **경기당 평균 안타를 타율로 해석하면 안 됩니다.**
- 추가 → 수정 → 삭제의 실제 CRUD 테스트 이후 기존 105건과 75안타로 복원되었음을 사용자가 확인했습니다.
- 채팅 응답과 Firestore 대화 저장·조회, Vercel 배포(`Ready`), 새로고침 후 관리자 키 자동 복원을 사용자 화면에서 확인했습니다.
- 서비스가 실행 중인 시점의 데이터는 변경될 수 있으며, 위 값은 고정된 기록이 아닌 검증 당시 수치입니다.

## 기술 스택 및 구성

- **Frontend**: Vanilla HTML, CSS, JavaScript, Vercel 정적 웹 배포
- **Backend**: Python 3.12, FastAPI, Pydantic, Uvicorn, Render
- **DB**: Firebase Cloud Firestore (자료 `data`, 대화 `conversations`)
- **AI**: OpenAI API (`OPENAI_MODEL` 기본값 `gpt-4o-mini`)
- **연결**: HTTPS JSON REST API, 허용 출처 기반 CORS

```text
사용자 브라우저 (Vercel HTML/JS)
   ├─ GET /api/data, /api/data/summary
   └─ 관리자 키가 필요한 CRUD/채팅/대화 관리
                  │ HTTPS
                  ▼
             Render FastAPI
            ├─ Firestore data ── 통계 계산
            ├─ Firestore conversations ── 대화 저장/조회
            └─ OpenAI API ── 요약 통계 기반 답변
```

## 주요 API

| 메서드 | 경로 | 기능 | 관리자 키 |
| --- | --- | --- | --- |
| GET | `/` | 서버 상태 | 불필요 |
| GET | `/api/data` | 기록 목록 | 불필요 |
| GET | `/api/data/summary` | 통계와 최근 추세 | 불필요 |
| POST | `/api/data` | 기록 생성 | 필요 |
| PUT | `/api/data/{id}` | 기록 수정 | 필요 |
| DELETE | `/api/data/{id}` | 기록 삭제 | 필요 |
| POST | `/api/chat` | GPT 답변 생성 및 대화 저장 | 필요 |
| POST | `/api/conversations` | 대화 저장 | 필요 |
| GET | `/api/conversations` | 대화 목록 | 필요 |
| GET | `/api/conversations/{id}` | 대화 상세 | 필요 |
| DELETE | `/api/conversations/{id}` | 대화 삭제 | 필요 |

관리자 인증은 요청 헤더 `x-admin-key`로 수행합니다. 데이터 입력 형식의 예는 `{"date":"2026-11-07","value":2,"memo":"검증용"}` 입니다. 실제 자료를 수정하지 않도록 주의하세요.

## 폴더 구조

```text
backend/
  main.py                  # FastAPI 진입점 및 CORS
  routers/
    data.py                # Firestore CRUD와 요약
    chat.py                # GPT 답변 및 대화 자동 저장
    conversations.py       # 대화 관리
    firestore.py           # 경기 기록 조회 보조 API
    admin.py               # 별도 관리자 API
  services/                # Firebase 및 인증 유틸리티
frontend/
  index.html               # 웹 화면
  styles.css               # 스타일
  app.js                   # API 호출 및 화면 이벤트
  config.js                # 공개 API 주소 (로컬 기본값)
  build.mjs                # Vercel 정적 빌드
  package.json             # npm build 명령
requirements.txt
.gitignore
README.md
SUBMISSION_GUIDE.md
```

## 로컬 실행

```powershell
git clone https://github.com/soyeon74/lee-woosung-ai-scout.git
cd lee-woosung-ai-scout
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

- 백엔드 로컬 실행에는 **본인 소유의 Firebase 인증 설정**과 환경변수가 별도로 필요합니다. 인증 파일을 저장소에 커밋하지 마세요.
- 웹 화면만 로컬 실행할 때:

```powershell
py -3.12 -m http.server 5500 --directory frontend
```

로컬 주소: `http://localhost:5500`. `frontend/config.js`의 공개 Render API 주소를 사용합니다.

## 배포 설정

### Render (FastAPI)

- Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- 주요 환경변수: `OPENAI_API_KEY`, `DATA_ADMIN_KEY`, `GOOGLE_APPLICATION_CREDENTIALS`, `ALLOWED_ORIGINS`
- Firebase 서비스 계정 인증파일은 **Render Secret File**로 관리합니다.
- `ALLOWED_ORIGINS`에는 실제 Vercel 주소와 필요한 로컬 주소만 쉼표로 구분해 설정합니다.

### Vercel (정적 웹)

- Root Directory: `frontend`
- Framework Preset: `Other`
- Build Command: `npm run build`
- Output Directory: `dist`
- Install Command: `npm install`
- 공개 환경변수: `API_BASE_URL=https://lee-woosung-ai-scout.onrender.com`

`build.mjs`는 공개 API URL을 `dist/config.js`에 작성합니다. **관리자 키·OpenAI 키·Firebase 인증키를 Vercel 프론트엔드 설정이나 코드에 넣으면 안 됩니다.**

## 보안 및 사용 범위

- 이 저장소는 코드 공개용이며 비밀 환경변수와 서비스 계정 파일을 포함하면 안 됩니다.
- **현재 관리 인증은 과제 시연용 단일 공유 관리자 키**입니다. 실제 다중 사용자 서비스에서는 로그인, 역할별 권한, 사용량 제한 등으로 교체해야 합니다.
- 브라우저 `sessionStorage`는 안전한 비밀 보관소가 아닙니다. 스크립트 침해 또는 공유 컴퓨터 환경에서는 키 노출 위험이 있습니다.
- 공개 통계 조회는 인증이 필요 없지만, 데이터 CRUD·GPT 채팅·대화 조회는 관리자 인증이 필요합니다.
- Firebase 데이터를 외부로 게시하거나 무단 변경하지 마세요. 채팅에 개인정보·내부자료를 입력하지 마세요.

## 검증 및 증빙

기능별 검증 결과와 화면 캡처 안내는 [SUBMISSION_GUIDE.md](SUBMISSION_GUIDE.md)를 참고하세요. 실제 화면 캡처는 관리자 키, 토큰, 개인 정보, 서비스 계정 인증 정보가 보이지 않게 촬영해야 합니다.

## 한계 및 개선 방향

- AI는 요약 통계 위주로 답변하므로 특정 경기별 상세 분석을 정확히 답하려면 해당 기록의 추가 조회 기능이 필요합니다.
- 최근 추세는 **시간순 마지막 10건과 이전 10건의 경기당 평균 안타를 비교**합니다. 통계적 유의성을 검정한 결과는 아닙니다.
- 정적 웹의 관리자 키는 탭 세션 저장 편의 기능만 제공하며, 실제 로그인 대체 수단은 아닙니다.
- 배포된 URL의 가동 상태는 시점에 따라 달라집니다.

---
작성/검증 기준일: **2026-11-07**. GitHub의 코드 구현과 사용자가 확인한 실습 결과를 구분하여 기록했습니다.
