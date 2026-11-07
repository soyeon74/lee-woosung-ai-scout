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
5. **대화 영속 저장**: 질문·답변을 Firestore `conversations` 컬렉션에 저장하고 목록·상세 조회·삭제 API를 제공합니다. 대화 목록의 삭제 버튼으로 선택한 대화를 지울 수 있습니다.
6. **웹 인터페이스**: HTML/CSS/JavaScript로 통계, 채팅, 대화 기록, 데이터 관리 화면을 구현했습니다.
7. **탭 세션 인증 편의**: 관리자 키 인증 성공 후 `sessionStorage`에 현재 탭 한정으로 보관하고 새로고침하면 복원합니다. '키 지우기'로 삭제할 수 있습니다.

## 데이터와 실제 점검 결과

2026-11-07 사용자 실행 검증 기준:

| 지표 | 검증값 |
| --- | ---: |
| 경기 기록 | **105건** |
| 총 안타 | **75안타** |
| 경기당 평균 안타 | 약 **0.714** |
| 실제 시즌 타율 (75안타 / 300타수) | **0.250** |
| 기간 | **2025-03-22 ~ 2025-10-04** |
| 최근 10경기 경기당 평균 안타 | **0.7** |
| 이전 10경기 경기당 평균 안타 | **0.6** |
| 최근 추세 | **증가** |

