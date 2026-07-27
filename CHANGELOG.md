# Changelog

## 0.3.0 - 2026-07-27

- Added `intelica-brain-recall`: read-only skill that checks
  `INDEX.md`/existing `.md` files in `intelica-brain-ia` (via the new
  `get_file_contents` tool on `intelica-brain-mcp`) before answering,
  instead of answering from scratch. Unlike the other skills, this one
  can trigger on relevant conversation topic, not only explicit
  invocation. Opens at most 2 files per question.
- `intelica-brain-mcp` gained a 5th tool, `get_file_contents(path, ref)`
  — read-only, no path restriction (reads carry no supply-chain risk,
  unlike writes).
- `intelica-brain-ia` gained an auto-generated `INDEX.md`, rebuilt by a
  GitHub Actions workflow on every push to `main` (see that repo).

## 0.2.0 - 2026-07-26

- Added `intelica-brain-fast`: single-pass version with no intermediate
  questions or preview — extracts, drafts, and pushes in one go, without
  invoking the other 3 skills.
- Added `scripts/build_push_args.py` (bundled in `intelica-brain-fast`):
  computes branch name, file paths, and the random suffix
  deterministically instead of having the model reason them out — real
  date, real randomness, no extra tokens spent on it.
- Trimmed all `SKILL.md` instructions ~58% (531 → 225 lines across the 4
  original skills), per Anthropic's Skill authoring best practices
  (concise instructions, progressive disclosure).
- Extracted `intelica-compression`'s 17-field schema into a separate
  `schema.md` reference file — only read when the exact format is
  needed, not on every invocation.
- Made compression output fields optional (omit if not applicable)
  instead of forcing empty `[]` on all 17 fields per topic — cuts output
  tokens on every run.
- Translated all `SKILL.md` instructions and the content the pipeline
  generates (titles, summaries, sections, PR title/body, commit
  messages) to English — measured ~31% fewer tokens for equivalent
  content. Literal identifiers (IDs, ARNs, resource names, `account`
  values) are never translated.
- Added `ARCHITECTURE.md` documenting both pipelines, key design
  decisions, and shared conventions.

## 0.1.0 - 2026-07-25

- First version: `intelica-brain` (orchestrator) plus the 3 decoupled
  pipeline skills — `intelica-compression`, `intelica-markdown`,
  `intelica-kb-storage`.
- Bundled `.mcp.json` registering `intelica-brain-mcp` on install, using
  `${INTELICA_MCP_URL}`/`${INTELICA_MCP_TOKEN}` env var references (never
  a hardcoded token in the repo).
- Pipeline: compress the conversation → draft `.md` files for RAG →
  persist as a single Pull Request in `ddvloayza/intelica-brain-ia` via
  `intelica-brain-mcp`'s `push_knowledge` tool. No merge tool, by design
  — merging always stays a human, manual step in GitHub.
