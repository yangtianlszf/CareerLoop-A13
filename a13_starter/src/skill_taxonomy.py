from __future__ import annotations

from typing import Iterable


SKILL_ALIAS_GROUPS: dict[str, tuple[str, ...]] = {
    "Java": ("java", "java开发"),
    "Spring": ("spring",),
    "Spring Boot": ("spring boot", "springboot"),
    "MySQL": ("mysql",),
    "SQL": ("sql", "数据库", "sql语句"),
    "Linux": ("linux", "linux运维"),
    "Redis": ("redis",),
    "Docker": ("docker",),
    "Git": ("git", "版本控制"),
    "JavaScript": ("javascript", "js"),
    "TypeScript": ("typescript", "ts"),
    "Vue": ("vue", "vue.js", "vuejs"),
    "React": ("react", "react.js", "reactjs"),
    "HTML": ("html", "html5"),
    "CSS": ("css", "css3"),
    "Python": ("python",),
    "Pytest": ("pytest",),
    "Postman": ("postman",),
    "JMeter": ("jmeter",),
    "Selenium": ("selenium",),
    "C": ("c", "c语言"),
    "C++": ("c++", "cpp", "c/c++"),
    "项目表达": ("项目表达", "项目讲解", "项目复盘", "star法"),
    "部署实施": ("部署", "上线", "实施", "交付"),
    "需求分析": ("需求分析", "需求梳理", "prd", "原型"),
}


_ALIAS_TO_CANONICAL: dict[str, str] = {}
for canonical, aliases in SKILL_ALIAS_GROUPS.items():
    _ALIAS_TO_CANONICAL[canonical.lower()] = canonical
    for alias in aliases:
        _ALIAS_TO_CANONICAL[str(alias).strip().lower()] = canonical


def normalize_skill_alias(skill: str | None) -> str:
    cleaned = str(skill or "").strip()
    if not cleaned:
        return ""
    return _ALIAS_TO_CANONICAL.get(cleaned.lower(), cleaned)


def normalize_skill_list(skills: Iterable[str] | None) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for skill in skills or []:
        canonical = normalize_skill_alias(skill)
        if not canonical:
            continue
        lowered = canonical.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        result.append(canonical)
    return result


def expand_skill_aliases(skill: str | None) -> list[str]:
    canonical = normalize_skill_alias(skill)
    if not canonical:
        return []
    aliases = [canonical]
    aliases.extend(SKILL_ALIAS_GROUPS.get(canonical, ()))
    seen: set[str] = set()
    result: list[str] = []
    for item in aliases:
        cleaned = str(item).strip()
        lowered = cleaned.lower()
        if not cleaned or lowered in seen:
            continue
        seen.add(lowered)
        result.append(cleaned)
    return result


def expand_skill_list(skills: Iterable[str] | None, *, max_per_skill: int = 3) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for skill in normalize_skill_list(skills):
        aliases = expand_skill_aliases(skill)[: max(1, max_per_skill)]
        for alias in aliases:
            lowered = alias.lower()
            if lowered in seen:
                continue
            seen.add(lowered)
            result.append(alias)
    return result
