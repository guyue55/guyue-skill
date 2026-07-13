"""Deterministic, explainable candidate routing for Guyue Skills."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable


MIN_ROUTE_SCORE = 10.0
MIN_COLLABORATION_SCORE = 20.0
LATIN_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9+_.-]*")
HAN_RUN_RE = re.compile(r"[\u3400-\u9fff]+")


def normalize_text(value: object) -> str:
    return " ".join(unicodedata.normalize("NFKC", str(value)).casefold().split())


def text_features(value: object) -> set[str]:
    """Return word and Han n-gram features without external tokenizers."""
    text = normalize_text(value)
    features = set(LATIN_TOKEN_RE.findall(text))
    for run in HAN_RUN_RE.findall(text):
        if len(run) == 1:
            features.add(run)
            continue
        features.update(run[index : index + 2] for index in range(len(run) - 1))
        if len(run) >= 3:
            features.update(run[index : index + 3] for index in range(len(run) - 2))
    return features


def feature_similarity(left: object, right: object) -> float:
    left_features = text_features(left)
    right_features = text_features(right)
    if not left_features or not right_features:
        return 0.0
    return len(left_features & right_features) / len(left_features | right_features)


def phrase_coverage(phrase: object, haystack: object) -> float:
    phrase_features = text_features(phrase)
    if not phrase_features:
        return 0.0
    return len(phrase_features & text_features(haystack)) / len(phrase_features)


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _direct_matches(phrases: Iterable[str], text: str) -> list[str]:
    normalized_text = normalize_text(text)
    return [phrase for phrase in phrases if normalize_text(phrase) in normalized_text]


def _negative_matches(phrases: list[str], text: str) -> list[str]:
    direct = _direct_matches(phrases, text)
    if direct:
        return direct
    fuzzy = []
    for phrase in phrases:
        features = text_features(phrase)
        if len(features) >= 2 and phrase_coverage(phrase, text) >= 0.85:
            fuzzy.append(phrase)
    return fuzzy


def _score_skill(skill: dict, intent: str, context_markers: list[str]) -> dict:
    name = str(skill.get("name", "")).strip()
    triggers = _string_list(skill.get("trigger_intent"))
    negatives = _string_list(skill.get("negative_intent"))
    required_context = _string_list(skill.get("required_any_context"))
    combined_context = "\n".join([intent, *context_markers])

    matched_context = _direct_matches(required_context, combined_context)
    if required_context and not matched_context:
        return {
            "name": name,
            "path": str(skill.get("path", "")),
            "score": 0.0,
            "reason": "missing_required_context",
            "matched_triggers": [],
            "matched_context": [],
            "negative_matches": [],
            "required_context": required_context,
        }

    negative_matches = _negative_matches(negatives, combined_context)
    if negative_matches:
        return {
            "name": name,
            "path": str(skill.get("path", "")),
            "score": 0.0,
            "reason": "negative_intent",
            "matched_triggers": [],
            "matched_context": matched_context,
            "negative_matches": negative_matches,
            "required_context": required_context,
        }

    score = 0.0
    matched_triggers: list[dict] = []
    normalized_query = normalize_text(combined_context)
    for trigger in triggers:
        normalized_trigger = normalize_text(trigger)
        if normalized_trigger and normalized_trigger in normalized_query:
            contribution = 30.0 + min(len(normalized_trigger), 12)
            score += contribution
            matched_triggers.append(
                {"trigger": trigger, "match": "exact", "score": contribution}
            )
            continue
        coverage = phrase_coverage(trigger, combined_context)
        if len(text_features(trigger)) >= 2 and coverage >= 0.6:
            contribution = round(14.0 * coverage, 3)
            score += contribution
            matched_triggers.append(
                {"trigger": trigger, "match": "partial", "score": contribution}
            )

    description = str(skill.get("description", ""))
    description_similarity = feature_similarity(combined_context, description)
    if description_similarity >= 0.08:
        score += min(10.0, description_similarity * 28.0)
    if score > 0:
        score += max(0, int(skill.get("routing_priority", 0))) / 20.0
        if matched_context:
            score += 20.0

    return {
        "name": name,
        "path": str(skill.get("path", "")),
        "score": round(score, 3),
        "reason": "matched" if score >= MIN_ROUTE_SCORE else "insufficient_signal",
        "matched_triggers": matched_triggers,
        "matched_context": matched_context,
        "negative_matches": [],
        "required_context": required_context,
    }


def _workflow_skill_names(workflow: dict) -> set[str]:
    names: set[str] = set()
    for stage in workflow.get("stages", []):
        if isinstance(stage, dict):
            names.update(_string_list(stage.get("skills")))
    return names


def _resolve_collaborations(
    manifest: dict,
    intent: str,
    context_markers: list[str],
    selected: list[dict],
    *,
    limit: int,
) -> tuple[int | None, list[dict]]:
    contract = manifest.get("collaboration_contract")
    if not isinstance(contract, dict):
        return None, []
    workflows = contract.get("workflows")
    if not isinstance(workflows, list):
        return contract.get("version"), []

    combined_context = "\n".join([intent, *context_markers])
    selected_names = {str(item.get("name", "")) for item in selected}
    candidates: list[dict] = []
    for workflow in workflows:
        if not isinstance(workflow, dict):
            continue
        workflow_id = str(workflow.get("id", "")).strip()
        triggers = _string_list(workflow.get("trigger_intent"))
        entry_skills = set(_string_list(workflow.get("entry_skills")))
        workflow_skills = _workflow_skill_names(workflow)
        required_context = _string_list(workflow.get("required_any_context"))
        matched_context = _direct_matches(required_context, combined_context)
        if required_context and not matched_context:
            continue
        matched_triggers = _direct_matches(triggers, combined_context)
        entry_matches = sorted(entry_skills & selected_names)
        selected_matches = sorted(workflow_skills & selected_names)
        if not matched_triggers and not entry_matches:
            continue
        score = sum(30.0 + min(len(normalize_text(item)), 12) for item in matched_triggers)
        score += 8.0 * len(entry_matches) + 3.0 * len(selected_matches)
        if score < MIN_COLLABORATION_SCORE:
            continue
        candidates.append(
            {
                "id": workflow_id,
                "state": "collaboration_candidate",
                "score": round(score, 3),
                "description": str(workflow.get("description", "")),
                "matched_triggers": matched_triggers,
                "matched_context": matched_context,
                "matched_entry_skills": entry_matches,
                "matched_selected_skills": selected_matches,
                "stages": workflow.get("stages", []),
                "completion_gate": str(workflow.get("completion_gate", "")),
                "requires": [
                    "stage_entry_evidence",
                    "action_specific_authorization",
                    "independent_completion_gate",
                ],
                "boundary": (
                    "Candidate sequence only; activate the minimum necessary stages, "
                    "preserve each Skill boundary, and never treat this as authorization."
                ),
            }
        )
    ranked = sorted(candidates, key=lambda item: (-item["score"], item["id"]))
    return contract.get("version"), ranked[:limit]


def resolve_routes(
    manifest: dict,
    intent: str,
    *,
    context_markers: list[str] | None = None,
    limit: int = 5,
) -> dict:
    """Rank route candidates and retain explainable rejection evidence."""
    if not intent.strip():
        raise ValueError("intent must contain non-whitespace text")
    if limit <= 0:
        raise ValueError("limit must be positive")
    skills = manifest.get("skills")
    if not isinstance(skills, list):
        raise ValueError("manifest skills must be a list")
    markers = [marker.strip() for marker in (context_markers or []) if marker.strip()]
    decisions = [
        _score_skill(skill, intent, markers)
        for skill in skills
        if isinstance(skill, dict) and str(skill.get("name", "")).strip()
    ]
    selected = sorted(
        (
            decision
            for decision in decisions
            if decision["reason"] == "matched"
        ),
        key=lambda item: (-item["score"], item["name"]),
    )[:limit]
    selected_names = {item["name"] for item in selected}
    rejected = sorted(
        (
            decision
            for decision in decisions
            if decision["name"] not in selected_names
            and decision["reason"]
            in {"missing_required_context", "negative_intent", "insufficient_signal"}
        ),
        key=lambda item: (item["reason"], item["name"]),
    )
    external_decisions = [
        _score_skill(dependency, intent, markers)
        for dependency in manifest.get("external_dependencies", [])
        if isinstance(dependency, dict)
        and str(dependency.get("name", "")).strip()
    ]
    external_by_name = {
        str(item.get("name", "")): item
        for item in manifest.get("external_dependencies", [])
        if isinstance(item, dict)
    }
    external_candidates = []
    for decision in sorted(
        (item for item in external_decisions if item["reason"] == "matched"),
        key=lambda item: (-item["score"], item["name"]),
    )[:limit]:
        dependency = external_by_name[decision["name"]]
        external_candidates.append(
            {
                **decision,
                "state": "external_candidate",
                "url": str(dependency.get("url", "")),
                "ref": str(dependency.get("ref", "")),
                "package_id": str(dependency.get("package_id", "")),
                "relationship": str(dependency.get("relationship", "")),
                "evidence_profile": str(dependency.get("evidence_profile", "")),
                "requires": [
                    "source_check",
                    "installation_check",
                    "security_check",
                    "action_specific_authorization",
                ],
                "boundary": (
                    "Candidate only; this result does not prove installation, "
                    "safety, authorization, or activation."
                ),
            }
        )
    contract = manifest.get("routing_contract", {})
    collaboration_version, collaboration_candidates = _resolve_collaborations(
        manifest,
        intent,
        markers,
        selected,
        limit=limit,
    )
    lifecycle_state = "selected" if selected else "failed"
    if not selected and collaboration_candidates:
        lifecycle_state = "collaboration_candidate"
    return {
        "routing_contract_version": (
            contract.get("version") if isinstance(contract, dict) else None
        ),
        "lifecycle_state": lifecycle_state,
        "selected": selected,
        "collaboration_contract_version": collaboration_version,
        "collaboration_candidates": collaboration_candidates,
        "external_candidates": external_candidates,
        "rejected": rejected,
        "context_markers": markers,
    }
