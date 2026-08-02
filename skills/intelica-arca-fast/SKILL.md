---
name: intelica-arca-fast
description: "Fast, silent path to turn the current conversation into a Pull Request in ITL-ORG-INFRA/intelica-brain-ia: extracts topics, drafts compact .md files, and pushes them via intelica-brain-mcp in one pass — no intermediate questions, no preview, no verbose mode. Invoke with '/intelica-arca-fast'. Trades some structure for speed compared to the full intelica-arca pipeline (intelica-compression + intelica-markdown + intelica-kb-storage). Does NOT activate automatically based on conversation topic — only with explicit invocation. Never asks the user anything mid-run."
---

# Intelica ARCA Fast

Single-pass, no-questions version of the Intelica ARCA pipeline. Does
everything itself (extract → draft → push) without invoking the other
skills — trades some structure for speed. Use `/intelica-arca` instead
when you want the richer per-field breakdown or the `--full` preview.

**Never asks anything mid-run.** No preview, no confirmation, no
verbose mode. Only output: the PR link (or a note if the MCP isn't
available).

## Step 1 — Extract (minimal)

Per distinct topic in the conversation (or the relevant segment): a
short `title`, `account` (`Portal-Prod | Interchange-Prod | Analytics-Prod | Intelica-Network | N/A`),
free-form `category`, and a `body` — one continuous write-up in English
covering what matters (context, decisions, resources, pending work,
risks) as prose/bullets, not separate structured fields. Keep literal
IDs/ARNs/resource names exactly as they appeared.

No documentable content → stop here, say why, don't push anything.

## Step 2 — Draft compact .md content (one per topic)

For each topic, write the full file content as one string (frontmatter +
body — the filename and path are computed in Step 3, not here):

```yaml
---
title: "<title>"
account: <account>
category_raw: "<category>"
category_confirmed: false
date: YYYY-MM-DD
---
```

Body: one H1 (= title), then just `## Summary` (2-4 lines) and
`## Details` (the rest of the write-up).

If more than one topic and they all share the same `account`, also
draft a short `index.md` content (relative links to each file, computed
paths come from Step 3's script output). If accounts differ, skip
`index.md` — its content just goes in the PR body instead.

## Step 3 — Compute deterministic parts (script, don't reason it out)

Run `scripts/build_push_args.py`, passing the drafted topics as JSON on
stdin: `[{"title": ..., "account": ..., "content": ..., "commit_message": ...}, ...]`.
It returns `new_branch_name` and `files` (with `path` already resolved)
ready to use — don't compute the date, slug, or random suffix yourself,
the script guarantees a real date and real randomness.

If Step 2 drafted an `index.md`, append it manually to the script's
`files` output: `path: inbox/{shared-account}/{date}-index.md` (same
date the script used).

## Step 4 — Push (one call, no confirmation)

Call `push_knowledge` directly (no other skill involved) with
`base_branch: "main"`, the `new_branch_name`/`files` from Step 3, and a
brief auto-written `title`/`body`.

Don't pass a sender: the server derives it from the authenticated personal
token and records it on the PR. Never ask for an email or any other
personal data.

If `intelica-brain-mcp` isn't loaded: create the files locally
(`create_file` + `present_files`) and say so — don't block, don't ask.

## Rules

- Never merges the PR.
- Never invokes `intelica-compression`, `intelica-markdown`, or
  `intelica-kb-storage` — fully self-contained.
- Doesn't accept credentials pasted in chat for any action.
- Only activates on explicit `/intelica-arca-fast` invocation.
