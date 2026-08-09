---
name: intelica-arca
description: "Closes out a conversation: consolidates everything intelica-arca-capture staged locally during it, drafts the final .md documents plus their graph fragments, and pushes them as a single Pull Request to ITL-ORG-INFRA/intelica-brain-ia via intelica-brain-mcp — all in one pass. Invoke with '/intelica-arca' (add '--full' to review the drafts before pushing). Works whether the conversation was long (several capture fragments) or short (none — it extracts from the live conversation instead). Does NOT activate on conversation topic, only on explicit invocation. Never merges the PR: that stays a human step in GitHub."
---

# Intelica ARCA

Turns a finished conversation into documented knowledge, in one pass:
consolidate → draft → push. Only output is the PR link, unless `--full`.

Never merges. The PR is the human gate, and there is no merge tool by
design.

## Step 1 — Consolidate the staged fragments

Get the `session_id` for this conversation, then:

```bash
python3 scripts/consolidate.py --session <session_id>
```

The script deduplicates entities by ID (merging their properties),
deduplicates relations, and returns every fact tagged with the fragment it
came from. Don't do that merging by hand — a long session can stage 300+
entities and the script does it exactly, for free.

**`fragment_count: 0`** means the conversation never compacted, so nothing
was staged. That's normal for a short chat: extract directly from the
conversation you're in, using the same shape the script would have
returned, and continue.

## Step 2 — Resolve what the script can't

This is the part that needs judgment, and it's why the facts come with
sequence numbers.

**Contradictions.** A higher sequence came later in the conversation. A
fact marked `DISCARDED:` overrides what it discards — the final document
must reflect the conclusion, not the abandoned hypothesis. Don't document
both as if they were equally true.

**Grouping.** One `.md` per coherent topic. Several unrelated topics in one
conversation → several files. Don't split a single topic across files, and
don't merge two unrelated ones to save effort.

**Relevance.** `seen_in` tells you whether an entity showed up once in
passing or recurred across the conversation. Recurring ones are usually the
subject; one-offs are usually context.

## Step 3 — Draft the documents

Write the prose in **Spanish**. A human reviews and merges this document,
that merge is the only gate in the whole system, and the team reads
Spanish — don't add friction to the step that most needs care. Writing it
in English was measured to save only 9.6% of tokens on a real document
from the repo, because these files are dense in identifiers that tokenize
the same either way.

Never translate literal identifiers (IDs, ARNs, resource names, `account`
values): those are exact retrieval keys.

Each topic produces two files.

**The document**, `inbox/<account>/<date>-<slug>.md`:

```yaml
---
title: "<what this documents>"
account: <account, or no-account>
category_raw: "<category, unnormalized>"
category_confirmed: false
date: <YYYY-MM-DD>
tags: [<relevant tags>]
graph: <date>-<slug>.graph.yaml
---
```

Then the body: what the situation was, what was found, what was decided,
and what remains open. Write what someone would need six months from now,
not a transcript.

**The graph fragment**, `inbox/<account>/<date>-<slug>.graph.yaml`:

```yaml
documents: <date>-<slug>.md
account: <account>
entities:
  - type: Resource
    id: i-0abc123
    resource_type: ec2_instance
relations:
  - from: i-0abc123
    type: BELONGS_TO
    to: Portal-Prod
```

Use the consolidated entities and relations, minus anything that belongs to
a different topic's file. Drop `seen_in` — that's working metadata, not
knowledge. Every entity must conform to `KNOWLEDGE_MODEL.md`; never invent
a type.

## Step 4 — Push

Feed the drafts to the script that computes the deterministic parts (real
date, slugs, branch name, random suffix, paths):

```bash
python3 scripts/build_push_args.py <<'EOF'
[{"title": "...", "account": "...", "content": "<full .md content>", "commit_message": "docs: ..."}]
EOF
```

Add the `.graph.yaml` files to the returned `files` list, using the same
path prefix as their `.md` sibling, then call `push_knowledge` with
`base_branch: "main"` and the script's `new_branch_name`/`files`.

Don't pass a sender. The server derives it from the authenticated personal
token — it isn't a parameter. Never ask the user for an email or any other
personal data.

With `--full`: show the drafted files and wait for confirmation before
pushing. Without it: push silently and report only the PR link.

If `intelica-brain-mcp` isn't loaded: write the files locally, say so, and
don't block.

## Rules

- Never merges the PR, in any mode.
- The staged fragments are **never deleted** — if the PR comes out wrong or
  you want to re-curate differently, the raw material is still there.
- The `.yaml` fragments never go to GitHub. Staging isn't knowledge.
- Doesn't accept credentials pasted in chat for any action.
- Only activates on explicit `/intelica-arca` invocation.
