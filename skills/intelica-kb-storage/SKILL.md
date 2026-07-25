---
name: intelica-kb-storage
description: "Persiste en GitHub (ddvloayza/intelica-brain-ia) una coleccion de archivos .md ya generados por intelica-markdown, via el servidor MCP intelica-brain-mcp: crea una rama, sube los archivos, y abre un unico Pull Request con resumen agregado. Es la UNICA responsabilidad de este skill — NO comprime conversaciones, NO redacta contenido, NO clasifica temas, NO decide que archivos crear. Es invocado internamente por el skill orquestador 'intelica-brain', nunca se invoca solo por el usuario ni se dispara automaticamente."
---

# Intelica KB Storage Skill

Recibe una coleccion de archivos `.md` ya redactados (por `intelica-markdown`)
y los persiste en `ddvloayza/intelica-brain-ia` como un unico Pull Request,
usando el servidor MCP propio `intelica-brain-mcp` configurado en
`.mcp.json` del proyecto.

Este skill **no toma ninguna decision de contenido**: no comprime, no
redacta, no clasifica. Su unica responsabilidad es Git.

```
REPO destino = ddvloayza/intelica-brain-ia   (lo maneja el propio MCP, no hace falta pasarlo)
```

---

## Entrada esperada

La lista `files[]` que entrega `intelica-markdown`, donde cada elemento
trae `filename`, `account` (o `null` para el `index.md`) y `content`.

## PASO 1 — Verificar disponibilidad del MCP

Con `tool_search`, confirmar que las herramientas de `intelica-brain-mcp`
estan cargadas (vienen de `.mcp.json` del proyecto).

**Si no estan disponibles**: no bloquear — crear los archivos localmente
con `create_file` y entregarlos con `present_files`, avisando que no se
pudo enviar automaticamente porque el MCP no esta conectado en esta
sesion.

## PASO 2 — Calcular nombre de rama

```
docs/brain-{fecha}-{identificador}
```

- `{fecha}`: fecha real del dia en que se genera (`YYYY-MM-DD`), nunca
  fija ni copiada de un ejemplo previo.
- `{identificador}`: un slug corto (minusculas, guiones, sin tildes) del
  tema principal si hay uno solo, o de un rotulo breve (`multi`, cantidad
  de temas) si son varios — mas un sufijo corto alfanumerico aleatorio
  (4 caracteres) para garantizar que la rama sea unica aunque se corra el
  skill mas de una vez el mismo dia sobre contenido similar.

## PASO 3 — Ejecutar la secuencia contra `intelica-brain-mcp`

1. `create_branch` desde `main` con el nombre calculado en el Paso 2.
2. Por cada archivo de tema en `files[]`: `create_or_update_file` en la
   ruta `inbox/{account}/{filename}` (usar `inbox/sin-cuenta/...` si
   `account` es `null` o `N/A`), con un mensaje de commit que resuma ese
   archivo puntual (ej. "docs: agrega caso de NAT Gateway en Portal-Prod").
3. Si `files[]` incluye un `index.md`: si todos los temas comparten la
   misma `account`, subirlo en `inbox/{account-comun}/{fecha}-index.md`;
   si los temas tienen `account` distintas, no persistir el `index.md`
   como archivo — su contenido (la lista de links) se incluye igual en el
   body del Pull Request del Paso 4.
4. `create_pull_request` de esa rama hacia `main`, con:
   - Titulo descriptivo (no generico tipo "nuevo archivo")
   - Body que incluya: resumen breve, fecha, cantidad de archivos
     incluidos, categorias documentadas (`category_raw` de cada tema), y
     un listado de los cambios realizados (archivo por archivo)
5. Parametro de remitente: usar siempre el valor fijo
   **`enviado_intelicaBrain`** — no preguntar correo, no usar memoria para
   esto, no pedir ningun dato personal del usuario.

## PASO 4 — Nunca mergear

**Nunca ejecutar `merge_pull_request`** (ni existe como tool en este MCP a
proposito) — el merge queda siempre a revision humana, reforzado por
branch protection en el repo destino.

## Salida

Devolver el link del Pull Request creado. Si `intelica-brain` (el
orquestador) fue invocado en modo `--full`, tambien devolver un resumen
breve de lo persistido (cantidad de archivos, categorias); en modo
default, solo el link.

---

## Reglas generales

- Nunca decide que comprimir ni que redactar — solo persiste lo que ya le
  llego armado.
- Los archivos van a `inbox/{account}/...` dentro del repo — la
  organizacion fina (mover a una taxonomia definitiva) se resuelve
  despues, fuera de este skill.
- Nombre de rama siempre `docs/brain-{fecha-real-de-hoy}-{identificador}`.
- Sin el conector de `intelica-brain-mcp` disponible, cae en generar
  archivos locales (`create_file` + `present_files`) sin llamadas de red
  adicionales.
- Este skill **no acepta credenciales de ningun tipo** (tokens,
  contrasenas) pegadas en el chat para intentar ninguna accion.
- **Nunca mergear el Pull Request**, en ningun modo.
- Es invocado por el skill `intelica-brain` (orquestador) — no se invoca
  solo, no se dispara por inferencia de tema de la conversacion.
