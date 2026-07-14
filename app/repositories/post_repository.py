from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.post import Post


def create_post(
    db: Session,
    title: str,
    content: str,
    nickname: str,
    password: str,
) -> Post:
    """
    새로운 게시글을 생성한다.

    비밀번호는 현재 프로젝트 요구사항에 따라
    전달받은 값을 그대로 DB에 저장한다.
    """

    post = Post(
        title=title,
        content=content,
        nickname=nickname,
        password=password,
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return post


def get_posts(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    keyword: str | None = None,
) -> list[Post]:
    """
    게시글 목록을 최신순으로 조회한다.

    keyword가 있으면 제목, 내용, 닉네임에서 검색한다.
    """

    statement = select(Post)

    if keyword:
        search_keyword = f"%{keyword}%"

        statement = statement.where(
            or_(
                Post.title.ilike(search_keyword),
                Post.content.ilike(search_keyword),
                Post.nickname.ilike(search_keyword),
            )
        )

    statement = (
        statement
        .order_by(Post.id.desc())
        .offset(skip)
        .limit(limit)
    )

    posts = db.scalars(statement).all()

    return list(posts)


def count_posts(
    db: Session,
    keyword: str | None = None,
) -> int:
    """
    검색 조건에 해당하는 전체 게시글 수를 반환한다.

    페이지네이션의 전체 페이지 수 계산에 사용한다.
    """

    statement = select(func.count(Post.id))

    if keyword:
        search_keyword = f"%{keyword}%"

        statement = statement.where(
            or_(
                Post.title.ilike(search_keyword),
                Post.content.ilike(search_keyword),
                Post.nickname.ilike(search_keyword),
            )
        )

    total = db.scalar(statement)

    return total or 0


def get_post_by_id(
    db: Session,
    post_id: int,
) -> Post | None:
    """
    게시글 ID로 게시글 한 건을 조회한다.

    게시글이 없으면 None을 반환한다.
    """

    statement = select(Post).where(Post.id == post_id)

    post = db.scalar(statement)

    return post


def increment_view_count(
    db: Session,
    post: Post,
) -> Post:
    """
    게시글 조회수를 1 증가시킨다.
    """

    post.view_count += 1

    db.commit()
    db.refresh(post)

    return post


def update_post(
    db: Session,
    post: Post,
    title: str,
    content: str,
) -> Post:
    """
    기존 게시글의 제목과 내용을 수정한다.

    비밀번호 확인은 Repository가 아닌 Service에서 처리한다.
    """

    post.title = title
    post.content = content

    db.commit()
    db.refresh(post)

    return post


def delete_post(
    db: Session,
    post: Post,
) -> None:
    """
    게시글을 삭제한다.

    비밀번호 확인은 Repository가 아닌 Service에서 처리한다.
    """

    db.delete(post)
    db.commit()