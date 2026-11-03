# exposure-incident-response-assurance

**Status report — evidence pack `t01.uni.lab`, snapshot at `2026-12-14T04:05:30Z`.**

This document records **what the situation is right now**, as far as the ten log files prove it. It does
not contain a response plan, a remediation order, or a fix. Every claim carries an evidence id
(`A-###`, `E-###`, `N-###`, `P-###`) or a file row you can re-check yourself.

| | |
|---|---|
| Case | CNET 463 — Case Study 3 (synthetic evidence pack) |
| Team / domain / network | T01 — `t01.uni.lab` — `10.170.0.0/16` |
| Snapshot time ("now") | `2026-12-14T04:05:30Z` — no line in any file is later |
| Incident | `IR-911`, declared `critical` at `03:53:30Z` (12 min before this snapshot) |
| Declared scope | `files`, `jump`, `backup` (`P-043`) |
| Services down or impaired | `files` (encrypted), `exam-app` (cannot read exam materials), `exam-db` (partially encrypted) |
| Next deadline | Exam session `D morning` at `07:30Z`, ~600 students — **3h24m30s away** |

---

## 1. State of each asset

| Asset | State at `04:05:30Z` | Basis |
|---|---|---|
| `files` (10.170.30.15) | **Encrypted.** ~70,700 files renamed to `.t01lck` in share `exam-materials`; ransom note `README_RESTORE.txt` present. EDR agent still reporting normally. | `E-048`, `E-049`, `E-051`, `E-052`, `E-058` |
| `exam-db` (10.170.30.10) | **Partially encrypted.** 395 renames in volume `db-data`. Agent heartbeats OK; logical integrity of the database is unknown. | `E-053`, `E-057` |
| `exam-app` (10.170.10.20) | **Running but impaired.** 69 requests failed on mount `/mnt/files/exam-materials` at `03:39:54Z`. | `P-042`, `E-056` |
| `idp` (10.170.10.10) | **Running and serving tokens.** Issued a token at `04:02:09Z`. Also the confirmed entry point; three EDR scans returned `clean`. | `A-072`, `E-055`, `E-013`, `E-024`, `E-054` |
| `jump` (10.170.40.20) | **Unknown — no telemetry.** EDR has not reported since `2026-12-13T20:52:00Z` (7h13m). Treat as attacker-controlled. | `E-007` |
| `backup` (10.170.30.30) | **Backup service stopped** at `03:01:24Z`; 24 repository snapshots purged at `03:01:42Z`. Repository now lists **0 snapshots**. The EDR agent is still reporting — that is a different process, not the backup service. | `E-043`, `E-044`, `E-047`, `backup_report.txt` |
| `soc-scan` (10.170.40.5) | Normal. Its `01:28Z` sweep was authorised. | `N-052`–`N-063`, `TEAM_INFO.txt` |
| User workstations | No compromise evidenced. 9 isolated `AUTH_FAIL` events over ~7.5h, no follow-on success. | `auth_idp.log` |
| `labsrv` (isolated lab) | No activity. Not part of this incident. | — |

---

## 2. What has already happened

Condensed to the events that produce the current state. All times UTC; the endpoint log was converted
from `+03:00` before comparison.

