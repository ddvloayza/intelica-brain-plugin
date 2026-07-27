# Arquitectura de intelica-brain-plugin

Documento para quien mantenga este repo a futuro (vos, o yo en otra
sesión) — no lo lee Claude al correr un skill, solo lo que cada
`SKILL.md` referencia explícitamente.

## Qué es esto

Un plugin de Claude Code/Desktop que convierte conversaciones largas en
conocimiento persistido como Pull Request en `ddvloayza/intelica-brain-ia`.
No incluye el servidor MCP en sí — eso vive en el repo separado
`ddvloayza/intelica-brain-mcp` (Lambda + Function URL). Este plugin solo
son los Skills que usan las tools de ese servidor.

## Los dos caminos

```
Conversacion
     │
     ├── /intelica-brain ──────────────┐
     │   (pipeline modular, 4 pasos)   │
     │                                  │
     │   intelica-compression          │
     │   (topics[] estructurado, 17     │
     │    campos opcionales)            │
     │        ↓                         │
     │   intelica-markdown              ├──→ PR en intelica-brain-ia
     │   (files[], .md por tema)        │
     │        ↓                         │
     │   intelica-kb-storage            │
     │   (push_knowledge → PR)          │
     │                                  │
     └── /intelica-brain-fast ─────────┘
         (un solo skill, sin preguntas,
          esquema minimo: title/account/
          category/body, directo a
          push_knowledge)
```

Elegí uno u otro según el caso: `/intelica-brain` cuando querés el
detalle estructurado por campo (arquitectura, riesgos, decisiones, etc.
por separado) o el preview con `--full`; `/intelica-brain-fast` cuando
solo querés que quede documentado ya, sin fricción ni preguntas.

Ninguno de los dos se activa solo por el tema de la conversación — ambos
requieren invocación explícita.

## Por qué Skills y no Subagentes

El pipeline necesita ver la conversación completa para comprimirla. Un
subagente (via la herramienta Agent) arranca sin contexto de la
conversación actual — habría que pasarle todo el texto a mano, lo que
anula el ahorro de tokens. Los Skills corren en la misma conversación,
así que ya tienen el contexto sin necesidad de repetirlo.

## Por qué `push_knowledge` y no 3 tools sueltas

El servidor MCP (`intelica-brain-mcp`) expone `create_branch`,
`create_or_update_file`, y `create_pull_request` por separado (para uso
manual/flexible), más una 4ta tool `push_knowledge` que hace las 3
operaciones en un solo hit — evita 3 round-trips de red por cada
persistencia. `intelica-kb-storage` y `intelica-brain-fast` usan
`push_knowledge`; las tools sueltas quedan como fallback si el servidor
está desactualizado.

## Por qué el contenido generado está en inglés

El tokenizador es más eficiente con inglés que con español (medido:
~31% menos tokens para el mismo contenido). Los `SKILL.md` (instrucciones
para Claude, nadie los lee como entregable) y el contenido de los `.md`
generados (título, resumen, secciones) están en inglés. Los
identificadores literales (IDs, ARNs, nombres de recursos, valores de
`account`) nunca se traducen — son claves de retrieval exacto.

## Convenciones que se repiten en ambos caminos

- Rama: `docs/brain-{fecha-real}-{identificador}` (+ sufijo random en
  `-fast` para garantizar unicidad sin coordinarse con nada más).
- Ruta de archivo: `inbox/{account}/{fecha}-{slug}.md` (`inbox/no-account/...`
  si no aplica cuenta).
- Remitente del PR: siempre el valor fijo `enviado_intelicaBrain` — nunca
  se pide email ni dato personal.
- Nunca hay tool de merge — el merge queda siempre a revisión humana en
  GitHub (branch protection en `intelica-brain-ia`).

## Estructura del repo

```
intelica-brain-plugin/
├── .claude-plugin/
│   ├── plugin.json        # manifest del plugin
│   └── marketplace.json   # se instala apuntando a este mismo repo
├── .mcp.json               # registra intelica-brain-mcp al instalar el plugin
├── skills/
│   ├── intelica-brain/            # orquestador del pipeline modular
│   ├── intelica-compression/      # conversacion -> topics[] estructurado
│   │   └── schema.md               # detalle de los 17 campos (referencia, no siempre se carga)
│   ├── intelica-markdown/         # topics[] -> files[] (.md)
│   ├── intelica-kb-storage/       # files[] -> PR (push_knowledge)
│   └── intelica-brain-fast/       # version de un solo paso, sin preguntas
└── README.md                # instalacion y configuracion para el equipo
```

## Historial de decisiones relevantes

- Se descartó OAuth completo (Cognito) para el servidor MCP: Cognito no
  soporta registro dinamico de clientes (RFC7591), que el cliente OAuth
  de Claude Code exige. Se optó por tokens personales emitidos desde la
  plataforma FinOps (`intelica-brain-mcp-token-issuer`, repo
  `intelica-brain-mcp`) en vez de bearer compartido — sin la complejidad
  de construir un Authorization Server propio.
- Se descartó fusionar `intelica-compression` + `intelica-markdown` en
  uno solo (la primera propuesta para "ir más rápido"): la doc oficial de
  Skills recomienda responsabilidad única + progressive disclosure, no
  fusión. `intelica-brain-fast` resuelve la necesidad de velocidad de
  otra forma (un skill nuevo, no una fusión de los existentes).
