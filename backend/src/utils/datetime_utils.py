from datetime import UTC, datetime


def parse_hh_datetime(date_str: str | None) -> datetime | None:
    if not date_str:
        return None

    dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")

    return dt.astimezone(UTC)