- 원자료 출처: [KBO 공식 타자 일별 기록 — 이우성(2025)](https://www.koreabaseball.com/Record/Player/HitterDetail/Daily.aspx?playerId=63260). 프로젝트 내부 `data/raw/lee_woosung_2025_daily.csv`를 정제하여 105개 기록을 구성했습니다.
- 원본 검산: 337타석, 300타수, 75안타, 시즌 타율 0.250. 로컬 분석 스크립트를 실행하여 `ANALYSIS_OK`를 확인했습니다. 0타수 경기 2개는 삭제하지 않았습니다.
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
.env.example
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

- 백엔드 로컬 실행 전에 `.env.example`을 `.env`로 복사하고 본인의 실제 설정을 입력해야 합니다. `OPENAI_API_KEY`, `DATA_ADMIN_KEY`, `GOOGLE_APPLICATION_CREDENTIALS`가 필수이며 `ALLOWED_ORIGINS`를 필요한 주소로 제한합니다. `.env.example`은 예시일 뿐 실제 비밀키를 포함하지 않습니다.
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

## 실제 사용 방법

1. [Vercel 웹사이트](https://lee-woosung-ai-scout-iota.vercel.app)에 접속합니다.
2. 첫 화면에서 Firestore의 경기 수·안타 합계·경기당 평균·추세를 확인합니다. 통계 조회는 관리자 키 없이 가능합니다.
3. GPT 채팅, 대화 불러오기 또는 기록 변경을 사용하려면 본인 관리자 키를 입력하고 **연결 확인**을 누릅니다. 관리자 키는 공개 문서·캡처·GitHub에 입력하지 마세요.
4. 질문 예시: **“최근 10경기와 이전 10경기의 경기당 평균 안타를 비교해줘.”** AI 답변 수치를 화면 통계와 대조합니다.
5. **대화 기록**에서 이전 대화를 선택하면 저장된 질문·답변을 다시 볼 수 있습니다. 불필요한 대화는 **대화 삭제**에서 확인 후 삭제합니다.
6. **경기 데이터 관리**에서 날짜·안타 수·메모를 지정하여 생성/수정/삭제할 수 있습니다. 실제 경기 자료 대신 임시 테스트 레코드만 사용하고 테스트 후 반드시 삭제합니다.
7. 같은 탭을 새로고침하면 인증된 키가 복원됩니다. **키 지우기**를 누르면 현재 탭의 저장된 키가 삭제됩니다. 공용 PC 사용을 금합니다.

## 오류 및 예외 처리

| 상황 | 예상 동작·해결 |
| --- | --- |
| 관리자 키가 비어 있음 | 관리자 키 입력 안내. 읽기 전용 통계는 조회 가능 |
| 관리자 키가 틀림 | API에서 HTTP 401 응답. 인증 성공 전에는 키를 세션에 저장하지 않음 |
| 필수 날짜/안타 입력이 없음 | HTML 입력 검증 및 Pydantic 검증 오류(422) |
| 음수·숫자가 아닌 안타 수 | 서버 입력 검증에서 거부 |
| 존재하지 않는 데이터나 대화 ID | 해당 API에서 HTTP 404 |
| Firestore 인증/연결 실패 | 서버에서 HTTP 503 응답, 웹 화면에 오류 메시지 |
| OpenAI 호출 실패/사용량 문제 | 채팅 API에서 HTTP 502 응답, 웹 화면에 오류 메시지 |
| 프론트에서 'Failed to fetch' 또는 CORS 오류 | Render 상태 및 `ALLOWED_ORIGINS`에 Vercel 정확한 출처가 있는지 확인 |
| Vercel 빌드 실패 | `frontend` Root Directory, Other, npm run build, dist 및 배포 로그 점검 |
| 브라우저 탭 종료 | `sessionStorage`는 일반적으로 제거되어 관리자 키 재입력이 필요할 수 있음 |

## 검증 시나리오 및 테스트 범위

| 시나리오 | 기대값/기준 | 확인 상태 |
| --- | --- | --- |
| Firestore 데이터 통계 | 105경기, 75안타, 경기당 0.714안타(검증 당시) | 사용자 실습에서 확인 |
| CRUD | 임시 기록 추가→수정→삭제 후 원래 데이터 수로 복귀 | 사용자 실습에서 확인 |
| AI 채팅 | Firestore 통계를 포함한 답변 및 대화 자동 저장 | 사용자 실습에서 확인 |
| 대화 목록·상세 불러오기 | 이전 질문·답변 재조회 | 사용자 실습에서 확인 |
| 관리자 키 새로고침 복원 | 같은 탭 F5 후 인증 복원 | 사용자 실습에서 확인 |
| Vercel 배포 | Production Ready | 사용자 배포 화면에서 확인 |
| **대화 삭제 UI** | 확인 후 대화 제거 | 코드 추가됨, 브라우저 실제 동작은 확인 필요 |
| **모바일 화면** | 510px/850px 반응형 배치 | CSS 구현 확인, 실기기 작동은 확인 필요 |
| **최신 배포·실시간 HTTP 응답** | Vercel Ready 및 Render API 200 | 별도 실시간 재확인 필요 |

위 표는 실제 사용자 검증과 코드 확인, 미검증 항목을 구분합니다. 미검증 항목을 성공으로 간주하지 않습니다.

## 사용한 AI 및 개발 과정 기록

- 사용 목적: FastAPI 데이터 API, Firestore 연계, 정적 프론트엔드, 배포/오류 진단, README 작성 보조.
- 확인 방법: Render에서 Firestore 105건 조회/요약, Swagger를 통한 채팅·대화 확인, 웹에서 CRUD 추가→수정→삭제, Vercel Production Ready, 새로고침 후 키 복원 확인.
- 해결한 문제: 사내 PC에서 gRPC DLL 실행 제한 → Render에서 백엔드 실행; Firebase 인증 파일을 Render Secret File로 구성; Vercel의 잘못된 FastAPI 프리셋을 Other/정적 빌드로 변경; CORS 출처 등록.
- 한계: 문서는 과제 개발 과정을 요약한 것으로 실제 프롬프트 로그 전체나 스크린샷을 포함하지 않습니다.

## 데이터 재검산

원본 CSV를 이용해 통계 검증 과정을 다시 실행할 수 있습니다.

```powershell
python scripts/analyze_kbo.py
```

2026-11-07 분리된 검사 환경에서 보관된 프로젝트 사본의 원자료를 재분석한 결과: **105건, 337타석, 300타수, 75안타, 타율 0.250, 0타수 기록 2건 보존, `ANALYSIS_OK`**. 이 검사는 분석 스크립트와 데이터의 정합성 검사이며 Render/Firestore 실시간 통신 검사는 아닙니다.

## 보안 및 사용 범위

- 이 저장소는 코드 공개용이며 비밀 환경변수와 서비스 계정 파일을 포함하면 안 됩니다.
- **현재 관리 인증은 과제 시연용 단일 공유 관리자 키**입니다. 실제 다중 사용자 서비스에서는 로그인, 역할별 권한, 사용량 제한 등으로 교체해야 합니다.
- 브라우저 `sessionStorage`는 안전한 비밀 보관소가 아닙니다. 스크립트 침해 또는 공유 컴퓨터 환경에서는 키 노출 위험이 있습니다.
- 공개 통계 조회는 인증이 필요 없지만, 데이터 CRUD·GPT 채팅·대화 조회는 관리자 인증이 필요합니다.
- Firebase 데이터를 외부로 게시하거나 무단 변경하지 마세요. 채팅에 개인정보·내부자료를 입력하지 마세요.

## 검증 및 증빙

필수 제출 캡처는 **통계 기반 채팅 질문·답변**, **데이터 CRUD 실제 실행**, **이전 대화 불러오기**입니다. 기능별 검증 결과와 화면 캡처 안내는 [SUBMISSION_GUIDE.md](SUBMISSION_GUIDE.md)를 참고하세요. 실제 화면 캡처는 관리자 키, 토큰, 개인 정보, 서비스 계정 인증 정보가 보이지 않게 촬영해야 합니다.

## 한계 및 개선 방향

- AI는 요약 통계 위주로 답변하므로 특정 경기별 상세 분석을 정확히 답하려면 해당 기록의 추가 조회 기능이 필요합니다.
- 최근 추세는 **시간순 마지막 10건과 이전 10건의 경기당 평균 안타를 비교**합니다. 통계적 유의성을 검정한 결과는 아닙니다.
- 정적 웹의 관리자 키는 탭 세션 저장 편의 기능만 제공하며, 실제 로그인 대체 수단은 아닙니다.
- 배포된 URL의 가동 상태는 시점에 따라 달라집니다.

---
작성/검증 기준일: **2026-11-07**. GitHub의 코드 구현과 사용자가 확인한 실습 결과를 구분하여 기록했습니다.
