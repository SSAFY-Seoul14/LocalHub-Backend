from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PostCreate(BaseModel):
    """
    게시글 작성 요청 스키마
    """

    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="게시글 제목",
        examples=["서울숲 다녀왔어요"],
    )

    content: str = Field(
        ...,
        min_length=1,
        description="게시글 내용",
        examples=["서울숲 산책 후기입니다."],
    )

    nickname: str = Field(
        ...,
        min_length=1,
        max_length=30,
        description="익명 작성자 닉네임",
        examples=["여행자"],
    )

    password: str = Field(
        ...,
        min_length=4,
        max_length=50,
        description="게시글 수정 및 삭제용 비밀번호",
        examples=["1234"],
    )

    @field_validator("title", "content", "nickname")
    @classmethod
    def validate_not_blank(cls, value: str) -> str:
        """
        공백만 입력되는 것을 방지한다.
        """

        stripped_value = value.strip()

        if not stripped_value:
            raise ValueError("공백만 입력할 수 없습니다.")

        return stripped_value


class PostUpdate(BaseModel):
    """
    게시글 수정 요청 스키마
    """

    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="수정할 게시글 제목",
        examples=["수정된 제목"],
    )

    content: str = Field(
        ...,
        min_length=1,
        description="수정할 게시글 내용",
        examples=["수정된 게시글 내용입니다."],
    )

    password: str = Field(
        ...,
        min_length=4,
        max_length=50,
        description="게시글 작성 시 사용한 비밀번호",
        examples=["1234"],
    )

    @field_validator("title", "content")
    @classmethod
    def validate_not_blank(cls, value: str) -> str:
        """
        제목과 내용에 공백만 입력되는 것을 방지한다.
        """

        stripped_value = value.strip()

        if not stripped_value:
            raise ValueError("공백만 입력할 수 없습니다.")

        return stripped_value


class PostDelete(BaseModel):
    """
    게시글 삭제 요청 스키마
    """

    password: str = Field(
        ...,
        min_length=4,
        max_length=50,
        description="게시글 작성 시 사용한 비밀번호",
        examples=["1234"],
    )


class PostListItem(BaseModel):
    """
    게시글 목록의 개별 항목
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    nickname: str
    view_count: int
    created_at: datetime
    updated_at: datetime


class PostListResponse(BaseModel):
    """
    게시글 목록 응답 스키마
    """

    total: int = Field(
        ...,
        ge=0,
        description="검색 조건에 해당하는 전체 게시글 수",
    )

    skip: int = Field(
        ...,
        ge=0,
        description="건너뛴 게시글 수",
    )

    limit: int = Field(
        ...,
        ge=1,
        description="한 번에 조회한 최대 게시글 수",
    )

    posts: list[PostListItem]


class PostDetailResponse(BaseModel):
    """
    게시글 상세 응답 스키마
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    nickname: str
    view_count: int
    created_at: datetime
    updated_at: datetime


class PostDeleteResponse(BaseModel):
    """
    게시글 삭제 성공 응답 스키마
    """

    message: str = Field(
        ...,
        description="삭제 처리 결과 메시지",
        examples=["게시글이 삭제되었습니다."],
    )