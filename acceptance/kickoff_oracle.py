"""Offline structural oracle for a fresh-agent kickoff evidence package."""

from __future__ import annotations

import argparse
import json
import re
import stat
import sys
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

if __package__:
    from .strict_json import DuplicateJsonKeyError
    from .strict_json import loads as strict_json_loads
    from .unicode_policy import (
        is_synthetic_ignorable,
        is_unsafe_evidence_character,
        nfkc_casefold,
    )
else:
    from strict_json import DuplicateJsonKeyError
    from strict_json import loads as strict_json_loads
    from unicode_policy import (  # type: ignore[no-redef]
        is_synthetic_ignorable,
        is_unsafe_evidence_character,
        nfkc_casefold,
    )


TECH_LANE_IDS = {"language", "stack", "tooling"}
LOCAL_LANE_IDS = {"context", "architecture", "delivery"}
CHALLENGE_LANE_ID = "challenge"
EXPLORATION_LANE_IDS = LOCAL_LANE_IDS | TECH_LANE_IDS
LANE_IDS = EXPLORATION_LANE_IDS | {CHALLENGE_LANE_ID}
LANE_CONCERNS = {
    "context": "OBJECTIVE_CONTEXT",
    "language": "CURRENT_TECHNOLOGY_LANGUAGE",
    "stack": "CURRENT_TECHNOLOGY_STACK_PORTFOLIO",
    "tooling": "CURRENT_TECHNOLOGY_TOOLING",
    "architecture": "ARCHITECTURE_RISK_PRIVACY",
    "delivery": "TESTING_BOOTSTRAP_PACKAGE_INSTALL",
    "challenge": "INDEPENDENT_CHALLENGE_REVIEW",
}
EXPECTED_FILES = {
    "coordination.json",
    "research/context.json",
    "research/language.json",
    "research/stack.json",
    "research/tooling.json",
    "research/architecture.json",
    "research/delivery.json",
    "research/challenge.json",
    "technology-options-research-brief.json",
    "technology-architecture-adr.json",
    "kickoff-plan.json",
}
COORDINATION_KEYS = {
    "schema_version",
    "objective",
    "phase",
    "status",
    "research_as_of",
    "coordinator",
    "coordinator_mode",
    "implementation_authorized",
    "install_authorized",
    "architecture_delivery_assignment",
    "delegations",
    "synthesis_artifacts",
    "steady_state_topology",
}
ARCHITECTURE_DELIVERY_KEYS = {
    "risk_class",
    "merged",
    "safe_merge_rationale",
    "challenger_cross_checks",
}
COUPLED_HAZARD_CROSS_CHECKS = {
    "PATH_RESOURCE_ALIASING",
    "SOURCE_PRESERVATION",
    "EXACT_COMMANDS",
    "FAILURE_INJECTION",
    "PLATFORM_PREREQUISITES",
}
DELEGATION_KEYS = {
    "lane_id",
    "owner",
    "scope",
    "artifact",
    "independent",
    "may_mutate_project",
    "may_use_git",
    "status",
    "receipt",
    "concern",
    "stage",
    "inputs",
}
RESEARCH_KEYS = {
    "schema_version",
    "lane_id",
    "author",
    "scope",
    "as_of",
    "status",
    "sources",
    "options",
    "recommendation",
    "decision_impact",
    "unproved_boundary",
}
STACK_RESEARCH_KEYS = RESEARCH_KEYS | {
    "portfolio_reference",
    "reuse_policy",
    "portfolio_assessments",
}
SOURCE_KEYS = {
    "source_kind",
    "publisher",
    "url",
    "retrieved_on",
    "evidence",
}
OPTION_KEYS = {"name", "strengths", "risks", "evidence_refs"}
LOCAL_RESEARCH_KEYS = {
    "schema_version",
    "lane_id",
    "author",
    "scope",
    "status",
    "local_inputs",
    "findings",
    "recommendations",
    "unproved_boundary",
}
LOCAL_INPUT_KEYS = {"path", "snapshot", "state", "evidence"}
CHALLENGE_KEYS = {
    "schema_version",
    "lane_id",
    "author",
    "scope",
    "status",
    "local_inputs",
    "reviewed_artifacts",
    "coupled_hazard_cross_checks",
    "verdict",
    "findings",
    "unproved_boundary",
}
CHALLENGE_FINDING_KEYS = {
    "finding_id",
    "severity",
    "statement",
    "recommended_adr_action",
    "recommended_plan_action",
}
DISPOSITION_KEYS = {
    "finding_id",
    "disposition",
    "response",
    "evidence_ref",
    "resolution_path",
}
BRIEF_KEYS = {
    "schema_version",
    "status",
    "as_of",
    "owner",
    "objective",
    "input_lanes",
    "evidence_refs",
    "options",
    "comparison_criteria",
    "recommendation",
    "unproved_boundaries",
}
BRIEF_OPTION_KEYS = {
    "concern",
    "option",
    "evidence_refs",
    "objective_fit",
    "solo_maintenance_cost",
}
ADR_KEYS = {
    "schema_version",
    "adr_id",
    "status",
    "date",
    "owner",
    "objective",
    "input_lanes",
    "evidence_refs",
    "technology_options_brief",
    "portfolio_reference",
    "reuse_policy",
    "portfolio_assessments",
    "new_stack_divergence",
    "challenge_dispositions",
    "decision",
    "alternatives",
    "constraints",
    "risks",
    "unproved_boundaries",
    "revisit_triggers",
}
PORTFOLIO_BASELINES = {"REFERENCE_SERVICE", "REFERENCE_APP", "SMALL_COMBINATION"}
PORTFOLIO_REFERENCE_KEYS = {"path", "status", "as_of", "evidence"}
PORTFOLIO_ASSESSMENT_KEYS = {
    "baseline",
    "fit",
    "objective_specific_fit",
    "solo_maintenance_cost",
    "evidence_ref",
    "disposition",
}
NEW_STACK_KEYS = {
    "selected",
    "objective_specific_justification",
    "solo_maintenance_cost",
    "evidence_refs",
}
DECISION_KEYS = {"language", "stack", "tooling", "architecture"}
ALTERNATIVE_KEYS = {"option", "reason_not_selected", "evidence_refs"}
PLAN_KEYS = {
    "schema_version",
    "status",
    "owner",
    "based_on",
    "input_lanes",
    "evidence_refs",
    "challenge_dispositions",
    "implementation_authorized",
    "install_authorized",
    "phases",
    "package_strategy",
    "authority_gate",
    "steady_state",
    "source_comprehension",
    "quality_control",
}
SOURCE_COMPREHENSION_KEYS = {
    "community_basis",
    "target_rule_path",
    "owner",
    "implementation_gate",
    "review_gate",
    "existing_debt_disposition",
    "exceptions",
}
SOURCE_IMPLEMENTATION_GATE = "ASSESS_ALL_CHANGED_HUMAN_AUTHORED_SOURCE_BEFORE_HANDOFF"
SOURCE_REVIEW_GATE = "NON_AUTHOR_READS_ALL_CHANGED_AUTHORED_SOURCE_MISSING_IS_FINDING"
QUALITY_CONTROL_KEYS = {
    "applicability",
    "owner",
    "location",
    "concerns",
    "unknown_policy",
    "action_rule",
    "challenge_rule",
    "automation_limit",
}
PHASE_KEYS = {
    "id",
    "owner",
    "entry_condition_tokens",
    "execution_state",
    "implementation_authorized",
    "install_authorized",
    "exact_paths",
    "actions",
    "evidence",
    "stop_condition",
}
PACKAGE_KEYS = {
    "action",
    "commands",
    "packages",
    "rationale",
    "evidence_ref",
    "install_authorized",
    "execution_state",
    "next_gate",
}
PACKAGE_ITEM_KEYS = {"name", "version_policy", "reason"}
AUTHORITY_KEYS = {
    "implementation_authorized",
    "install_authorized",
    "external_effects_authorized",
    "required_authority_holder",
    "next_gate",
}
STEADY_STATE_KEYS = {"topology", "kickoff_research_lanes_end", "review_rule"}
ISO_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


