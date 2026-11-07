
import getpass

from firebase_admin import auth

from backend.services.firebase_service import get_firestore_client


def main():
    # 기존 Firebase 초기화 서비스 재사용
    get_firestore_client()

    print("Firebase 관리자 권한 설정")
    uid = input("관리자 UID 입력: ").strip()

    if not uid:
        raise ValueError("UID를 입력해야 합니다.")

    user = auth.get_user(uid)

    print("대상 이메일:", user.email)
    print("대상 UID:", user.uid)

    confirm = input(
        "이 계정에 관리자 권한을 부여하시겠습니까? (YES): "
    ).strip()

    if confirm != "YES":
        print("작업을 취소했습니다.")
        return

    existing_claims = user.custom_claims or {}
    new_claims = {
        **existing_claims,
        "admin": True,
    }

    auth.set_custom_user_claims(uid, new_claims)

    updated_user = auth.get_user(uid)

    if not (updated_user.custom_claims or {}).get("admin"):
        raise RuntimeError("관리자 권한 확인에 실패했습니다.")

    print("ADMIN_CLAIM_SET_OK")
    print("ADMIN_UID:", updated_user.uid)


if __name__ == "__main__":
    main()
