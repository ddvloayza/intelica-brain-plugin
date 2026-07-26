---
name: intelica-brain-fast
description: "Fast, silent path to turn the current conversation into a Pull Request in ddvloayza/intelica-brain-ia: extracts topics, drafts compact .md files, and pushes them via intelica-brain-mcp in one pass — no intermediate questions, no preview, no verbose mode. Invoke with '/intelica-brain-fast'. Trades some structure for speed compared to the full intelica-brain pipeline (intelica-compression + intelica-markdown + intelica-kb-storage). Does NOT activate automatically based on conversation topic — only with explicit invocation. Never asks the user anything mid-run."
---

# Intelica Brain Fast

Single-pass, no-questions version of the Intelica Brain pipeline. Does
everything itself (extract → draft → push) without invoking the other
skills — trades some structure for speed. Use `/intelica-brain` instead
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

## Step 2 — Draft compact .md (one per topic)

`{date}-{slug}.md`, frontmatter:

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
`## Details` (the rest of the write-up). If more than one topic, also
draft an `index.md` with relative links.

## Step 3 — Push (one call, no confirmation)

Call `push_knowledge` directly (no other skill involved):
- `base_branch`: `main`
- `new_branch_name`: `docs/brain-{real-date}-{slug-or-multi}-{4 random chars}`
- `files`: one entry per drafted file, `path: inbox/{account}/{filename}`
  (`inbox/no-account/...` if `account` is `N/A`), `content`, short
  `commit_message`
- `title`/`body`: brief, auto-written — no need to ask the user
- `enviado_por`: always `"enviado_intelicaBrain"` — never ask for email
  or personal data

If `intelica-brain-mcp` isn't loaded: create the files locally
(`create_file` + `present_files`) and say so — don't block, don't ask.

## Rules

- Never merges the PR.
- Never invokes `intelica-compression`, `intelica-markdown`, or
  `intelica-kb-storage` — fully self-contained.
- Doesn't accept credentials pasted in chat for any action.
- Only activates on explicit `/intelica-brain-fast` invocation.