class KickoffVerificationError(ValueError):
    """Raised when the evidence package violates the kickoff contract."""


def _object(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise KickoffVerificationError(f"{label} must be an object")
    keys = set(value)
    if keys != expected:
        raise KickoffVerificationError(
            f"{label} keys differ: missing={sorted(expected - keys)}, "
            f"extra={sorted(keys - expected)}"
        )
    return value


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise KickoffVerificationError(f"{label} must be non-empty text")
    return value


def _identity_key(value: Any, label: str) -> str:
    """Return a compatibility-normalized key for one separation-critical identity.

    The kickoff separation invariants (owner != coordinator, challenger distinct from
    every research owner, architecture/delivery merge detection) protect independence,
    so they compare *identities*, not raw code points. Raw ``==``/``in`` would fail open
    to confusable aliases: a fullwidth or otherwise compatibility-equivalent spelling,
    or surrounding-whitespace padding that ``nfkc_casefold`` preserves, reads as a
    distinct person (WB-047). This mirrors the three sibling oracles: reject
    non-stripped (surrounding-whitespace) text, reject unsafe evidence characters,
    reject synthetic Unicode ignorables, then key on the shared double-NFKC casefold so
    aliases of one identity collapse together.
    """
    text = _text(value, label)
    if text != text.strip():
        raise KickoffVerificationError(f"{label} must not have surrounding whitespace")
    if any(is_unsafe_evidence_character(character) for character in text):
        raise KickoffVerificationError(
            f"{label} must not contain unsafe Unicode evidence characters"
        )
    if any(is_synthetic_ignorable(character) for character in text):
        raise KickoffVerificationError(f"{label} must not contain synthetic Unicode ignorables")
    return nfkc_casefold(text)


def _text_list(value: Any, label: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        raise KickoffVerificationError(f"{label} must be a text list")
    for index, item in enumerate(value):
        _text(item, f"{label}[{index}]")
    return value


def _date(value: Any, label: str) -> str:
    value = _text(value, label)
    if not ISO_DATE_RE.fullmatch(value):
        raise KickoffVerificationError(f"{label} must be YYYY-MM-DD")
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise KickoffVerificationError(f"{label} is not a real date") from exc
    return value


def _schema_one(value: Any, label: str) -> None:
    if type(value) is not int or value != 1:
        raise KickoffVerificationError(f"{label} must be integer 1")


def _relative_path(value: Any, label: str, *, markdown: bool = False) -> str:
    text = _text(value, label)
    if "://" in text:
        raise KickoffVerificationError(f"{label} must be a local relative path")
    path_text = text.split("#", 1)[0]
    path = Path(path_text)
    if (
        path.is_absolute()
        or path.as_posix() != path_text
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise KickoffVerificationError(f"{label} must be a canonical relative path")
    if markdown and not path_text.endswith(".md"):
        raise KickoffVerificationError(f"{label} must be a relative Markdown path")
    return text


def _load(path: Path, root: Path | None = None) -> dict[str, Any]:
    if path.is_symlink():
        raise KickoffVerificationError(f"artifact must not be a symlink: {path}")
    if root is not None:
        try:
            path.resolve(strict=True).relative_to(root.resolve(strict=True))
        except (OSError, ValueError) as exc:
            raise KickoffVerificationError(f"artifact escapes package: {path}") from exc
    try:
        value = strict_json_loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, DuplicateJsonKeyError) as exc:
        raise KickoffVerificationError(f"invalid JSON artifact {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise KickoffVerificationError(f"artifact {path} must contain one object")
    return value


def _validate_source(value: Any, label: str, as_of: str, *, synthetic: bool = False) -> str:
    source = _object(value, SOURCE_KEYS, label)
    if source["source_kind"] == "SYNTHETIC" and synthetic:
        reference = _relative_path(source["url"], f"{label}.url")
        _text(source["publisher"], f"{label}.publisher")
        _text(source["evidence"], f"{label}.evidence")
        if _date(source["retrieved_on"], f"{label}.retrieved_on") != as_of:
            raise KickoffVerificationError("synthetic source date differs")
        return reference
    if source["source_kind"] != "PRIMARY_OFFICIAL":
        raise KickoffVerificationError(f"{label}.source_kind must be PRIMARY_OFFICIAL")
    _text(source["publisher"], f"{label}.publisher")
    url = _text(source["url"], f"{label}.url")
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise KickoffVerificationError(f"{label}.url must be an absolute HTTPS URL")
    if _date(source["retrieved_on"], f"{label}.retrieved_on") != as_of:
        raise KickoffVerificationError(f"{label}.retrieved_on must match research_as_of")
    _text(source["evidence"], f"{label}.evidence")
    return url


def _validate_research(
    report: dict[str, Any], delegation: dict[str, Any], as_of: str, *, synthetic: bool = False
) -> tuple[str, dict[str, Any]]:
    lane_id = delegation["lane_id"]
    expected_keys = STACK_RESEARCH_KEYS if lane_id == "stack" else RESEARCH_KEYS
    report = _object(report, expected_keys, f"research/{lane_id}")
    _schema_one(report["schema_version"], f"research/{lane_id}.schema_version")
    if report["lane_id"] != lane_id or report["author"] != delegation["owner"]:
        raise KickoffVerificationError(f"research/{lane_id} ownership mismatch")
    if report["scope"] != delegation["scope"]:
        raise KickoffVerificationError(f"research/{lane_id} scope mismatch")
    if _date(report["as_of"], f"research/{lane_id}.as_of") != as_of:
        raise KickoffVerificationError(f"research/{lane_id}.as_of mismatch")
    status = report["status"]
    if status not in {"PROVED", "UNPROVED", "BLOCKED"}:
        raise KickoffVerificationError(f"research/{lane_id}.status is invalid")
    if not isinstance(report["sources"], list) or not isinstance(report["options"], list):
        raise KickoffVerificationError(f"research/{lane_id} sources/options must be lists")
    _text(report["recommendation"], f"research/{lane_id}.recommendation")
    _text(report["decision_impact"], f"research/{lane_id}.decision_impact")
    urls = {
        _validate_source(source, f"research/{lane_id}.sources[{index}]", as_of, synthetic=synthetic)
        for index, source in enumerate(report["sources"])
    }
    for index, value in enumerate(report["options"]):
        option = _object(value, OPTION_KEYS, f"research/{lane_id}.options[{index}]")
        _text(option["name"], f"research/{lane_id}.options[{index}].name")
        _text_list(option["strengths"], f"research/{lane_id}.options[{index}].strengths")
        _text_list(option["risks"], f"research/{lane_id}.options[{index}].risks")
        refs = _text_list(
            option["evidence_refs"], f"research/{lane_id}.options[{index}].evidence_refs"
        )
        if not set(refs).issubset(urls):
            raise KickoffVerificationError(f"research/{lane_id} option cites unknown source")

    if status == "PROVED":
        if not urls or not report["options"]:
            raise KickoffVerificationError(f"research/{lane_id} PROVED needs sources/options")
        if report["unproved_boundary"] is not None:
            raise KickoffVerificationError(f"research/{lane_id} PROVED boundary must be null")
    else:
        _text(report["unproved_boundary"], f"research/{lane_id}.unproved_boundary")
    if lane_id == "stack":
        portfolio_state = _validate_portfolio(report, f"research/{lane_id}", as_of)
        if status == "PROVED" and portfolio_state != "PROVED":
            raise KickoffVerificationError(
                "PROVED stack lane cannot hide unproved portfolio evidence"
            )
        if status == "UNPROVED" and portfolio_state == "BLOCKED":
            raise KickoffVerificationError(
                "UNPROVED stack lane cannot hide blocked portfolio evidence"
            )
    return status, report


def _validate_portfolio(value: dict[str, Any], label: str, as_of: str) -> str:
    portfolio_reference = _object(
        value["portfolio_reference"], PORTFOLIO_REFERENCE_KEYS, f"{label}.portfolio_reference"
    )
    reference_path = _relative_path(
        portfolio_reference["path"], f"{label}.portfolio_reference.path", markdown=True
    )
    reference_status = portfolio_reference["status"]
    if reference_status not in {"PROVED", "UNPROVED", "BLOCKED"}:
        raise KickoffVerificationError(f"{label}.portfolio_reference.status is invalid")
    if _date(portfolio_reference["as_of"], f"{label}.portfolio_reference.as_of") != as_of:
        raise KickoffVerificationError(f"{label}.portfolio reference date must match research date")
    _text(portfolio_reference["evidence"], f"{label}.portfolio_reference.evidence")
    if value["reuse_policy"] != "PREFER_REUSE_WHEN_FIT_NOT_FORCED":
        raise KickoffVerificationError(f"{label} must prefer portfolio reuse when fit")

    assessments = value["portfolio_assessments"]
    if not isinstance(assessments, list) or len(assessments) != len(PORTFOLIO_BASELINES):
        raise KickoffVerificationError(
            f"{label} needs generic service, application and small-combination assessments"
        )
    assessed: set[str] = set()
    has_unproved = reference_status == "UNPROVED"
    has_blocked = reference_status == "BLOCKED"
    for index, item in enumerate(assessments):
        assessment = _object(
            item, PORTFOLIO_ASSESSMENT_KEYS, f"{label}.portfolio_assessments[{index}]"
        )
        baseline = assessment["baseline"]
        if baseline not in PORTFOLIO_BASELINES or baseline in assessed:
            raise KickoffVerificationError(
                "portfolio baseline tokens must be unique reference shapes"
            )
        assessed.add(baseline)
        fit = assessment["fit"]
        disposition = assessment["disposition"]
        if fit not in {"FIT", "PARTIAL", "NO_FIT", "UNPROVED", "BLOCKED"}:
            raise KickoffVerificationError(f"portfolio assessment {baseline} fit is invalid")
        if disposition not in {"REUSE", "COMBINE", "DECLINE", "UNPROVED", "BLOCKED"}:
            raise KickoffVerificationError(
                f"portfolio assessment {baseline} disposition is invalid"
            )
        for key in ("objective_specific_fit", "solo_maintenance_cost"):
            _text(assessment[key], f"portfolio assessment {baseline}.{key}")
        evidence_ref = _relative_path(
            assessment["evidence_ref"], f"portfolio assessment {baseline}.evidence_ref"
        )
        if evidence_ref != reference_path and not evidence_ref.startswith(reference_path + "#"):
            raise KickoffVerificationError(f"portfolio assessment {baseline} cites another source")
        has_unproved = has_unproved or fit == "UNPROVED" or disposition == "UNPROVED"
        has_blocked = has_blocked or fit == "BLOCKED" or disposition == "BLOCKED"
    if has_blocked:
        return "BLOCKED"
    if has_unproved:
        return "UNPROVED"
    return "PROVED"


def _validate_local_inputs(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise KickoffVerificationError(f"{label} must cite at least one exact local input")
    for index, item in enumerate(value):
        local_input = _object(item, LOCAL_INPUT_KEYS, f"{label}[{index}]")
        _relative_path(local_input["path"], f"{label}[{index}].path")
        _text(local_input["snapshot"], f"{label}[{index}].snapshot")
        if local_input["state"] not in {"DIRECT", "INFERRED", "UNPROVED", "BLOCKED"}:
            raise KickoffVerificationError(f"{label}[{index}].state is invalid")
        _text(local_input["evidence"], f"{label}[{index}].evidence")
    return [item["state"] for item in value]


def _validate_local_research(report: dict[str, Any], delegation: dict[str, Any]) -> str:
    lane_id = delegation["lane_id"]
    report = _object(report, LOCAL_RESEARCH_KEYS, f"research/{lane_id}")
    _schema_one(report["schema_version"], f"research/{lane_id}.schema_version")
    if report["lane_id"] != lane_id or report["author"] != delegation["owner"]:
        raise KickoffVerificationError(f"research/{lane_id} ownership mismatch")
    if report["scope"] != delegation["scope"]:
        raise KickoffVerificationError(f"research/{lane_id} scope mismatch")
    status = report["status"]
    if status not in {"PROVED", "UNPROVED", "BLOCKED"}:
        raise KickoffVerificationError(f"research/{lane_id}.status is invalid")
    states = _validate_local_inputs(report["local_inputs"], f"research/{lane_id}.local_inputs")
    _text_list(report["findings"], f"research/{lane_id}.findings")
    _text_list(report["recommendations"], f"research/{lane_id}.recommendations")
    if status == "PROVED":
        if report["unproved_boundary"] is not None:
            raise KickoffVerificationError(f"research/{lane_id} PROVED boundary must be null")
    else:
        _text(report["unproved_boundary"], f"research/{lane_id}.unproved_boundary")
    _validate_status_states(status, states, f"research/{lane_id}")
    return status


def _validate_status_states(status: str, states: list[str], label: str) -> None:
    if status == "PROVED" and any(state in {"UNPROVED", "BLOCKED"} for state in states):
        raise KickoffVerificationError(f"{label} PROVED cannot hide unproved/blocked inputs")
    if status == "UNPROVED" and ("UNPROVED" not in states or "BLOCKED" in states):
        raise KickoffVerificationError(
            f"{label} UNPROVED must expose an unproved, non-blocked input"
        )
    if status == "BLOCKED" and "BLOCKED" not in states:
        raise KickoffVerificationError(f"{label} BLOCKED must expose a blocked input")


def _validate_challenge(
    report: dict[str, Any],
    delegation: dict[str, Any],
    required_cross_checks: list[str],
) -> tuple[str, dict[str, dict[str, Any]]]:
    report = _object(report, CHALLENGE_KEYS, "research/challenge")
    _schema_one(report["schema_version"], "challenge.schema_version")
    if report["lane_id"] != CHALLENGE_LANE_ID:
        raise KickoffVerificationError("challenge lane is invalid")
    if report["author"] != delegation["owner"] or report["scope"] != delegation["scope"]:
        raise KickoffVerificationError("challenge ownership/scope mismatch")
    status = report["status"]
    if status not in {"PROVED", "UNPROVED", "BLOCKED"}:
        raise KickoffVerificationError("challenge status is invalid")
    states = _validate_local_inputs(report["local_inputs"], "research/challenge.local_inputs")
    if report["reviewed_artifacts"] != [
        "technology-options-research-brief.json",
        "technology-architecture-adr.json",
        "kickoff-plan.json",
    ]:
        raise KickoffVerificationError("challenge must review all three draft synthesis artifacts")
    challenge_cross_checks = _text_list(
        report["coupled_hazard_cross_checks"],
        "research/challenge.coupled_hazard_cross_checks",
        allow_empty=True,
    )
    if challenge_cross_checks != required_cross_checks:
        raise KickoffVerificationError(
            "challenge coupled-hazard cross-checks must match the coordination assignment"
        )
    if report["verdict"] not in {"CLEAN", "FINDING", "BLOCKED"}:
        raise KickoffVerificationError("challenge verdict is invalid")
    if not isinstance(report["findings"], list):
        raise KickoffVerificationError("challenge findings must be a list")
    findings: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(report["findings"]):
        finding = _object(item, CHALLENGE_FINDING_KEYS, f"challenge.findings[{index}]")
        finding_id = _text(finding["finding_id"], f"challenge.findings[{index}].id")
        if finding_id in findings:
            raise KickoffVerificationError("challenge finding IDs must be unique")
        if finding["severity"] not in {"HIGH", "MEDIUM", "LOW"}:
            raise KickoffVerificationError(f"challenge finding {finding_id} severity invalid")
        for key in ("statement", "recommended_adr_action", "recommended_plan_action"):
            _text(finding[key], f"challenge finding {finding_id}.{key}")
        findings[finding_id] = finding
    if report["verdict"] == "CLEAN" and findings:
        raise KickoffVerificationError("CLEAN challenge cannot contain findings")
    if report["verdict"] == "FINDING" and not findings:
        raise KickoffVerificationError("FINDING challenge requires findings")
    if (status == "BLOCKED") != (report["verdict"] == "BLOCKED"):
        raise KickoffVerificationError("challenge BLOCKED status and verdict must agree")
    if status == "PROVED":
        if report["unproved_boundary"] is not None:
            raise KickoffVerificationError("proved challenge boundary must be null")
    else:
        _text(report["unproved_boundary"], "challenge.unproved_boundary")
    _validate_status_states(status, states, "research/challenge")
    return status, findings


def _validate_challenge_dispositions(
    value: Any,
    label: str,
    findings: dict[str, dict[str, Any]],
    artifact: str,
) -> dict[str, str]:
    if not isinstance(value, list):
        raise KickoffVerificationError(f"{label} must be a list")
    dispositions: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(value):
        disposition = _object(item, DISPOSITION_KEYS, f"{label}[{index}]")
        finding_id = disposition["finding_id"]
        if finding_id not in findings or finding_id in dispositions:
            raise KickoffVerificationError(f"{label} contains unknown/duplicate finding")
        if disposition["disposition"] not in {
            "ACCEPTED",
            "REJECTED_WITH_REASON",
            "DEFERRED_BLOCKED",
        }:
            raise KickoffVerificationError(f"{label} finding {finding_id} disposition invalid")
        response = _text(disposition["response"], f"{label} finding {finding_id}.response")
        if len(response.strip()) < 24:
            raise KickoffVerificationError(
                f"{label} finding {finding_id} response is not meaningful"
            )
        if disposition["evidence_ref"] != "research/challenge.json":
            raise KickoffVerificationError(f"{label} finding {finding_id} evidence ref invalid")
        resolution_path = _relative_path(
            disposition["resolution_path"], f"{label} finding {finding_id}.resolution_path"
        )
        if disposition["disposition"] == "ACCEPTED":
            expected_prefix = artifact + "#"
            if not resolution_path.startswith(expected_prefix):
                raise KickoffVerificationError(
                    f"{label} accepted finding {finding_id} must identify its resolved field"
                )
            top_field = resolution_path[len(expected_prefix) :].split("/", 1)[0]
            allowed_fields = (
                {
                    "constraints",
                    "risks",
                    "decision",
                    "revisit_triggers",
                    "new_stack_divergence",
                    "alternatives",
                }
                if artifact == "technology-architecture-adr.json"
                else {"phases", "package_strategy", "authority_gate", "steady_state"}
            )
            if top_field not in allowed_fields:
                raise KickoffVerificationError(
                    f"{label} accepted finding {finding_id} resolution field is invalid"
                )
        dispositions[finding_id] = disposition
    if set(dispositions) != set(findings):
        raise KickoffVerificationError(f"{label} must dispose every challenge finding")
    return {finding_id: item["disposition"] for finding_id, item in dispositions.items()}


def _validate_coordination(package: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    value = _load(package / "coordination.json", package)
    synthetic = value.get("evidence_mode") == "SYNTHETIC_SCHEMA_ONLY"
    if "evidence_mode" in value and not synthetic:
        raise KickoffVerificationError(
            "coordination.evidence_mode must be SYNTHETIC_SCHEMA_ONLY or absent"
        )
    value = _object(
        value, COORDINATION_KEYS | ({"evidence_mode"} if synthetic else set()), "coordination"
    )
    _schema_one(value["schema_version"], "coordination.schema_version")
    if value["phase"] != "KICKOFF_RESEARCH":
        raise KickoffVerificationError("coordination phase is invalid")
    _text(value["objective"], "coordination.objective")
    if value["status"] not in {"READY_FOR_AUTHORIZATION", "UNPROVED", "BLOCKED"}:
        raise KickoffVerificationError("coordination.status is invalid")
    _date(value["research_as_of"], "coordination.research_as_of")
    coordinator_key = _identity_key(value["coordinator"], "coordination.coordinator")
    if value["coordinator_mode"] != "ORCHESTRATOR_ONLY":
        raise KickoffVerificationError("initial coordinator must be ORCHESTRATOR_ONLY")
    if value["implementation_authorized"] is not False:
        raise KickoffVerificationError("implementation must remain unauthorized")
    if value["install_authorized"] is not False:
        raise KickoffVerificationError("package installation must remain unauthorized")
    if value["synthesis_artifacts"] != [
        "technology-options-research-brief.json",
        "technology-architecture-adr.json",
        "kickoff-plan.json",
    ]:
        raise KickoffVerificationError("coordination synthesis_artifacts differ")
    if value["steady_state_topology"] != "PROPORTIONAL_SINGLE_AGENT_DEFAULT":
        raise KickoffVerificationError(
            "steady state must return to proportional single-agent default"
        )

    delegations = value["delegations"]
    if not isinstance(delegations, list) or len(delegations) != len(LANE_IDS):
        raise KickoffVerificationError("all six concern artifacts and one challenge are required")
    by_lane: dict[str, dict[str, Any]] = {}
    research_owners: set[str] = set()
    for index, item in enumerate(delegations):
        delegation = _object(item, DELEGATION_KEYS, f"delegations[{index}]")
        lane_id = delegation["lane_id"]
        if lane_id not in LANE_IDS or lane_id in by_lane:
            raise KickoffVerificationError(
                "delegation lane IDs are missing, duplicated, or unknown"
            )
        owner_key = _identity_key(delegation["owner"], f"delegations[{index}].owner")
        if owner_key == coordinator_key:
            raise KickoffVerificationError("kickoff owners must be non-coordinator")
        if lane_id != CHALLENGE_LANE_ID:
            research_owners.add(owner_key)
        _text(delegation["scope"], f"delegations[{index}].scope")
        if delegation["concern"] != LANE_CONCERNS[lane_id]:
            raise KickoffVerificationError(f"delegation {lane_id} concern mismatch")
        expected_stage = "CHALLENGE" if lane_id == CHALLENGE_LANE_ID else "EXPLORATION"
        if delegation["stage"] != expected_stage:
            raise KickoffVerificationError(f"delegation {lane_id} stage mismatch")
        inputs = _text_list(delegation["inputs"], f"delegations[{index}].inputs")
        if lane_id == CHALLENGE_LANE_ID and inputs != [
            "technology-options-research-brief.json",
            "technology-architecture-adr.json",
            "kickoff-plan.json",
        ]:
            raise KickoffVerificationError("challenge must follow all draft synthesis artifacts")
        if delegation["artifact"] != f"research/{lane_id}.json":
            raise KickoffVerificationError(f"delegation {lane_id} artifact mismatch")
        _relative_path(delegation["artifact"], f"delegations[{index}].artifact")
        if delegation["independent"] is not True:
            raise KickoffVerificationError(f"delegation {lane_id} must be independent")
        if delegation["may_mutate_project"] is not False or delegation["may_use_git"] is not False:
            raise KickoffVerificationError(f"delegation {lane_id} must be read-only/no-Git")
        if delegation["status"] not in {"COMPLETE", "UNPROVED", "BLOCKED"}:
            raise KickoffVerificationError(f"delegation {lane_id} status invalid")
        _text(delegation["receipt"], f"delegations[{index}].receipt")
        by_lane[lane_id] = delegation
    if set(by_lane) != LANE_IDS:
        raise KickoffVerificationError("every required kickoff concern lane is required")
    if len(research_owners) < 2:
        raise KickoffVerificationError("kickoff requires at least two distinct research owners")
    if _identity_key(by_lane[CHALLENGE_LANE_ID]["owner"], "challenge owner") in research_owners:
        raise KickoffVerificationError("challenger must be distinct from every research owner")

    assignment = _object(
        value["architecture_delivery_assignment"],
        ARCHITECTURE_DELIVERY_KEYS,
        "coordination.architecture_delivery_assignment",
    )
    if assignment["risk_class"] not in {"LOWER_RISK", "HIGH_RISK_OR_DESTRUCTIVE"}:
        raise KickoffVerificationError("architecture/delivery risk class is invalid")
    if not isinstance(assignment["merged"], bool):
        raise KickoffVerificationError("architecture/delivery merged flag must be boolean")
    actually_merged = _identity_key(
        by_lane["architecture"]["owner"], "architecture owner"
    ) == _identity_key(by_lane["delivery"]["owner"], "delivery owner")
    if assignment["merged"] is not actually_merged:
        raise KickoffVerificationError(
            "architecture/delivery merged flag must match attributed ownership"
        )
    cross_checks = _text_list(
        assignment["challenger_cross_checks"],
        "coordination.architecture_delivery_assignment.challenger_cross_checks",
        allow_empty=True,
    )
    if len(cross_checks) != len(set(cross_checks)):
        raise KickoffVerificationError("challenger coupled-hazard cross-checks must be unique")
    if actually_merged:
        if assignment["risk_class"] != "LOWER_RISK":
            raise KickoffVerificationError(
                "high-risk or destructive architecture and delivery concerns must use different owners"
            )
        rationale = _text(
            assignment["safe_merge_rationale"],
            "coordination.architecture_delivery_assignment.safe_merge_rationale",
        )
        if len(rationale.strip()) < 32:
            raise KickoffVerificationError("lower-risk safe-merge rationale must be concrete")
        if set(cross_checks) != COUPLED_HAZARD_CROSS_CHECKS or len(cross_checks) != len(
            COUPLED_HAZARD_CROSS_CHECKS
        ):
            raise KickoffVerificationError(
                "lower-risk architecture/delivery merge requires all named coupled-hazard cross-checks"
            )
    elif assignment["safe_merge_rationale"] is not None or cross_checks:
        raise KickoffVerificationError(
            "separate architecture/delivery owners must use null rationale and no merge cross-check list"
        )
    if value["status"] == "READY_FOR_AUTHORIZATION" and any(
        item["status"] != "COMPLETE" for item in delegations
    ):
        raise KickoffVerificationError(
            "ready coordination cannot contain unproved/blocked delegation"
        )
    return value, by_lane


def _validate_brief(
    package: Path,
    coordination: dict[str, Any],
    research_statuses: dict[str, str],
) -> str:
    value = _object(
        _load(package / "technology-options-research-brief.json", package),
        BRIEF_KEYS,
        "technology_options_brief",
    )
    _schema_one(value["schema_version"], "technology_options_brief.schema_version")
    if _date(value["as_of"], "technology_options_brief.as_of") != coordination["research_as_of"]:
        raise KickoffVerificationError("technology options brief date mismatch")
    if (
        value["owner"] != coordination["coordinator"]
        or value["objective"] != coordination["objective"]
    ):
        raise KickoffVerificationError("technology options brief owner/objective mismatch")
    if set(value["input_lanes"]) != TECH_LANE_IDS or len(value["input_lanes"]) != len(
        TECH_LANE_IDS
    ):
        raise KickoffVerificationError(
            "technology options brief must synthesize language/stack/tooling"
        )
    refs = _text_list(value["evidence_refs"], "technology_options_brief.evidence_refs")
    required_refs = {f"research/{lane}.json" for lane in TECH_LANE_IDS}
    if not required_refs.issubset(set(refs)):
        raise KickoffVerificationError("technology options brief must cite every technology lane")
    for index, ref in enumerate(refs):
        _relative_path(ref, f"technology_options_brief.evidence_refs[{index}]")
    options = value["options"]
    required_concerns = {"LANGUAGE", "STACK", "TOOLING", "PORTFOLIO_REUSE"}
    if not isinstance(options, list) or len(options) != len(required_concerns):
        raise KickoffVerificationError("technology options brief requires four decision options")
    concerns: set[str] = set()
    for index, item in enumerate(options):
        option = _object(item, BRIEF_OPTION_KEYS, f"technology_options_brief.options[{index}]")
        concern = option["concern"]
        if concern not in required_concerns or concern in concerns:
            raise KickoffVerificationError(
                "technology options brief concerns must be unique and complete"
            )
        concerns.add(concern)
        for key in ("option", "objective_fit", "solo_maintenance_cost"):
            _text(option[key], f"technology_options_brief.options[{index}].{key}")
        option_refs = _text_list(
            option["evidence_refs"], f"technology_options_brief.options[{index}].evidence_refs"
        )
        if not set(option_refs).issubset(set(refs)):
            raise KickoffVerificationError(
                "technology options brief option cites undeclared evidence"
            )
    _text_list(value["comparison_criteria"], "technology_options_brief.comparison_criteria")
    _text(value["recommendation"], "technology_options_brief.recommendation")
    tech_states = [research_statuses[lane] for lane in TECH_LANE_IDS]
    expected_status = (
        "BLOCKED"
        if "BLOCKED" in tech_states
        else "UNPROVED"
        if "UNPROVED" in tech_states
        else "READY_FOR_ADR"
    )
    if value["status"] != expected_status:
        raise KickoffVerificationError("technology options brief status hides lane state")
    boundaries = value["unproved_boundaries"]
    if expected_status == "READY_FOR_ADR":
        if boundaries != []:
            raise KickoffVerificationError(
                "proved technology options brief boundaries must be empty"
            )
    else:
        _text_list(boundaries, "technology_options_brief.unproved_boundaries")
    return expected_status


def _validate_adr(
    package: Path,
    coordination: dict[str, Any],
    research_statuses: dict[str, str],
    challenge_findings: dict[str, dict[str, Any]],
    stack_report: dict[str, Any],
) -> dict[str, str]:
    value = _object(_load(package / "technology-architecture-adr.json", package), ADR_KEYS, "adr")
    _schema_one(value["schema_version"], "adr.schema_version")
    if value["adr_id"] != "ADR-KICKOFF-001":
        raise KickoffVerificationError("ADR id is invalid")
    allowed_status = {"PROPOSED_FOR_AUTHORIZATION", "PROPOSED_WITH_UNPROVED", "BLOCKED"}
    if value["status"] not in allowed_status:
        raise KickoffVerificationError("ADR status is invalid")
    if _date(value["date"], "adr.date") != coordination["research_as_of"]:
        raise KickoffVerificationError("ADR date must match research date")
    if value["owner"] != coordination["coordinator"]:
        raise KickoffVerificationError("ADR must be owned by coordinator")
    if value["objective"] != coordination["objective"]:
        raise KickoffVerificationError("ADR objective mismatch")
    if set(value["input_lanes"]) != LANE_IDS or len(value["input_lanes"]) != len(LANE_IDS):
        raise KickoffVerificationError("ADR must synthesize every exploration and challenge lane")
    required_refs = {f"research/{lane}.json" for lane in LANE_IDS}
    evidence_refs = _text_list(value["evidence_refs"], "adr.evidence_refs")
    for index, ref in enumerate(evidence_refs):
        _relative_path(ref, f"adr.evidence_refs[{index}]")
    if not required_refs.issubset(set(evidence_refs)):
        raise KickoffVerificationError("ADR must reference every research artifact")
    if (
        value["technology_options_brief"] != "technology-options-research-brief.json"
        or value["technology_options_brief"] not in evidence_refs
    ):
        raise KickoffVerificationError("ADR must cite the coordinator technology options brief")
    challenge_dispositions = _validate_challenge_dispositions(
        value["challenge_dispositions"],
        "adr.challenge_dispositions",
        challenge_findings,
        "technology-architecture-adr.json",
    )

    portfolio_status = _validate_portfolio(value, "adr", coordination["research_as_of"])
    for key in ("portfolio_reference", "reuse_policy", "portfolio_assessments"):
        if value[key] != stack_report[key]:
            raise KickoffVerificationError(f"ADR {key} must synthesize the stack lane exactly")
    assessments = value["portfolio_assessments"]
    dispositions: set[str] = set()
    for assessment in assessments:
        dispositions.add(assessment["disposition"])

    divergence = _object(value["new_stack_divergence"], NEW_STACK_KEYS, "adr.new_stack_divergence")
    if not isinstance(divergence["selected"], bool):
        raise KickoffVerificationError("new_stack_divergence.selected must be boolean")
    if not isinstance(divergence["evidence_refs"], list):
        raise KickoffVerificationError("new_stack_divergence.evidence_refs must be a list")
    if divergence["selected"]:
        _text(
            divergence["objective_specific_justification"],
            "adr.new_stack_divergence.objective_specific_justification",
        )
        _text(
            divergence["solo_maintenance_cost"],
            "adr.new_stack_divergence.solo_maintenance_cost",
        )
        divergence_refs = _text_list(
            divergence["evidence_refs"], "adr.new_stack_divergence.evidence_refs"
        )
        if not set(divergence_refs).issubset(set(value["evidence_refs"])):
            raise KickoffVerificationError("new-stack divergence cites unknown evidence")
    else:
        if (
            divergence["objective_specific_justification"] is not None
            or divergence["solo_maintenance_cost"] is not None
        ):
            raise KickoffVerificationError("no-divergence ADR must use null justification/cost")
        if not ({"REUSE", "COMBINE"} & dispositions):
            raise KickoffVerificationError(
                "no-divergence ADR must reuse or combine a portfolio baseline"
            )
    decision = _object(value["decision"], DECISION_KEYS, "adr.decision")
    for key in ("language", "stack", "tooling"):
        _text(decision[key], f"adr.decision.{key}")
    _text_list(decision["architecture"], "adr.decision.architecture")
    if not isinstance(value["alternatives"], list) or not value["alternatives"]:
        raise KickoffVerificationError("ADR needs at least one alternative")
    for index, item in enumerate(value["alternatives"]):
        alternative = _object(item, ALTERNATIVE_KEYS, f"adr.alternatives[{index}]")
        _text(alternative["option"], f"adr.alternatives[{index}].option")
        _text(alternative["reason_not_selected"], f"adr.alternatives[{index}].reason")
        alternative_refs = _text_list(
            alternative["evidence_refs"], f"adr.alternatives[{index}].evidence_refs"
        )
        if not set(alternative_refs).issubset(set(evidence_refs)):
            raise KickoffVerificationError("ADR alternative cites undeclared evidence")
    _text_list(value["constraints"], "adr.constraints")
    _text_list(value["risks"], "adr.risks")
    _text_list(value["revisit_triggers"], "adr.revisit_triggers")
    if not isinstance(value["unproved_boundaries"], list):
        raise KickoffVerificationError("adr.unproved_boundaries must be a list")
    has_blocked = portfolio_status == "BLOCKED" or "BLOCKED" in research_statuses.values()
    has_deferred = "DEFERRED_BLOCKED" in challenge_dispositions.values()
    has_unproved = portfolio_status == "UNPROVED" or "UNPROVED" in research_statuses.values()
    expected_status = (
        "BLOCKED"
        if has_blocked or has_deferred
        else "PROPOSED_WITH_UNPROVED"
        if has_unproved
        else "PROPOSED_FOR_AUTHORIZATION"
    )
    if value["status"] != expected_status:
        raise KickoffVerificationError("ADR status does not propagate research/challenge state")
    if expected_status != "PROPOSED_FOR_AUTHORIZATION":
        _text_list(value["unproved_boundaries"], "adr.unproved_boundaries")
    elif value["unproved_boundaries"] != []:
        raise KickoffVerificationError("proved ADR unproved_boundaries must be empty")
    return challenge_dispositions


def _validate_plan(
    package: Path,
    coordination: dict[str, Any],
    challenge_findings: dict[str, dict[str, Any]],
    research_statuses: dict[str, str],
) -> dict[str, str]:
    value = _object(_load(package / "kickoff-plan.json", package), PLAN_KEYS, "plan")
    _schema_one(value["schema_version"], "plan.schema_version")
    if value["status"] not in {
        "AWAITING_IMPLEMENTATION_AUTHORIZATION",
        "AWAITING_WITH_UNPROVED",
        "BLOCKED",
    }:
        raise KickoffVerificationError("plan.status is invalid")
    if (
        value["owner"] != coordination["coordinator"]
        or value["based_on"] != "technology-architecture-adr.json"
    ):
        raise KickoffVerificationError("plan owner/based_on mismatch")
    if set(value["input_lanes"]) != LANE_IDS or len(value["input_lanes"]) != len(LANE_IDS):
        raise KickoffVerificationError("plan must synthesize every exploration and challenge lane")
    required_refs = {f"research/{lane}.json" for lane in LANE_IDS} | {
        "technology-options-research-brief.json"
    }
    plan_refs = _text_list(value["evidence_refs"], "plan.evidence_refs")
    for index, ref in enumerate(plan_refs):
        _relative_path(ref, f"plan.evidence_refs[{index}]")
    if not required_refs.issubset(set(plan_refs)):
        raise KickoffVerificationError("plan must reference every research artifact")
    challenge_dispositions = _validate_challenge_dispositions(
        value["challenge_dispositions"],
        "plan.challenge_dispositions",
        challenge_findings,
        "kickoff-plan.json",
    )
    if value["implementation_authorized"] is not False:
        raise KickoffVerificationError("plan must not authorize implementation")
    if value["install_authorized"] is not False:
        raise KickoffVerificationError("plan must not authorize package installation")

    # Bootstrap proves that a target owns an operating rule and gates; it cannot infer
    # comment quality. The separate non-author full-source read remains semantic proof.
    comprehension = _object(
        value["source_comprehension"],
        SOURCE_COMPREHENSION_KEYS,
        "plan.source_comprehension",
    )
    for key in ("community_basis", "owner", "existing_debt_disposition"):
        _text(comprehension[key], f"plan.source_comprehension.{key}")
    _relative_path(
        comprehension["target_rule_path"],
        "plan.source_comprehension.target_rule_path",
        markdown=True,
    )
    exceptions = _text_list(comprehension["exceptions"], "plan.source_comprehension.exceptions")
    if len(exceptions) != len(set(exceptions)):
        raise KickoffVerificationError("plan.source_comprehension.exceptions must be unique")
    if comprehension["implementation_gate"] != SOURCE_IMPLEMENTATION_GATE:
        raise KickoffVerificationError(
            "plan.source_comprehension.implementation_gate must require the complete "
            "changed authored-source assessment before handoff"
        )
    if comprehension["review_gate"] != SOURCE_REVIEW_GATE:
        raise KickoffVerificationError(
            "plan.source_comprehension.review_gate must require non-author complete "
            "changed-source review and a missing-contract finding"
        )

    quality = _object(value["quality_control"], QUALITY_CONTROL_KEYS, "plan.quality_control")
    if quality["applicability"] not in {
        "MERGED_SMALL_CODED_PROJECT",
        "MATERIAL_MULTI_COMPONENT_CODED_PROJECT",
    }:
        raise KickoffVerificationError("plan.quality_control.applicability is invalid")
    for key in (
        "owner",
        "location",
        "unknown_policy",
        "action_rule",
        "challenge_rule",
        "automation_limit",
    ):
        _text(quality[key], f"plan.quality_control.{key}")
    concerns = _text_list(quality["concerns"], "plan.quality_control.concerns")
    required_concerns = {
        "ARCHITECTURE_OWNERSHIP",
        "SOURCE_COMPREHENSION",
        "TESTING_EVIDENCE",
    }
    if not required_concerns.issubset(set(concerns)):
        raise KickoffVerificationError("plan.quality_control omits a core coded-project concern")

    phases = value["phases"]
    expected_order = ["kickoff", "bootstrap", "package-install", "implementation"]
    if (
        not isinstance(phases, list)
        or [item.get("id") for item in phases if isinstance(item, dict)] != expected_order
    ):
        raise KickoffVerificationError(
            "plan phases must be kickoff/bootstrap/package-install/implementation"
        )
    for index, item in enumerate(phases):
        phase = _object(item, PHASE_KEYS, f"plan.phases[{index}]")
        for key in ("owner", "stop_condition"):
            _text(phase[key], f"plan.phases[{index}].{key}")
        tokens = _text_list(
            phase["entry_condition_tokens"], f"plan.phases[{index}].entry_condition_tokens"
        )
        allowed_tokens = {
            "EVIDENCE_PACKAGE_VALID",
            "IMPLEMENTATION_AUTHORIZED",
            "INSTALL_AUTHORIZED",
            "BOOTSTRAP_ACCEPTED",
            "RED_TEST_ACCEPTED",
        }
        if not set(tokens).issubset(allowed_tokens) or len(tokens) != len(set(tokens)):
            raise KickoffVerificationError(f"plan.phases[{index}] has invalid entry tokens")
        if phase["execution_state"] not in {
            "READY_FOR_AUTHORITY_REQUEST",
            "REVIEW_UNPROVED_BOUNDARIES",
            "BLOCKED_BY_EVIDENCE",
            "BLOCKED_PENDING_AUTHORITY",
        }:
            raise KickoffVerificationError(f"plan.phases[{index}].execution_state is invalid")
        if (
            phase["implementation_authorized"] is not False
            or phase["install_authorized"] is not False
        ):
            raise KickoffVerificationError(
                f"plan.phases[{index}] must preserve false authority flags"
            )
        exact_paths = _text_list(phase["exact_paths"], f"plan.phases[{index}].exact_paths")
        for path_index, declared in enumerate(exact_paths):
            _relative_path(declared, f"plan.phases[{index}].exact_paths[{path_index}]")
        for key in ("actions", "evidence"):
            _text_list(phase[key], f"plan.phases[{index}].{key}")
        required_phase_tokens = {
            "kickoff": {"EVIDENCE_PACKAGE_VALID"},
            "bootstrap": {"IMPLEMENTATION_AUTHORIZED"},
            "package-install": {"IMPLEMENTATION_AUTHORIZED", "BOOTSTRAP_ACCEPTED"},
            "implementation": {"IMPLEMENTATION_AUTHORIZED", "RED_TEST_ACCEPTED"},
        }
        if not required_phase_tokens[phase["id"]].issubset(set(tokens)):
            raise KickoffVerificationError(f"plan.phases[{index}] omits a required gate token")
        expected_execution = "BLOCKED_PENDING_AUTHORITY"
        if phase["id"] == "kickoff":
            expected_execution = {
                "AWAITING_IMPLEMENTATION_AUTHORIZATION": "READY_FOR_AUTHORITY_REQUEST",
                "AWAITING_WITH_UNPROVED": "REVIEW_UNPROVED_BOUNDARIES",
                "BLOCKED": "BLOCKED_BY_EVIDENCE",
            }[value["status"]]
        if phase["execution_state"] != expected_execution:
            raise KickoffVerificationError(f"plan.phases[{index}] execution state hides authority")

    phase_by_id = {phase["id"]: phase for phase in phases}
    target_rule_path = comprehension["target_rule_path"]
    bootstrap_phase = phase_by_id["bootstrap"]
    implementation_phase = phase_by_id["implementation"]
    if bootstrap_phase["owner"] != comprehension["owner"]:
        raise KickoffVerificationError(
            "plan.source_comprehension.owner must own the gated bootstrap phase"
        )
    if target_rule_path not in bootstrap_phase["exact_paths"]:
        raise KickoffVerificationError(
            "plan.source_comprehension.target_rule_path must be owned by the gated bootstrap phase"
        )
    required_bootstrap_action = (
        f"Adopt the target-owned source-comprehension rule at {target_rule_path} "
        "before product source."
    )
    required_bootstrap_evidence = (
        f"Inspect {target_rule_path} and record its community basis, owner, "
        "implementation/review gates, exceptions, and debt disposition."
    )
    if required_bootstrap_action not in bootstrap_phase["actions"]:
        raise KickoffVerificationError(
            "gated bootstrap actions must create/adopt the exact target source rule"
        )
    if required_bootstrap_evidence not in bootstrap_phase["evidence"]:
        raise KickoffVerificationError(
            "gated bootstrap evidence must verify the exact target source rule"
        )
    if SOURCE_IMPLEMENTATION_GATE not in implementation_phase["actions"]:
        raise KickoffVerificationError(
            "implementation phase must execute the declared source-comprehension gate"
        )
    if SOURCE_REVIEW_GATE not in implementation_phase["evidence"]:
        raise KickoffVerificationError(
            "implementation evidence must execute the declared non-author review gate"
        )

    strategy = _object(value["package_strategy"], PACKAGE_KEYS, "plan.package_strategy")
    if strategy["action"] not in {"INSTALL", "NO_THIRD_PARTY_PACKAGES"}:
        raise KickoffVerificationError("package strategy action is invalid")
    if strategy["install_authorized"] is not False:
        raise KickoffVerificationError("package strategy must keep install_authorized false")
    if strategy["execution_state"] != "BLOCKED_PENDING_AUTHORITY":
        raise KickoffVerificationError("package strategy must remain blocked pending authority")
    if strategy["next_gate"] not in {
        "REQUEST_INSTALL_AUTHORIZATION",
        "CONFIRM_NO_INSTALL_REQUIRED",
    }:
        raise KickoffVerificationError("package strategy next_gate is invalid")
    if not isinstance(strategy["commands"], list) or not isinstance(strategy["packages"], list):
        raise KickoffVerificationError("package strategy commands/packages must be lists")
    _text(strategy["rationale"], "plan.package_strategy.rationale")
    if strategy["evidence_ref"] != "research/tooling.json":
        raise KickoffVerificationError("package strategy must cite tooling research")
    if strategy["action"] == "INSTALL":
        _text_list(strategy["commands"], "plan.package_strategy.commands")
        if not strategy["packages"]:
            raise KickoffVerificationError("INSTALL strategy needs package entries")
        if strategy["next_gate"] != "REQUEST_INSTALL_AUTHORIZATION":
            raise KickoffVerificationError("INSTALL strategy must request install authorization")
        if "INSTALL_AUTHORIZED" not in phases[2]["entry_condition_tokens"]:
            raise KickoffVerificationError(
                "package-install phase must require install authorization"
            )
    elif strategy["commands"] or strategy["packages"]:
        raise KickoffVerificationError("no-package strategy must have empty commands/packages")
    elif strategy["next_gate"] != "CONFIRM_NO_INSTALL_REQUIRED":
        raise KickoffVerificationError(
            "no-package strategy must confirm that no install is required"
        )
    elif "INSTALL_AUTHORIZED" in phases[2]["entry_condition_tokens"]:
        raise KickoffVerificationError("no-package strategy must not imply an install gate")
    for index, item in enumerate(strategy["packages"]):
        package_item = _object(item, PACKAGE_ITEM_KEYS, f"plan.package_strategy.packages[{index}]")
        for key in PACKAGE_ITEM_KEYS:
            _text(package_item[key], f"plan.package_strategy.packages[{index}].{key}")

    gate = _object(value["authority_gate"], AUTHORITY_KEYS, "plan.authority_gate")
    for key in ("implementation_authorized", "install_authorized", "external_effects_authorized"):
        if gate[key] is not False:
            raise KickoffVerificationError(f"plan.authority_gate.{key} must be false")
    if gate["required_authority_holder"] != "USER":
        raise KickoffVerificationError("plan authority holder must be USER")
    expected_next_gate = {
        "AWAITING_IMPLEMENTATION_AUTHORIZATION": "REQUEST_IMPLEMENTATION_AUTHORIZATION",
        "AWAITING_WITH_UNPROVED": "REVIEW_UNPROVED_BOUNDARIES",
        "BLOCKED": "RESOLVE_BLOCKED_EVIDENCE",
    }[value["status"]]
    if gate["next_gate"] != expected_next_gate:
        raise KickoffVerificationError("plan authority next_gate does not match plan status")
    steady = _object(value["steady_state"], STEADY_STATE_KEYS, "plan.steady_state")
    if (
        steady["topology"] != "PROPORTIONAL_SINGLE_AGENT_DEFAULT"
        or steady["kickoff_research_lanes_end"] is not True
    ):
        raise KickoffVerificationError(
            "plan must end kickoff lanes and return to proportional topology"
        )
    _text(steady["review_rule"], "plan.steady_state.review_rule")
    expected_status = (
        "BLOCKED"
        if "BLOCKED" in research_statuses.values()
        or "DEFERRED_BLOCKED" in challenge_dispositions.values()
        else "AWAITING_WITH_UNPROVED"
        if "UNPROVED" in research_statuses.values()
        else "AWAITING_IMPLEMENTATION_AUTHORIZATION"
    )
    if value["status"] != expected_status:
        raise KickoffVerificationError("plan status does not propagate blocked research/challenge")
    return challenge_dispositions


def _entries(directory: Path) -> list[tuple[Path, int]]:
    """Return every entry below a directory with its lstat mode, failing on any it cannot inspect."""
    entries: list[tuple[Path, int]] = []
    pending = [directory]
    while pending:
        for entry in pending.pop().iterdir():
            mode = entry.lstat().st_mode
            entries.append((entry, mode))
            if stat.S_ISDIR(mode):
                pending.append(entry)
    return entries


def verify(package: Path) -> None:
    """Check a kickoff evidence package, raising KickoffVerificationError on any violation."""
    if package.is_symlink():
        raise KickoffVerificationError("package directory must not be a symlink")
    try:
        package = package.resolve(strict=True)
    # Python 3.11 and 3.12 raise RuntimeError for a symlink loop.
    except (OSError, RuntimeError) as exc:
        raise KickoffVerificationError(f"package cannot be resolved: {package}") from exc
    if not package.is_dir():
        raise KickoffVerificationError(f"package is not a directory: {package}")
    try:
        entries = _entries(package)
    except OSError as exc:
        raise KickoffVerificationError(f"package cannot be listed: {exc.strerror}") from exc
    actual: set[str] = set()
    for path, mode in entries:
        if stat.S_ISLNK(mode):
            raise KickoffVerificationError(f"package must not contain symlinks: {path}")
        if not stat.S_ISREG(mode) and not stat.S_ISDIR(mode):
            raise KickoffVerificationError(f"package must hold only files and directories: {path}")
        try:
            path.resolve(strict=True).relative_to(package)
        except (OSError, ValueError) as exc:
            raise KickoffVerificationError(f"artifact escapes package: {path}") from exc
        if stat.S_ISREG(mode):
            actual.add(path.relative_to(package).as_posix())
    if actual != EXPECTED_FILES:
        raise KickoffVerificationError(
            f"artifact paths differ: missing={sorted(EXPECTED_FILES - actual)}, "
            f"extra={sorted(actual - EXPECTED_FILES)}"
        )
    coordination, delegations = _validate_coordination(package)
    statuses: dict[str, str] = {}
    tech_reports: dict[str, dict[str, Any]] = {}
    for lane_id in sorted(TECH_LANE_IDS):
        delegation = delegations[lane_id]
        statuses[lane_id], tech_reports[lane_id] = _validate_research(
            _load(package / delegation["artifact"], package),
            delegation,
            coordination["research_as_of"],
            synthetic=coordination.get("evidence_mode") == "SYNTHETIC_SCHEMA_ONLY",
        )
    for lane_id in sorted(LOCAL_LANE_IDS):
        delegation = delegations[lane_id]
        statuses[lane_id] = _validate_local_research(
            _load(package / delegation["artifact"], package), delegation
        )
    _validate_brief(package, coordination, statuses)
    challenge_status, challenge_findings = _validate_challenge(
        _load(package / delegations[CHALLENGE_LANE_ID]["artifact"], package),
        delegations[CHALLENGE_LANE_ID],
        coordination["architecture_delivery_assignment"]["challenger_cross_checks"],
    )
    statuses[CHALLENGE_LANE_ID] = challenge_status
    for lane_id, status in statuses.items():
        expected_delegation_status = (
            "BLOCKED" if status == "BLOCKED" else "UNPROVED" if status == "UNPROVED" else "COMPLETE"
        )
        if delegations[lane_id]["status"] != expected_delegation_status:
            raise KickoffVerificationError(f"delegation {lane_id} status hides report state")
    adr_dispositions = _validate_adr(
        package, coordination, statuses, challenge_findings, tech_reports["stack"]
    )
    plan_dispositions = _validate_plan(package, coordination, challenge_findings, statuses)
    if adr_dispositions != plan_dispositions:
        raise KickoffVerificationError("ADR and plan challenge dispositions disagree")
    expected_coordination_status = (
        "BLOCKED"
        if "BLOCKED" in statuses.values() or "DEFERRED_BLOCKED" in adr_dispositions.values()
        else "UNPROVED"
        if "UNPROVED" in statuses.values()
        else "READY_FOR_AUTHORIZATION"
    )
    if coordination["status"] != expected_coordination_status:
        raise KickoffVerificationError("coordination status does not propagate blocked state")


def main(argv: list[str] | None = None) -> int:
    """Run the command line and return the exit code."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        verify(args.package)
    except (OSError, UnicodeDecodeError, KickoffVerificationError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    coordination = _load(args.package / "coordination.json")
    print(
        json.dumps(
            {
                "status": "PASS",
                "evidence_mode": coordination.get("evidence_mode", "LIVE_STRUCTURE_ONLY"),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
