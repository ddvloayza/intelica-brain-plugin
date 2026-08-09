---
title: "Análisis de métricas CPU/RAM/Storage de Denver Prd (90 días)"
account: Portal-Prod
category_raw: "Análisis de capacidad / investigación de picos de uso"
category_confirmed: false
tags: [denver, ec2, cloudwatch, capacity, sql-server, cpu, ram, storage, picos, cwagent]
date: 2026-07-25
entities: ["itl-0003-portal-prd-ec2-denver-02", "10.10.4.10", "eu-south-2", "denver_metrics_90d.py", "denver_metrics_90d.csv", "denver_metrics_report.html", "dbo.vw_active_session_history"]
related: []
---

# Análisis de métricas CPU/RAM/Storage de Denver Prd (90 días)

## Resumen
Diego pidió extraer métricas de CPU, RAM y Storage de Denver Prd (EC2 Windows con SQL Server) de los últimos 3 meses, para identificar los picos de horas de uso y determinar si algún recurso llega a su techo. Se construyó un script boto3 read-only que extrae los datos a resolución horaria (única resolución de CloudWatch que cubre 90 días) y un reporte HTML con 6 gráficos. Se identificaron rangos de picos de CPU>=95% y RAM>=90%, y se investigó en la base de datos (`dbo.vw_active_session_history`) qué sesiones los originaron. Un hallazgo preliminar (que el pico diario de las 20:00 correspondía a los jobs `DBA_BK_ASSOCINV_DAILY` / `DBA_BK_DB_DLY`) fue descartado tras verificar una noche regular sin encontrar esos jobs en la ventana correspondiente.

## Contexto técnico
Denver Prd es la instancia `itl-0003-portal-prd-ec2-denver-02` (r5.4xlarge, IP `10.10.4.10`, cuenta Portal-Prod, región `eu-south-2`), un servidor Windows con SQL Server. `CPUUtilization` es nativo del namespace `AWS/EC2` y siempre está disponible. RAM y Disco no existen en CloudWatch salvo que el CloudWatch Agent esté instalado y publicando al namespace `CWAgent` (contadores Windows tipo `Memory % Committed Bytes In Use` / `Available MBytes` y `LogicalDisk % Free Space`). CloudWatch retiene datos de 1 minuto por 15 días, de 5 minutos por 63 días, y de 1 hora por 455 días — para cubrir los 90 días completos solicitados, la única resolución disponible es `period=3600` (1 hora).

## Decisiones técnicas
- Usar `period=3600` (resolución horaria) como única forma de cubrir 90 días completos dentro de la retención de CloudWatch.
- Usar `Maximum` por hora para detectar picos reales y `Average` por hora para el perfil de uso.
- Reescribir los 6 gráficos del reporte HTML de `<canvas>` a `<svg>` con elementos DOM reales (`<path>`, `<line>`, `<circle>`, `<text>`), porque el canvas dependía de aceleración GPU / motor Canvas 2D del navegador, que fallaba en el entorno del usuario.
- Marcar para reescritura o eliminación el hallazgo #3 del documento (pico de CPU de las 20:00 causado por jobs `DBA_BK_*`) tras confirmar, contra una noche regular (2026-07-21, 19:30–21:30 hora Lima), que esos jobs no aparecen en la ventana del pico.

## Arquitectura y componentes
- EC2 Windows (Denver Prd) con SQL Server
- CloudWatch (namespace `AWS/EC2` para CPU, namespace `CWAgent` para RAM/Disco)
- SQL Server: vista `dbo.vw_active_session_history` para historial de sesiones activas
- Script Python/boto3 (read-only) para extracción de métricas
- Reporte HTML con gráficos SVG

## Requisitos
- Extraer métricas de CPU, RAM y Storage de Denver Prd de los últimos 3 meses.
- Identificar los picos de horas de uso.
- Determinar si algún recurso llega a su techo/capacidad máxima.
- Para cada rango de pico identificado, determinar la sesión/usuario de base de datos que lo originó.

