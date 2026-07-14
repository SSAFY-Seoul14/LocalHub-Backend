from fastapi import APIRouter


router = APIRouter(
    tags=["Health"],
)


@router.get(
    "/health",
    summary="서버 상태 확인",
)
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
    }