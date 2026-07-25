---
name: intelica-markdown
description: "Genera uno o mas archivos .md optimizados para RAG a partir del objeto estructurado que produce el skill intelica-compression — nunca a partir de la conversacion cruda. Decide automaticamente cuantos archivos crear (uno por tema) y genera un index.md con enlaces relativos si hay mas de uno. NUNCA toca Git, NUNCA hace commits, NUNCA crea ramas ni Pull Requests — solo devuelve la coleccion de archivos. Es invocado internamente por el skill orquestador 'intelica-brain', nunca se invoca solo ni se dispara automaticamente."
---

# Intelica Markdown Skill

Convierte el objeto estructurado de `intelica-compression` en documentacion
Markdown lista para RAG. Nunca recibe la conversacion cruda — solo el
bloque `topics[]` ya extraido. Nunca toma decisiones de clasificacion o
contenido nuevas; eso ya lo resolvio `intelica-compression`.

Este skill **nunca** conoce Git — no crea ramas, no hace commits, no abre
Pull Requests. Su unica salida es una coleccion de archivos (ruta +
contenido) que otro skill (`intelica-kb-storage`) persiste.

---

## Cuantos archivos generar

- **Un `.md` por cada elemento de `topics[]`** — nunca mezclar dos temas en
  un mismo archivo, aunque hayan surgido en la misma conversacion.
- Si `topics` tiene un solo elemento: generar solo ese archivo, sin
  `index.md`.
- Si `topics` tiene mas de un elemento: generar un archivo por tema **mas**
  un `index.md` que enlace a todos, usando rutas relativas.

## Ruta y nombre de archivo

Por cada tema: `{fecha}-{slug}.md`, donde:
- `{fecha}` es la fecha real del dia en que se genera (`YYYY-MM-DD`), tal
  como la trae el tema si `intelica-compression` la incluyo, o la fecha
  actual real si no.
- `{slug}` es un slug corto derivado del `title` del tema (minusculas,
  guiones, sin tildes ni espacios).

La ruta completa dentro del repo la define `intelica-kb-storage` (no este
skill) — este skill solo entrega el nombre de archivo y el contenido; no
decide la carpeta de destino en `intelica-brain-ia`.

## Frontmatter (obligatorio, uno por archivo de tema)

```yaml
---
title: "Titulo descriptivo y autonomo del tema"
account: <valor de account del tema>
category_raw: "<valor de category_raw del tema, sin normalizar>"
category_confirmed: false
tags: [<tags del tema>]
date: YYYY-MM-DD
entities: [<entities del tema>]
related: []
---
```

`category_confirmed` siempre `false` — queda pendiente de normalizacion
posterior fuera de este skill. `related` se completa solo si
`intelica-compression` referencio explicitamente otro tema/archivo; si no,
queda `[]`.

## Cuerpo (por archivo de tema)

Mapear los campos del objeto estructurado a estas secciones — omitir una
seccion completa si el campo correspondiente vino vacio, en vez de dejarla
con contenido generico:

```
## Resumen
(campo summary)

## Contexto tecnico
(campo technical_context)

## Decisiones tecnicas
(campo decisions, como lista)

## Arquitectura y componentes
(campo architecture, como lista)

## Requisitos
(campo requirements, como lista)

## Patrones y convenciones
(campo patterns_conventions, como lista)

## Recursos o entidades involucradas
(campo resources, como tabla: recurso | ID/ARN | cuenta)

## Codigo relevante
(campo important_code)

## Archivos relevantes
(campo relevant_files, como lista)

## Buenas practicas
(campo best_practices, como lista)

## Riesgos
(campo risks, como lista)

## Preguntas abiertas
(campo open_questions, como lista)

## Supuestos
(campo assumptions, como lista)

## Artefactos generados
(campo artifacts, como lista)

## Tareas pendientes
(campo pending_work, como lista)
```

Reglas de redaccion:
- **Un solo H1** por archivo, igual al `title` del frontmatter — todo lo
  demas es `##` o mas profundo.
- Secciones **autocontenidas** — repetir el sujeto explicito en cada una,
  nunca referencias implicitas ("esta instancia..." sin nombrarla).
- Repetir siempre los identificadores literales (IDs, ARNs, nombres de
  recursos) tal cual vinieron en `entities`/`resources` — favorece
  retrieval por coincidencia exacta.
- Nunca inventar contenido que no vino en el objeto estructurado.

## `index.md` (solo si hay mas de un tema)

```markdown
# Indice

- [Titulo del tema 1](./{fecha}-{slug-1}.md)
- [Titulo del tema 2](./{fecha}-{slug-2}.md)
```

Un enlace relativo por archivo generado, en el mismo orden que
`topics[]`. Sin frontmatter propio.

## Formato de salida (obligatorio)

Devolver la coleccion de archivos como lista `files[]`, cada uno con su
nombre y contenido completo (frontmatter + cuerpo ya armados):

```yaml
files:
  - filename: "{fecha}-{slug}.md"
    account: "<account del tema, para que intelica-kb-storage arme la ruta>"
    content: |
      <contenido completo del archivo, frontmatter incluido>
  - filename: "index.md"          # solo si hubo mas de un tema
    account: null
    content: |
      <contenido del indice>
```

## Reglas generales

- Nunca clasifica ni decide contenido nuevo — solo transforma lo que ya
  vino estructurado.
- Nunca toca Git ni sabe que existe un repositorio destino.
- Nunca inventa IDs, ARNs, cifras ni relaciones no presentes en la entrada.
- Es invocado por el skill `intelica-brain` (orquestador) — no se invoca
  solo, no se dispara por inferencia de tema de la conversacion.
