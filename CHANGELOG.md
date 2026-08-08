# Changelog

## 0.7.0 - 2026-08-08

- **Ya no hace falta configurar `INTELICA_MCP_TOKEN` a mano.** El servidor
  `intelica-brain-mcp` ahora anuncia su propio authorization server OAuth
  (`token-issuer`), asi que "Conectar" en la pantalla de Conectores lleva
  al login de FinOps directamente — sin token que copiar ni pegar, y sin
  variables de entorno que configurar en cada maquina. `.mcp.json` se
  simplifico para reflejar esto: ya no declara un header de auth estatico.
- Cada persona sigue autenticando con su propia cuenta de FinOps, no con
  una credencial compartida entre el equipo.
- El camino anterior (generar un token en `/generate-token` y pegarlo a
  mano) sigue existiendo para usos fuera de Claude Desktop/Code, pero deja
  de ser lo que usa este plugin.

## 0.6.0 - 2026-08-04

- **Nuevo `intelica-arca-diagnose`.** El "Provider" tipo recetario que
  habíamos diseñado en la arquitectura de ARCA v2 (reconoce el tipo de
  problema, propone el comando de solo lectura, la persona lo corre y
  pega la salida) nunca se había escrito como skill. Se auto-activa con
  problemas activos ("no puedo conectar A con B", "access denied") —
  distinto de `intelica-arca-recall`, que es para preguntas informativas
  sobre lo ya documentado.
- No tiene su propio camino de persistencia: lo que descubre durante el
  diagnóstico lo captura `intelica-arca-capture` igual que cualquier otra
  conversación. Esto simplifica el diseño original, que asumía que el
  Provider necesitaba parsear y subir el resultado por su cuenta.
- Primero consulta el grafo (mismas tools que `recall`) antes de proponer
  nada — no sugiere un comando para algo que ya se puede ver ahí.
- Nunca propone un comando que cree, modifique o borre un recurso de AWS.

## 0.5.1 - 2026-08-04

- **El hook ahora viene incluido en el plugin** (`hooks/hooks.json`), asi que
  se registra solo al instalarlo. Antes habia que pegar un bloque en
  `settings.json` con una ruta absoluta al script — fragil (se rompe si el
  repo cambia de lugar) y facil de saltearse. Usa `${CLAUDE_PLUGIN_ROOT}`,
  que resuelve la ruta del plugin en runtime.
- `intelica-arca-capture` declara `user-invocable: false`. No cambia el
  comportamiento — Claude ya lo podia invocar y el usuario no lo veia en el
  menu `/` — pero deja la intencion explicita en el frontmatter en vez de
  depender de un efecto lateral no documentado.
- Documentado un limite verificado: un hook **no puede invocar un skill**.
  Solo manda el mensaje a Claude por stderr al salir con codigo 2, y Claude
  decide invocarlo. La captura no es deterministica como un cron.

## 0.5.0 - 2026-08-04

Rediseño del lado de curacion en tres momentos, reemplazando el pipeline de
un solo pase.

- **Nuevo `intelica-arca-capture`** (automatico, disparado por el hook
  `PreCompact`): guarda lo relevante de la conversacion en staging local
  antes de que la compactacion lo degrade. La compactacion nativa resume
  para poder seguir trabajando, y en el proceso descarta los identificadores
  exactos y el razonamiento de las decisiones — justo lo que vale
  documentar. Nuevo `hooks/precompact-capture.sh`, que hay que configurar a
  mano en `settings.json` (ver README).
- **`intelica-arca` reescrito**: ahora consolida los fragimentos de la sesion
  y persiste el PR en un solo pase. Si la conversacion nunca se compacto,
  extrae directo de la conversacion viva.
- **Retirados** `intelica-compression`, `intelica-markdown`,
  `intelica-kb-storage` e `intelica-arca-fast`. Todos asumian un solo pase
  sobre la conversacion completa, premisa que el staging local reemplaza.
