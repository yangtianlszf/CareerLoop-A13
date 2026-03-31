from __future__ import annotations


def student_profile_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "school_name": {"type": ["string", "null"]},
            "major": {"type": ["string", "null"]},
            "education_level": {"type": ["string", "null"]},
            "target_roles": {"type": "array", "items": {"type": "string"}},
            "target_industries": {"type": "array", "items": {"type": "string"}},
            "city_preference": {"type": ["string", "null"]},
            "skills": {"type": "array", "items": {"type": "string"}},
            "soft_skills": {"type": "array", "items": {"type": "string"}},
            "certificates": {"type": "array", "items": {"type": "string"}},
            "projects": {"type": "array", "items": {"type": "string"}},
            "internships": {"type": "array", "items": {"type": "string"}},
            "awards": {"type": "array", "items": {"type": "string"}},
            "profile_completeness": {"type": "integer", "minimum": 0, "maximum": 100},
            "competitiveness_score": {"type": "integer", "minimum": 0, "maximum": 100},
            "missing_sections": {"type": "array", "items": {"type": "string"}},
        },
        "required": [
            "name",
            "school_name",
            "major",
            "education_level",
            "target_roles",
            "target_industries",
            "city_preference",
            "skills",
            "soft_skills",
            "certificates",
            "projects",
            "internships",
            "awards",
            "profile_completeness",
            "competitiveness_score",
            "missing_sections",
        ],
        "additionalProperties": False,
    }


def job_profile_schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "required_skills": {"type": "array", "items": {"type": "string"}},
            "soft_skills": {"type": "array", "items": {"type": "string"}},
            "certificates": {"type": "array", "items": {"type": "string"}},
            "education_requirement": {"type": ["string", "null"]},
            "experience_requirement": {"type": ["string", "null"]},
            "city": {"type": ["string", "null"]},
            "salary_range": {"type": ["string", "null"]},
            "growth_path": {"type": "array", "items": {"type": "string"}},
        },
        "required": [
            "title",
            "required_skills",
            "soft_skills",
            "certificates",
            "education_requirement",
            "experience_requirement",
            "city",
            "salary_range",
            "growth_path",
        ],
        "additionalProperties": False,
    }
