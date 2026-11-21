#!/usr/bin/env python3
"""Keep the reviewable Markdown synchronized with the in-app legal text."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "mobile/src/legal/policies.json"
TARGET = ROOT / "docs/TERMS_AND_PRIVACY.md"


def render(data):
    lines = [
        "# Общи условия и Политика за поверителност / Terms and Privacy Policy",
        "",
        "**Draft for operator review; not a declaration of completed GDPR compliance.**",
        f"Version: {data['version']}. Developer: {data['developer']}. Contact: {data['contact']}. Scope: {data['scope']}.",
        "",
        "The Settings text and this Markdown have one source: mobile/src/legal/policies.json.",
        "Before public testing confirm controller/member-state/contact details, retention, processors/transfers, account deletion and actual email delivery. No CAPTCHA. Sample photographs are illustrative and not exact product matches.",
        "",
    ]
    for language, heading in [("bg", "Български"), ("en", "English")]:
        lines += ["# " + heading, ""]
        for kind, title in [
            ("terms", "Общи условия / Terms"),
            ("privacy", "Политика за поверителност / Privacy"),
        ]:
            lines += ["## " + title, ""]
            for section in data[kind][language]:
                lines += ["### " + section["title"], "", section["body"], ""]
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = render(json.loads(SOURCE.read_text()))
    if args.check:
        if TARGET.read_text() != text:
            raise SystemExit(
                "Legal Markdown differs from in-app policy; render it before review"
            )
        print("Legal Markdown matches in-app policy")
    else:
        TARGET.write_text(text)
        print(TARGET)