| Time | Event | Evidence |
|---|---|---|
| `12-13T20:52:00Z` | `jump` EDR stops reporting — telemetry blind spot opens | `E-007` |
| `12-13T22:17Z` | Last good full backup begins (227.6 GB, SUCCESS, ends ~`22:58Z`) — this is the newest known-good copy | `backup_report.txt` |
| `12-14T01:13:01Z` | `203.0.113.226` reaches `idp:443` from the internet | `N-048` |
| `01:15:15Z` | `/oauth/introspect` returns 200 with 15,198 bytes, flagged `response_larger_than_normal` | `P-027` |
| `01:17:31Z` | **Session created for `svc.sso` with `no_credential_presented`** — 4m30s after first contact | `A-038` |
| `01:55:47Z` | `adm.lina` logs into `jump` from `idp`, `mfa=not_required`, `path=service_trust_rule` | `A-047`, `N-067` |
| `01:59:19Z` | SOC alert `SA-9458` raised, then **auto-closed** as "known maintenance pattern" | `P-033` |
| `02:19:48Z` / `02:24:31Z` / `02:31:06Z` | `adm.lina` logs into `files`, `exam-db`, `backup` from `jump`, `mfa=not_required` | `A-052`, `A-054`, `A-059` |
| `02:29:31Z` | **4,688,452,260 bytes (4.69 GB) leave `files` for `192.0.2.190:443`** | `N-074` |
| `03:01:24Z` | `backup-agent` stopped; 24 snapshots purged | `E-043`, `E-044` |
| `03:26:28Z`–`03:28:55Z` | Encryption: 70,700 files on `files`, 395 on `exam-db`, ransom note dropped | `E-048`–`E-053` |
| `03:27:30Z` | EDR `CS-207` critical — `action=detected_only`. First true detection, **+2h14m29s** | `E-050` |
| `03:39:54Z` | `exam-app` loses the exam-materials mount | `P-042` |
| `03:53:30Z` | `IR-911` declared, scope `files,jump,backup` | `P-043` |
| `04:05:30Z` | **Snapshot. Last log line is a request for advice; no containment action appears in any file.** | `P-044` |

---

## 3. What is established, and what is not

### Confirmed by evidence

- The entry point was the internet-facing identity service, and it produced a session with no
  credential presented (`A-038`) — i.e. authentication was not the gate that stopped anyone.
- Four privileged logins by `adm.lina` ran with `mfa=not_required` over trust rules
  (`A-047`, `A-052`, `A-054`, `A-059`). MFA is documented as deployed for all users (`TEAM_INFO.txt`).
- **4.69 GB left the Servers zone** to an external address before encryption began (`N-074`).
- **Recovery was destroyed before impact:** 24 snapshots purged at `03:01:42Z`, encryption started
  `03:26:28Z` — the two are 24m46s apart and ordered.
- **71,095 files** were renamed to `.t01lck` on two hosts (`E-048`–`E-053`).
- The declared incident scope (`files, jump, backup`) **does not include `exam-db`, which was also
  encrypted** (`E-053`), nor `idp`, which was the entry point (`P-043` vs `A-038`).

### Not established — open as of this snapshot

| Question | Why it is still open |
|---|---|
| Were `idp`'s token-signing keys or secrets taken during the `01:15:15Z` response? | Only the abnormal response size is logged (`P-027`); content is not. Affects whether any session is trustworthy. |
| Is `jump` still under attacker control? | Its EDR has been dark 7h13m (`E-007`) and there is no host telemetry after `01:55:47Z`. |
| What exactly was in the 4.69 GB? | Volume is known (`N-074`), content is not. Exam materials and staff shares are on that host (`TEAM_INFO.txt`). |
| Was `adm.lina` a stolen credential or an insider? | The account behaved outside both approved change windows, but the pack does not establish who held it. |
| Is there persistence on `idp`, `exam-db`, or `backup`? | `idp` EDR scans report `clean` (`E-013`, `E-024`, `E-054`); web-layer and database-level persistence would not appear there. |
| Is the `13 Dec 22:58Z` backup restorable? | Repository reports 0 snapshots and the same credential family reached the console (`backup_report.txt`, `F5`). |
| Is containment under way outside the logs? | Nothing in the pack shows it (`P-044` is the last line). Absence of evidence, not evidence of absence. |

---

## 4. Response posture at this moment

- **Declared:** yes, `IR-911`, critical, at `03:53:30Z` — **2h40m29s** after first contact.
- **Contained:** not evidenced anywhere in the pack.
- **Eradicated:** not evidenced.
- **Recovered:** no. `files` is encrypted and the exam application cannot read its materials.
- **Detection quality:** one true positive was raised and automatically closed (`P-033`); the destructive
  phase was detected by an EDR rule configured to `detected_only` (`E-050`).
