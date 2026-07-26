# intelica-compression output schema

Full field reference. See SKILL.md for the flow — this file is just the
format detail.

```yaml
topics:
  - title: "Short, descriptive topic title"
    account: "Portal-Prod | Interchange-Prod | Analytics-Prod | Intelica-Network | N/A"
    category_raw: "Free-form classification determined by your own analysis"
    tags: [tag1, tag2]
    entities: ["vpc-...", "arn:aws:...", "literal-resource-name"]
    summary: "2-4 lines: what the topic was about and where it landed"
    technical_context: "Context needed to understand the rest without rereading the conversation"
    decisions: ["technical decision + reason", "..."]
    architecture: ["component/service involved", "..."]
    requirements: ["explicit or inferred requirement", "..."]
    patterns_conventions: ["established pattern or convention", "..."]
    resources:
      - resource: "resource name"
        id: "literal ID/ARN"
        account: "account if applicable"
    important_code: ["key code fragment or reference, not all code shown", "..."]
    relevant_files: ["mentioned file/path", "..."]
    best_practices: ["applied or agreed-upon best practice", "..."]
    pending_work: ["pending task", "..."]
    risks: ["identified risk", "..."]
    open_questions: ["question left unanswered at close", "..."]
    assumptions: ["assumption not explicitly confirmed", "..."]
    artifacts: ["file/PR/script/resource generated during the conversation", "..."]
```

Every field is optional — include only what applies to the topic. A
missing field means "not applicable," not "empty on purpose."

`important_code`: key fragments or references, not all code shown in the
conversation. `entities`/`resources`: use literal IDs/ARNs exactly as
they appeared (favors exact-match retrieval in `intelica-markdown`).
