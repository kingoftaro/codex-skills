#!/usr/bin/env python3
"""Compute a STEP digest or validate a versioned phase handoff."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, NamedTuple


STEP_PATTERN = re.compile(r"^- Current executable step:\s*`([^`]+)`\s*$", re.MULTILINE)
CHECKPOINT_PATTERN = re.compile(
    r"^- Current STEP checkpoint:\s*`(sha256:[0-9a-f]{64})`\s*$", re.MULTILINE
)
SCHEMA_PATTERN = re.compile(r"^- Handoff schema version:\s*([^\s]+)\s*$", re.MULTILINE)
STATUS_BASELINE_PATTERN = re.compile(
    r"^- Schema/migration version:\s*(.+?)\s*$", re.MULTILINE
)
STEP_BASELINE_PATTERN = re.compile(
    r"^- Current schema/migration:\s*(.+?)\s*$", re.MULTILINE
)
REVIEW_RESULT_PATTERN = re.compile(r"^- Result:\s*(PASS|STALE|BLOCKED)\s*$", re.MULTILINE)
PHASE_STATE_PATTERN = re.compile(r"^- Phase state:\s*(.+?)\s*$", re.MULTILINE)
STEP_REVIEW_RESULT_PATTERN = re.compile(
    r"^- Pre-step consistency review:\s*(PASS|STALE|BLOCKED)\s*$", re.MULTILINE
)
STATUS_REVIEW_CHECKPOINT_PATTERN = re.compile(
    r"^- Repository/worktree checkpoint reviewed:\s*(.+?)\s*$", re.MULTILINE
)
STEP_REVIEW_CHECKPOINT_PATTERN = re.compile(
    r"^- Reviewed repository/worktree checkpoint:\s*(.+?)\s*$", re.MULTILINE
)
SUPPORTED_SCHEMA_V1 = "1"
SUPPORTED_SCHEMA_V2 = 2
SUPPORTED_PHASE_STATES = {
    "not started",
    "in progress",
    "development complete",
    "accepted",
    "release blocked",
}
NON_EXECUTABLE_PHASE_STATES = {"development complete", "accepted"}
PLACEHOLDER_PATTERN = re.compile(r"\{\{[A-Z][A-Z0-9_]*\}\}")
TEMPLATE_NAMES = (
    "STATUS_TEMPLATE.md",
    "STEP_TEMPLATE.md",
)
LEGACY_TEMPLATE_PLACEHOLDERS = frozenset(
    {
        "{{ACTUAL_RESULT}}", "{{ALLOWED_EFFECTS}}", "{{ALLOWED_SCOPE}}",
        "{{AUTHORITY_PATH}}", "{{BASELINE_COMMAND}}", "{{BEFORE_OPERATION_AFTER}}",
        "{{BLOCKED_EFFECTS}}", "{{BRANCH}}", "{{CAPABILITY}}",
        "{{CLEAN_OR_SUMMARY}}", "{{CODE_OR_MIGRATION}}", "{{COMMAND}}",
        "{{COMMIT_OR_UNCOMMITTED_EXPLANATION}}", "{{COMPATIBILITY}}",
        "{{COMPATIBILITY_RULE}}", "{{CONCURRENCY_OR_SIDE_EFFECT_TEST}}",
        "{{CONCURRENCY_RULE}}", "{{CONSUMERS}}", "{{CURRENT_STEP_DOCUMENT}}",
        "{{CURRENT_STEP_SHA256}}", "{{DEGRADED_PATH}}",
        "{{DOCUMENT_CODE_GIT_STATE_AND_RECOMMENDED_ACTION}}", "{{EVIDENCE}}",
        "{{EXACT_COMMANDS}}", "{{EXACT_CONTRACT}}",
        "{{EXPLICITLY_EXCLUDED_WORK}}", "{{FACT_SOURCE}}", "{{FAILURE_TEST}}",
        "{{FAKES_AND_IMPORT_PATHS}}", "{{FORBIDDEN_SCOPE}}",
        "{{FORBIDDEN_SHORTCUT}}", "{{GIT_CHECKPOINT}}", "{{INTERFACE}}",
        "{{INTERFACE_BASELINE}}", "{{INTERFACES}}", "{{LAST_ACCEPTED_STEP}}",
        "{{MINIMAL_WIRING}}", "{{MISSING_OR_SCAFFOLDED_ITEM}}",
        "{{NEXT_CHANGE}}", "{{NEXT_STEP}}", "{{NORMAL_TEST}}",
        "{{PASS_STALE_OR_BLOCKED}}", "{{PATH}}", "{{PATH_OR_SCOPE}}",
        "{{PATH_OR_SYMBOL}}", "{{PHASE_ID}}", "{{PHASE_STATE}}",
        "{{PREDECESSOR}}", "{{PRODUCER}}", "{{PURPOSE}}",
        "{{READ_ONLY_SCOPE}}", "{{REASON}}", "{{REGISTRY_SINGLETON_CACHE_FIXTURE}}",
        "{{REPOSITORY_ROOT}}", "{{RESOLUTION}}",
        "{{REVIEWED_REPOSITORY_CHECKPOINT}}", "{{RISK}}", "{{SCHEMA_BASELINE}}",
        "{{SCHEMA_VERSION}}", "{{SCOPE}}", "{{SEVERITY}}",
        "{{SINGLE_VERIFIABLE_OUTCOME}}", "{{SMALLEST_SAFE_CHANGE}}",
        "{{STEP_ID}}", "{{STEP_NAME}}", "{{STOP_CONDITION}}",
        "{{TEST_CONSTRAINT_OR_VALIDATOR}}", "{{TEST_OR_REPORT}}", "{{TESTS}}",
        "{{TESTS_BEFORE_REPORTS}}", "{{TIME}}", "{{TIMESTAMP_WITH_TIMEZONE}}",
        "{{VERIFIABLE_ENTRY_CONDITION}}", "{{VERSION_OR_HASH}}", "{{WORKDIR}}",
    }
)
REQUIRED_STEP_SECTIONS_V1 = (
    "Handoff contract",
    "One outcome",
    "Non-goals",
    "Entry conditions and verified baseline",
    "File boundary",
    "Contracts and invariants",
    "Side-effect policy",
    "Implementation order",
    "Required pre-code rehearsal",
    "Acceptance",
    "Stop and degrade",
    "Deliverables",
)
REQUIRED_ACCEPTANCE_SECTIONS = (
    "Normal cases",
    "Failure and adversarial cases",
    "Validation commands",
)
REQUIRED_STEP_SECTIONS_V2 = (
    "Outcome",
    "Contract references and delta",
    "File boundary",
    "Risk controls",
    "Acceptance",
    "Stop conditions",
)
FENCE_OPEN_PATTERN = re.compile(
    r"^ {0,3}(?P<marker>`{3,}|~{3,})(?P<info>[^\r\n]*)$"
)
HEADING_PATTERN = re.compile(
    r"^(?P<marks>#{1,6})[ \t]+(?P<title>.*?)[ \t]*$",
    re.MULTILINE,
)
SHA256_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
GIT_HEAD_PATTERN = re.compile(r"^[0-9a-f]{40,64}$")
CONTRACT_ID_ROW_PATTERN = re.compile(
    r"^[ \t]{0,3}\|[ \t]*`(?P<id>[A-Za-z0-9][A-Za-z0-9._:/-]*)`[ \t]*\|",
    re.MULTILINE,
)
CONTRACT_ID_BULLET_PATTERN = re.compile(
    r"^[ \t]{0,3}-[ \t]+(?:Contract ID|ID):[ \t]*"
    r"`(?P<id>[A-Za-z0-9][A-Za-z0-9._:/-]*)`[ \t]*$",
    re.IGNORECASE | re.MULTILINE,
)
ACTIVE_PACKS_PATTERN = re.compile(r"^- Active packs:\s*(.+?)\s*$", re.MULTILINE)
RISK_PACK_NAME_PATTERN = re.compile(r"`([a-z][a-z0-9-]*)`")
SUPPORTED_RISK_PACKS = {
    "adjacent-paths",
    "public-compatibility",
    "data-migration",
    "concurrency-state",
    "external-effects",
    "security-privacy",
    "shared-state",
}
SCHEMA_V1_DEPRECATION = (
    "handoff schema 1 is deprecated and receives compatibility fixes only; "
    "migrate to schema 2 before support is removed in the first breaking "
    "release on or after 2026-12-01"
)

GitSnapshotProvider = Callable[[Path, Path, Path], dict[str, str]]
WarningSink = Callable[[str], None]


class FencedBlock(NamedTuple):
    start: int
    end: int
    body_start: int
    body_end: int
    marker: str
    info: str
    closed: bool


class PreparedStatus(NamedTuple):
    status: Path
    step: Path
    checkpoint: str
    original_bytes: bytes
    updated_bytes: bytes


def digest_bytes(path: Path) -> bytes:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.digest()


def sha256(path: Path) -> str:
    return f"sha256:{digest_bytes(path).hex()}"


def single_match(pattern: re.Pattern[str], text: str, label: str) -> str:
    matches = pattern.findall(text)
    if len(matches) != 1:
        raise ValueError(f"STATUS.md must contain exactly one valid {label}; found {len(matches)}")
    return matches[0]


def bundled_template_placeholders() -> set[str]:
    assets = Path(__file__).resolve().parent.parent / "assets"
    placeholders = set(LEGACY_TEMPLATE_PLACEHOLDERS)
    for name in TEMPLATE_NAMES:
        template = assets / name
        if not template.is_file():
            raise ValueError(f"bundled handoff template is missing: {template}")
        placeholders.update(PLACEHOLDER_PATTERN.findall(template.read_text(encoding="utf-8")))
    return placeholders


def reject_unresolved_placeholders(text: str, label: str) -> None:
    unresolved = sorted(set(PLACEHOLDER_PATTERN.findall(text)) & bundled_template_placeholders())
    if unresolved:
        raise ValueError(
            f"{label} contains unresolved bundled template placeholders: "
            + ", ".join(unresolved)
        )


def fenced_blocks(text: str) -> list[FencedBlock]:
    blocks: list[FencedBlock] = []
    opened: tuple[int, int, str, str] | None = None
    offset = 0
    for line in text.splitlines(keepends=True):
        raw = line.rstrip("\r\n")
        content_end = offset + len(raw)
        line_end = offset + len(line)
        if opened is None:
            match = FENCE_OPEN_PATTERN.fullmatch(raw)
            if match is not None:
                marker = match.group("marker")
                opened = (offset, line_end, marker, match.group("info").strip())
        else:
            start, body_start, marker, info = opened
            closing = re.fullmatch(
                rf" {{0,3}}{re.escape(marker[0])}{{{len(marker)},}}[ \t]*",
                raw,
            )
            if closing is not None:
                blocks.append(
                    FencedBlock(
                        start=start,
                        end=content_end,
                        body_start=body_start,
                        body_end=offset,
                        marker=marker,
                        info=info,
                        closed=True,
                    )
                )
                opened = None
        offset = line_end

    if opened is not None:
        start, body_start, marker, info = opened
        blocks.append(
            FencedBlock(
                start=start,
                end=len(text),
                body_start=body_start,
                body_end=len(text),
                marker=marker,
                info=info,
                closed=False,
            )
        )
    return blocks


def without_fenced_blocks(text: str) -> str:
    characters = list(text)
    for block in fenced_blocks(text):
        for index in range(block.start, block.end):
            if characters[index] not in "\r\n":
                characters[index] = " "
    return "".join(characters)


def section_body(text: str, level: int, title: str) -> str:
    marker = "#" * level
    visible = without_fenced_blocks(text)
    headings = list(HEADING_PATTERN.finditer(visible))
    matches = [
        match
        for match in headings
        if len(match.group("marks")) == level and match.group("title") == title
    ]
    if len(matches) != 1:
        raise ValueError(
            f"current STEP must contain exactly one {marker} {title} section; "
            f"found {len(matches)}"
        )
    selected = matches[0]
    body_end = len(text)
    for heading in headings:
        if heading.start() <= selected.start():
            continue
        if len(heading.group("marks")) <= level:
            body_end = heading.start()
            break
    body = text[selected.end() : body_end].strip()
    substantive_lines = [
        line.strip()
        for line in body.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not substantive_lines:
        raise ValueError(f"current STEP section {marker} {title} has no content")
    return body


def validate_step_structure_v1(text: str) -> None:
    for title in REQUIRED_STEP_SECTIONS_V1:
        section_body(text, 2, title)
    acceptance = section_body(text, 2, "Acceptance")
    for title in REQUIRED_ACCEPTANCE_SECTIONS:
        section_body(acceptance, 3, title)


def validate_step_structure_v2(text: str) -> None:
    for title in REQUIRED_STEP_SECTIONS_V2:
        section_body(text, 2, title)


def resolve_file_inside(root: Path, relative: str, label: str) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute():
        raise ValueError(f"{label} path must be relative to the phase directory")
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"{label} path escapes the phase directory") from exc
    if not resolved.is_file():
        raise ValueError(f"{label} does not exist or is not a file: {relative}")
    return resolved


def resolve_inside(root: Path, relative: str) -> Path:
    return resolve_file_inside(root, relative, "current STEP")


def contract_ids(text: str, section_title: str, label: str) -> set[str]:
    body = without_fenced_blocks(section_body(text, 2, section_title))
    found = CONTRACT_ID_ROW_PATTERN.findall(body) + CONTRACT_ID_BULLET_PATTERN.findall(body)
    if not found:
        raise ValueError(
            f"{label} must reference at least one backticked contract ID table row or ID bullet"
        )
    if len(found) != len(set(found)):
        raise ValueError(f"{label} contains duplicate contract ID rows")
    return set(found)


def validate_risk_packs(step_text: str) -> set[str]:
    body = without_fenced_blocks(section_body(step_text, 2, "Risk controls"))
    matches = ACTIVE_PACKS_PATTERN.findall(body)
    if len(matches) != 1:
        raise ValueError(
            "current STEP Risk controls must contain exactly one '- Active packs:' line"
        )
    value = matches[0].strip()
    if value.casefold().rstrip(".") == "none":
        return set()
    names = RISK_PACK_NAME_PATTERN.findall(value)
    residue = RISK_PACK_NAME_PATTERN.sub("", value).replace(",", "").strip()
    if not names or residue:
        raise ValueError(
            "active risk packs must be 'none' or comma-separated backticked pack names"
        )
    unknown = sorted(set(names) - SUPPORTED_RISK_PACKS)
    if unknown:
        raise ValueError("current STEP names unsupported risk packs: " + ", ".join(unknown))
    if len(names) != len(set(names)):
        raise ValueError("current STEP contains duplicate active risk packs")
    return set(names)


def validate_v1(root: Path, text: str) -> tuple[Path, str]:
    reject_unresolved_placeholders(text, "STATUS.md")
    status_visible = without_fenced_blocks(text)
    phase_state = single_match(PHASE_STATE_PATTERN, status_visible, "Phase state")
    if phase_state not in SUPPORTED_PHASE_STATES:
        raise ValueError(f"unsupported phase state: {phase_state}")
    if phase_state in NON_EXECUTABLE_PHASE_STATES:
        raise ValueError(f"phase state is not executable: {phase_state}")
    relative = single_match(STEP_PATTERN, status_visible, "Current executable step")
    expected = single_match(CHECKPOINT_PATTERN, status_visible, "Current STEP checkpoint")
    step = resolve_inside(root, relative)
    step_text = step.read_text(encoding="utf-8")
    reject_unresolved_placeholders(step_text, "current STEP")
    validate_step_structure_v1(step_text)
    step_visible = without_fenced_blocks(step_text)

    status_schema = single_match(SCHEMA_PATTERN, status_visible, "Handoff schema version")
    step_schema = single_match(
        SCHEMA_PATTERN,
        step_visible,
        "Handoff schema version in STEP",
    )
    if status_schema != SUPPORTED_SCHEMA_V1 or step_schema != SUPPORTED_SCHEMA_V1:
        raise ValueError(
            f"unsupported or mixed handoff schema: STATUS={status_schema}, "
            f"STEP={step_schema}, supported={SUPPORTED_SCHEMA_V1}"
        )

    result = single_match(
        REVIEW_RESULT_PATTERN,
        status_visible,
        "pre-step consistency Result",
    )
    if result != "PASS":
        raise ValueError(f"pre-step consistency Result is not executable: {result}")

    step_review = single_match(
        STEP_REVIEW_RESULT_PATTERN,
        step_visible,
        "pre-step consistency review in STEP",
    )
    if step_review != "PASS":
        raise ValueError(f"STEP pre-step consistency review is not executable: {step_review}")

    status_baseline = single_match(
        STATUS_BASELINE_PATTERN,
        status_visible,
        "Schema/migration version",
    )
    step_baseline = single_match(
        STEP_BASELINE_PATTERN,
        step_visible,
        "Current schema/migration",
    )
    if status_baseline != step_baseline:
        raise ValueError(
            "schema/migration baseline mismatch: "
            f"STATUS={status_baseline!r}, STEP={step_baseline!r}"
        )

    status_review = single_match(
        STATUS_REVIEW_CHECKPOINT_PATTERN,
        status_visible,
        "Repository/worktree checkpoint reviewed",
    )
    step_review = single_match(
        STEP_REVIEW_CHECKPOINT_PATTERN,
        step_visible,
        "Reviewed repository/worktree checkpoint",
    )
    if status_review != step_review:
        raise ValueError(
            "reviewed repository/worktree checkpoint mismatch: "
            f"STATUS={status_review!r}, STEP={step_review!r}"
        )

    actual = sha256(step)
    if actual != expected:
        raise ValueError(f"current STEP checkpoint mismatch: expected {expected}, actual {actual}")
    return step, actual


def phase_manifest(text: str) -> tuple[dict[str, Any], FencedBlock] | None:
    blocks = fenced_blocks(text)
    matches = [
        block
        for block in blocks
        if block.closed and block.info == "json phase-handoff"
    ]
    if not matches:
        if any("phase-handoff" in block.info.split() for block in blocks):
            raise ValueError("STATUS.md phase-handoff JSON block is malformed")
        return None
    if len(matches) != 1:
        raise ValueError(
            "STATUS.md must contain exactly one phase-handoff JSON block; "
            f"found {len(matches)}"
        )
    block = matches[0]
    try:
        manifest = json.loads(text[block.body_start : block.body_end])
    except json.JSONDecodeError as exc:
        raise ValueError(f"STATUS.md phase-handoff JSON is invalid: {exc.msg}") from exc
    if not isinstance(manifest, dict):
        raise ValueError("STATUS.md phase-handoff JSON must be an object")
    return manifest, block


def required_string(mapping: dict[str, Any], key: str, label: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must contain a non-empty string {key!r}")
    return value.strip()


def validate_phase_state(phase_state: str) -> None:
    if phase_state not in SUPPORTED_PHASE_STATES:
        raise ValueError(f"unsupported phase state: {phase_state}")
    if phase_state in NON_EXECUTABLE_PHASE_STATES:
        raise ValueError(f"phase state is not executable: {phase_state}")


def default_git_runner(cwd: Path, args: tuple[str, ...]) -> bytes:
    completed = subprocess.run(
        ("git", "-C", str(cwd), *args),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise ValueError(f"Git snapshot command failed ({' '.join(args)}): {detail}")
    return completed.stdout


def capture_git_snapshot(
    phase_dir: Path,
    status: Path,
    step: Path,
    *,
    runner: Callable[[Path, tuple[str, ...]], bytes] = default_git_runner,
) -> dict[str, str]:
    root_text = runner(phase_dir, ("rev-parse", "--show-toplevel")).decode("utf-8").strip()
    if not root_text:
        raise ValueError("Git did not report a repository root")
    repository_root = Path(root_text).resolve()
    try:
        status_relative = status.resolve().relative_to(repository_root).as_posix()
        step_relative = step.resolve().relative_to(repository_root).as_posix()
    except ValueError as exc:
        raise ValueError("STATUS.md and current STEP must be inside the Git repository") from exc

    head = runner(repository_root, ("rev-parse", "HEAD")).decode("ascii").strip().lower()
    if not GIT_HEAD_PATTERN.fullmatch(head):
        raise ValueError(f"Git reported an unsupported HEAD value: {head!r}")

    exclusions = {status_relative, step_relative}
    pathspec = (".", *(f":(exclude){path}" for path in sorted(exclusions)))
    tracked_diff = runner(
        repository_root,
        (
            "-c",
            "core.quotePath=false",
            "diff",
            "--binary",
            "--no-ext-diff",
            "--no-textconv",
            "--no-renames",
            "HEAD",
            "--",
            *pathspec,
        ),
    )
    untracked_output = runner(
        repository_root,
        ("ls-files", "--others", "--exclude-standard", "-z"),
    )

    fingerprint = hashlib.sha256()
    fingerprint.update(b"tracked-diff\0")
    fingerprint.update(tracked_diff)
    for raw_relative in sorted(part for part in untracked_output.split(b"\0") if part):
        relative = raw_relative.decode("utf-8")
        if relative in exclusions:
            continue
        candidate = (repository_root / Path(relative)).resolve()
        try:
            candidate.relative_to(repository_root)
        except ValueError as exc:
            raise ValueError(f"Git reported an untracked path outside the repository: {relative}") from exc
        if not candidate.is_file():
            raise ValueError(f"Git reported a non-file untracked path: {relative}")
        fingerprint.update(b"\0untracked\0")
        fingerprint.update(raw_relative)
        fingerprint.update(b"\0")
        fingerprint.update(digest_bytes(candidate))

    return {
        "head": head,
        "worktree_sha256": f"sha256:{fingerprint.hexdigest()}",
    }


def validate_v2(
    root: Path,
    status: Path,
    text: str,
    manifest: dict[str, Any],
    *,
    snapshot_provider: GitSnapshotProvider | None = None,
) -> tuple[Path, str]:
    reject_unresolved_placeholders(text, "STATUS.md")
    if manifest.get("handoff_schema") != SUPPORTED_SCHEMA_V2:
        raise ValueError(
            "unsupported phase-handoff JSON schema: "
            f"{manifest.get('handoff_schema')!r}; supported={SUPPORTED_SCHEMA_V2}"
        )

    phase_state = required_string(manifest, "phase_state", "phase-handoff JSON")
    validate_phase_state(phase_state)
    result = required_string(manifest, "review_result", "phase-handoff JSON")
    if result not in {"PASS", "STALE", "BLOCKED"}:
        raise ValueError(f"unsupported review result: {result}")
    if result != "PASS":
        raise ValueError(f"pre-step consistency Result is not executable: {result}")

    relative = required_string(manifest, "current_step", "phase-handoff JSON")
    step = resolve_inside(root, relative)
    step_text = step.read_text(encoding="utf-8")
    reject_unresolved_placeholders(step_text, "current STEP")
    validate_step_structure_v2(step_text)
    validate_risk_packs(step_text)

    registry_relative = required_string(
        manifest,
        "contract_registry",
        "phase-handoff JSON",
    )
    registry = resolve_file_inside(root, registry_relative, "contract registry")
    registry_text = registry.read_text(encoding="utf-8")
    reject_unresolved_placeholders(registry_text, "contract registry")
    expected_registry = required_string(
        manifest,
        "contract_registry_sha256",
        "phase-handoff JSON",
    )
    if not SHA256_PATTERN.fullmatch(expected_registry):
        raise ValueError(
            "phase-handoff JSON contract_registry_sha256 must be prepared as sha256:<64 hex>"
        )
    actual_registry = sha256(registry)
    if actual_registry != expected_registry:
        raise ValueError(
            "contract registry checkpoint mismatch: "
            f"expected {expected_registry}, actual {actual_registry}"
        )
    registry_ids = contract_ids(registry_text, "Contract registry", "contract registry")
    referenced_ids = contract_ids(
        step_text,
        "Contract references and delta",
        "current STEP",
    )
    missing_ids = sorted(referenced_ids - registry_ids)
    if missing_ids:
        raise ValueError(
            "current STEP references contract IDs absent from the registry: "
            + ", ".join(missing_ids)
        )

    expected = required_string(manifest, "step_sha256", "phase-handoff JSON")
    if not SHA256_PATTERN.fullmatch(expected):
        raise ValueError("phase-handoff JSON step_sha256 must be prepared as sha256:<64 hex>")
    actual = sha256(step)
    if actual != expected:
        raise ValueError(f"current STEP checkpoint mismatch: expected {expected}, actual {actual}")

    repository = manifest.get("repository")
    if not isinstance(repository, dict):
        raise ValueError("phase-handoff JSON must contain a repository object")
    mode = required_string(repository, "mode", "phase-handoff repository")
    if mode == "manual":
        required_string(repository, "checkpoint", "manual repository checkpoint")
    elif mode == "git":
        expected_head = required_string(repository, "head", "Git repository checkpoint")
        expected_worktree = required_string(
            repository,
            "worktree_sha256",
            "Git repository checkpoint",
        )
        if not GIT_HEAD_PATTERN.fullmatch(expected_head):
            raise ValueError("Git repository head must be prepared from the live repository")
        if not SHA256_PATTERN.fullmatch(expected_worktree):
            raise ValueError("Git worktree_sha256 must be prepared from the live repository")
        provider = snapshot_provider or capture_git_snapshot
        observed = provider(root, status, step)
        if observed.get("head") != expected_head:
            raise ValueError(
                "live Git HEAD mismatch: "
                f"expected {expected_head}, actual {observed.get('head')}"
            )
        if observed.get("worktree_sha256") != expected_worktree:
            raise ValueError(
                "live Git worktree mismatch: "
                f"expected {expected_worktree}, actual {observed.get('worktree_sha256')}"
            )
    else:
        raise ValueError(f"unsupported repository mode: {mode}")
    return step, actual


def validate(
    phase_dir: Path,
    *,
    snapshot_provider: GitSnapshotProvider | None = None,
    warning_sink: WarningSink | None = None,
) -> tuple[Path, str]:
    root = phase_dir.resolve()
    status = root / "STATUS.md"
    if not status.is_file():
        raise ValueError(f"STATUS.md is missing: {status}")
    text = status.read_text(encoding="utf-8")
    parsed = phase_manifest(text)
    if parsed is None:
        result = validate_v1(root, text)
        if warning_sink is not None:
            warning_sink(SCHEMA_V1_DEPRECATION)
        return result
    manifest, _ = parsed
    return validate_v2(
        root,
        status,
        text,
        manifest,
        snapshot_provider=snapshot_provider,
    )


def build_prepared_status(
    phase_dir: Path,
    *,
    snapshot_provider: GitSnapshotProvider | None = None,
) -> PreparedStatus:
    root = phase_dir.resolve()
    status = root / "STATUS.md"
    if not status.is_file():
        raise ValueError(f"STATUS.md is missing: {status}")
    original_bytes = status.read_bytes()
    text = original_bytes.decode("utf-8")
    reject_unresolved_placeholders(text, "STATUS.md")
    parsed = phase_manifest(text)
    if parsed is None:
        raise ValueError("--prepare requires a schema 2 phase-handoff JSON block")
    manifest, manifest_block = parsed
    if manifest.get("handoff_schema") != SUPPORTED_SCHEMA_V2:
        raise ValueError("--prepare supports only phase-handoff schema 2")
    phase_state = required_string(manifest, "phase_state", "phase-handoff JSON")
    validate_phase_state(phase_state)
    result = required_string(manifest, "review_result", "phase-handoff JSON")
    if result != "PASS":
        raise ValueError(f"pre-step consistency Result is not executable: {result}")

    relative = required_string(manifest, "current_step", "phase-handoff JSON")
    step = resolve_inside(root, relative)
    step_text = step.read_text(encoding="utf-8")
    reject_unresolved_placeholders(step_text, "current STEP")
    validate_step_structure_v2(step_text)
    validate_risk_packs(step_text)
    checkpoint = sha256(step)
    manifest["step_sha256"] = checkpoint

    registry_relative = required_string(
        manifest,
        "contract_registry",
        "phase-handoff JSON",
    )
    registry = resolve_file_inside(root, registry_relative, "contract registry")
    registry_text = registry.read_text(encoding="utf-8")
    reject_unresolved_placeholders(registry_text, "contract registry")
    registry_ids = contract_ids(registry_text, "Contract registry", "contract registry")
    referenced_ids = contract_ids(
        step_text,
        "Contract references and delta",
        "current STEP",
    )
    missing_ids = sorted(referenced_ids - registry_ids)
    if missing_ids:
        raise ValueError(
            "current STEP references contract IDs absent from the registry: "
            + ", ".join(missing_ids)
        )
    manifest["contract_registry_sha256"] = sha256(registry)

    repository = manifest.get("repository")
    if not isinstance(repository, dict):
        raise ValueError("phase-handoff JSON must contain a repository object")
    mode = required_string(repository, "mode", "phase-handoff repository")
    if mode == "git":
        provider = snapshot_provider or capture_git_snapshot
        repository.update(provider(root, status, step))
    elif mode == "manual":
        required_string(repository, "checkpoint", "manual repository checkpoint")
    else:
        raise ValueError(f"unsupported repository mode: {mode}")

    manifest["prepared_at"] = dt.datetime.now(dt.timezone.utc).isoformat().replace(
        "+00:00", "Z"
    )
    newline = "\r\n" if "\r\n" in text else "\n"
    serialized = json.dumps(manifest, indent=2).replace("\n", newline)
    block = f"```json phase-handoff{newline}{serialized}{newline}```"
    updated = (
        text[: manifest_block.start]
        + block
        + text[manifest_block.end :]
    )
    validate_v2(
        root,
        status,
        updated,
        manifest,
        snapshot_provider=snapshot_provider,
    )
    return PreparedStatus(
        status=status,
        step=step,
        checkpoint=checkpoint,
        original_bytes=original_bytes,
        updated_bytes=updated.encode("utf-8"),
    )


def atomic_replace_bytes(path: Path, content: bytes) -> None:
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as target:
            temporary_path = Path(target.name)
            target.write(content)
            target.flush()
            os.fsync(target.fileno())
        shutil.copymode(path, temporary_path)
        os.replace(temporary_path, path)
        temporary_path = None
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def prepare(
    phase_dir: Path,
    *,
    snapshot_provider: GitSnapshotProvider | None = None,
    dry_run: bool = False,
) -> tuple[Path, str]:
    root = phase_dir.resolve()
    candidate = build_prepared_status(
        root,
        snapshot_provider=snapshot_provider,
    )
    if dry_run:
        return candidate.step, candidate.checkpoint

    atomic_replace_bytes(candidate.status, candidate.updated_bytes)
    try:
        return validate(root, snapshot_provider=snapshot_provider)
    except Exception as validation_error:
        try:
            if candidate.status.read_bytes() != candidate.updated_bytes:
                raise OSError(
                    "STATUS.md changed concurrently after preparation; "
                    "the original was not restored"
                )
            atomic_replace_bytes(candidate.status, candidate.original_bytes)
        except OSError as rollback_error:
            raise OSError(
                "prepared STATUS.md failed final validation and could not be "
                f"safely restored: {validation_error}"
            ) from rollback_error
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("phase_dir", nargs="?", help="phase directory containing STATUS.md")
    mode.add_argument("--digest", metavar="STEP_PATH", help="print the SHA-256 checkpoint for one STEP")
    mode.add_argument(
        "--prepare",
        metavar="PHASE_DIR",
        help="atomically populate a schema 2 STEP digest and live Git checkpoint",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="preflight --prepare without changing STATUS.md",
    )
    args = parser.parse_args()
    if args.dry_run and not args.prepare:
        parser.error("--dry-run requires --prepare")
    try:
        if args.digest:
            step = Path(args.digest).resolve()
            if not step.is_file():
                raise ValueError(f"STEP does not exist or is not a file: {step}")
            print(sha256(step))
        elif args.prepare:
            step, checkpoint = prepare(Path(args.prepare), dry_run=args.dry_run)
            action = "would prepare" if args.dry_run else "prepared"
            print(f"PASS: {action} {step} and validated {checkpoint}")
        else:
            step, checkpoint = validate(
                Path(args.phase_dir),
                warning_sink=lambda message: print(
                    f"WARNING: {message}",
                    file=sys.stderr,
                ),
            )
            print(f"PASS: {step} has a complete handoff structure and matches {checkpoint}")
    except (OSError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
