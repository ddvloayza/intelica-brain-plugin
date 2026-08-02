# Knowledge Model (ARCA)

Esquema de entidades y relaciones que producen los Providers y consume el
grafo. **Es fijo y curado**: un Provider no puede inventar tipos nuevos por
su cuenta — agregar un tipo de entidad o relacion es una decision
deliberada, que se toma editando este archivo.

Por que fijo y no emergente: el ahorro de tokens de consultar un grafo (en
vez de leer archivos completos) depende de que las consultas sean
predecibles. Si el Provider de AWS llama `SecurityGroup` a algo y el de
Terraform le dice `FirewallRule`, el grafo se vuelve inconsistente y el
Retrieval Engine no puede escribir queries confiables sobre el.

## Principio de trazabilidad

**Toda entidad y toda relacion tiene que poder trazarse al `.md` que la
documenta.** Por eso los fragmentos de grafo viven en el frontmatter del
propio `.md` (ver "Formato"), no en archivos aparte: el vinculo con la
fuente es estructural, no algo que haya que mantener sincronizado a mano.

Esto es lo que le permite a Claude citar de donde sale cada dato, y es la
version estructural de la regla que ya tiene `intelica-arca-recall`:
nunca fabricar una fuente.

## Entidades

Toda entidad tiene `type` e `id`. El resto de las propiedades son
opcionales salvo que se indique.

### `Account`
Cuenta de AWS.

| Propiedad | Requerida | Ejemplo |
|---|---|---|
| `id` | si | `Portal-Prod` |
| `account_id` | no | `060795899335` |
| `environment` | no | `prod`, `dev` |

### `Resource`
Cualquier recurso de AWS: instancia, security group, VPC, subnet, bucket,
Lambda, RDS, IAM role. **Es una sola entidad con `resource_type` como
propiedad**, no una entidad distinta por cada servicio — asi un servicio
nuevo de AWS no obliga a tocar el esquema.

| Propiedad | Requerida | Ejemplo |
|---|---|---|
| `id` | si | `i-0abc123`, `itl-0003-portal-prd-ec2-denver-02` |
| `resource_type` | si | `ec2_instance`, `security_group`, `vpc`, `subnet`, `s3_bucket`, `lambda`, `rds_instance`, `iam_role` |
| `name` | no | `denver-02` |
| `region` | no | `eu-south-2` |

### `Finding`
Hallazgo de seguridad o vulnerabilidad. Tambien se usa para **drift**
(cuando dos fuentes se contradicen, ej. el state de Terraform no coincide
con el inventario real).

| Propiedad | Requerida | Ejemplo |
|---|---|---|
| `id` | si | `CVE-2024-1234`, `drift-sg-0xyz-2026-08` |
| `finding_type` | si | `vulnerability`, `security`, `drift` |
| `severity` | no | `critical`, `high`, `medium`, `low` |
| `status` | no | `open`, `mitigated`, `accepted` |
| `source` | no | `GuardDuty`, `Inspector` |

### `Document`
El `.md` curado que documenta algo. **No se declara a mano** — se deriva
solo, del archivo que contiene el frontmatter (ver "Formato").

| Propiedad | Requerida | Ejemplo |
|---|---|---|
| `id` | si (automatico) | `inbox/Portal-Prod/2026-07-25-analisis-metricas.md` |
| `title` | si (del frontmatter) | `Analisis de metricas CPU/RAM...` |
| `date` | si (del frontmatter) | `2026-07-25` |

### `Decision`
Decision de arquitectura u operacion, estilo ADR.

| Propiedad | Requerida | Ejemplo |
|---|---|---|
| `id` | si | `usar-period-3600-cloudwatch` |
| `title` | si | `Usar period=3600 para cubrir 90 dias` |
| `date` | no | `2026-07-25` |
| `status` | no | `active`, `superseded`, `deprecated` |

### `Incident`
Incidente ya ocurrido.

| Propiedad | Requerida | Ejemplo |
|---|---|---|
| `id` | si | `guardduty-portal-prod-2026-07` |
| `date` | no | `2026-07-14` |
| `severity` | no | `high` |

### `Project`
Proyecto o repo que ya existe en la organizacion. **No** proyectos
hipoteticos que se estan planeando — solo cosas que existen.

| Propiedad | Requerida | Ejemplo |
|---|---|---|
| `id` | si | `intelica-brain-mcp` |
| `repo` | no | `ddvloayza/intelica-brain-mcp` |

### Entidad explicitamente excluida: `Person`

**No existe** una entidad `Person`, por privacidad. Quien hizo o dijo algo
no se modela en el grafo. La autoria de un PR queda en el propio PR (via
el token personal autenticado), no en el conocimiento.

## Relaciones

Toda relacion es `from` → `to`, con un `type` de esta lista.

