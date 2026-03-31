import hashlib

from src.parsers.base.parser_result import ParserVacancyResult


def make_fingerprint(v: ParserVacancyResult) -> str:
    raw = f"{v.title}_{v.company_name}_{v.city}_{v.address}"
    return hashlib.sha256(raw.lower().encode()).hexdigest()