- **Time to first true signal:** 2h14m29s. **Time to declaration:** 2h40m29s. **Time to containment:** unknown.

---

## 5. Recovery capability as it currently stands

These are properties of the environment, not of the incident.

| Item | Current value |
|---|---|
| Newest known-good full backup | `2026-12-13T22:17Z`, 227.6 GB, SUCCESS (`backup_report.txt`) |
| Local repository snapshots | **0** — 24 purged at `03:01:42Z` (`E-044`) |
| Offline copy | `tape-04`, `2026-12-11T23:00:00Z` (`backup_report.txt`) |
| Last restore test | `2026-10-18T09:00:00Z` — **FAILED**, stopped at step 2 of 6 after 11h18m |
| Reason it failed | `backup vault key not found at \files\ops\vault\` — that path sits on the encrypted file server |
| Documented restore success rate | Dashboard says 1 of 3; the report contains no passing test |
| Data-loss window, if repository were usable | 4h28m28s (`22:58:00Z` → `03:26:28Z`) |
| Data-loss window, if only `tape-04` is usable | 52h26m28s (`12-11T23:00Z` → `12-14T03:26:28Z`) |
| Measured RTO | **None exists.** No restore has completed, so no RTO has ever been observed |

---

## 6. Telemetry gaps that limit this report

- `jump` EDR: dark 7h13m at snapshot time (`E-007`) — the host where the pivot happened.
- Vulnerability scanning: dashboard reports 100% completion for "User, Servers and DMZ" only
  (`assurance_dashboard.txt`). The **Admin zone is unscanned**, and that is where `jump` and `backup` sit.
- `idp` host scans are clean while the host was compromised at the web layer — clean scans do not clear it.
- No log in the pack records what the attacker did *inside* `jump` between `01:55:47Z` and `03:01:24Z`.

---

## 7. Bottom line

As of `2026-12-14T04:05:30Z`: an external party entered through the identity service, moved to the jump
host without MFA, took 4.69 GB off the file server, destroyed 24 backup snapshots, and encrypted
71,095 files across two servers. The incident is declared but not contained. The file server is
unusable, the exam application is degraded, the jump host is unobservable, and the only recovery copy
that is not on the compromised network is 52 hours old. The next exam session starts in 3h24m.

---

## 8. Verifying this report

Only PowerShell needed; run from the repository root.

```powershell
# Files encrypted (expect 71095)
(Select-String endpoint_edr.log -Pattern 'FILE_RENAME_BURST count=(\d+)' |
  ForEach-Object { [int]$_.Matches[0].Groups[1].Value } | Measure-Object -Sum).Sum

# Privileged logins that skipped MFA (expect 4, all adm.lina)
Select-String auth_idp.log -Pattern 'mfa=not_required'

# Exfiltration record (expect 4688452260 bytes)
Select-String network_fw_dns.log -Pattern 'dst=192\.0\.2\.190'

# Data-loss window from last good backup to encryption (expect 0.04:28:28)
(([datetimeoffset]'2026-12-14T03:26:28Z') - ([datetimeoffset]'2026-12-13T22:58:00Z')).ToString('d\.hh\:mm\:ss')
```

---

## 9. Provenance

Evidence pack: 10 files in the repository root (`findings.csv`, `auth_idp.log`, `endpoint_edr.log`,
`network_fw_dns.log`, `app_audit.log`, `change_calendar.csv`, `backup_report.txt`,
`recovery_dependencies.csv`, `exam_schedule.csv`, `assurance_dashboard.txt`). All synthetic —
case study designed and prepared by **Dr. Mohammed Jubur**, Jazan University, CNET 463. Team T01.
Licence: [`LICENSE`](LICENSE).

`ANALYSIS.md` holds the separate Part A–E work (exposure ranking, control-effectiveness review). This
README deliberately contains no recommendations — it is the state of play only.
