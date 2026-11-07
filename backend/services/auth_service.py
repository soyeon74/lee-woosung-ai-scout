
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth

from backend.services.firebase_service import get_firestore_client


bearer_scheme = HTTPBearer(
    auto_error=False,
    description="Firebase Authentication ID Token",
)


def require_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
):
    """Firebase 로그인 토큰과 관리자 권한을 검증합니다."""

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요합니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 기존 Firebase Admin SDK 초기화
    get_firestore_client()

    try:
        decoded_token = auth.verify_id_token(
            credentials.credentials,
            check_revoked=True,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않거나 만료된 로그인 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if decoded_token.get("admin") is not True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 없습니다.",
        )

    return {
        "uid": decoded_token["uid"],
        "admin": True,
    }
