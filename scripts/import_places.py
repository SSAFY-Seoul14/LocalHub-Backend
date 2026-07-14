import json
import sys
from pathlib import Path
from typing import Any

from sqlalchemy import select


# scripts/import_places.py를 직접 실행해도 app 패키지를 찾을 수 있도록
# 프로젝트 루트를 Python 경로에 추가한다.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.db.database import Place, SessionLocal, init_db  # noqa: E402


DATA_DIR = PROJECT_ROOT / "data" / "서울"


def to_float(value: Any) -> float | None:
    """빈 문자열은 None으로, 좌표 문자열은 float로 변환한다."""
    if value is None or value == "":
        return None

    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"좌표를 숫자로 변환할 수 없습니다: {value!r}") from exc


def to_int(value: Any) -> int:
    """contentTypeId처럼 정수로 사용할 값을 안전하게 변환한다."""
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"정수로 변환할 수 없습니다: {value!r}") from exc


def build_place(
    item: dict[str, Any],
    *,
    region: str,
    content_type: str,
    content_type_id: int,
    source_file: str,
) -> Place:
    """TourAPI JSON 항목 하나를 Place ORM 객체로 변환한다."""
    item_type_id = item.get("contenttypeid", content_type_id)

    return Place(
        content_id=item["contentid"],
        content_type_id=to_int(item_type_id),
        region=region,
        content_type=content_type,
        title=item.get("title", ""),
        address=item.get("addr1", ""),
        address_detail=item.get("addr2", ""),
        zipcode=item.get("zipcode", ""),
        telephone=item.get("tel", ""),
        longitude=to_float(item.get("mapx")),
        latitude=to_float(item.get("mapy")),
        map_level=item.get("mlevel", ""),
        area_code=item.get("areacode", ""),
        sigungu_code=item.get("sigungucode", ""),
        legal_region_code=item.get("lDongRegnCd", ""),
        legal_sigungu_code=item.get("lDongSignguCd", ""),
        category1=item.get("cat1", ""),
        category2=item.get("cat2", ""),
        category3=item.get("cat3", ""),
        classification1=item.get("lclsSystm1", ""),
        classification2=item.get("lclsSystm2", ""),
        classification3=item.get("lclsSystm3", ""),
        image_url=item.get("firstimage", ""),
        thumbnail_url=item.get("firstimage2", ""),
        copyright_type=item.get("cpyrhtDivCd", ""),
        source_created_at=item.get("createdtime", ""),
        source_modified_at=item.get("modifiedtime", ""),
        source_file=source_file,
    )


def update_place(target: Place, source: Place) -> None:
    """
    같은 content_id가 이미 있을 때 원본 최신 내용으로 갱신한다.

    스크립트를 여러 번 실행해도 중복 행이 생기지 않도록 하는 처리다.
    """
    for column in Place.__table__.columns:
        if column.name in {"id", "content_id"}:
            continue
        setattr(target, column.name, getattr(source, column.name))


def load_json_file(file_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """JSON 파일을 읽고 최상위 메타데이터 및 items 배열을 검증한다."""
    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

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
            f"{file_path.name}: 최상위 필드가 누락되었습니다: {sorted(missing)}"
        )

    items = data["items"]
    if not isinstance(items, list):
        raise ValueError(f"{file_path.name}: items는 배열이어야 합니다.")

    if data["total"] != len(items):
        raise ValueError(
            f"{file_path.name}: total={data['total']}이지만 "
            f"items 개수는 {len(items)}개입니다."
        )

    return data, items


def import_places() -> None:
    """data/서울의 모든 JSON 파일을 data/localhub.db에 적재한다."""
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

    init_db()

    inserted = 0
    updated = 0
    processed = 0

    with SessionLocal() as session:
        try:
            for file_path in json_files:
                data, items = load_json_file(file_path)

                region = str(data["region"])
                content_type = str(data["contentType"])
                content_type_id = to_int(data["contentTypeId"])

                file_inserted = 0
                file_updated = 0

                for item in items:
                    if not item.get("contentid"):
                        raise ValueError(
                            f"{file_path.name}: contentid가 없는 항목이 있습니다."
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
                            Place.content_id == incoming.content_id
                        )
                    )

                    if existing is None:
                        session.add(incoming)
                        inserted += 1
                        file_inserted += 1
                    else:
                        update_place(existing, incoming)
                        updated += 1
                        file_updated += 1

                    processed += 1

                # 파일 단위로 flush하여 컬럼/제약조건 오류를 일찍 확인한다.
                session.flush()

                print(
                    f"[완료] {file_path.name}: "
                    f"전체 {len(items):,}건 / "
                    f"신규 {file_inserted:,}건 / "
                    f"갱신 {file_updated:,}건"
                )

            session.commit()

        except Exception:
            session.rollback()
            raise

    print("-" * 60)
    print(f"처리 완료: 총 {processed:,}건")
    print(f"신규 저장: {inserted:,}건")
    print(f"기존 갱신: {updated:,}건")
    print(f"DB 위치: {PROJECT_ROOT / 'data' / 'localhub.db'}")


if __name__ == "__main__":
    import_places()