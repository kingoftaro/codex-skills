#!/usr/bin/env python3
"""Validate this skill's structure and references using only the Python standard library."""

from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path


NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def frontmatter(content: str) -> tuple[dict[str, str], list[str]]:
    failures: list[str] = []
    if not content.startswith("---\n"):
        return {}, ["SKILL.md must start with YAML frontmatter"]
    closing = content.find("\n---\n", 4)
    if closing < 0:
        return {}, ["SKILL.md frontmatter is not closed"]
    values: dict[str, str] = {}
    for line in content[4:closing].splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            failures.append(f"invalid frontmatter line: {line}")
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    unexpected = sorted(set(values) - {"name", "description"})
    if unexpected:
        failures.append(f"unexpected frontmatter keys: {unexpected}")
    return values, failures


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    skill_path = root / "SKILL.md"
    if not skill_path.is_file():
        return ["SKILL.md is missing"]
    content = skill_path.read_text(encoding="utf-8")
    metadata, metadata_failures = frontmatter(content)
    failures.extend(metadata_failures)

    name = metadata.get("name", "")
    description = metadata.get("description", "")
    if not NAME_PATTERN.fullmatch(name):
        failures.append(f"invalid skill name: {name!r}")
    if name != root.name:
        failures.append(f"folder name {root.name!r} does not match skill name {name!r}")
    if not description:
        failures.append("description is missing")
    if len(description) > 1024:
        failures.append(f"description exceeds 1024 characters: {len(description)}")
    if "<" in description or ">" in description:
        failures.append("description contains angle brackets")
    if len(content.splitlines()) >= 500:
        failures.append("SKILL.md must remain under 500 lines")
    placeholder_token = "TO" + "DO"
    if re.search(rf"\b{placeholder_token}\b|\[{placeholder_token}", content, re.IGNORECASE):
        failures.append("SKILL.md contains a placeholder marker")

    for markdown in sorted(root.rglob("*.md")):
        text = markdown.read_text(encoding="utf-8")
        for target in LINK_PATTERN.findall(text):
            clean = target.split("#", 1)[0]
            if not clean or re.match(r"^[a-z]+://", clean, re.IGNORECASE):
                continue
            if not (markdown.parent / clean).resolve().exists():
                failures.append(f"broken link in {markdown.relative_to(root)}: {target}")

    agents_yaml = root / "agents" / "openai.yaml"
    if not agents_yaml.is_file():
        failures.append("agents/openai.yaml is missing")
    else:
        agents_text = agents_yaml.read_text(encoding="utf-8")
        for key in ("display_name:", "short_description:", "default_prompt:"):
            if key not in agents_text:
                failures.append(f"agents/openai.yaml missing {key[:-1]}")
        if f"${name}" not in agents_text:
            failures.append("default_prompt must mention the skill explicitly")

    for script in sorted((root / "scripts").glob("*.py")):
        try:
            ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
        except (OSError, UnicodeError, SyntaxError) as exc:
            failures.append(f"invalid Python script {script.name}: {exc}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_root", nargs="?", default=str(Path(__file__).resolve().parent.parent))
    args = parser.parse_args()
    root = Path(args.skill_root).resolve()
    failures = validate(root)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        print(f"Validation failed with {len(failures)} issue(s).")
        return 1
    print(f"PASS: {root} is structurally valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
