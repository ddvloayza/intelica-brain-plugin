# Arquitectura de Intelica ARCA (plugin)

Documento para quien mantenga este repo a futuro (vos, o yo en otra
sesión) — no lo lee Claude al correr un skill, solo lo que cada `SKILL.md`
referencia explícitamente.

## Qué es esto

**ARCA** — Automated Retrieval & Context Architecture. La capa de
conocimiento de Intelica sobre AWS, como plugin de Claude Code/Desktop.
Dos lados: consultar lo ya documentado antes de responder, y convertir
conversaciones en documentación persistida como PR en
`ITL-ORG-INFRA/intelica-brain-ia`.

No incluye el servidor MCP — eso vive en `ddvloayza/intelica-brain-mcp`
(Lambda + Function URL). Este plugin son los Skills que usan sus tools.

## Los tres momentos

```
DURANTE la conversación                    (automático)
  contexto se llena
       ↓
  hook PreCompact frena la compactación (exit 2)
       ↓
  intelica-arca-capture extrae y escribe:
       ~/.intelica-arca/sessions/<session_id>/001.json
       ↓
  compactación nativa sigue su curso
       ↓
  se repite → 002.json, 003.json...


AL CERRAR                                  (/intelica-arca)
  consolidate.py: merge + dedup de los NNN.json
       ↓
  el skill resuelve contradicciones y redacta
       ↓
  build_push_args.py: fecha, slug, rama, rutas
       ↓
  push_knowledge → PR
       ↓
  vos mergeás  ← único gate humano


AL PREGUNTAR                               (intelica-arca-recall)
  find_entity / traverse / find_documents   → grafo
  get_file_contents                         → documentos
```

## Por qué la captura corre en la compactación

La compactación nativa de Claude Code genera un resumen **optimizado para
que Claude siga trabajando**, no para documentar: conserva el objetivo,
las decisiones clave y el estado actual, pero pierde los identificadores
exactos, los casos borde y el razonamiento detrás de cada decisión — justo
el material que vale documentar.

Se evaluó capturar ese resumen nativo en vez de extraer aparte, y se
descartó por dos motivos verificados: está optimizado para otra cosa
(pierde lo que necesitamos), y su formato en la transcripción es interno e
inestable entre versiones de Claude Code, así que parsearlo se rompería
solo.

## Por qué el hook no extrae, solo frena

Un hook de Claude Code es un comando de shell — no puede razonar sobre la
conversación. Lo que sí puede es elegir el momento y devolverle el control
a Claude, que todavía tiene el contexto completo: con exit code 2 frena la
compactación y le muestra un mensaje. El hook decide *cuándo*; el skill
hace *qué*.

`hooks/precompact-capture.sh` deja un archivo `.capturing` como marca para
no frenar dos veces la misma compactación — sin eso, hook y skill se
bloquearían mutuamente en loop. Y si no puede leer el `session_id`, sale
con 0 en vez de frenar: perder una captura es molesto, dejar la sesión
trabada es peor.

## Por qué Python y no el LLM

El corte no es por "cuántos skills" sino por **qué es determinista y qué
necesita criterio**.

| Tarea | Dónde |
|---|---|
| Numerar fragmentos, resolver el directorio de sesión, timestamps | `write_capture.py` |
| Deduplicar entidades por ID acumulando propiedades | `consolidate.py` |
| Deduplicar relaciones, agrupar por cuenta | `consolidate.py` |
| Fecha real, slugs, nombre de rama, sufijo random, rutas | `build_push_args.py` |
| Decidir qué importa de la conversación | skill (criterio) |
| Resolver contradicciones entre fragmentos | skill (criterio) |
| Redactar la narrativa | skill (criterio) |

El caso que lo justifica: una sesión larga puede dejar 8 fragmentos con 40
entidades cada uno. Deduplicar 320 leyéndolas todas es caro y el LLM lo
hace inconsistente. Python lo hace exacto y gratis.

Lo que **no** se puede scriptear: si un fragmento afirma algo que otro
después descartó, decidir cuál sobrevive y cómo se narra. Por eso
`consolidate.py` devuelve cada hecho con su número de fragmento en vez de
intentar resolverlo — el orden es la evidencia, la decisión es del skill.

