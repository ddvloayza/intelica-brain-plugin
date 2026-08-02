# Intelica ARCA

**ARCA** — Automated Retrieval & Context Architecture. Plugin de Claude
Code/Desktop que es la capa de conocimiento de Intelica sobre AWS:
consulta lo ya documentado antes de responder, y convierte conversaciones
largas en documentacion persistida como Pull Request en
`ITL-ORG-INFRA/intelica-brain-ia`.

```
skills/
├── intelica-arca-recall/      (consulta antes de responder — el unico que se auto-activa)
├── intelica-arca/             (orquestador del pipeline — "/intelica-arca")
├── intelica-arca-fast/        (via rapida de un solo paso — "/intelica-arca-fast")
├── intelica-compression/      (conversacion -> objeto estructurado)
├── intelica-markdown/         (objeto estructurado -> archivos .md)
└── intelica-kb-storage/       (archivos .md -> Pull Request via MCP)
```

Los ultimos 3 nunca se llaman entre si ni se invocan directo — toda la
coordinacion la hace `intelica-arca`. Ver el `SKILL.md` de cada uno para
el detalle.

## Los dos lados

**Consultar** (`intelica-arca-recall`): usa el grafo de conocimiento
(`find_entity`, `traverse`, `find_documents`) para preguntas sobre
recursos concretos — que security groups tiene una instancia, quien usa
un SG, que hay en una VPC — y los documentos para preguntas narrativas.
Ver [KNOWLEDGE_MODEL.md](KNOWLEDGE_MODEL.md) para el esquema de entidades
y relaciones.

**Documentar** (`intelica-arca` / `intelica-arca-fast`): comprime la
conversacion y la sube como PR. El merge siempre queda a revision humana
— no existe tool de merge, a proposito.

## Requisito: el servidor MCP

Este plugin **no reemplaza** el servidor MCP `intelica-brain-mcp`
(repo separado: `ddvloayza/intelica-brain-mcp`) — lo necesita. El skill
`intelica-kb-storage` llama a sus tools (`create_branch`,
`create_or_update_file`, `create_pull_request`) para persistir en GitHub.

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

Sin esas variables seteadas (o sin el plugin instalado), `intelica-kb-storage`
cae en un modo local (genera los archivos pero no los sube), sin fallar
el pipeline.

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

## Uso

```
/intelica-arca
```

o, para ver el detalle antes de enviar (objeto de compresion + archivos
generados):

```
/intelica-arca --full
```

No se activa automaticamente por el tema de la conversacion — solo con
estas invocaciones explicitas.
