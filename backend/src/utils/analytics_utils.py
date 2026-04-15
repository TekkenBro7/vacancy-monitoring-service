def normalize_experience(exp: str | None) -> str:
    if not exp:
        return "Не указано"

    exp_lower = exp.lower().strip()

    no_exp_patterns = [
        "без опыта",
        "нет опыта",
        "no experience",
        "не имеет значения",
        "опыт работы не имеет значения",
        "intern",
        "internship",
        "стажер",
    ]
    if any(p in exp_lower for p in no_exp_patterns):
        return "Без опыта"

    import re

    patterns = [
        r"(\d+)\+?\s*(?:years?|лет|год[а]?)",
        r"(?:от|from|at least)\s*(\d+)",
        r"^(\d+)\+?\s*(?:years?|лет)?",
        r"(\d+)-\d+\s*(?:years?|лет|год)",
    ]

    years = None
    for pattern in patterns:
        match = re.search(pattern, exp_lower)
        if match:
            years = int(match.group(1))
            break

    if "senior" in exp_lower or "lead" in exp_lower:
        return "5+ лет (Senior)"
    if "middle" in exp_lower:
        return "3-5 лет (Middle)"
    if "junior" in exp_lower:
        return "1-3 года (Junior)"

    if years is not None:
        if years == 0:
            return "Без опыта"
        elif years == 1:
            return "1-3 года (Junior)"
        elif years <= 3:
            return "1-3 года (Junior)"
        elif years <= 5:
            return "3-5 лет (Middle)"
        elif years <= 7:
            return "5+ лет (Senior)"
        else:
            return "7+ лет (Lead/Expert)"

    if "1 года до 3" in exp_lower or "1-3" in exp_lower:
        return "1-3 года (Junior)"
    if "3 до 6" in exp_lower or "3-6" in exp_lower or "от 3 лет" in exp_lower:
        return "3-5 лет (Middle)"
    if "более 6" in exp_lower or "от 6" in exp_lower:
        return "5+ лет (Senior)"

    return "Не указано"


def normalize_employment(emp: str | None) -> str:
    if not emp:
        return "Не указано"

    emp_lower = emp.lower().strip()

    if any(p in emp_lower for p in ["full", "полн", "полная"]):
        return "Полная занятость"
    if any(p in emp_lower for p in ["part", "частич", "неполн"]):
        return "Частичная занятость"
    if any(p in emp_lower for p in ["project", "проект"]):
        return "Проектная работа"
    if any(p in emp_lower for p in ["intern", "стаж"]):
        return "Стажировка"
    if any(p in emp_lower for p in ["contract", "контракт", "договор"]):
        return "Контракт"
    if any(p in emp_lower for p in ["freelance", "фриланс"]):
        return "Фриланс"

    return "Не указано"


def normalize_schedule(sch: str | None) -> str:
    if not sch:
        return "Не указано"

    sch_lower = sch.lower().strip()

    if any(p in sch_lower for p in ["remote", "удален", "удалён", "дистанц"]):
        return "Удалённая работа"
    if any(p in sch_lower for p in ["office", "офис"]):
        return "В офисе"
    if any(p in sch_lower for p in ["hybrid", "гибрид", "смешан"]):
        return "Гибридный"
    if any(p in sch_lower for p in ["flex", "гибк", "свободн"]):
        return "Гибкий график"
    if any(p in sch_lower for p in ["full day", "полный день"]):
        return "Полный день"
    if any(p in sch_lower for p in ["shift", "смен"]):
        return "Сменный график"

    return "Не указано"
