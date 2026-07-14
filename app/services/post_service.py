from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.post import Post
from app.repositories import post_repository
from app.schemas.post import (
    PostCreate,
    PostDelete,
    PostDeleteResponse,
    PostListResponse,
    PostUpdate,
)


def create_post(
    db: Session,
    post_data: PostCreate,
) -> Post:
    """
    게시글을 생성한다.

    현재 프로젝트 요구사항에 따라 비밀번호를 평문으로 저장한다.
    응답 스키마에는 비밀번호를 포함하지 않는다.
    """

    return post_repository.create_post(
        db=db,
        title=post_data.title,
        content=post_data.content,
        nickname=post_data.nickname,
        password=post_data.password,
    )


def get_post_list(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    keyword: str | None = None,
) -> PostListResponse:
    """
    게시글 목록과 전체 게시글 수를 반환한다.

    keyword가 있으면 제목, 내용, 닉네임을 검색한다.
    """

    normalized_keyword = normalize_keyword(keyword)

    posts = post_repository.get_posts(
        db=db,
        skip=skip,
        limit=limit,
        keyword=normalized_keyword,
    )

    total = post_repository.count_posts(
        db=db,
        keyword=normalized_keyword,
    )

    return PostListResponse(
        total=total,
        skip=skip,
        limit=limit,
        posts=posts,
    )


def get_post_detail(
    db: Session,
    post_id: int,
) -> Post:
    """
    게시글 상세 정보를 조회한다.

    게시글이 존재하면 조회수를 1 증가시킨 후 반환한다.
    """

    post = get_existing_post(
        db=db,
        post_id=post_id,
    )

    return post_repository.increment_view_count(
        db=db,
        post=post,
    )


def update_post(
    db: Session,
    post_id: int,
    post_data: PostUpdate,
) -> Post:
    """
    게시글 비밀번호를 확인한 뒤 제목과 내용을 수정한다.
    """

    post = get_existing_post(
        db=db,
        post_id=post_id,
    )

    verify_password(
        saved_password=post.password,
        input_password=post_data.password,
    )

    return post_repository.update_post(
        db=db,
        post=post,
        title=post_data.title,
        content=post_data.content,
    )


def delete_post(
    db: Session,
    post_id: int,
    post_data: PostDelete,
) -> PostDeleteResponse:
    """
    게시글 비밀번호를 확인한 뒤 게시글을 삭제한다.
    """

    post = get_existing_post(
        db=db,
        post_id=post_id,
    )

    verify_password(
        saved_password=post.password,
        input_password=post_data.password,
    )

    post_repository.delete_post(
        db=db,
        post=post,
    )

    return PostDeleteResponse(
        message="게시글이 삭제되었습니다.",
    )


def get_existing_post(
    db: Session,
    post_id: int,
) -> Post:
    """
    게시글을 조회하고, 존재하지 않으면 404 오류를 발생시킨다.
    """

    post = post_repository.get_post_by_id(
        db=db,
        post_id=post_id,
    )

    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다.",
        )

    return post


def verify_password(
    saved_password: str,
    input_password: str,
) -> None:
    """
    저장된 비밀번호와 사용자가 입력한 비밀번호를 비교한다.

    일치하지 않으면 403 오류를 발생시킨다.
    """

    if saved_password != input_password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비밀번호가 일치하지 않습니다.",
        )


def normalize_keyword(
    keyword: str | None,
) -> str | None:
    """
    검색어 앞뒤 공백을 제거한다.

    검색어가 없거나 공백만 있으면 None을 반환한다.
    """

    if keyword is None:
        return None

    normalized_keyword = keyword.strip()

    if not normalized_keyword:
        return None

    return normalized_keyword