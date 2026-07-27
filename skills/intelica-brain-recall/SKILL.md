---
name: intelica-brain-recall
description: "Checks Intelica's AWS knowledge base (ddvloayza/intelica-brain-ia, via intelica-brain-mcp) for documented answers before responding from scratch. Use when the user asks about something that may already be documented there — past incidents, architecture decisions, AWS resources/accounts (Portal-Prod, Interchange-Prod, Analytics-Prod, Intelica-Network), or 'did we handle this before'-type questions. Reads INDEX.md first, then opens only the 1-2 most relevant files — never the whole repo. Unlike the other intelica-brain skills, this one CAN trigger on relevant conversation topic, not only on explicit invocation (also invokable directly with '/intelica-brain-recall'). If nothing relevant is found, say so and answer normally — never fabricate a source."
---

# Intelica Brain Recall

Checks the knowledge base before answering, instead of answering from
scratch. Read-only — never writes, never opens a PR.

## When to use

The current question plausibly relates to Intelica AWS infrastructure
history: a specific account (`Portal-Prod`, `Interchange-Prod`,
`Analytics-Prod`, `Intelica-Network`), a resource type, an incident, or
"did we already deal with this?". Skip it for generic questions
unrelated to Intelica's infra.

## Step 1 — Check the index

Call `get_file_contents(path="INDEX.md")`. If it fails (MCP not loaded,
or `INDEX.md` doesn't exist yet because nothing's been merged), say so
briefly and answer normally — don't block.

## Step 2 — Pick candidates

Scan the index table (title, account, category, path) for entries that
plausibly match the question. Pick **at most 2** — don't open more just
to be thorough, that defeats the point of checking the index first.

Nothing plausible → say the knowledge base doesn't seem to have this
yet, and answer from your own knowledge instead. Don't force a match.

## Step 3 — Read only those files

Call `get_file_contents(path=<candidate>)` for each of the (at most 2)
picks. Use their content to inform the answer.

## Step 4 — Answer, citing the source

Base the answer on what the file(s) said, and mention which document(s)
it came from (path or title) so the user can open it themselves if they
want the full context. Don't claim something is documented if it isn't
— if the files didn't actually cover the question, say so.

## Rules

- Read-only: never `create_branch`, `create_or_update_file`,
  `create_pull_request`, or `push_knowledge` from this skill.
- Never open more than 2 files per question — that's the token budget
  this whole design is built around.
- Never invent a citation — if nothing relevant was found, say so
  plainly.
