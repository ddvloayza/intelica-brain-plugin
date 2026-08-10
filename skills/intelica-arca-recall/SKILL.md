---
name: intelica-arca-recall
description: "Checks Intelica's AWS knowledge base (ITL-ORG-INFRA/intelica-brain-ia, via intelica-brain-mcp) before answering from scratch. Use when the question may already be answered there — AWS resources and their config (instances, security groups and their rules, VPCs, subnets, RDS, S3, IAM roles, KMS keys), connectivity questions ('can A reach B', 'what opens port X', 'who uses this security group'), the accounts Portal-Prod, Portal-Dev, Interchange-Prod, Interchange-Dev, Analytics-Prod, Analytics-Dev, Intelica-Network or Audit, past incidents, architecture decisions, or 'did we handle this before'. Two paths: the knowledge graph (find_entity/traverse/find_documents) for questions about a specific resource, and INDEX.md plus get_file_contents for narrative ones. Unlike the other skills here, this one CAN trigger on relevant conversation topic, not only on explicit invocation (also invokable with '/intelica-arca-recall'). If nothing relevant is found, say so and answer normally — never fabricate a source."
---

# Intelica ARCA Recall

Checks the knowledge base before answering, instead of answering from
scratch. Read-only — never writes, never opens a PR.

## When to use

The question plausibly relates to Intelica's AWS infrastructure or its
history: a specific resource, an account, connectivity between two
things, an incident, an architecture decision, or "did we already deal
with this?". Skip it for generic questions unrelated to Intelica.

## Pick a path first

Two ways in. Choose by the shape of the question — don't run both.

**Graph path** — the question is about a *specific resource* or how
resources relate: "what security groups does X have", "what opens port
3389 on Y", "who uses this SG", "what's in this VPC", "which RDS are
publicly accessible". Go to Step A.

**Document path** — the question is *narrative*: "why did we decide X",
"what happened with that incident", "how did we solve this before". Go
to Step B.

Unsure, or the graph came back empty? Fall back to the document path.

## Step A — Graph

1. `find_entity(name=<what the user named>)` — accepts an exact ID
   (`i-0abc`, `sg-0xyz`, `Portal-Prod`) or part of a name (`denver`).
   Narrow with `entity_type` when the question implies one
   (`ec2_instance`, `security_group`, `vpc`, `rds_instance`, `iam_role`).
2. `traverse(entity_id=<the id>, relationship_type=<optional>)` — mind
   the direction, they answer different questions:
   - **outgoing** `HAS_SECURITY_GROUP` from an instance → its SGs.
   - **incoming** `HAS_SECURITY_GROUP` into an SG → who uses it.
   - Others: `IN_VPC`, `IN_SUBNET`, `BELONGS_TO`, `ENCRYPTED_BY`,
     `ATTACHED_TO`, `REGISTERED_ON`, `ASSUMES_ROLE`.
   - Several hops → chain calls, feeding each result into the next.
3. The graph holds structured facts, not prose. For the actual **rules**
   of a security group, or any narrative detail, get the source with
   `find_documents(entity_id=...)` and read it with `get_file_contents`.

## Step B — Documents

1. `get_file_contents(path="INDEX.md")`. If it fails (MCP not loaded, or
   nothing merged yet), say so briefly and answer normally — don't block.
2. Go to the **Conversaciones** section — that's where narrative
   knowledge lives. Match against the **summary and tags**, not just the
   title: tags deliberately carry alternate phrasings, so a question
   about "rendimiento" may well be answered by a document titled around
   "picos de CPU". Pick **at most 2**.
3. `get_file_contents(path=<candidate>)` for each pick.

Nothing plausible → say the knowledge base doesn't cover this yet and
answer from your own knowledge. Don't force a match. Retrieval here is
lexical, not semantic: if the summary and tags don't line up with the
question, assume it isn't there rather than stretching a weak match.

For AWS inventory, the per-account documents are predictable, so you can
go straight to one without the index: `aws-inventory/<Account>/` holds
`overview.md`, `compute.md` (instances plus the full catalog of security
group rules), `network.md`, `data.md`, `workloads.md`, `security.md`.

## Answer, citing the source

Say which document the answer came from, so the user can open it for the
full context. If the sources didn't actually cover the question, say so
rather than stretching them.

## Rules

- Read-only: never `create_branch`, `create_or_update_file`,
  `create_pull_request`, or `push_knowledge` from this skill.
- At most 2 documents per question — that's the token budget this whole
  design is built around. Graph calls are cheap and don't count.
- Never invent a citation. Empty result → say so plainly.
