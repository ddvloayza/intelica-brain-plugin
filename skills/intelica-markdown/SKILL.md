---
name: intelica-markdown
description: "Generates one or more .md files optimized for RAG from the structured object produced by intelica-compression — never from the raw conversation. Automatically decides how many files to create (one per topic) and generates an index.md with relative links if there is more than one. NEVER touches Git, NEVER commits, NEVER creates branches or Pull Requests — only returns the file collection. Invoked internally by the orchestrator skill 'intelica-arca', never invoked alone nor triggered automatically."
---

# Intelica Markdown Skill

Converts `topics[]` (from `intelica-compression`) into RAG-ready
Markdown. Never receives the raw conversation, never classifies new
content, never touches Git — only returns files (path + content) that
`intelica-kb-storage` persists.

**Write all generated prose in English**, regardless of the source
conversation's language. Keep literal identifiers (IDs, ARNs, resource
names, account values) exactly as they came in `topics[]` — never
translate those.

## Files to generate

- One `.md` per element of `topics[]` — never mix two topics.
- 1 topic → no `index.md`. More than one → add `index.md` with relative
  links to all, same order as `topics[]`.
- Filename: `{date}-{slug}.md` (`slug` = title, lowercase/hyphens/no
  accents). `intelica-kb-storage` decides the destination folder, not
  this skill.

## Frontmatter per topic file

```yaml
---
title: "<topic's title>"
account: <topic's account>
category_raw: "<topic's category_raw, unnormalized>"
category_confirmed: false
tags: [<topic's tags>]
date: YYYY-MM-DD
entities: [<topic's entities>]
related: []
---
```

## Body: field → section mapping

If a field wasn't present in the topic (omitted by
`intelica-compression`), omit that entire section — never pad it with
generic content.

| Section | Field |
|---|---|
| Summary | `summary` |
| Technical context | `technical_context` |
| Technical decisions | `decisions` (list) |
| Architecture and components | `architecture` (list) |
| Requirements | `requirements` (list) |
| Patterns and conventions | `patterns_conventions` (list) |
| Resources or entities involved | `resources` (table: resource \| ID/ARN \| account) |
| Relevant code | `important_code` |
| Relevant files | `relevant_files` (list) |
| Best practices | `best_practices` (list) |
| Risks | `risks` (list) |
| Open questions | `open_questions` (list) |
| Assumptions | `assumptions` (list) |
| Generated artifacts | `artifacts` (list) |
| Pending work | `pending_work` (list) |

Rules: one H1 (= `title`) per file, everything else `##`+.
Self-contained sections (repeat the subject, never "this instance..."
without naming it). Literal IDs/ARNs/names exactly as they came in
`entities`/`resources`. Never invent content absent from the input.

## `index.md` (only if more than one topic)

```markdown
# Index

- [Topic 1 title](./{date}-{slug-1}.md)
- [Topic 2 title](./{date}-{slug-2}.md)
```

## Output format

```yaml
files:
  - filename: "{date}-{slug}.md"
    account: "<topic's account, so intelica-kb-storage can build the path>"
    content: |
      <full content, frontmatter included>
  - filename: "index.md"          # only if there was more than one topic
    account: null
    content: |
      <index content>
```