## Por qué 3 skills y no más

Los skills se cargan por *progressive disclosure*: solo `name` +
`description` está siempre en contexto (~100 tokens cada uno); el
`SKILL.md` completo se carga al dispararse. Entonces partir en más skills
solo conviene si **no siempre corren juntos** — si son una secuencia fija,
los cargás todos igual y pagás las descripciones extra sin ganar nada.

- `capture` y `arca` tienen disparadores distintos (uno automático mitad de
  conversación, otro invocado al final) → separados, obligatoriamente.
- Consolidar y persistir siempre van juntos → un solo skill.
- `recall` es el lado de consulta, y es el único que puede auto-activarse
  por tema → separado.

## Por qué el contenido generado está en inglés

El tokenizador es más eficiente con inglés que con español (medido: ~31%
menos tokens para el mismo contenido). Los `SKILL.md` (instrucciones para
Claude, nadie los lee como entregable) y el contenido de los `.md`
generados están en inglés. Los identificadores literales (IDs, ARNs,
nombres de recursos, valores de `account`) nunca se traducen — son claves
de retrieval exacto.

## Convenciones

- Rama: `docs/brain-{fecha-real}-{identificador}-{sufijo}`.
- Ruta: `inbox/{account}/{fecha}-{slug}.md` (+ su `.graph.yaml` hermano).
  `inbox/no-account/...` si no aplica cuenta.
- Remitente del PR: lo resuelve el servidor desde el token personal
  autenticado — no es un parámetro que mande el skill, y nunca se pide
  email ni dato personal. (Antes era el valor fijo
  `enviado_intelicaBrain`; se cambió para que la autoría quede atada a
  quien autenticó de verdad, en vez de ser autodeclarada por el caller.)
- Los fragmentos de staging **nunca** se borran y **nunca** van a GitHub.
- Nunca hay tool de merge — el merge queda siempre a revisión humana.

## Estructura del repo

```
intelica-brain-plugin/
├── .claude-plugin/
│   ├── plugin.json         # manifest del plugin
│   └── marketplace.json    # se instala apuntando a este mismo repo
├── .mcp.json               # registra intelica-brain-mcp al instalar
├── hooks/
│   └── precompact-capture.sh   # dispara la captura (se configura a mano)
├── skills/
│   ├── intelica-arca-capture/  # automático: conversación -> staging local
│   │   └── scripts/write_capture.py
│   ├── intelica-arca/          # invocado: staging -> .md + .graph.yaml -> PR
│   │   └── scripts/
│   │       ├── consolidate.py
│   │       └── build_push_args.py
│   └── intelica-arca-recall/   # consulta: grafo + documentos
├── KNOWLEDGE_MODEL.md      # esquema fijo de entidades y relaciones
└── README.md               # instalación y configuración para el equipo
```

## Historial de decisiones relevantes

- Se descartó OAuth completo (Cognito) para el servidor MCP: Cognito no
  soporta registro dinámico de clientes (RFC7591), que el cliente OAuth de
  Claude Code exige. Se optó por tokens personales emitidos desde la
  plataforma FinOps en vez de bearer compartido — sin la complejidad de
  construir un Authorization Server propio. Después el bearer compartido se
  eliminó del todo.
- Se descartó fusionar `intelica-compression` + `intelica-markdown` cuando
  el objetivo era "ir más rápido", por single-responsibility. Ese pipeline
  terminó retirado igual en 0.5.0, pero por otro motivo: asumía un solo
  pase sobre la conversación completa, y el staging local por compactación
  reemplaza esa premisa.
- Se revirtió a propósito la decisión de "contexto en proceso 100%
  efímero". El problema original era no guardar borradores de curación a
  medio hacer; el problema del staging es distinto — no perder detalle en
  la compactación. Misma mecánica, motivo distinto.
- Los fragmentos de grafo de documentos generados van en un archivo
  hermano `.graph.yaml`, no en el frontmatter: medido sobre el inventario
  real de AWS, el frontmatter llegaba al 85% del archivo (500+ entidades
  por cuenta), lo que hacía que cada lectura gastara tokens en datos que
  solo le sirven al grafo. Ver `KNOWLEDGE_MODEL.md`.