- **Los documentos curados ahora emiten fragmento de grafo.** Antes
  `intelica-markdown` emitia `entities` como lista plana de strings, que
  `build_graph.py` ignora por no tener tipo — el resultado era que las
  conversaciones llegaban al `INDEX.md` pero no al grafo. Los tipos
  `Decision` e `Incident` del esquema no tenian quien los produjera.
- **El trabajo pesado pasa a Python.** `write_capture.py` (secuencia,
  directorio de sesion, timestamp) y `consolidate.py` (dedup de entidades
  por ID acumulando propiedades, dedup de relaciones, agrupado por cuenta).
  El LLM queda solo con lo que necesita criterio: que extraer, y como
  resolver contradicciones entre fragmentos. Una sesion larga puede dejar
  300+ entidades — deduplicarlas leyendolas todas seria caro e
  inconsistente.
- Revierte a proposito la decision de "contexto en proceso efimero": el
  staging local persiste. El motivo es distinto al original — no es guardar
  borradores a medio hacer, es no perder detalle en la compactacion.

## 0.4.0 - 2026-08-02

- Renombrado a **Intelica ARCA** (Automated Retrieval & Context
  Architecture). Cambia el `name` del plugin (`intelica-brain` →
  `intelica-arca`), asi que hay que **desinstalar y reinstalar** — no
  alcanza con actualizar.
- Los 3 skills invocables se renombran: `/intelica-brain` →
  `/intelica-arca`, `/intelica-brain-fast` → `/intelica-arca-fast`,
  `/intelica-brain-recall` → `/intelica-arca-recall`. Los 3 internos
  (`intelica-compression`, `intelica-markdown`, `intelica-kb-storage`) no
  cambian: nunca se invocan directo y ya tenian nombre neutro.
- **Fix**: los skills mandaban `enviado_por` a `push_knowledge`, un
  parametro que el servidor ya no acepta — habrian fallado en la proxima
  corrida. La autoria ahora la resuelve el servidor desde el token
  personal autenticado, lo que ademas la vuelve verificable en vez de
  autodeclarada por el caller.
- `intelica-arca-recall` reescrito para el grafo de conocimiento: elige
  entre el grafo (`find_entity`/`traverse`/`find_documents`) para
  preguntas sobre un recurso concreto, y los documentos para las
  narrativas. Su `description` ahora cubre preguntas de conectividad e
  inventario, no solo incidentes y decisiones.
- Nuevo `KNOWLEDGE_MODEL.md`: esquema fijo y curado de entidades y
  relaciones que alimentan el grafo.
- Metadata del plugin completada (`displayName`, `keywords`, `category`,
  `homepage`, `repository`, `license`) — es lo que se muestra al
  instalarlo. Los plugins de Claude Code no soportan icono ni imagen.


## 0.3.0 - 2026-07-27

- Added `intelica-arca-recall`: read-only skill that checks
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

- Added `intelica-arca-fast`: single-pass version with no intermediate
  questions or preview — extracts, drafts, and pushes in one go, without
  invoking the other 3 skills.
- Added `scripts/build_push_args.py` (bundled in `intelica-arca-fast`):
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

- First version: `intelica-arca` (orchestrator) plus the 3 decoupled
  pipeline skills — `intelica-compression`, `intelica-markdown`,
  `intelica-kb-storage`.
- Bundled `.mcp.json` registering `intelica-brain-mcp` on install, using
  `${INTELICA_MCP_URL}`/`${INTELICA_MCP_TOKEN}` env var references (never
  a hardcoded token in the repo).
- Pipeline: compress the conversation → draft `.md` files for RAG →
  persist as a single Pull Request in `ddvloayza/intelica-brain-ia` via
  `intelica-brain-mcp`'s `push_knowledge` tool. No merge tool, by design
  — merging always stays a human, manual step in GitHub.
