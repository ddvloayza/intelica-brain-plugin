---
name: intelica-brain
description: "Orquesta el pipeline completo de Intelica Brain: comprime la conversacion actual (intelica-compression), genera los .md correspondientes (intelica-markdown), y los persiste como Pull Request en intelica-brain-ia (intelica-kb-storage) — en ese orden, pasando la salida de cada skill al siguiente. Invocar con '/intelica-brain' (alias retrocompatible: '/intelica-kb-storage', 'storage-intelica-brain'). Sin flag: modo silencioso, solo devuelve el/los link(s) de PR. Con flag '--full': muestra el objeto de compresion, los .md generados, y el resultado antes de enviarlos. NO activar automaticamente por el tema de la conversacion — solo con estas invocaciones explicitas. Los 3 skills que orquesta nunca se llaman entre si, ni se invocan directamente por el usuario."
---

# Intelica Brain — Skill orquestador

Convierte la conversacion actual en conocimiento persistido en
`ddvloayza/intelica-brain-ia`, coordinando 3 skills desacoplados en
secuencia. Ninguno de los 3 skills se llama entre si — toda la
coordinacion (validar entradas, pasar la salida de uno al siguiente,
manejar errores, decidir el modo de salida) la hace este skill.

```
Conversacion
  ↓
intelica-compression   (objeto estructurado)
  ↓
intelica-markdown      (coleccion de archivos .md)
  ↓
intelica-kb-storage    (Pull Request en intelica-brain-ia)
```

---

## Comando de activacion

```
/intelica-brain
```

o, con mas detalle en la salida:

```
/intelica-brain --full
```

Se aceptan como alias retrocompatibles las invocaciones previas:
`/intelica-kb-storage` y la frase `storage-intelica-brain` (o variantes
cercanas) — mismo comportamiento por default (silencioso).

Este skill **no se activa automaticamente** por el tema de la
conversacion — solo con estas invocaciones explicitas. Varias personas del
equipo pueden tener este skill instalado; sus conversaciones normales no
deben disparar nada.

**Diferencia entre los dos modos:**

| | Default (sin flag) | `--full` |
|---|---|---|
| Objeto de `intelica-compression` | No se muestra | Se muestra completo |
| Archivos de `intelica-markdown` | No se muestran | Se muestran completos antes de enviar |
| Envio por PR | Directo, sin confirmacion de contenido | Directo, con el contenido ya mostrado antes |
| Resultado final | Solo el link de PR | Link de PR + resumen (cantidad de archivos, categorias) |

---

## PASO 1 — Validar que corresponde iniciar el pipeline

Si la conversacion no tiene contenido documentable (charla puramente
trivial, o el usuario aclara que no queria iniciar el flujo), abortar sin
invocar ningun skill y avisar brevemente por que no se genero nada.

## PASO 2 — Invocar `intelica-compression`

Usar la herramienta de Skill para invocar `intelica-compression` sobre la
conversacion actual (o el tramo relevante). Recibir el bloque
`topics: []`.

Si `topics` viene vacio, detener el pipeline aqui — no continuar a
`intelica-markdown` ni a `intelica-kb-storage`. Avisar que no se detecto
contenido documentable.

**En modo `--full`**: mostrar el objeto estructurado completo antes de
continuar al Paso 3.

## PASO 3 — Invocar `intelica-markdown`

Pasar el bloque `topics[]` (sin modificarlo) como entrada de
`intelica-markdown`. Recibir la coleccion `files[]`.

**En modo `--full`**: mostrar el contenido completo de cada archivo antes
de continuar al Paso 4.

## PASO 4 — Invocar `intelica-kb-storage`

Pasar `files[]` (sin modificarlo) como entrada de `intelica-kb-storage`.
Recibir el link del Pull Request (o, si el MCP no esta disponible, la
confirmacion de archivos generados localmente).

## PASO 5 — Reportar resultado

**En modo default**: devolver solo el/los link(s) de Pull Request, sin
repetir contenido ni clasificacion.

**En modo `--full`**: devolver el link del PR junto con un resumen breve
(cantidad de archivos, categorias documentadas, cuentas involucradas).

---

## Manejo de errores

- Si `intelica-compression` falla o no puede procesar la conversacion:
  detener el pipeline, no invocar los skills siguientes, informar el
  motivo.
- Si `intelica-markdown` falla: detener el pipeline, no invocar
  `intelica-kb-storage`, informar el motivo. El objeto de
  `intelica-compression` no se pierde — se puede reintentar sin volver a
  comprimir.
- Si `intelica-kb-storage` informa que el MCP no esta disponible: no es un
  error del pipeline — es el fallback documentado (archivos locales via
  `create_file`/`present_files`). Reportarlo como tal, no como fallo.
- En ningun caso el orquestador reintenta un paso automaticamente sin que
  el usuario lo pida de nuevo.

## Reglas generales

- Los 3 skills (`intelica-compression`, `intelica-markdown`,
  `intelica-kb-storage`) **nunca se llaman entre si** — toda invocacion
  pasa por este orquestador.
- Ningun paso pide datos personales del usuario; el remitente del PR es
  siempre el valor fijo `enviado_intelicaBrain` (lo aplica
  `intelica-kb-storage`).
- **Nunca mergear el Pull Request**, en ningun modo — el merge queda
  siempre a revision humana.
- Este skill no acepta credenciales de ningun tipo (tokens, contrasenas)
  pegadas en el chat para intentar ninguna accion.
