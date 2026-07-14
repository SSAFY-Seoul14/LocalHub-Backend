from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.post import (
    PostCreate,
    PostDelete,
    PostDeleteResponse,
    PostDetailResponse,
    PostListResponse,
    PostUpdate,
)
from app.services import post_service


router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
)


@router.get(
    "",
    response_model=PostListResponse,
    summary="게시글 목록 조회",
    description="게시글 목록을 최신순으로 조회합니다.",
)
def get_posts(
    db: Annotated[Session, Depends(get_db)],
    skip: Annotated[
        int,
        Query(
            ge=0,
            description="건너뛸 게시글 수",
        ),
    ] = 0,
    limit: Annotated[
        int,
        Query(
            ge=1,
            le=100,
            description="조회할 게시글 수",
        ),
    ] = 20,
    keyword: Annotated[
        str | None,
        Query(
            max_length=100,
            description="제목, 내용, 닉네임 검색어",
        ),
    ] = None,
) -> PostListResponse:
    """
    게시글 목록을 조회한다.

    - 기본 20개 조회
    - 최대 100개 조회
    - 최신 게시글부터 정렬
    - 제목, 내용, 닉네임 검색 지원
    """

    return post_service.get_post_list(
        db=db,
        skip=skip,
        limit=limit,
        keyword=keyword,
    )


@router.get(
    "/{post_id}",
    response_model=PostDetailResponse,
    summary="게시글 상세 조회",
    description="게시글 한 건을 조회하고 조회수를 1 증가시킵니다.",
)
def get_post(
    post_id: Annotated[
        int,
        Path(
            ge=1,
            description="조회할 게시글 번호",
        ),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> PostDetailResponse:
    """
    게시글 상세 내용을 조회한다.

    게시글이 존재하지 않으면 404 오류를 반환한다.
    상세 조회에 성공하면 조회수가 1 증가한다.
    """

    return post_service.get_post_detail(
        db=db,
        post_id=post_id,
    )


@router.post(
    "",
    response_model=PostDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="게시글 작성",
    description="새로운 익명 게시글을 작성합니다.",
)
def create_post(
    post_data: PostCreate,
    db: Annotated[Session, Depends(get_db)],
) -> PostDetailResponse:
    """
    새로운 게시글을 생성한다.

    비밀번호는 수정 및 삭제 시 확인에 사용되며,
    API 응답에는 포함되지 않는다.
    """

    return post_service.create_post(
        db=db,
        post_data=post_data,
    )


@router.put(
    "/{post_id}",
    response_model=PostDetailResponse,
    summary="게시글 수정",
    description="비밀번호 확인 후 게시글 제목과 내용을 수정합니다.",
)
def update_post(
    post_id: Annotated[
        int,
        Path(
            ge=1,
            description="수정할 게시글 번호",
        ),
    ],
    post_data: PostUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> PostDetailResponse:
    """
    게시글의 제목과 내용을 수정한다.

    작성할 때 사용한 비밀번호가 일치해야 한다.
    """

    return post_service.update_post(
        db=db,
        post_id=post_id,
        post_data=post_data,
    )


@router.delete(
    "/{post_id}",
    response_model=PostDeleteResponse,
    summary="게시글 삭제",
    description="비밀번호 확인 후 게시글을 삭제합니다.",
)
def delete_post(
    post_id: Annotated[
        int,
        Path(
            ge=1,
            description="삭제할 게시글 번호",
        ),
    ],
    post_data: PostDelete,
    db: Annotated[Session, Depends(get_db)],
) -> PostDeleteResponse:
    """
    게시글을 삭제한다.

    작성할 때 사용한 비밀번호가 일치해야 한다.
    """

    return post_service.delete_post(
        db=db,
        post_id=post_id,
        post_data=post_data,
    )