#!/usr/bin/env python3
"""Computes the deterministic parts of a push_knowledge call (today's date,
slugs, a random branch suffix, file paths) so the model doesn't have to --
dates and "random" characters are exactly what LLMs are unreliable at
generating by reasoning alone.

Usage:
    python3 build_push_args.py <<'EOF'
    [
      {"title": "NAT Gateway cost spike", "account": "Portal-Prod",
       "content": "<full drafted .md content, frontmatter included>",
       "commit_message": "docs: add NAT Gateway cost spike"}
    ]
    EOF

Prints JSON on stdout, ready to pass as push_knowledge's `new_branch_name`
and `files` arguments:
    {"new_branch_name": "...", "files": [{"path": ..., "content": ..., "commit_message": ...}, ...]}
"""

import json
import re
import secrets
import sys
import unicodedata
from datetime import date, timezone, datetime


def slugify(title: str) -> str:
    text = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or "topic"


def main() -> None:
    topics = json.load(sys.stdin)
    if not topics:
        json.dump({"error": "no topics provided"}, sys.stdout)
        sys.exit(1)

    today = datetime.now(timezone.utc).date().isoformat()
    suffix = secrets.token_hex(2)  # 4 hex chars

    if len(topics) == 1:
        identifier = slugify(topics[0]["title"])
    else:
        identifier = f"multi-{len(topics)}"

    branch = f"docs/brain-{today}-{identifier}-{suffix}"

    files = []
    for topic in topics:
        slug = slugify(topic["title"])
        account = topic.get("account") or "no-account"
        if account in ("N/A", "n/a", ""):
            account = "no-account"
        filename = f"{today}-{slug}.md"
        files.append(
            {
                "path": f"inbox/{account}/{filename}",
                "content": topic["content"],
                "commit_message": topic.get("commit_message", f"docs: add {slug}"),
            }
        )

    json.dump({"new_branch_name": branch, "files": files}, sys.stdout)


if __name__ == "__main__":
    main()
