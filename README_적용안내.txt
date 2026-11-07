2차 패치: AI 채팅 + 대화 기록 (기존 CRUD 패치 1차 적용 완료 전제)

1. FastAPI 서버 Ctrl+C 종료.
2. 기존 backend/main.py 백업.
3. ZIP을 프로젝트 루트 C:\AI-Projects\lee-woosung-ai-scout 에 압축 해제. 동일한 파일 backend/main.py는 덮어쓰기.
4. .venv\Scripts\python.exe -m pip install openai
5. OPENAI_API_KEY, DATA_ADMIN_KEY, GOOGLE_APPLICATION_CREDENTIALS 환경변수는 안전하게 별도 설정.
6. .venv\Scripts\python.exe -m uvicorn backend.main:app --reload
7. http://127.0.0.1:8000/docs 에서 POST /api/chat, POST/GET/GET {id}/DELETE /api/conversations 확인.

주의:
- 사내 PC의 Windows Code Integrity 정책 때문에 grpc의 cygrpc 모듈이 차단된 경우 /docs 표시는 가능하지만 Firestore 연동과 /api/chat 호출은 실패합니다.
- 회사 보안 정책을 우회하지 마세요. 허용된 환경(또는 승인된 Render 배포)에서 기능 테스트해야 합니다.
- 비밀키(.env, 서비스계정 JSON, OPENAI_API_KEY, DATA_ADMIN_KEY) 파일을 ZIP이나 GitHub에 포함하지 마세요.
- ChatGPT 구독과 OpenAI API 요금은 별도입니다. 사용량 제한을 설정하세요.
- 이 단계는 서버 코드 등록 테스트용이며, 실제 운영을 위한 사용자별 권한 분리는 아직 구현하지 않았습니다.
