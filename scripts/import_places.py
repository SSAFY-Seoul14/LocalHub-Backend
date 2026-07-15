import json
import sys
from pathlib import Path
from typing import Any

from sqlalchemy import select


# scripts/import_places.py를 직접 실행해도
# app 패키지를 찾을 수 있도록 프로젝트 루트를 Python 경로에 추가한다.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


from app.db.database import SessionLocal, init_db  # noqa: E402
from app.models.place import Place  # noqa: E402


DATA_DIR = PROJECT_ROOT / "data" / "서울"


def clean_string(value: Any) -> str:
    """
    JSON 값을 문자열로 정리한다.

    None은 빈 문자열로 변환하고,
    문자열 앞뒤의 불필요한 공백을 제거한다.
    """
    if value is None:
        return ""

    return str(value).strip()


def to_float(value: Any) -> float | None:
    """
    좌표 문자열을 실수로 변환한다.

    빈 문자열이나 None은 좌표가 없는 것으로 보고 None을 반환한다.
    """
    if value is None:
        return None

    cleaned_value = str(value).strip()

    if not cleaned_value:
        return None

    try:
        return float(cleaned_value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"좌표를 숫자로 변환할 수 없습니다: {value!r}"
        ) from exc


def to_int(value: Any) -> int:
    """
    contentTypeId처럼 정수로 사용할 값을 안전하게 변환한다.
    """
    if value is None:
        raise ValueError("정수로 변환할 값이 없습니다.")

    cleaned_value = str(value).strip()

    if not cleaned_value:
        raise ValueError(
            f"빈 값을 정수로 변환할 수 없습니다: {value!r}"
        )

    try:
        return int(cleaned_value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"정수로 변환할 수 없습니다: {value!r}"
        ) from exc


def build_place(
    item: dict[str, Any],
    *,
    region: str,
    content_type: str,
    content_type_id: int,
    source_file: str,
) -> Place:
    """
    TourAPI JSON 항목 하나를 Place SQLAlchemy 객체로 변환한다.

    일반 장소 데이터에는 축제 상세 필드가 없으므로
    해당 필드는 빈 문자열로 저장된다.
    """
    # 항목의 contenttypeid가 빈 문자열이면
    # JSON 최상위 contentTypeId를 사용한다.
    item_type_id = item.get("contenttypeid")

    if item_type_id is None or not str(item_type_id).strip():
        item_type_id = content_type_id

    return Place(
        # TourAPI 식별 정보
        content_id=clean_string(item["contentid"]),
        content_type_id=to_int(item_type_id),
        region=clean_string(region),
        content_type=clean_string(content_type),

        # 장소 기본 정보
        title=clean_string(item.get("title")),

        # 주소
        address=clean_string(item.get("addr1")),
        address_detail=clean_string(item.get("addr2")),
        zipcode=clean_string(item.get("zipcode")),

        # 연락처
        telephone=clean_string(item.get("tel")),

        # 위치
        longitude=to_float(item.get("mapx")),
        latitude=to_float(item.get("mapy")),
        map_level=clean_string(item.get("mlevel")),

        # 지역 코드
        area_code=clean_string(item.get("areacode")),
        sigungu_code=clean_string(item.get("sigungucode")),
        legal_region_code=clean_string(
            item.get("lDongRegnCd")
        ),
        legal_sigungu_code=clean_string(
            item.get("lDongSignguCd")
        ),

        # 관광 분류
        category1=clean_string(item.get("cat1")),
        category2=clean_string(item.get("cat2")),
        category3=clean_string(item.get("cat3")),
        classification1=clean_string(
            item.get("lclsSystm1")
        ),
        classification2=clean_string(
            item.get("lclsSystm2")
        ),
        classification3=clean_string(
            item.get("lclsSystm3")
        ),

        # 이미지
        image_url=clean_string(item.get("firstimage")),
        thumbnail_url=clean_string(
            item.get("firstimage2")
        ),

        # 저작권
        copyright_type=clean_string(
            item.get("cpyrhtDivCd")
        ),

        # 축제·공연·행사 상세 정보
        event_start_date=clean_string(
            item.get("eventstartdate")
        ),
        event_end_date=clean_string(
            item.get("eventenddate")
        ),
        event_place=clean_string(
            item.get("eventplace")
        ),
        play_time=clean_string(
            item.get("playtime")
        ),
        program=clean_string(
            item.get("program")
        ),
        sub_event=clean_string(
            item.get("subevent")
        ),

        # 주최·주관
        sponsor1=clean_string(
            item.get("sponsor1")
        ),
        sponsor1_telephone=clean_string(
            item.get("sponsor1tel")
        ),
        sponsor2=clean_string(
            item.get("sponsor2")
        ),
        sponsor2_telephone=clean_string(
            item.get("sponsor2tel")
        ),

        # 홈페이지 및 예매
        event_homepage=clean_string(
            item.get("eventhomepage")
        ),
        booking_place=clean_string(
            item.get("bookingplace")
        ),

        # 관람 및 이용 정보
        age_limit=clean_string(
            item.get("agelimit")
        ),
        festival_grade=clean_string(
            item.get("festivalgrade")
        ),
        place_info=clean_string(
            item.get("placeinfo")
        ),
        spend_time_festival=clean_string(
            item.get("spendtimefestival")
        ),
        discount_info_festival=clean_string(
            item.get("discountinfofestival")
        ),
        use_time_festival=clean_string(
            item.get("usetimefestival")
        ),

        # TourAPI 원본 생성·수정 시간
        source_created_at=clean_string(
            item.get("createdtime")
        ),
        source_modified_at=clean_string(
            item.get("modifiedtime")
        ),

        # 데이터 출처
        source_file=source_file,
    )


