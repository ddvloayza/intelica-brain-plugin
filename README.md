# intelica-brain-plugin

Plugin de Claude Code/Desktop: transforma conversaciones largas en
conocimiento estructurado y lo persiste como Pull Request en
`ddvloayza/intelica-brain-ia`.

Contiene 1 skill orquestador + 3 skills desacoplados:

```
skills/
├── intelica-brain/            (orquestador — "/intelica-brain")
├── intelica-compression/      (conversacion -> objeto estructurado)
├── intelica-markdown/         (objeto estructurado -> archivos .md)
└── intelica-kb-storage/       (archivos .md -> Pull Request via MCP)
```

Ninguno de los 3 skills se llama entre si — toda la coordinacion la hace
`intelica-brain`. Ver el `SKILL.md` de cada uno para el detalle completo.

## Requisito: el servidor MCP

Este plugin **no reemplaza** el servidor MCP `intelica-brain-mcp`
(repo separado: `ddvloayza/intelica-brain-mcp`) — lo necesita. El skill
`intelica-kb-storage` llama a sus tools (`create_branch`,
`create_or_update_file`, `create_pull_request`) para persistir en GitHub.

El plugin ya trae su propio `.mcp.json` (en la raiz de este repo), asi que
instalar el plugin **registra el servidor automaticamente** — no hace
falta que cada proyecto tenga su propio `.mcp.json` por separado.

Lo unico que cada persona necesita configurar en su maquina es la variable
de entorno con el bearer token real (el `.mcp.json` del plugin solo trae
la referencia `${INTELICA_MCP_TOKEN}`, nunca el valor real, porque este
repo se comparte con el equipo):

```bash
export INTELICA_MCP_TOKEN="el-bearer-token-real"
```

Agregala a tu `~/.zshrc` (o el profile de tu shell) para que persista
entre sesiones, y reiniciá Claude Desktop despues de setearla.

Sin esa variable seteada (o sin el plugin instalado), `intelica-kb-storage`
cae en un modo local (genera los archivos pero no los sube), sin fallar
el pipeline.

## Instalar el plugin

Una vez que este contenido este pusheado a un repo de GitHub:

```
/plugin marketplace add <owner>/<nombre-del-repo>
/plugin install intelica-brain@intelica-brain-marketplace
```

Reemplaza `<owner>/<nombre-del-repo>` por el repo real donde vive esto
(por ejemplo `ddvloayza/intelica-brain-plugin`).

## Uso

```
/intelica-brain
```

o, para ver el detalle antes de enviar (objeto de compresion + archivos
generados):

```
/intelica-brain --full
```

No se activa automaticamente por el tema de la conversacion — solo con
estas invocaciones explicitas.
