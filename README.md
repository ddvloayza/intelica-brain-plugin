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

Cada proyecto donde se use este plugin necesita, ademas de instalar el
plugin, tener configurado su propio `.mcp.json` apuntando al servidor:

```json
{
  "mcpServers": {
    "intelica-brain-mcp": {
      "type": "http",
      "url": "https://<tu-function-url>.lambda-url.us-east-1.on.aws/mcp",
      "headers": {
        "Authorization": "Bearer ${INTELICA_MCP_TOKEN}"
      }
    }
  }
}
```

Sin ese `.mcp.json`, `intelica-kb-storage` cae en un modo local (genera
los archivos pero no los sube), sin fallar el pipeline.

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
