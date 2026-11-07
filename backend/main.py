"""FastAPI application entrypoint."""
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
from backend.routers.data import router as data_router
from backend.routers.chat import router as chat_router
from backend.routers.conversations import router as conversations_router
from backend.routers.firestore import router as firestore_router
from backend.routers.admin import router as admin_router

app = FastAPI(title="이우성 AI 스카우팅 비서 API", description="KBO 기록 기반 데이터 분석", version="0.3.0")
origins = [x.strip() for x in os.getenv("ALLOWED_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False,
                   allow_methods=["GET", "POST", "PUT", "DELETE"],
                   allow_headers=["Content-Type", "X-Admin-Key", "Authorization"])
app.include_router(data_router)
app.include_router(chat_router)
app.include_router(conversations_router)
app.include_router(firestore_router)
app.include_router(admin_router)

@app.get("/", tags=["시스템"])
def health_check():
    return {"status": "ok", "service": "Lee Woo-sung AI Scout", "version": "0.3.0"}
