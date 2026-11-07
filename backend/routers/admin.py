
from fastapi import APIRouter, Depends

from backend.services.auth_service import require_admin

router = APIRouter(
    prefix="/api/admin",
    tags=["관리자 인증"],
)


@router.get("/me")
def read_admin_profile(
    admin: dict = Depends(require_admin),
):
    return {
        "authenticated": True,
        "role": "admin",
        "uid": admin["uid"],
    }
