"""Measure Guyue discovery and activated Skill context budgets."""

from __future__ import annotations

from pathlib import Path

from src.skill_router import feature_similarity


MAX_DESCRIPTION_CHARS = 1024
MAX_DISCOVERY_CHARS = 12000
MAX_ROOT_SKILL_CHARS = 24000
MAX_SKILL_BODY_CHARS = 40000
MAX_SKILL_BODY_LINES = 500
COLLISION_THRESHOLD = 0.72


def _skill_signature(skill: dict) -> str:
    triggers = skill.get("trigger_intent", [])
    trigger_text = " ".join(str(item) for item in triggers) if isinstance(triggers, list) else ""
    return f"{skill.get('description', '')} {trigger_text}".strip()


def analyze_context_budget(repo_root: Path, manifest: dict) -> dict:
    """Return deterministic errors, warnings, collisions, and size metrics."""
    repo_root = repo_root.resolve()
    skills = manifest.get("skills")
    if not isinstance(skills, list):
        return {
            "metrics": {},
            "errors": ["manifest skills must be a list"],
            "warnings": [],
            "route_collisions": [],
            "largest_skill_bodies": [],
        }

    errors: list[str] = []
    warnings: list[str] = []
    discovery_chars = 0
    routing_metadata_chars = 0
    body_rows = []

    root_skill = repo_root / "SKILL.md"
    root_skill_text = (
        root_skill.read_text(encoding="utf-8") if root_skill.is_file() else ""
    )
    root_skill_chars = len(root_skill_text)
    root_skill_bytes = root_skill.stat().st_size if root_skill.is_file() else 0
    if not root_skill.is_file():
        errors.append("root SKILL.md not found")
    elif root_skill_chars > MAX_ROOT_SKILL_CHARS:
        errors.append(
            f"root SKILL.md has {root_skill_chars} chars; budget is {MAX_ROOT_SKILL_CHARS}"
        )

    for index, skill in enumerate(skills, start=1):
        if not isinstance(skill, dict):
            errors.append(f"skill #{index} must be an object")
            continue
        name = str(skill.get("name", "")).strip() or f"skill-{index}"
        description = str(skill.get("description", ""))
        path_value = str(skill.get("path", "")).strip()
        discovery_chars += len(name) + len(description)
        routing_metadata_chars += len(_skill_signature(skill))
        for field in ("negative_intent", "required_any_context"):
            values = skill.get(field, [])
            if isinstance(values, list):
                routing_metadata_chars += sum(len(str(value)) for value in values)

        if len(description) > MAX_DESCRIPTION_CHARS:
            errors.append(
                f"{name} description has {len(description)} chars; limit is {MAX_DESCRIPTION_CHARS}"
            )
        path = (repo_root / path_value).resolve() if path_value else repo_root / "<missing>"
        try:
            path.relative_to(repo_root)
        except ValueError:
            errors.append(f"{name} path escapes repository: {path_value}")
            continue
        if not path.is_file():
            errors.append(f"{name} Skill body not found: {path_value or '<missing>'}")
            continue
        text = path.read_text(encoding="utf-8")
        line_count = len(text.splitlines())
        char_count = len(text)
        body_rows.append(
            {"name": name, "path": path_value, "chars": char_count, "lines": line_count}
        )
        if char_count > MAX_SKILL_BODY_CHARS:
            errors.append(
                f"{name} Skill body has {char_count} chars; budget is {MAX_SKILL_BODY_CHARS}"
            )
        if line_count > MAX_SKILL_BODY_LINES:
            errors.append(
                f"{name} Skill body has {line_count} lines; budget is {MAX_SKILL_BODY_LINES}"
            )

    if discovery_chars > MAX_DISCOVERY_CHARS:
        errors.append(
            f"discovery metadata has {discovery_chars} chars; budget is {MAX_DISCOVERY_CHARS}"
        )
    elif discovery_chars > int(MAX_DISCOVERY_CHARS * 0.8):
        warnings.append("discovery metadata is above 80% of its local budget")
    if root_skill_chars > int(MAX_ROOT_SKILL_CHARS * 0.8):
        warnings.append("root SKILL.md is above 80% of its local budget")

    collisions = []
    valid_skills = [skill for skill in skills if isinstance(skill, dict)]
    for left_index, left in enumerate(valid_skills):
        left_name = str(left.get("name", "")).strip()
        for right in valid_skills[left_index + 1 :]:
            right_name = str(right.get("name", "")).strip()
            similarity = feature_similarity(_skill_signature(left), _skill_signature(right))
            if similarity >= COLLISION_THRESHOLD:
                collisions.append(
                    {
                        "left": left_name,
                        "right": right_name,
                        "similarity": round(similarity, 3),
                    }
                )
    collisions.sort(key=lambda item: (-item["similarity"], item["left"], item["right"]))
    if collisions:
        warnings.append(
            f"{len(collisions)} route-description pair(s) exceed the collision threshold"
        )

    body_rows.sort(key=lambda item: (-item["chars"], item["name"]))
    return {
        "metrics": {
            "skill_count": len(skills),
            "discovery_chars": discovery_chars,
            "discovery_budget_chars": MAX_DISCOVERY_CHARS,
            "routing_metadata_chars": routing_metadata_chars,
            "root_skill_chars": root_skill_chars,
            "root_skill_bytes": root_skill_bytes,
            "root_skill_budget_chars": MAX_ROOT_SKILL_CHARS,
        },
        "errors": errors,
        "warnings": warnings,
        "route_collisions": collisions,
        "largest_skill_bodies": body_rows[:10],
    }