def update_place(
    target: Place,
    source: Place,
) -> None:
    """
    같은 content_id가 이미 존재하면 최신 JSON 내용으로 갱신한다.

    id, content_id와 서비스 생성·수정 시간은
    새 Place 객체의 값으로 덮어쓰지 않는다.
    """
    excluded_columns = {
        "id",
        "content_id",
        "created_at",
        "updated_at",
    }

    for column in Place.__table__.columns:
        if column.name in excluded_columns:
            continue

        setattr(
            target,
            column.name,
            getattr(source, column.name),
        )


def load_json_file(
    file_path: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """
    JSON 파일을 읽고 최상위 구조와 items 배열을 검증한다.
    """
    with file_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(
            f"{file_path.name}: "
            "JSON 최상위 데이터는 객체여야 합니다."
        )

    required_top_level = {
        "region",
        "contentType",
        "contentTypeId",
        "total",
        "items",
    }

    missing = required_top_level - data.keys()

    if missing:
        raise ValueError(
            f"{file_path.name}: "
            f"최상위 필드가 누락되었습니다: {sorted(missing)}"
        )

    items = data["items"]

    if not isinstance(items, list):
        raise ValueError(
            f"{file_path.name}: items는 배열이어야 합니다."
        )

    try:
        total = to_int(data["total"])
    except ValueError as exc:
        raise ValueError(
            f"{file_path.name}: total 값이 올바르지 않습니다."
        ) from exc

    if total != len(items):
        raise ValueError(
            f"{file_path.name}: "
            f"total={total}이지만 "
            f"items 개수는 {len(items)}개입니다."
        )

    return data, items


def import_places() -> None:
    """
    data/서울 폴더의 모든 JSON 파일을
    data/localhub.db의 places 테이블에 적재한다.

    content_id가 이미 존재하면 기존 데이터를 갱신하고,
    존재하지 않으면 새 장소로 저장한다.
    """
    if not DATA_DIR.exists():
        raise FileNotFoundError(
            f"데이터 폴더를 찾을 수 없습니다: {DATA_DIR}\n"
            "JSON 파일을 LocalHub-Backend/data/서울/에 넣어주세요."
        )

    json_files = sorted(DATA_DIR.glob("*.json"))

    if not json_files:
        raise FileNotFoundError(
            f"JSON 파일을 찾을 수 없습니다: {DATA_DIR}"
        )

    # 모델을 불러오고 places 테이블이 없으면 생성한다.
    init_db()

    inserted = 0
    updated = 0
    processed = 0

    with SessionLocal() as session:
        try:
            for file_path in json_files:
                data, items = load_json_file(file_path)

                region = clean_string(data["region"])
                content_type = clean_string(
                    data["contentType"]
                )
                content_type_id = to_int(
                    data["contentTypeId"]
                )

                file_inserted = 0
                file_updated = 0

                for item_index, item in enumerate(
                    items,
                    start=1,
                ):
                    if not isinstance(item, dict):
                        raise ValueError(
                            f"{file_path.name}: "
                            f"{item_index}번째 항목은 "
                            "객체 형식이어야 합니다."
                        )

                    content_id = clean_string(
                        item.get("contentid")
                    )

                    if not content_id:
                        raise ValueError(
                            f"{file_path.name}: "
                            f"{item_index}번째 항목에 "
                            "contentid가 없습니다."
                        )

                    title = clean_string(
                        item.get("title")
                    )

                    if not title:
                        raise ValueError(
                            f"{file_path.name}: "
                            f"contentid={content_id} 항목에 "
                            "title이 없습니다."
                        )

                    incoming = build_place(
                        item,
                        region=region,
                        content_type=content_type,
                        content_type_id=content_type_id,
                        source_file=file_path.name,
                    )

                    existing = session.scalar(
                        select(Place).where(
                            Place.content_id
                            == incoming.content_id
                        )
                    )

                    if existing is None:
                        session.add(incoming)

                        inserted += 1
                        file_inserted += 1
                    else:
                        update_place(
                            existing,
                            incoming,
                        )

                        updated += 1
                        file_updated += 1

                    processed += 1

                # 파일 단위로 SQL을 DB에 전달하여
                # 컬럼 및 제약조건 오류를 빠르게 확인한다.
                session.flush()

                print(
                    f"[완료] {file_path.name}: "
                    f"전체 {len(items):,}건 / "
                    f"신규 {file_inserted:,}건 / "
                    f"갱신 {file_updated:,}건"
                )

            # 모든 파일이 정상 처리된 경우에만 실제 저장을 확정한다.
            session.commit()

        except Exception:
            # 중간 오류가 발생하면 이번 실행의 변경 내용을 취소한다.
            session.rollback()
            raise

    print("-" * 60)
    print(f"처리 완료: 총 {processed:,}건")
    print(f"신규 저장: {inserted:,}건")
    print(f"기존 갱신: {updated:,}건")
    print(
        "DB 위치: "
        f"{PROJECT_ROOT / 'data' / 'localhub.db'}"
    )


if __name__ == "__main__":
    import_places()