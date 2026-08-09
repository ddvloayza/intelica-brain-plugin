---
title: "CPU/RAM/Storage metrics analysis for Denver Prd (90 days)"
account: Portal-Prod
category_raw: "Capacity analysis / usage peak investigation"
category_confirmed: false
tags: [denver, ec2, cloudwatch, capacity, sql-server, cpu, ram, storage, peaks, cwagent]
date: 2026-07-25
entities: ["itl-0003-portal-prd-ec2-denver-02", "10.10.4.10", "eu-south-2", "denver_metrics_90d.py", "denver_metrics_90d.csv", "denver_metrics_report.html", "dbo.vw_active_session_history"]
related: []
---

# CPU/RAM/Storage metrics analysis for Denver Prd (90 days)

## Summary
Diego asked to extract CPU, RAM and Storage metrics from Denver Prd (Windows EC2 running SQL Server) for the last 3 months, to identify usage peak hours and determine whether any resource is hitting its ceiling. A read-only boto3 script was built that extracts the data at hourly resolution (the only CloudWatch resolution covering 90 days) along with an HTML report containing 6 charts. Peak ranges of CPU>=95% and RAM>=90% were identified, and the database (`dbo.vw_active_session_history`) was investigated to find which sessions caused them. A preliminary finding (that the daily 20:00 peak corresponded to the `DBA_BK_ASSOCINV_DAILY` / `DBA_BK_DB_DLY` jobs) was discarded after checking a regular night and not finding those jobs in the matching window.

## Technical context
Denver Prd is the instance `itl-0003-portal-prd-ec2-denver-02` (r5.4xlarge, IP `10.10.4.10`, account Portal-Prod, region `eu-south-2`), a Windows server running SQL Server. `CPUUtilization` is native to the `AWS/EC2` namespace and is always available. RAM and Disk do not exist in CloudWatch unless the CloudWatch Agent is installed and publishing to the `CWAgent` namespace (Windows counters such as `Memory % Committed Bytes In Use` / `Available MBytes` and `LogicalDisk % Free Space`). CloudWatch retains 1-minute data for 15 days, 5-minute data for 63 days, and 1-hour data for 455 days — to cover the full 90 days requested, the only available resolution is `period=3600` (1 hour).

## Technical decisions
- Use `period=3600` (hourly resolution) as the only way to cover a full 90 days within CloudWatch retention.
- Use hourly `Maximum` to detect real peaks and hourly `Average` for the usage profile.
- Rewrite the HTML report's 6 charts from `<canvas>` to `<svg>` with real DOM elements (`<path>`, `<line>`, `<circle>`, `<text>`), because canvas depended on GPU acceleration / the browser's Canvas 2D engine, which failed in the user's environment.
- Flag finding #3 of the document for rewrite or removal (the 20:00 CPU peak attributed to `DBA_BK_*` jobs) after confirming, against a regular night (2026-07-21, 19:30–21:30 Lima time), that those jobs do not appear in the peak window.

## Architecture and components
- Windows EC2 (Denver Prd) running SQL Server
- CloudWatch (`AWS/EC2` namespace for CPU, `CWAgent` namespace for RAM/Disk)
- SQL Server: `dbo.vw_active_session_history` view for active session history
- Python/boto3 script (read-only) for metrics extraction
- HTML report with SVG charts

## Requirements
- Extract CPU, RAM and Storage metrics from Denver Prd for the last 3 months.
- Identify usage peak hours.
- Determine whether any resource is hitting its ceiling/maximum capacity.
- For each identified peak range, determine the database session/user that caused it.

## Patterns and conventions
- Strictly read-only scripts (only `ec2:Describe*` and `cloudwatch:ListMetrics`/`GetMetricData`).
- Group consecutive timestamps with a gap tolerance (`gap_hours`) to build peak ranges, instead of listing them one by one.
- Thresholds defined in the script: `CPU_WARN=90%`, `MEM_WARN=90%`, `DISK_FREE_MIN=10%`; the final peak analysis used `CPU>=95%` and `RAM>=90%` over the hourly `Maximum` value.
- To query multiple specific time windows in `vw_active_session_history` without one large window crowding out another, use `UNION ALL` with `TOP N` per range block instead of a single `WHERE ... OR ...` with one global `TOP N`.

## Resources or entities involved
| Resource | ID/ARN | Account |
|---|---|---|
| Denver Prd (EC2) | itl-0003-portal-prd-ec2-denver-02 / 10.10.4.10 | Portal-Prod |

## Relevant code
- Function `group_consecutive(ts_series, gap_hours)` to group timestamps into continuous ranges allowing gaps of up to `gap_hours`.
- SQL query against `dbo.vw_active_session_history` using `UNION ALL` of `SELECT TOP 10000 ... WHERE run_date >= X AND run_date < Y` blocks to guarantee rows from each of the 9 anomaly ranges outside the backup window.
- Targeted confirmation query over a "regular" night (2026-07-21 19:30–21:30 Lima) against `dbo.vw_active_session_history`, explicitly searching `program_name`/`query_text` for `DBA_BK`.

## Relevant files
- /mnt/user-data/outputs/denver_metrics_90d.py
- denver_metrics_90d.csv
- /mnt/user-data/outputs/denver_metrics_report.html
- /mnt/user-data/outputs/denver_confirmar_backup_20h.sql

## Good practices
- Confirm the root cause hypothesis against real data from a "regular" night before including a finding in the final document.
- Do not assume findings from earlier investigations (e.g. the NAT Gateway investigation) apply directly to a new context without verifying them against current data.

## Risks
- The `DBA_BK_*` job names may have changed since the earlier NAT Gateway investigation, which could produce false negatives in the root cause search.
- Relying on memory from earlier investigations without verifying against current data can lead to incorrect findings in the final document.

## Open questions
- What is the real cause of the daily 20:00 CPU peak on Denver Prd, if it is not the `DBA_BK_*` jobs?
- Did the backup jobs change names, or does the 20:00 pattern correspond to a different process altogether?

## Assumptions
(none)

## Generated artifacts
- denver_metrics_90d.py
- denver_metrics_90d.csv
- denver_metrics_report.html
- denver_confirmar_backup_20h.sql
- SQL queries with 9 anomaly ranges (UNION ALL) outside the backup window

## Pending tasks
- Rewrite or remove finding #3 of the document (the 20:00 CPU peak), since the `DBA_BK_*` jobs do not explain it.
- Investigate the real cause of the daily 20:00 CPU peak if it is not the `DBA_BK_*` backups.
- Finish identifying, via the 9 anomaly windows outside the backup schedule, the sessions/users responsible for each peak (67 of the 71 CPU>=95% ranges are already explained by the daily 20:00 pattern; the ranges outside that pattern remain unresolved).
