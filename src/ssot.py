#!/usr/bin/env python3
"""SSOT interview, classification, and propose-only DSL emission.

This is a domain pack on wellmanifest/dsl. Canonical documents are JSON AST
conforming to wellmanifest.ssot/decision/v1. The line-oriented text form is a
projection, not a second language.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCHEMA_DECISION = "wellmanifest.ssot/decision/v1"
SCHEMA_INTERVIEW = "wellmanifest.ssot/interview/v1"
SCHEMA_STANDARDS_LOCK = "wellmanifest.standards-lock/v1"
IDENTIFIER = re.compile(r"^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$")
SEMVER = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
)
RELATIVE_PATH = re.compile(r"^(?!/)(?!.*(?:^|/)\.\.(?:/|$))(?!.*\\).+$")
REVISION = re.compile(r"^[a-f0-9]{40}$")
DIGEST = re.compile(r"^sha256:[a-f0-9]{64}$")
MERGE_POLICIES = {"trusted-validator", "manual"}
ON_COMPATIBLE = {"create_pr", "create_ticket", "none"}
ON_BREAKING = {"create_ticket", "block", "none"}

KINDS = {
    "generated_mirror",
    "vendored_copy",
    "facade",
    "allowed_divergence",
    "real_fork",
    "same_file_noise",
    "query_namespace",
    "served_artifact",
    "inventory_vs_runtime",
    "capability_surface",
    "locale_catalog",
    "config_binding",
    "pin_policy",
}
PACKAGING = {
    "git-submodule",
    "npm",
    "pip",
    "vendored-copy",
    "monorepo-path",
    "facade-reexport",
    "unknown",
}
RELATIONSHIPS = {
    "generated_mirror",
    "vendored_copy",
    "facade",
    "allowed_divergence",
    "real_fork",
    "query_namespace",
    "served_artifact",
    "inventory_vs_runtime",
    "capability_surface",
    "locale_catalog",
    "config_binding",
    "unknown",
}
ACTIONS = {
    "edit_upstream",
    "bump_pin",
    "keep_both_checkouts",
    "keep_facade_reexport_canonical",
    "add_parity_test",
    "keep_parity_test",
    "document_known_divergent",
    "vendor_and_gate_drift",
    "choose_canonical",
    "ask_clarifying_questions",
    "ignore_analyzer_until_interview",
    "scope_query_keys",
    "rebuild_served_artifact",
    "refuse_overwrite_dirty_tree",
    "do_not_count_discovery_as_connected",
    "test_operator_and_admin_separately",
    "use_locale_catalog",
    "bind_to_config_source",
    "declare_env_override",
}
FORBIDS = {
    "delete_either_tree",
    "delete_generated_mirror",
    "treat_analyzer_as_debt",
    "couple_standalone_to_foreign_monorepo",
    "fork_logic_into_consumer",
    "leak_query_across_modules",
    "treat_source_as_served",
    "overwrite_dirty_working_tree",
    "count_lan_scan_as_connected_agent",
    "treat_visible_edit_as_authorized",
    "hardcode_ui_locale",
    "hardcode_deployment_value",
}

NOISE_QUESTION = (
    "Analyzer reports are noisy (CC on constants, docs as god modules, "
    "generated files, same-file fuzzy matches). Which pairs has a human "
    "confirmed as real debt?"
)
REASON_QUESTION = (
    "allowed_divergence requires a documented KNOWN_DIVERGENT reason. "
    "Why may these copies differ?"
)
IDENTICAL_QUESTION = (
    "These look like vendored copies. Must they stay byte-identical "
    "(parity test) or are they different protocols by design?"
)


class Finding:
    def __init__(self, code: str, message: str, path: str = "$") -> None:
        self.code = code
        self.message = message
        self.path = path

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(document: Mapping[str, Any]) -> str:
    return json.dumps(document, indent=2, ensure_ascii=False, sort_keys=False) + "\n"


def _is_identifier(value: Any) -> bool:
    return isinstance(value, str) and bool(IDENTIFIER.fullmatch(value))


def _is_semver(value: Any) -> bool:
    return isinstance(value, str) and bool(SEMVER.fullmatch(value))


def _is_path(value: Any) -> bool:
    return isinstance(value, str) and 0 < len(value) <= 500 and bool(
        RELATIVE_PATH.fullmatch(value)
    )


def load_questionnaire(path: Path | None = None) -> dict[str, Any]:
    questionnaire = path or repo_root() / "questions" / "interview.json"
    return load_json(questionnaire)


def _as_bool(raw: str) -> bool:
    value = raw.strip().lower()
    if value in {"y", "yes", "true", "1"}:
        return True
    if value in {"n", "no", "false", "0"}:
        return False
    raise ValueError(f"expected yes/no, got {raw!r}")


def _as_bool_or_unknown(raw: str) -> bool | str:
    value = raw.strip().lower()
    if value in {"unknown", "u", "?"}:
        return "unknown"
    return _as_bool(raw)


def _as_list(raw: str) -> list[str]:
    return [part.strip() for part in raw.split(",") if part.strip()]


def parse_answer(question: Mapping[str, Any], raw: str) -> Any:
    kind = question["type"]
    text = raw.strip()
    if not text:
        if question.get("required"):
            raise ValueError(f"{question['id']} is required")
        return None
    if kind == "bool":
        return _as_bool(text)
    if kind == "bool-or-unknown":
        return _as_bool_or_unknown(text)
    if kind == "identifier":
        value = text.replace(" ", "-").lower()
        if not _is_identifier(value):
            raise ValueError(f"{question['id']} must be a stable identifier")
        return value
    if kind in {"string-list", "path-list", "enum-list"}:
        items = _as_list(text)
        choices = question.get("choices")
        if choices:
            unknown = [item for item in items if item not in choices]
            if unknown:
                raise ValueError(f"{question['id']} unknown values: {unknown}")
        return items
    if kind == "enum":
        if text not in question.get("choices", []):
            raise ValueError(f"{question['id']} must be one of {question['choices']}")
        return text
    return text


def interview_from_answers(answers: Mapping[str, Any]) -> dict[str, Any]:
    document = dict(answers)
    document.setdefault("schema", SCHEMA_INTERVIEW)
    return document


def _action(name: str, target: str | None = None) -> dict[str, str]:
    item = {"do": name}
    if target:
        item["target"] = target
    return item


# Kinds a human states (runtime, UI, fleet, config): what they must propose and forbid.
# One table drives both classify() and validate_decision(), so the contract cannot drift between them.
# actions: (name, takes canonical_ref); validation reports missing actions first, then missing forbids.
STATED_KINDS: dict[str, dict[str, Any]] = {
    "query_namespace": {
        "code": "SSOT-QUERY-001",
        "actions": [("scope_query_keys", True)],
        "forbid": ["leak_query_across_modules"],
        "rationale": (
            "Shell or hardware result keys must stay in the owning module. "
            "URI DSL and capability ACL reject unknown extension keys "
            "(wellmanifest.poa / wellmanifest.dsl unknownPolicy=reject). "
            "Strip or namespace foreign keys on navigate and on arrival; do "
            "not fail the whole page on leftover COMMAND/ADDRESS from another domain."
        ),
    },
    "served_artifact": {
        "code": "SSOT-SERVE-001",
        "actions": [("rebuild_served_artifact", True)],
        "forbid": ["treat_source_as_served"],
        "rationale": (
            "Source edits are not the served SSOT when nginx or a static "
            "dist has no HMR. Rebuild and reload the artifact; a hard "
            "refresh and a longer TestQL WAIT are required before claiming "
            "the UI is fixed."
        ),
    },
    "inventory_vs_runtime": {
        "code": "SSOT-FLEET-001",
        "actions": [("do_not_count_discovery_as_connected", False), ("refuse_overwrite_dirty_tree", False)],
        "required_actions": [],
        "forbid": ["count_lan_scan_as_connected_agent", "overwrite_dirty_working_tree"],
        "check_forbid": ["overwrite_dirty_working_tree", "count_lan_scan_as_connected_agent"],  # report order kept from 0.2.0-dev
        "rationale": (
            "LAN discovery, connected agents, and applied git revision are "
            "three different truths. A scan that sees a host is not an "
            "online agent. A fail-closed updater must refuse a dirty tree "
            "instead of overwriting live hardware work "
            "(wellmanifest.deployment deploy-source-exact)."
        ),
    },
    "capability_surface": {
        "code": "SSOT-POA-001",
        "actions": [("test_operator_and_admin_separately", False)],
        "forbid": ["treat_visible_edit_as_authorized"],
        "rationale": (
            "Visible chrome (Edit, list, scanner) is not a grant. Operator "
            "and admin are different POA capabilities. A 403/429 on write "
            "while Edit is on screen is expected unless the session holds "
            "the write capability. TestQL must cover both roles."
        ),
    },
    "locale_catalog": {
        "code": "SSOT-I18N-001",
        "actions": [("use_locale_catalog", True)],
        "forbid": ["hardcode_ui_locale"],
        "rationale": (
            "Operator-facing copy belongs in the locale catalog. A hardcoded "
            "getContent() or Polish heading stays Polish when lang=en. "
            "Treat the catalog as SSOT; do not ship page-local strings."
        ),
    },
    "config_binding": {
        "code": "SSOT-CONFIG-001",
        "actions": [("bind_to_config_source", True), ("declare_env_override", False)],
        "forbid": ["hardcode_deployment_value"],
        "rationale": (
            "A deployment value (host, port, URL, LAN address, absolute path, "
            "model id, interval) has one declared configuration source. Code, "
            "grammar, UI and tests refer to it by name and resolve it at run "
            "time; a literal copy is a second SSOT that drifts per node. The "
            "override is one declared, documented name (explicit last layer "
            "wins, as in wellmanifest.env-dsl), not an ambient lookup. Secrets "
            "are out of scope here: they follow wellmanifest.secrets."
        ),
    },
}


def _stated_kind(kind: str, canonical_ref: str | None) -> tuple[str, list[dict[str, str]], list[str], str]:
    spec = STATED_KINDS[kind]
    actions = [_action(name, canonical_ref if takes_ref else None) for name, takes_ref in spec["actions"]]
    return kind, actions, list(spec["forbid"]), spec["rationale"]


def _stated_kind_findings(kind: str | None, decision: Mapping[str, Any], prefix: str) -> list[Finding]:
    spec = STATED_KINDS.get(kind or "")
    if not spec:
        return []
    have_actions = {item.get("do") for item in decision.get("actions") or []}
    have_forbid = set(decision.get("forbid") or [])
    required = spec.get("required_actions", [name for name, _ in spec["actions"]])
    out = [Finding(spec["code"], f"{kind} must propose {name}", f"{prefix}.actions") for name in required if name not in have_actions]
    out += [Finding(spec["code"], f"{kind} must forbid {name}", f"{prefix}.forbid") for name in spec.get("check_forbid", spec["forbid"]) if name not in have_forbid]
    return out


def classify(answers: Mapping[str, Any]) -> dict[str, Any]:
    """Turn typed interview answers into a propose-only SSOT decision document."""

    questions: list[str] = []
    trees = list(answers.get("trees") or [])
    relationship = answers.get("relationship", "unknown")
    canonical = {"ref": str(answers.get("canonical_ref") or answers.get("subject_id"))}
    facade_path = (answers.get("facade_path") or "").strip()
    gate_path = (answers.get("gate_path") or "").strip()
    reason = (answers.get("divergence_reason") or "").strip()
    subject = str(answers["subject_id"])
    analyzer_present = bool(answers.get("analyzer_present"))
    analyzer_noise = bool(answers.get("analyzer_noise"))
    confirmed = bool(answers.get("human_confirmed_debt"))
    same_remote = bool(answers.get("same_git_remote"))
    same_pin = answers.get("same_pin")
    can_import = bool(answers.get("consumer_can_import"))
    packaging = list(answers.get("packaging") or [])

    # Analyzer output is never debt by itself. The interview decides.
    treat_as_debt = False

    policy_forbid = [
        "delete_generated_mirror",
        "treat_analyzer_as_debt",
        "couple_standalone_to_foreign_monorepo",
        "fork_logic_into_consumer",
    ]
    policy = {
        "kind": "pin_policy",
        "edit": "upstream",
        "onChange": "bump_pin" if same_remote or "git-submodule" in packaging else "re_vendor",
        "forbid": policy_forbid,
    }

    kind: str | None = None
    actions: list[dict[str, str]] = []
    forbid: list[str] = []
    decision_questions: list[str] = []
    extra: dict[str, Any] = {}
    known_relationship = relationship in {
        "generated_mirror",
        "vendored_copy",
        "facade",
        "allowed_divergence",
        "real_fork",
        "query_namespace",
        "served_artifact",
        "inventory_vs_runtime",
        "capability_surface",
        "locale_catalog",
        "config_binding",
    }
    detected_mirror = same_remote and same_pin is True and len(trees) >= 2

    # Stated runtime/UI/fleet kinds win over inferred dual-checkout mirrors.
    if relationship in STATED_KINDS:
        kind, actions, forbid, extra["rationale"] = _stated_kind(relationship, answers.get("canonical_ref"))
    elif relationship == "generated_mirror" or detected_mirror:
        kind = "generated_mirror"
        actions = [
            _action("edit_upstream", answers.get("canonical_ref")),
            _action("bump_pin", subject),
            _action("keep_both_checkouts"),
        ]
        forbid = ["delete_either_tree", "delete_generated_mirror"]
        extra["rationale"] = (
            "Dual checkouts of the same package are generated deployment mirrors, "
            "not forks. Edit upstream and bump the pin; do not delete either tree."
        )
    elif relationship == "facade" or facade_path or "facade-reexport" in packaging:
        kind = "facade"
        actions = [_action("keep_facade_reexport_canonical", answers.get("canonical_ref"))]
        forbid = ["fork_logic_into_consumer"]
        if facade_path:
            extra["facade"] = {"path": facade_path}
            if _is_path(facade_path):
                canonical.setdefault("path", facade_path)
        if answers.get("canonical_ref"):
            canonical["module"] = str(answers["canonical_ref"])
        extra["rationale"] = (
            "A facade re-exports the canonical implementation. Keep the thin "
            "import; do not copy business logic into the consumer."
        )
    elif (
        relationship == "allowed_divergence"
        or answers.get("different_protocol_by_design")
        or answers.get("must_stay_identical") == "may_drift"
    ) and relationship != "vendored_copy":
        kind = "allowed_divergence"
        actions = [_action("document_known_divergent")]
        forbid = []
        if reason:
            extra["knownDivergent"] = {"reason": reason}
        else:
            decision_questions.append(REASON_QUESTION)
            questions.append(REASON_QUESTION)
        extra["rationale"] = (
            "Copies may differ by design. Record a KNOWN_DIVERGENT reason so "
            "drift stays a conscious state."
        )
    elif (
        relationship == "vendored_copy"
        or "vendored-copy" in packaging
        or answers.get("must_stay_identical") == "identical"
    ):
        if answers.get("different_protocol_by_design"):
            kind = "allowed_divergence"
            actions = [_action("document_known_divergent")]
            if reason:
                extra["knownDivergent"] = {"reason": reason}
            else:
                decision_questions.append(REASON_QUESTION)
                questions.append(REASON_QUESTION)
        elif answers.get("must_stay_identical") == "unknown":
            kind = "vendored_copy"
            actions = [_action("ask_clarifying_questions")]
            decision_questions.append(IDENTICAL_QUESTION)
            questions.append(IDENTICAL_QUESTION)
        else:
            kind = "vendored_copy"
            gate_kind = "parity_test"
            extra["gate"] = {
                "kind": gate_kind,
                "path": gate_path or "tests/test_ssot_parity.py",
            }
            actions = [
                _action("keep_parity_test" if gate_path else "add_parity_test", extra["gate"]["path"])
            ]
            if not can_import:
                actions.append(_action("vendor_and_gate_drift"))
                forbid.append("couple_standalone_to_foreign_monorepo")
            extra["rationale"] = (
                "Vendored copies must stay identical unless moved to "
                "KNOWN_DIVERGENT. Gate drift with a parity test; do not couple "
                "a standalone product to another monorepo just to import SSOT."
            )
    elif relationship == "real_fork":
        kind = "real_fork"
        actions = [_action("choose_canonical", answers.get("canonical_ref"))]
        extra["rationale"] = (
            "Independent evolution. Choose one canonical owner or document "
            "why the fork must remain."
        )
    elif analyzer_present and analyzer_noise and not confirmed and not known_relationship:
        kind = "same_file_noise"
        actions = [
            _action("ask_clarifying_questions"),
            _action("ignore_analyzer_until_interview"),
        ]
        forbid = ["treat_analyzer_as_debt"]
        decision_questions.append(NOISE_QUESTION)
        questions.append(NOISE_QUESTION)
        extra["rationale"] = (
            "Indexes are noisy. Ask clarifying questions before treating "
            "analyzer output as debt."
        )
    else:
        kind = "same_file_noise"
        actions = [_action("ask_clarifying_questions")]
        questions.append(IDENTICAL_QUESTION)
        decision_questions.append(IDENTICAL_QUESTION)

    if not can_import and "couple_standalone_to_foreign_monorepo" not in policy_forbid:
        policy_forbid.append("couple_standalone_to_foreign_monorepo")
    if not can_import and kind in {"vendored_copy", "facade", "generated_mirror"}:
        if not any(item["do"] == "vendor_and_gate_drift" for item in actions):
            if kind == "vendored_copy":
                actions.append(_action("vendor_and_gate_drift"))
        if "couple_standalone_to_foreign_monorepo" not in forbid:
            forbid.append("couple_standalone_to_foreign_monorepo")

    decision: dict[str, Any] = {
        "id": f"{subject}.pair",
        "kind": kind,
        "canonical": canonical,
        "trees": trees,
        "actions": actions,
        "forbid": forbid,
    }
    if extra.get("facade"):
        decision["facade"] = extra["facade"]
    if extra.get("gate"):
        decision["gate"] = extra["gate"]
    if extra.get("knownDivergent"):
        decision["knownDivergent"] = extra["knownDivergent"]
    if extra.get("rationale"):
        decision["rationale"] = extra["rationale"]
    if decision_questions:
        decision["questions"] = decision_questions

    return {
        "schema": SCHEMA_DECISION,
        "id": subject,
        "version": "0.1.0",
        "purpose": str(answers.get("purpose") or f"SSOT decisions for {subject}"),
        "context": {
            "subject": subject,
            "languages": list(answers.get("languages") or ["other"]),
            "packaging": packaging or ["unknown"],
            "analyzer": {
                "present": analyzer_present,
                "kind": answers.get("analyzer_kind") or "none",
                "treatAsDebtUntilInterview": treat_as_debt,
            },
        },
        "policy": policy,
        "decisions": [decision],
        "questions": questions,
    }


def validate_interview(document: Mapping[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    if document.get("schema") != SCHEMA_INTERVIEW:
        findings.append(Finding("SSOT-KIND-001", "interview schema must be wellmanifest.ssot/interview/v1"))
    if not _is_identifier(document.get("subject_id")):
        findings.append(Finding("SSOT-KIND-001", "subject_id must be a stable identifier", "$.subject_id"))
    trees = document.get("trees")
    if not isinstance(trees, list) or not trees:
        findings.append(Finding("SSOT-TREE-001", "at least one tree path is required", "$.trees"))
    elif not all(_is_path(item) for item in trees):
        findings.append(Finding("SSOT-TREE-001", "trees must be repository-relative paths", "$.trees"))
    if document.get("relationship") not in RELATIONSHIPS:
        findings.append(Finding("SSOT-KIND-001", "unknown relationship", "$.relationship"))
    packaging = document.get("packaging")
    if not isinstance(packaging, list) or not packaging or any(item not in PACKAGING for item in packaging):
        findings.append(Finding("SSOT-KIND-001", "packaging contains an unknown value", "$.packaging"))
    return findings


def validate_decision(document: Mapping[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    if document.get("schema") != SCHEMA_DECISION:
        findings.append(Finding("SSOT-KIND-001", "decision schema must be wellmanifest.ssot/decision/v1"))
    if not _is_identifier(document.get("id")):
        findings.append(Finding("SSOT-KIND-001", "id must be a stable identifier", "$.id"))
    if not _is_semver(document.get("version")):
        findings.append(Finding("SSOT-KIND-001", "version must be SemVer", "$.version"))

    context = document.get("context")
    if not isinstance(context, dict):
        findings.append(Finding("SSOT-KIND-001", "context is required", "$.context"))
        return findings
    analyzer = context.get("analyzer") or {}
    if analyzer.get("treatAsDebtUntilInterview") and not document.get("decisions"):
        findings.append(
            Finding(
                "SSOT-NOISE-001",
                "analyzer output must not be treated as debt before the interview",
                "$.context.analyzer",
            )
        )

    policy = document.get("policy")
    if not isinstance(policy, dict) or policy.get("kind") != "pin_policy":
        findings.append(Finding("SSOT-PIN-001", "document policy must be pin_policy", "$.policy"))
    else:
        forbid = set(policy.get("forbid") or [])
        if "delete_generated_mirror" not in forbid:
            findings.append(
                Finding(
                    "SSOT-PIN-001",
                    "pin_policy must forbid deleting a generated mirror",
                    "$.policy.forbid",
                )
            )
        if "couple_standalone_to_foreign_monorepo" not in forbid:
            findings.append(
                Finding(
                    "SSOT-COUPLE-001",
                    "pin_policy must forbid coupling a standalone product to a foreign monorepo",
                    "$.policy.forbid",
                )
            )

    decisions = document.get("decisions")
    if not isinstance(decisions, list):
        findings.append(Finding("SSOT-KIND-001", "decisions must be an array", "$.decisions"))
        return findings

    questions = document.get("questions")
    if not isinstance(questions, list):
        findings.append(Finding("SSOT-KIND-001", "questions must be an array", "$.questions"))

    for index, decision in enumerate(decisions):
        prefix = f"$.decisions[{index}]"
        if not isinstance(decision, dict):
            findings.append(Finding("SSOT-KIND-001", "decision must be an object", prefix))
            continue
        kind = decision.get("kind")
        if kind not in KINDS:
            findings.append(Finding("SSOT-KIND-001", f"unknown kind {kind!r}", f"{prefix}.kind"))
        trees = decision.get("trees") or []
        if kind == "generated_mirror":
            if len(trees) < 2:
                findings.append(
                    Finding("SSOT-TREE-001", "generated_mirror needs at least two trees", f"{prefix}.trees")
                )
            forbid = set(decision.get("forbid") or [])
            if "delete_either_tree" not in forbid and "delete_generated_mirror" not in forbid:
                findings.append(
                    Finding("SSOT-PIN-001", "generated_mirror must forbid deleting either tree", f"{prefix}.forbid")
                )
        if kind == "allowed_divergence":
            known = decision.get("knownDivergent") or {}
            if not known.get("reason"):
                pending = decision.get("questions") or questions or []
                if not pending:
                    findings.append(
                        Finding(
                            "SSOT-REASON-001",
                            "allowed_divergence needs a KNOWN_DIVERGENT reason or a clarifying question",
                            f"{prefix}.knownDivergent",
                        )
                    )
        if kind == "vendored_copy":
            gate = decision.get("gate") or {}
            pending = list(decision.get("questions") or []) + list(questions or [])
            if gate.get("kind") not in {"parity_test", "pin_check"} and not pending:
                findings.append(
                    Finding("SSOT-KIND-001", "vendored_copy needs a parity_test or pin_check gate", f"{prefix}.gate")
                )
        if kind == "facade":
            facade = decision.get("facade") or {}
            canonical = decision.get("canonical") or {}
            if not facade.get("path") and not canonical.get("module"):
                findings.append(
                    Finding("SSOT-KIND-001", "facade needs a facade path or canonical module", prefix)
                )
        if kind == "same_file_noise":
            pending = list(decision.get("questions") or []) + list(questions or [])
            if not pending:
                findings.append(
                    Finding(
                        "SSOT-NOISE-001",
                        "same_file_noise must ask clarifying questions before treating output as debt",
                        f"{prefix}.questions",
                    )
                )
        findings.extend(_stated_kind_findings(kind, decision, prefix))
        for tree in trees:
            if not _is_path(tree):
                findings.append(Finding("SSOT-TREE-001", f"invalid tree path {tree!r}", f"{prefix}.trees"))
        for action in decision.get("actions") or []:
            if action.get("do") not in ACTIONS:
                findings.append(Finding("SSOT-KIND-001", f"unknown action {action.get('do')!r}", f"{prefix}.actions"))
        for item in decision.get("forbid") or []:
            if item not in FORBIDS:
                findings.append(Finding("SSOT-KIND-001", f"unknown forbid {item!r}", f"{prefix}.forbid"))
    return findings


def _lock_document(document: Mapping[str, Any]) -> Mapping[str, Any]:
    lock = document.get("standardsLock")
    if isinstance(lock, dict):
        return lock
    return document


def _lock_entries(document: Mapping[str, Any]) -> list[Any]:
    lock = _lock_document(document)
    if isinstance(lock.get("entries"), list):
        return list(lock["entries"])
    return []


def validate_standards_lock(document: Mapping[str, Any]) -> list[Finding]:
    """Validate a wellmanifest.standards-lock/v1 document (fail closed).

    Accepts either a standalone standards-lock document or the
    ``standardsLock`` block embedded in a ``dsl-manifest.json``.
    """

    lock = _lock_document(document)
    findings: list[Finding] = []
    if lock.get("schema") != SCHEMA_STANDARDS_LOCK:
        findings.append(
            Finding(
                "SSOT-LOCK-001",
                f"standards-lock schema must be {SCHEMA_STANDARDS_LOCK}",
                "$.schema",
            )
        )
    entries = _lock_entries(document)
    if not entries:
        findings.append(Finding("SSOT-LOCK-001", "standards-lock needs at least one entry", "$.entries"))
        return findings

    for index, entry in enumerate(entries):
        prefix = f"$.entries[{index}]"
        if not isinstance(entry, dict):
            findings.append(Finding("SSOT-LOCK-001", "entry must be an object", prefix))
            continue
        if not _is_identifier(entry.get("standard")):
            findings.append(Finding("SSOT-LOCK-001", "standard must be a stable identifier", f"{prefix}.standard"))
        if not _is_semver(entry.get("version")):
            findings.append(Finding("SSOT-LOCK-001", "version must be SemVer", f"{prefix}.version"))
        repository = entry.get("repository")
        if not isinstance(repository, str) or not repository.startswith("https://"):
            findings.append(Finding("SSOT-LOCK-001", "repository must be an https URI", f"{prefix}.repository"))
        if not isinstance(entry.get("revision"), str) or not REVISION.fullmatch(entry["revision"]):
            findings.append(
                Finding("SSOT-LOCK-001", "revision must be a 40-character git sha", f"{prefix}.revision")
            )
        contracts = entry.get("contracts")
        if not isinstance(contracts, list) or not contracts:
            findings.append(Finding("SSOT-LOCK-001", "entry needs at least one contract", f"{prefix}.contracts"))
            continue
        for contract_index, contract in enumerate(contracts):
            cprefix = f"{prefix}.contracts[{contract_index}]"
            if not isinstance(contract, dict):
                findings.append(Finding("SSOT-LOCK-001", "contract must be an object", cprefix))
                continue
            ref = contract.get("ref")
            if not isinstance(ref, str) or not ref.startswith(("https://", "schema://")):
                findings.append(Finding("SSOT-LOCK-001", "contract ref must be a URI", f"{cprefix}.ref"))
            if not isinstance(contract.get("digest"), str) or not DIGEST.fullmatch(contract["digest"]):
                findings.append(Finding("SSOT-LOCK-001", "contract digest must be sha256:<hex>", f"{cprefix}.digest"))

    migrations = lock.get("migrations")
    if migrations is not None:
        if not isinstance(migrations, list):
            findings.append(Finding("SSOT-LOCK-001", "migrations must be an array", "$.migrations"))
        else:
            for index, migration in enumerate(migrations):
                prefix = f"$.migrations[{index}]"
                if not isinstance(migration, dict):
                    findings.append(Finding("SSOT-LOCK-001", "migration must be an object", prefix))
                    continue
                if not _is_semver(migration.get("from")):
                    findings.append(Finding("SSOT-LOCK-001", "migration.from must be SemVer", f"{prefix}.from"))
                if not _is_semver(migration.get("to")):
                    findings.append(Finding("SSOT-LOCK-001", "migration.to must be SemVer", f"{prefix}.to"))
                steps = migration.get("steps")
                if not isinstance(steps, list) or not steps or not all(
                    isinstance(step, str) and step.strip() for step in steps
                ):
                    findings.append(Finding("SSOT-LOCK-001", "migration needs at least one step", f"{prefix}.steps"))

    policy = lock.get("updatePolicy")
    if policy is not None:
        if not isinstance(policy, dict):
            findings.append(Finding("SSOT-LOCK-001", "updatePolicy must be an object", "$.updatePolicy"))
        else:
            merge = policy.get("merge")
            if merge not in MERGE_POLICIES:
                findings.append(
                    Finding(
                        "SSOT-LOCK-001",
                        "updatePolicy.merge must be trusted-validator or manual (never automatic)",
                        "$.updatePolicy.merge",
                    )
                )
            if policy.get("onNewCompatible") not in ON_COMPATIBLE:
                findings.append(
                    Finding("SSOT-LOCK-001", "unknown updatePolicy.onNewCompatible", "$.updatePolicy.onNewCompatible")
                )
            if policy.get("onBreaking") not in ON_BREAKING:
                findings.append(
                    Finding("SSOT-LOCK-001", "unknown updatePolicy.onBreaking", "$.updatePolicy.onBreaking")
                )
    return findings


def detect_standards_drift(lock: Mapping[str, Any], upstream: Mapping[str, Any]) -> list[Finding]:
    """Compare a lock against the current upstream standards and flag stale pins.

    Drift is never silent: every entry whose revision or contract digest no
    longer matches upstream yields a finding so an adopter can bump the pin.
    """

    findings: list[Finding] = []
    upstream_entries = {entry.get("standard"): entry for entry in _lock_entries(upstream)}
    for index, entry in enumerate(_lock_entries(lock)):
        if not isinstance(entry, dict):
            continue
        standard = entry.get("standard")
        current = upstream_entries.get(standard)
        if not isinstance(current, dict):
            findings.append(
                Finding(
                    "SSOT-STALE-001",
                    f"{standard!r} is not present in the upstream standards",
                    f"$.entries[{index}]",
                )
            )
            continue
        prefix = f"$.entries[{index}]"
        if entry.get("revision") != current.get("revision"):
            findings.append(
                Finding(
                    "SSOT-STALE-001",
                    f"{standard!r} revision is stale: pinned {entry.get('revision')!r}, "
                    f"current {current.get('revision')!r}",
                    f"{prefix}.revision",
                )
            )
        if entry.get("version") != current.get("version"):
            findings.append(
                Finding(
                    "SSOT-STALE-001",
                    f"{standard!r} version is stale: pinned {entry.get('version')!r}, "
                    f"current {current.get('version')!r}",
                    f"{prefix}.version",
                )
            )
        current_contracts = {item.get("ref"): item for item in current.get("contracts") or []}
        for contract_index, contract in enumerate(entry.get("contracts") or []):
            ref = contract.get("ref")
            current_contract = current_contracts.get(ref) if isinstance(contract, dict) else None
            if (
                isinstance(contract, dict)
                and isinstance(current_contract, dict)
                and contract.get("digest") != current_contract.get("digest")
            ):
                findings.append(
                    Finding(
                        "SSOT-STALE-001",
                        f"{standard!r} contract {ref!r} digest is stale",
                        f"{prefix}.contracts[{contract_index}].digest",
                    )
                )
    return findings


def _quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def render_dsl(document: Mapping[str, Any]) -> str:
    """Lossless-enough text projection of a decision document."""

    lines = [
        "DOCUMENT SSOT",
        f"ID {document['id']}",
        f"VERSION {document['version']}",
        f"SCHEMA {document['schema']}",
    ]
    if document.get("purpose"):
        lines.append(f"PURPOSE {_quote(str(document['purpose']))}")
    context = document["context"]
    lines.append("")
    lines.append("CONTEXT")
    lines.append(f"  SUBJECT {context['subject']}")
    for language in context.get("languages") or []:
        lines.append(f"  LANGUAGE {language}")
    for item in context.get("packaging") or []:
        lines.append(f"  PACKAGING {item}")
    analyzer = context.get("analyzer") or {}
    lines.append(
        "  ANALYZER {kind} present={present} treat_as_debt={debt}".format(
            kind=analyzer.get("kind", "none"),
            present=str(bool(analyzer.get("present"))).lower(),
            debt=str(bool(analyzer.get("treatAsDebtUntilInterview"))).lower(),
        )
    )
    policy = document["policy"]
    lines.append("")
    lines.append("POLICY pin")
    lines.append(f"  EDIT {policy['edit']}")
    lines.append(f"  ON_CHANGE {policy['onChange']}")
    for item in policy.get("forbid") or []:
        lines.append(f"  FORBID {item}")
    for decision in document.get("decisions") or []:
        lines.append("")
        lines.append(f"DECISION {decision['id']}")
        lines.append(f"  KIND {decision['kind']}")
        canonical = decision.get("canonical") or {}
        if canonical.get("ref"):
            lines.append(f"  CANONICAL {canonical['ref']}")
        if canonical.get("module"):
            lines.append(f"  MODULE {canonical['module']}")
        if canonical.get("path"):
            lines.append(f"  CANONICAL_PATH {canonical['path']}")
        for tree in decision.get("trees") or []:
            lines.append(f"  TREE {tree}")
        facade = decision.get("facade") or {}
        if facade.get("path"):
            lines.append(f"  FACADE {facade['path']}")
        gate = decision.get("gate") or {}
        if gate.get("kind"):
            lines.append(f"  GATE {gate['kind']} {gate.get('path', '')}".rstrip())
        known = decision.get("knownDivergent") or {}
        if known.get("reason"):
            lines.append(f"  REASON {_quote(known['reason'])}")
        if decision.get("rationale"):
            lines.append(f"  RATIONALE {_quote(decision['rationale'])}")
        for action in decision.get("actions") or []:
            target = f" {action['target']}" if action.get("target") else ""
            lines.append(f"  ACTION {action['do']}{target}")
        for item in decision.get("forbid") or []:
            lines.append(f"  FORBID {item}")
        for question in decision.get("questions") or []:
            lines.append(f"  QUESTION {_quote(question)}")
    if document.get("questions"):
        lines.append("")
        lines.append("QUESTIONS")
        for question in document["questions"]:
            lines.append(f"  QUESTION {_quote(question)}")
    lines.append("")
    return "\n".join(lines)


def _unquote(value: str) -> str:
    text = value.strip()
    if len(text) >= 2 and text[0] == text[-1] == '"':
        return bytes(text[1:-1], "utf-8").decode("unicode_escape")
    return text


def parse_dsl(text: str) -> dict[str, Any]:
    """Parse the text projection back to the canonical JSON AST."""

    document: dict[str, Any] = {
        "schema": SCHEMA_DECISION,
        "context": {"languages": [], "packaging": [], "analyzer": {}},
        "policy": {"kind": "pin_policy", "forbid": []},
        "decisions": [],
        "questions": [],
    }
    section = "root"
    current: dict[str, Any] | None = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        tokens = line.strip().split(None, 1)
        head = tokens[0]
        rest = tokens[1] if len(tokens) > 1 else ""

        if indent == 0:
            if head == "DOCUMENT":
                continue
            if head == "ID":
                document["id"] = rest
            elif head == "VERSION":
                document["version"] = rest
            elif head == "SCHEMA":
                document["schema"] = rest
            elif head == "PURPOSE":
                document["purpose"] = _unquote(rest)
            elif head == "CONTEXT":
                section = "context"
                current = document["context"]
            elif head == "POLICY":
                section = "policy"
                current = document["policy"]
            elif head == "DECISION":
                section = "decision"
                current = {
                    "id": rest,
                    "canonical": {},
                    "trees": [],
                    "actions": [],
                    "forbid": [],
                    "questions": [],
                }
                document["decisions"].append(current)
            elif head == "QUESTIONS":
                section = "questions"
                current = document
            continue

        if section == "context" and current is not None:
            if head == "SUBJECT":
                current["subject"] = rest
            elif head == "LANGUAGE":
                current["languages"].append(rest)
            elif head == "PACKAGING":
                current["packaging"].append(rest)
            elif head == "ANALYZER":
                parts = rest.split()
                current["analyzer"]["kind"] = parts[0]
                for part in parts[1:]:
                    key, _, value = part.partition("=")
                    if key == "present":
                        current["analyzer"]["present"] = value == "true"
                    elif key == "treat_as_debt":
                        current["analyzer"]["treatAsDebtUntilInterview"] = value == "true"
        elif section == "policy" and current is not None:
            if head == "EDIT":
                current["edit"] = rest
            elif head == "ON_CHANGE":
                current["onChange"] = rest
            elif head == "FORBID":
                current["forbid"].append(rest)
        elif section == "decision" and current is not None:
            if head == "KIND":
                current["kind"] = rest
            elif head == "CANONICAL":
                current["canonical"]["ref"] = rest
            elif head == "MODULE":
                current["canonical"]["module"] = rest
            elif head == "CANONICAL_PATH":
                current["canonical"]["path"] = rest
            elif head == "TREE":
                current["trees"].append(rest)
            elif head == "FACADE":
                current["facade"] = {"path": rest}
            elif head == "GATE":
                kind, _, path = rest.partition(" ")
                current["gate"] = {"kind": kind, "path": path}
            elif head == "REASON":
                current["knownDivergent"] = {"reason": _unquote(rest)}
            elif head == "RATIONALE":
                current["rationale"] = _unquote(rest)
            elif head == "ACTION":
                name, _, target = rest.partition(" ")
                item = {"do": name}
                if target:
                    item["target"] = target
                current["actions"].append(item)
            elif head == "FORBID":
                current["forbid"].append(rest)
            elif head == "QUESTION":
                current["questions"].append(_unquote(rest))
        elif section == "questions":
            if head == "QUESTION":
                document["questions"].append(_unquote(rest))

    for decision in document["decisions"]:
        if not decision["questions"]:
            del decision["questions"]
        if not decision["canonical"]:
            del decision["canonical"]
    return document


def render_findings(findings: Sequence[Finding], output_format: str) -> str:
    if output_format == "json":
        return json.dumps(
            {
                "schema": "wellmanifest.ssot/check-result/v1",
                "status": "failed" if findings else "passed",
                "findings": [item.as_dict() for item in findings],
            },
            indent=2,
            sort_keys=True,
        )
    if not findings:
        return "ok"
    return "\n".join(f"{item.code} {item.path}: {item.message}" for item in findings)


def _read_document(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix in {".dsl", ".ssot"} or text.lstrip().startswith("DOCUMENT SSOT"):
        return parse_dsl(text)
    return json.loads(text)


def run_interview(answers_path: Path | None, output: Path | None, output_format: str) -> int:
    if answers_path is None:
        questionnaire = load_questionnaire()
        answers: dict[str, Any] = {"schema": SCHEMA_INTERVIEW}
        for question in questionnaire["questions"]:
            prompt = f"{question['prompt']}\n> "
            raw = input(prompt)
            value = parse_answer(question, raw)
            if value is not None:
                answers[question["id"]] = value
    else:
        answers = load_json(answers_path)
    findings = validate_interview(answers)
    if findings:
        print(render_findings(findings, "text"), file=sys.stderr)
        return 1
    document = classify(answers)
    payload = render_dsl(document) if output_format == "dsl" else dump_json(document)
    if output:
        output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 0


def cmd_questions() -> int:
    questionnaire = load_questionnaire()
    for index, question in enumerate(questionnaire["questions"], start=1):
        required = "required" if question.get("required") else "optional"
        print(f"{index:02d}. [{question['id']}] ({required}) {question['prompt']}")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ssot", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    interview = sub.add_parser("interview", help="ask the questionnaire or classify saved answers")
    interview.add_argument("--answers", type=Path, help="JSON interview answers")
    interview.add_argument("--output", type=Path, help="write the decision document")
    interview.add_argument("--format", choices=("json", "dsl"), default="json")
    classify_cmd = sub.add_parser("classify", help="classify interview JSON into a decision document")
    classify_cmd.add_argument("answers", type=Path)
    classify_cmd.add_argument("--format", choices=("json", "dsl"), default="json")
    suggest = sub.add_parser("suggest", help="emit the text DSL projection")
    suggest.add_argument("document", type=Path)
    validate = sub.add_parser("validate", help="validate a decision or interview document")
    validate.add_argument("document", type=Path)
    validate.add_argument("--format", choices=("text", "json"), default="text")
    standards = sub.add_parser("standards", help="validate a standards-lock document and detect drift")
    standards.add_argument("document", type=Path)
    standards.add_argument("--upstream", type=Path, help="upstream standards lock or manifest to detect drift against")
    standards.add_argument("--format", choices=("text", "json"), default="text")
    sub.add_parser("questions", help="print the questionnaire")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)
    if args.command == "questions":
        return cmd_questions()
    if args.command == "interview":
        return run_interview(args.answers, args.output, args.format)
    if args.command == "classify":
        answers = load_json(args.answers)
        findings = validate_interview(answers)
        if findings:
            print(render_findings(findings, "text"), file=sys.stderr)
            return 1
        document = classify(answers)
        sys.stdout.write(render_dsl(document) if args.format == "dsl" else dump_json(document))
        return 0
    if args.command == "suggest":
        document = _read_document(args.document)
        findings = validate_decision(document)
        if findings:
            print(render_findings(findings, "text"), file=sys.stderr)
            return 1
        sys.stdout.write(render_dsl(document))
        return 0
    if args.command == "standards":
        lock = _read_document(args.document)
        findings = validate_standards_lock(lock)
        if args.upstream:
            findings += detect_standards_drift(lock, _read_document(args.upstream))
        print(render_findings(findings, args.format))
        return 1 if findings else 0
    document = _read_document(args.document)
    if document.get("schema") == SCHEMA_INTERVIEW:
        findings = validate_interview(document)
    else:
        findings = validate_decision(document)
    print(render_findings(findings, args.format))
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
