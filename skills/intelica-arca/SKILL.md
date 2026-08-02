---
name: intelica-arca
description: "Orchestrates the full Intelica Brain pipeline: compresses the current conversation (intelica-compression), generates the corresponding .md files (intelica-markdown), and persists them as a Pull Request in intelica-brain-ia (intelica-kb-storage) — in that order, passing each skill's output to the next. Invoke with '/intelica-arca' (backward-compatible alias: '/intelica-kb-storage', 'storage-intelica-arca'). No flag: silent mode, returns only the PR link(s). With '--full': shows the compression object, the generated .md files, and the result before sending. Do NOT activate automatically based on conversation topic — only with these explicit invocations. The 3 skills it orchestrates never call each other, nor are they invoked directly by the user."
---

# Intelica ARCA — Orchestrator skill

Turns the current conversation into knowledge persisted in
`ITL-ORG-INFRA/intelica-brain-ia`, coordinating 3 skills in sequence. None of
them call each other — all coordination (passing one's output to the
next, handling errors) is done by this skill.

```
Conversation → intelica-compression (topics[]) → intelica-markdown (files[]) → intelica-kb-storage (PR)
```

## Activation

`/intelica-arca` (silent, only the PR link) or `/intelica-arca --full`
(shows the compression object and the files before sending, and returns
a summary at the end). Backward-compatible aliases:
`/intelica-kb-storage`, `storage-intelica-arca`.

Does not activate automatically based on conversation topic — only with
these explicit invocations.

## Pipeline

1. **Validate**: if there's no documentable content, abort without
   invoking anything and explain why.
2. **`intelica-compression`** on the conversation → `topics[]`. Empty →
   stop the pipeline, report why. `--full` → show the full object.
3. **`intelica-markdown`** with unmodified `topics[]` → `files[]`.
   `--full` → show each file.
4. **`intelica-kb-storage`** with unmodified `files[]` → PR link (or
   confirmation of local files if the MCP isn't available — not an
   error, it's the expected fallback).
5. **Report**: default → only the link(s). `--full` → link + summary
   (file count, categories, accounts).

If a step fails, stop the pipeline there (don't continue to the next
ones) and report why. Don't retry automatically without the user asking.

## Rules

- The 3 skills never call each other — everything goes through this
  orchestrator.
- The PR sender is resolved server-side from the authenticated personal
  token — it isn't a parameter. Never ask for personal data.
- Never merge the PR, in any mode.
- Doesn't accept credentials pasted in chat for any action.