## Patrones y convenciones
- Scripts estrictamente read-only (solo `ec2:Describe*` y `cloudwatch:ListMetrics`/`GetMetricData`).
- Agrupar timestamps consecutivos con tolerancia de hueco (`gap_hours`) para construir rangos de picos, en vez de listarlos uno por uno.
- Umbrales definidos en el script: `CPU_WARN=90%`, `MEM_WARN=90%`, `DISK_FREE_MIN=10%`; el análisis final de picos usó `CPU>=95%` y `RAM>=90%` sobre el valor `Maximum` horario.
- Para consultar múltiples ventanas de tiempo específicas en `vw_active_session_history` sin que una ventana grande le quite espacio a otra, usar `UNION ALL` con `TOP N` por cada bloque de rango en vez de un único `WHERE ... OR ...` con un solo `TOP N` global.

## Recursos o entidades involucradas
| Recurso | ID/ARN | Cuenta |
|---|---|---|
| Denver Prd (EC2) | itl-0003-portal-prd-ec2-denver-02 / 10.10.4.10 | Portal-Prod |

## Código relevante
- Función `group_consecutive(ts_series, gap_hours)` para agrupar timestamps en rangos continuos permitiendo huecos de hasta `gap_hours`.
- Query SQL contra `dbo.vw_active_session_history` usando `UNION ALL` de bloques `SELECT TOP 10000 ... WHERE run_date >= X AND run_date < Y` para garantizar filas de cada uno de los 9 rangos de anomalías fuera del horario de backup.
- Query de confirmación puntual sobre una noche "regular" (2026-07-21 19:30–21:30 Lima) contra `dbo.vw_active_session_history`, buscando explícitamente `program_name`/`query_text` con `DBA_BK`.

## Archivos relevantes
- /mnt/user-data/outputs/denver_metrics_90d.py
- denver_metrics_90d.csv
- /mnt/user-data/outputs/denver_metrics_report.html
- /mnt/user-data/outputs/denver_confirmar_backup_20h.sql

## Buenas prácticas
- Confirmar la hipótesis de causa raíz contra datos reales de una noche "regular" antes de incluir un hallazgo en el documento final.
- No asumir que hallazgos de investigaciones anteriores (ej. la investigación de NAT Gateway) aplican directamente a un contexto nuevo sin verificarlos contra datos actuales.

## Riesgos
- Los nombres de los jobs `DBA_BK_*` pudieron cambiar desde la investigación anterior de NAT Gateway, lo que podría generar falsos negativos en la búsqueda de causa raíz.
- Basarse en memoria de investigaciones anteriores sin verificar contra datos actuales puede llevar a hallazgos incorrectos en el documento final.

## Preguntas abiertas
- ¿Cuál es la causa real del pico de CPU diario a las 20:00 en Denver Prd, si no son los jobs `DBA_BK_*`?
- ¿Los jobs de backup cambiaron de nombre, o el patrón de las 20:00 corresponde a otro proceso distinto?

## Supuestos
(ninguno)

## Artefactos generados
- denver_metrics_90d.py
- denver_metrics_90d.csv
- denver_metrics_report.html
- denver_confirmar_backup_20h.sql
- Queries SQL con 9 rangos de anomalías (UNION ALL) fuera de horario de backup

## Tareas pendientes
- Reescribir o eliminar el hallazgo #3 del documento (pico de CPU de las 20:00), ya que los jobs `DBA_BK_*` no lo explican.
- Investigar la causa real del pico de CPU diario de las 20:00 si no son los backups `DBA_BK_*`.
- Terminar de identificar, vía las 9 ventanas de anomalías fuera de horario de backup, las sesiones/usuarios responsables de cada pico (67 de los 71 rangos de CPU>=95% ya se explican por el patrón diario de las 20:00; quedan por resolver los rangos fuera de ese patrón).
