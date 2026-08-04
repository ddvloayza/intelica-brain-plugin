# Intelica ARCA

**ARCA** — Automated Retrieval & Context Architecture. Plugin de Claude
Code/Desktop que es la capa de conocimiento de Intelica sobre AWS:
consulta lo ya documentado antes de responder, y convierte conversaciones
largas en documentacion persistida como Pull Request en
`ITL-ORG-INFRA/intelica-brain-ia`.

```
skills/
├── intelica-arca-capture/     (automatico, lo dispara el hook PreCompact)
├── intelica-arca/             (invocado al cerrar — "/intelica-arca")
└── intelica-arca-recall/      (consulta antes de responder — el unico que se auto-activa por tema)
```

## Los tres momentos

**Capturar** (`intelica-arca-capture`, automatico): justo antes de que
Claude Code compacte el contexto, guarda lo relevante de la conversacion en
staging local (`~/.intelica-arca/sessions/<session_id>/`). Corre solo,
disparado por el hook — no se invoca a mano.

Por que en ese momento: la compactacion resume la conversacion para poder
seguir trabajando, no para documentar. Conserva el objetivo y el estado, y
descarta los identificadores exactos y el razonamiento de las decisiones —
justo lo que vale guardar. La captura corre mientras todo eso todavia esta
en contexto.

**Cerrar** (`intelica-arca`, invocado): consolida los fragmentos de esa
sesion, resuelve contradicciones, redacta los `.md` finales con su fragmento
de grafo, y los sube como un solo PR. Todo en un pase. Si la conversacion
fue corta y nunca se compacto, extrae directo de la conversacion viva.

**Consultar** (`intelica-arca-recall`): usa el grafo de conocimiento
(`find_entity`, `traverse`, `find_documents`) para preguntas sobre recursos
concretos — que security groups tiene una instancia, quien usa un SG, que
hay en una VPC — y los documentos para preguntas narrativas. Ver
[KNOWLEDGE_MODEL.md](KNOWLEDGE_MODEL.md) para el esquema de entidades y
relaciones.

El merge del PR siempre queda a revision humana — no existe tool de merge,
a proposito.

## Que es Python y que es criterio

El trabajo pesado no lo hace el LLM. Deduplicar 300 entidades por ID,
calcular fechas, slugs y nombres de rama, y numerar los fragmentos son
tareas deterministas: las hacen scripts (`scripts/` de cada skill), exactas
y sin costo de tokens. El LLM solo decide **que importa** de la
conversacion y **resuelve las contradicciones** al consolidar — que es lo
que no se puede scriptear.

## Requisito: el servidor MCP

Este plugin **no reemplaza** el servidor MCP `intelica-brain-mcp`
(repo separado: `ddvloayza/intelica-brain-mcp`) — lo necesita. `intelica-arca`
usa `push_knowledge` para persistir en GitHub, y `intelica-arca-recall` usa
`find_entity` / `traverse` / `find_documents` / `get_file_contents` para
consultar.

El plugin ya trae su propio `.mcp.json` (en la raiz de este repo), asi que
instalar el plugin **registra el servidor automaticamente** — no hace
falta que cada proyecto tenga su propio `.mcp.json` por separado.

Lo unico que cada persona necesita configurar en su maquina son dos
variables de entorno (el `.mcp.json` del plugin solo trae las referencias
`${INTELICA_MCP_URL}` y `${INTELICA_MCP_TOKEN}`, nunca los valores reales,
porque este repo se comparte con el equipo):

```bash
export INTELICA_MCP_URL="https://<tu-function-url>.lambda-url.us-east-1.on.aws/mcp"
export INTELICA_MCP_TOKEN="el-bearer-token-real"
```

Agregalas a tu `~/.zshrc` (o el profile de tu shell) para que persistan
entre sesiones, y reiniciá Claude Desktop despues de setearlas.

Sin esas variables seteadas (o sin el plugin instalado), `intelica-arca`
cae en un modo local (genera los archivos pero no los sube) en vez de
fallar.

### Plan Team: puede necesitar habilitacion del owner

En workspaces de Claude Team/Enterprise, agregar un conector MCP remoto
nuevo suele estar deshabilitado hasta que un admin/owner del workspace
habilita "Custom Connectors" a nivel organizacion (Settings → Connectors).
Si el instalador te aparece bloqueado, pedile eso al owner antes de seguir
— no es un problema de esta configuracion.

## Instalar el plugin

Una vez que este contenido este pusheado a un repo de GitHub:

```
/plugin marketplace add <owner>/<nombre-del-repo>
/plugin install intelica-arca@intelica-arca-marketplace
```

Reemplaza `<owner>/<nombre-del-repo>` por el repo real donde vive esto
(por ejemplo `ddvloayza/intelica-brain-plugin`).

## Instalar el hook de captura

El plugin instala los skills, pero **el hook hay que configurarlo a mano** —
Claude Code no lo hace al instalar. Agregá esto a tu `settings.json`
(`~/.claude/settings.json` para todos tus proyectos, o
`.claude/settings.json` para uno solo), ajustando la ruta al repo:

```json
{
  "hooks": {
    "PreCompact": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "~/Diego/intelica-brain-plugin/hooks/precompact-capture.sh"
          }
        ]
      }
    ]
  }
}
```

Sin el hook, la captura automatica no corre — pero `/intelica-arca` sigue
funcionando: al no encontrar fragmentos, extrae directo de la conversacion.
Se pierde solo el detalle de las conversaciones largas que ya se compactaron.

## Uso

Al cerrar una conversacion que valga documentar:

```
/intelica-arca
```

o, para revisar los archivos antes de que se suban:

```
/intelica-arca --full
```

No se activa por el tema de la conversacion — solo con esas invocaciones.
`intelica-arca-recall` si puede activarse solo cuando preguntas algo que
podria estar ya documentado.

## Staging local

Los fragmentos de captura viven en `~/.intelica-arca/sessions/<session_id>/`
como `001.json`, `002.json`, etc. **Nunca se borran** y **nunca van a
GitHub**: son material de trabajo, no conocimiento. Si un PR sale mal o
queres re-curar con otro criterio, el crudo sigue ahi.

Para moverlos a otra ruta: `export INTELICA_ARCA_STAGING=/otra/ruta`.