| Tipo | De | A | Significado |
|---|---|---|---|
| `BELONGS_TO` | `Resource`, `Decision`, `Document` | `Account`, `Project` | pertenencia |
| `HAS_SECURITY_GROUP` | `Resource` | `Resource` (security_group) | la instancia tiene ese SG |
| `IN_VPC` | `Resource` | `Resource` (vpc) | esta en esa VPC |
| `IN_SUBNET` | `Resource` | `Resource` (subnet) | esta en esa subnet |
| `ASSUMES_ROLE` | `Resource` | `Resource` (iam_role) | asume ese rol |
| `ENCRYPTED_BY` | `Resource` | `Resource` (kms_key) | cifrado con esa clave KMS |
| `ATTACHED_TO` | `Resource` | `Resource` | volumen o ENI adjunto a una instancia |
| `REGISTERED_ON` | `Resource` | `Resource` (load_balancer) | esta detras de ese balanceador |
| `AFFECTS` | `Finding` | `Resource` | el hallazgo afecta a ese recurso |
| `MITIGATED_BY` | `Finding` | `Decision`, `Document` | como se mitigo |
| `RELATED_TO` | `Incident` | `Resource`, `Finding` | involucrado en el incidente |
| `DOCUMENTED_IN` | cualquiera | `Document` | **automatica** — ver abajo |

`DOCUMENTED_IN` no se declara a mano: toda entidad que aparezca en el
frontmatter de un `.md` queda automaticamente vinculada a ese `Document`.

## Convencion de IDs

Los IDs tienen que ser **estables entre curaciones distintas** — si la
misma instancia aparece en dos `.md` diferentes, tiene que ser el mismo
nodo del grafo, no dos.

Regla: **usar el identificador real del mundo cuando existe.**

| Entidad | ID a usar |
|---|---|
| `Account` | el nombre de la cuenta tal cual (`Portal-Prod`) |
| `Resource` | el ID de AWS (`i-0abc123`, `sg-0xyz`, `vpc-0abc`) o el nombre canonico si es mas estable (`itl-0003-portal-prd-ec2-denver-02`) |
| `Finding` | el ID de la fuente (`CVE-...`, ID de GuardDuty) |
| `Document` | la ruta del archivo en el repo |
| `Decision` | slug en kebab-case, descriptivo y unico |
| `Incident` | slug en kebab-case, con fecha si ayuda a desambiguar |
| `Project` | el nombre del repo, sin el owner |

Nunca usar como ID algo que cambia: una IP, un nombre para mostrar, un
timestamp.

## Formato

Hay **dos formas validas** de emitir un fragmento de grafo. El reconstructor
acepta las dos, y las une.

### A) Inline en el frontmatter — para documentos curados a mano

Cuando un documento sale de una conversacion y tiene pocas entidades (una
decena), van en el frontmatter, en `entities` y `relations`. El vinculo con
el `Document` es estructural: estan dentro del archivo que documentan.

### B) Archivo hermano `.graph.yaml` — para documentos generados

Cuando el documento lo genera un Provider a partir de un inventario, las
entidades son cientos y **no** entran en el frontmatter: medido sobre el
inventario real de AWS, el frontmatter llegaba al **85% del archivo** (500+
entidades por cuenta). Eso hace que cada lectura del `.md` gaste tokens en
datos que solo le sirven al grafo, no a quien lee.

En ese caso el fragmento va en un archivo hermano, por convencion de nombre:

```
compute.md            <- el documento, liviano, para leer
compute.graph.yaml    <- su fragmento de grafo
```

El `.md` declara `graph: compute.graph.yaml` en su frontmatter, y el
`.graph.yaml` declara `documents: compute.md`. La relacion `DOCUMENTED_IN`
se deriva de ese par, igual que en el caso inline.

### Ejemplo (forma A, inline)

```yaml
---
title: "Conectividad entre Denver-02 y la instancia de reportes"
account: Portal-Prod
date: 2026-08-02
tags: [ec2, security-group, conectividad]

entities:
  - type: Resource
    id: itl-0003-portal-prd-ec2-denver-02
    resource_type: ec2_instance
    region: eu-south-2
  - type: Resource
    id: sg-0xyz789
    resource_type: security_group
  - type: Account
    id: Portal-Prod

relations:
  - from: itl-0003-portal-prd-ec2-denver-02
    type: HAS_SECURITY_GROUP
    to: sg-0xyz789
  - from: itl-0003-portal-prd-ec2-denver-02
    type: BELONGS_TO
    to: Portal-Prod
---

# Conectividad entre Denver-02 y la instancia de reportes
...
```

### Compatibilidad con el formato viejo

Los `.md` que ya existen tienen `entities` como lista plana de strings sin
tipo:

```yaml
entities: ["itl-0003-portal-prd-ec2-denver-02", "10.10.4.10", "eu-south-2"]
```

El reconstructor del grafo **ignora** las entradas que sean strings sueltos
(no tienen tipo, no se puede saber que son) y solo procesa las que son
objetos con `type` e `id`. Asi los archivos viejos no rompen el build, y se
pueden ir migrando de a poco sin un big-bang.

## Como se extiende

Agregar un tipo de entidad, de relacion, o un `resource_type` nuevo es una
decision deliberada:

1. Editar este archivo.
2. Que pase por PR y review humano, igual que cualquier otro cambio.

Un Provider **nunca** emite un tipo que no este aca. Si se encuentra algo
que no encaja, se modela con lo que hay (ej. un servicio de AWS nuevo es un
`resource_type` nuevo, no una entidad nueva) o se propone extender el
esquema — pero eso lo decide una persona, no el Provider.
