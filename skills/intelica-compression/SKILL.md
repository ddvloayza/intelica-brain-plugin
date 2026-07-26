---
name: intelica-compression
description: "Compresses a long conversation (AWS infra, development, or Claude/GitHub tooling) into a structured knowledge object, removing greetings, tests, repeated content, and redundant answers. NEVER generates markdown or touches Git — returns only the structured object (YAML) for another skill (intelica-markdown) to turn into files. Invoked internally by the orchestrator skill 'intelica-brain', never invoked alone by the user nor triggered automatically by conversation topic."
---

# Intelica Compression Skill

Extracts a structured knowledge object from the conversation — not a
summary. Never writes Markdown or touches Git; its only output is the
YAML defined below, consumed by `intelica-markdown`.

**Write all generated prose (title, summary, decisions, etc.) in
English**, regardless of the conversation's language. Never translate
literal identifiers — resource names, ARNs, IDs, account names — keep
those exactly as they appeared.

Remove: greetings, exploratory chat without conclusion, failed debug
attempts (the final result is kept), repetition, back-and-forth that
didn't change the outcome.

Never invent data that didn't appear. Anything ambiguous goes to
`open_questions` or `assumptions`, never filled in by forced inference.

## Step 1 — Detect topics

Identify one or more distinct topics/problems in the conversation (or
the relevant segment, if it mixes unrelated topics). By your own
analysis, without asking: short title, free-form `category_raw`, AWS
account if applicable (`Portal-Prod | Interchange-Prod | Analytics-Prod | Intelica-Network | N/A`).

No documentable topics → `topics: []`, stop the pipeline here.

## Step 2 — Structure each topic

One topic = one `topics[]` block, never mix two topics into one.
Fill in `schema.md` (same directory) — **only the fields that apply**;
omit entirely the ones that don't (don't pad with `[]` or generic
content).

## Output format

Return exactly the YAML block from `schema.md`, nothing before or after
unless explanation is requested for debugging.
