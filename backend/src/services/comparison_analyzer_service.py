from src.ai.groq_client import GroqClient
from src.ai.prompts import COMPARISON_ANALYSIS_PROMPT
from src.core.logger import logger
from src.models.companies import Vacancy
from src.models.users import User, UserProfile


class ComparisonAnalyzerService:
    def __init__(self, groq_client: GroqClient):
        self.client = groq_client

    def _format_vacancy(self, vacancy: Vacancy, index: int) -> str:
        lines = [f"### Вакансия {index}: {vacancy.title}"]

        if vacancy.company:
            lines.append(f"**Компания:** {vacancy.company.name}")

        salary_parts = []
        if vacancy.salary_from:
            salary_parts.append(f"от {vacancy.salary_from:,}".replace(",", " "))
        if vacancy.salary_to:
            salary_parts.append(f"до {vacancy.salary_to:,}".replace(",", " "))
        if salary_parts:
            currency = vacancy.currency.symbol if vacancy.currency else ""
            lines.append(f"**Зарплата:** {' '.join(salary_parts)} {currency}")
        else:
            lines.append("**Зарплата:** не указана")

        location_parts = []
        if vacancy.location:
            location_parts.append(vacancy.location.name)
        if vacancy.address:
            location_parts.append(vacancy.address)
        if vacancy.is_remote:
            location_parts.append("(удалённая работа)")
        if location_parts:
            lines.append(f"**Локация:** {', '.join(location_parts)}")

        if vacancy.experience:
            lines.append(f"**Опыт:** {vacancy.experience}")
        if vacancy.education:
            lines.append(f"**Образование:** {vacancy.education}")
        if vacancy.employment:
            lines.append(f"**Занятость:** {vacancy.employment}")
        if vacancy.schedule:
            lines.append(f"**График:** {vacancy.schedule}")
        if vacancy.internship:
            lines.append("**Тип:** Стажировка")

        if vacancy.skills:
            skills_str = ", ".join(s.name for s in vacancy.skills)
            lines.append(f"**Требуемые навыки:** {skills_str}")

        if vacancy.description:
            desc = vacancy.description[:1500]
            if len(vacancy.description) > 1500:
                desc += "..."
            lines.append(f"\n**Описание:**\n{desc}")

        if vacancy.vacancy_url:
            lines.append(f"\n**Ссылка:** {vacancy.vacancy_url}")

        return "\n".join(lines)

    def _format_vacancies(self, vacancies: list[Vacancy]) -> str:
        formatted = []
        for i, vacancy in enumerate(vacancies, 1):
            formatted.append(self._format_vacancy(vacancy, i))
            formatted.append("\n---\n")
        return "\n".join(formatted)

    def _format_user_info(self, user: User, profile: UserProfile | None) -> dict:
        user_name = "Не указано"
        if profile and profile.full_name:
            user_name = profile.full_name
        elif user.username:
            user_name = user.username

        desired_position = "Не указана"
        if profile and profile.desired_position:
            desired_position = profile.desired_position

        desired_salary = "Не указана"
        if profile and profile.desired_salary:
            desired_salary = f"{profile.desired_salary:,}".replace(",", " ")

        user_skills = "Не указаны"
        if user.skills:
            user_skills = ", ".join(s.name for s in user.skills)

        user_city = "Не указан"
        if profile and profile.city:
            user_city = profile.city.name

        user_address = "Не указан"
        if profile and profile.address:
            user_address = profile.address

        remote_preference = "Не важно"
        if profile and profile.preferred_remote is not None:
            remote_preference = "Удалённая работа" if profile.preferred_remote else "Работа в офисе"

        internship_preference = "Не важно"
        if profile and profile.preferred_internship is not None:
            internship_preference = (
                "Ищу стажировку" if profile.preferred_internship else "Ищу работу (не стажировку)"
            )

        employment_preference = "Не указан"
        if profile and profile.preferred_employment:
            employment_preference = profile.preferred_employment

        schedule_preference = "Не указан"
        if profile and profile.preferred_schedule:
            schedule_preference = profile.preferred_schedule

        bio = "Не указано"
        if profile and profile.bio:
            bio = profile.bio

        return {
            "user_name": user_name,
            "desired_position": desired_position,
            "desired_salary": desired_salary,
            "user_skills": user_skills,
            "user_city": user_city,
            "user_address": user_address,
            "remote_preference": remote_preference,
            "internship_preference": internship_preference,
            "employment_preference": employment_preference,
            "schedule_preference": schedule_preference,
            "bio": bio,
        }

    def _build_user_context(self, user_info: dict) -> str:
        lines = ["## Информация о пользователе\n"]

        lines.append(f"**Имя:** {user_info['user_name']}")
        lines.append(f"**Желаемая должность:** {user_info['desired_position']}")
        lines.append(f"**Ожидаемая зарплата:** {user_info['desired_salary']}")
        lines.append(f"**Навыки:** {user_info['user_skills']}")
        lines.append(f"**Город:** {user_info['user_city']}")

        if user_info["user_address"] != "Не указан":
            lines.append(f"**Адрес:** {user_info['user_address']}")

        lines.append("\n### Предпочтения по работе:\n")
        lines.append(f"- **Формат работы:** {user_info['remote_preference']}")
        lines.append(f"- **Тип позиции:** {user_info['internship_preference']}")
        lines.append(f"- **Тип занятости:** {user_info['employment_preference']}")
        lines.append(f"- **График:** {user_info['schedule_preference']}")

        if user_info["bio"] != "Не указано":
            lines.append(f"\n### О себе:\n{user_info['bio']}")

        return "\n".join(lines)

    async def analyze(
        self,
        vacancies: list[Vacancy],
        user: User,
        profile: UserProfile | None,
        language: str = "ru",
    ) -> str:
        if len(vacancies) < 2:
            return "❌ Для анализа необходимо минимум 2 вакансии."

        vacancies_text = self._format_vacancies(vacancies)
        user_info = self._format_user_info(user, profile)
        user_context = self._build_user_context(user_info)

        prompt = COMPARISON_ANALYSIS_PROMPT.format(
            user_context=user_context,
            user_name=user_info["user_name"],
            desired_position=user_info["desired_position"],
            desired_salary=user_info["desired_salary"],
            user_skills=user_info["user_skills"],
            user_city=user_info["user_city"],
            remote_preference=user_info["remote_preference"],
            internship_preference=user_info["internship_preference"],
            employment_preference=user_info["employment_preference"],
            schedule_preference=user_info["schedule_preference"],
            vacancies_text=vacancies_text,
        )

        logger.info(f"Analyzing {len(vacancies)} vacancies for user {user.id}")

        response = await self.client.chat(content=prompt)

        return response.content
