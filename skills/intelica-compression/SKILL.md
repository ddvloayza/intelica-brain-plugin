---
name: intelica-compression
description: "Comprime una conversacion larga (infra AWS, desarrollo, o herramientas Claude/GitHub) en un objeto estructurado de conocimiento, eliminando saludos, pruebas, contenido repetido y respuestas redundantes. NUNCA genera markdown ni toca Git — devuelve unicamente el objeto estructurado (YAML) para que otro skill (intelica-markdown) lo transforme en archivos. Es invocado internamente por el skill orquestador 'intelica-brain', nunca se invoca solo por el usuario ni se dispara automaticamente por el tema de la conversacion."
---

# Intelica Compression Skill

Transforma una conversacion larga en un objeto de conocimiento estructurado.
No es un resumen — es una extraccion. Elimina todo lo que no aporta
conocimiento reutilizable y conserva, en forma estructurada, todo lo que si.

Este skill **nunca** decide formato de archivo, nunca escribe Markdown final,
y nunca toca Git. Su unica salida es el objeto estructurado definido mas
abajo, que otro skill (`intelica-markdown`) consume.

---

## Que eliminar

- Saludos y cierre de cortesia
- Conversacion trivial o exploratoria que no llego a ninguna conclusion
- Pruebas, intentos fallidos y curls/comandos de debugging que no aportan
  una decision o hallazgo final (el resultado final si se conserva)
- Contenido repetido — si algo se dijo dos veces, queda una sola vez
- Respuestas redundantes o círculos de aclaracion que no cambiaron el
  resultado

## Que conservar (identificar como minimo)

- Decisiones tecnicas y su motivo
- Arquitectura y componentes/servicios involucrados
- Requisitos (explicitos o inferidos con claridad)
- Patrones y convenciones establecidas
- Tareas pendientes
- Riesgos identificados
- Preguntas abiertas (sin responder al cierre de la conversacion)
- Supuestos asumidos (no confirmados explicitamente)
- Artefactos generados (archivos, PRs, scripts, recursos creados)
- Codigo importante (fragmentos que definen un comportamiento clave, no
  todo el codigo mostrado)
- Archivos y rutas relevantes mencionadas
- Buenas practicas aplicadas o acordadas
- Contexto tecnico necesario para entender el resto sin releer la
  conversacion completa

Nunca inventar datos que no aparecieron en la conversacion. Si algo quedo
ambiguo, se marca como pregunta abierta o supuesto, nunca se completa por
inferencia forzada.

---

## PASO 1 — Detectar temas

Recorrer la conversacion completa (o el tramo mas relevante, si la
conversacion mezcla temas claramente distintos y no relacionados).
Identificar uno o mas temas/problemas distintos — igual que ya hace
`intelica-kb-storage` hoy, este paso no pregunta al usuario cual tramo usar
salvo ambiguedad genuina.

Para cada tema, determinar por analisis propio (nunca preguntando):
- Un titulo corto y descriptivo
- Una clasificacion libre (`category_raw`) que describa el contenido real
  (no una categoria fija tipo Incidencia/Reporte)
- La cuenta AWS involucrada si aplica (`Portal-Prod`, `Interchange-Prod`,
  `Analytics-Prod`, `Intelica-Network`, o `N/A`)

Si ningun tema amerita documentarse (charla puramente exploratoria sin
conclusion, o el usuario aclaro que no queria iniciar el flujo), devolver
`topics: []` y detenerse ahi — el resto del pipeline no continua sin temas.

## PASO 2 — Extraer y estructurar por tema

Por cada tema detectado, completar el objeto estructurado de salida (ver
formato abajo). Un tema = un bloque `topics[]`. Nunca mezclar dos temas en
un mismo bloque.

Si un campo no aplica a este tema en particular, se omite o se deja como
lista vacia — no se rellena con contenido generico.

---

## Formato de salida (obligatorio)

Devolver exactamente este bloque YAML como resultado del skill (nada mas
antes o despues, salvo que se te pida explicacion adicional para debug):

```yaml
topics:
  - title: "Titulo corto y descriptivo del tema"
    account: "Portal-Prod | Interchange-Prod | Analytics-Prod | Intelica-Network | N/A"
    category_raw: "Clasificacion libre determinada por analisis propio"
    tags: [tag1, tag2]
    entities: ["vpc-...", "arn:aws:...", "nombre-recurso-literal"]
    summary: "2-4 lineas: de que se trato el tema y en que quedo"
    technical_context: "Contexto tecnico necesario para entender el resto sin releer la conversacion"
    decisions: ["decision tecnica 1 + motivo", "..."]
    architecture: ["componente/servicio involucrado", "..."]
    requirements: ["requisito explicito o inferido", "..."]
    patterns_conventions: ["patron o convencion establecida", "..."]
    resources:
      - resource: "nombre del recurso"
        id: "ID/ARN literal"
        account: "cuenta si aplica"
    important_code: ["fragmento o referencia a codigo clave, no todo el codigo mostrado", "..."]
    relevant_files: ["ruta/archivo mencionado", "..."]
    best_practices: ["buena practica aplicada o acordada", "..."]
    pending_work: ["tarea pendiente", "..."]
    risks: ["riesgo identificado", "..."]
    open_questions: ["pregunta sin responder al cierre", "..."]
    assumptions: ["supuesto no confirmado explicitamente", "..."]
    artifacts: ["archivo/PR/script/recurso generado durante la conversacion", "..."]
```

Listas vacias (`[]`) para lo que no aplique — nunca omitir el campo por
completo (`intelica-markdown` espera todas las claves presentes).

## Reglas generales

- Nunca genera Markdown final, nunca crea archivos, nunca toca Git.
- Nunca pregunta al usuario para clasificar o completar un campo — analisis
  propio siempre; si algo es genuinamente ambiguo, va a `open_questions` o
  `assumptions`, no se pregunta en el chat.
- Nunca inventa IDs, ARNs, cifras ni decisiones que no se dijeron.
- Un tema por bloque `topics[]` — nunca mezclar.
- Es invocado por el skill `intelica-brain` (orquestador) — no se invoca
  solo, no se dispara por inferencia de tema de la conversacion.
