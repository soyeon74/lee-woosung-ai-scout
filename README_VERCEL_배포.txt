이우성 AI 스카우팅 비서 - Vercel 배포용 프론트엔드

1. 이 ZIP을 프로젝트 최상위 폴더(C:\AI-Projects\lee-woosung-ai-scout)에 압축 해제하여 frontend 폴더를 덮어쓰기 합니다.
2. frontend 내의 index.html, styles.css, app.js, config.js, package.json, build.mjs, .gitignore가 있는지 확인합니다.
3. GitHub main에 frontend/ 폴더를 커밋하고 푸시합니다.
4. Vercel New Project에서 GitHub 저장소 soyeon74/lee-woosung-ai-scout 선택
5. Root Directory: frontend
   Framework Preset: Other
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm install (기본값)
6. Environment Variable: API_BASE_URL = https://lee-woosung-ai-scout.onrender.com
7. Deploy 후 실제 Vercel URL이 정해지면 Render의 ALLOWED_ORIGINS에 URL을 추가하고 재배포합니다.
   예) http://localhost:5500,https://<실제-프로젝트>.vercel.app

보안:
- API_BASE_URL은 공개된 API 주소입니다. Firebase 키/OpenAI 키/DATA_ADMIN_KEY는 Vercel 환경변수나 소스코드에 등록하지 마세요.
- 이 프론트는 학습용입니다. 입력된 관리자 키를 브라우저 메모리에서 사용하여 API에 전달합니다. 공개 서비스로 전환하기 전에 실제 로그인/사용자별 권한 체계가 필요합니다.
- 기존 관리자 키 스크린샷이 노출되었으므로 반드시 교체된 키를 사용하세요.
