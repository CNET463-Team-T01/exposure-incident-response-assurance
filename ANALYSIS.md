# Working analysis (Parts A–E)

> **Not the status report.** For the current state of the incident see [`README.md`](README.md).
> This file holds the deeper Part A–E reasoning: exposure ranking, response decisions, RTO/RPO
> derivation, and the critique of the management dashboard. It contains recommendations; the README does not.

# Original description

Prioritising exploitable exposure, reconstructing the attack path from multi-source logs, running
incident response and backup recovery (RTO/RPO), and proving control effectiveness with security
metrics — built on a synthetic evidence pack.

| | |
|---|---|
| Case | CNET 463 — Case Study 3 (synthetic evidence pack) |
| Team | T01 — org tag `t01`, domain `t01.uni.lab`, network `10.170.0.0/16` |
| Analysis cutoff ("now") | `2026-12-14T04:05:30Z` — no log line in any file is later |
| Machine-readable evidence | 10 files in the repository root (see §2) |
| Status | Analysis complete for Parts A–E; write-ups and tooling in progress (see §10) |

> This repository is a **documentation-first case study**. The evidence pack is fixed input; every
> conclusion below cites an evidence id (`A-###`, `E-###`, `N-###`, `P-###`) or a file row. Nothing is
> asserted without a pointer the reader can re-check.

---

## 1. What this repository is (and is not)

It is an incident-response and assurance workbench for **one** security event on a small university
network: a student examination system whose file server was exfiltrated and encrypted, whose backup
retention was deliberately destroyed, and whose identity service was the entry point.

It is **not** a live detection system, a scanner, or a SIEM connector. There is no agent, no API key,
and no runtime dependency. Anyone with the ten files and a PowerShell prompt can reproduce every
number in this README.

The core discipline the pack rewards, and the one this document is organised around:

1. **Evidence beats severity.** The exploited vulnerability has the *lowest* CVSS score of the eight
   findings (F4, 5.5). Ranking by CVSS alone gets the response order wrong.
2. **Time is not free.** The only log written in local time (`+03:00`) is the endpoint log. Comparing
   it raw against UTC logs silently shifts the whole attack two hours earlier and destroys the
   causality chain.
3. **Authorised activity looks like an attack.** An approved scanner swept six hosts at
   `01:28:00Z`, and two approved change windows opened on the jump host. Both are noise here.
4. **A backup job that succeeds is not a backup that restores.** The dashboard reports 100% job
   success beside 1-of-3 restore-test success. Part D exists because those two numbers are different
   claims.

---

## 2. Evidence pack

| File | Contains | Ids | Timestamp format |
|---|---|---|---|
| `findings.csv` | 8 vulnerability findings with CVSS, KEV, EPSS, reachability | `F1`–`F8` | n/a |
| `auth_idp.log` | Identity, SSO and privileged-login events | `A-001`–`A-072` | UTC (`Z`) |
| `endpoint_edr.log` | EDR heartbeats, scans, file-activity and service events | `E-001`–`E-058` | **local `+03:00`** |
| `network_fw_dns.log` | Firewall accepts/drops and DNS queries | `N-001`–`N-089` | UTC (`Z`) |
| `app_audit.log` | Web/application access, SOC alerts, change board | `P-001`–`P-044` | UTC (`Z`) |
| `change_calendar.csv` | 2 approved change windows | `CHG-9865`, `CHG-5871` | UTC (`Z`) |
| `backup_report.txt` | 7 nightly jobs, offline copy, repository state, restore tests | n/a | UTC (`Z`) |
| `recovery_dependencies.csv` | Service dependency and recovery order | n/a | n/a |
| `exam_schedule.csv` | 7 examination sessions | `D-1`…`D+2` | UTC (`Z`) |
| `assurance_dashboard.txt` | Management metrics, week ending `2026-12-13` | n/a | n/a |

**Hosts in scope:** `idp` (identity, DMZ, High), `exam-app` (DMZ, High), `exam-db` (Servers, High),
`files` (Servers, Medium), `backup` (Servers, High), `jump` (Admin, High), `soc-scan` (Admin, Low),
`adm-ws` (Admin, Medium), `labsrv` (isolated lab, Low).

---

## 3. Headline findings

| # | Finding | Evidence |
|---|---|---|
| 1 | The identity service was compromised **from the internet in 4.5 minutes** — injection-style probing of `/oauth/introspect`, a 15 KB abnormal response, then a session created with **no credential presented**. | `N-048`, `P-021`–`P-027`, `A-038` |
| 2 | The attacker entered the **jump host as `adm.lina` with `mfa=not_required`** over a `service_trust_rule` that trusts the identity server as a source. | `A-047`, `N-067` |
| 3 | That jump-host login raised a SOC alert which **auto-closed as "known maintenance"** — while the only approved change that day belonged to a *different* account (`adm.rakan`). | `P-033`, `change_calendar.csv` |
| 4 | **4.69 GB left the Servers zone to `192.0.2.190:443`** from the file server before any encryption. | `N-074` |
| 5 | **24 backup snapshots were purged** (`snapshot-purge --all`) 25 minutes before encryption started — recovery was targeted deliberately, not damaged incidentally. | `E-043`, `E-044` |
| 6 | **71,095 files renamed** to `.t01lck` across `files` and `exam-db`; a ransom note was dropped; the EDR alert fired as `action=detected_only`. | `E-048`–`E-053` |
| 7 | The exam application was already failing at `03:39:54Z` — 69 requests failed on the `/mnt/files/exam-materials` mount. **The next session starts `07:30Z` with ~600 students.** | `P-042`, `exam_schedule.csv` |
| 8 | The jump host's EDR had been **not reporting since `2026-12-13T20:52:00Z`**, 4h21m before the intrusion — so the pivot and the privilege escalation have no host telemetry. | `E-007` |

---

## 4. Part A — prioritised exposure

### 4.1 Ranking rule

CVSS is used last. The queue is ordered by:

1. **Confirmed attacker activity** on or through the asset (outranks every theoretical finding).
2. **Known-exploited + high EPSS** (KEV `Y`, EPSS ≥ 0.40) combined with real reachability.
3. **Business criticality and blast radius** at the current date — the exam timetable is live.
4. **Existing control quality** (a control that has already been bypassed counts for zero).
5. CVSS 9.x on an asset with no route is demoted, not promoted.

### 4.2 The queue

| Rank | Finding | Asset | Why it sits here | Decision |
|---|---|---|---|---|
| 1 | **F4** session-validation flaw, 5.5, KEV, EPSS 0.83 | `idp` | Internet-facing, no privilege needed, **confirmed exploited** (`N-048`, `A-038`). A forgeable session defeats MFA for everything behind it. | Virtual patch + WAF rule now; **rotate token-signing keys**, not just passwords |
| 2 | **F2** auth bypass, 8.7, KEV, EPSS 0.49 | `files` | Reachable from User *and* Admin zones, no privilege needed, and `files` is the confirmed exfiltration and encryption target (`N-074`, `E-048`). | Patch or virtual patch; disable anonymous/legacy auth; audit all share ACLs |
| 3 | **F6** RDP gateway privesc, 8.2, Low priv, EPSS 0.29 | `jump` | "Admin zone, **plus trusted server sources**" is exactly the `service_trust_rule` path used in `A-047`. Combined with the EDR blind spot (`E-007`), this host is a trusted foothold. | **Delete `service_trust_rule`**; require MFA from every source; rebuild `jump` from clean media |
| 4 | **F5** backup console credential exposure, 7.4, EPSS 0.11 | `backup` | Low EPSS but confirmed destructive stage: `adm.lina` reached `backup` (`A-059`), then the agent was stopped and 24 snapshots purged (`E-043`, `E-044`). "Console shares admin credentials" is why one credential opened everything. | Break the shared credential family; separate backup-admin account with MFA; immutable/air-gapped repository |
| 5 | **F1** browser memory corruption, 8.6, KEV, EPSS 0.40 | 300 user workstations | KEV, needs user interaction, EDR already present. No compromise evidence — hence rank 5, not 1. | Emergency patch; verify EDR actually blocks the exploit rather than logs it |
| 6 | **F8** template injection, 7.3, EPSS 0.34 | `exam-app` | Authenticated, mitigated by PEP+WAF, no exploitation evidence. Ranked here only because it is the student-facing service during an active exam week. | Virtual patch before the service is declared restored |
| 7 | **F7** printer firmware command injection, 9.6 | 13 printers | CVSS 9.6 but an isolated VLAN, no sensitive data, EPSS 0.07. Blast radius is the reason it is last. | Schedule; no incident capacity that competes with the exam |
| 8 | **F3** teaching-lab RCE, 9.5 | `labsrv` | **CVSS 9.5, EPSS 0.06, "no route out".** The pack's clearest trap: critical score, no path. | Keep the zone isolation; **prevent** any new route from being added for convenience |

**Net position:** F3 and F7 are demoted on reachability and blast radius; F4 is promoted on evidence.
Two of the eight "open critical findings" (`assurance_dashboard.txt`) are not actionable this week,
while the one that was actually used scores 5.5. That gap is the finding, not the footnote.

---

## 5. Part B — reconstructed attack path

All times UTC. Endpoint timestamps converted from `+03:00` before comparison.

| Time (UTC) | Evidence | Event |
|---|---|---|
| `2026-12-13T20:15:00Z` | `P-001` | `CHG-9865` opens for `adm.rakan` on `jump` — legitimate, in window |
| `2026-12-13T20:52:00Z` | `E-007` | **`jump` EDR stops reporting** (`service_unreachable`) — blind spot established |
| `2026-12-13T22:17:00Z` | `backup_report.txt` | Last good full backup starts (`nightly-exam-services`, 227.6 GB, SUCCESS, ends ~`22:58Z`) |
| `2026-12-14T01:13:01Z` | `N-048` | **Initial access:** `203.0.113.226` → `idp:443` (2,050 bytes) |
| `01:13:01Z`–`01:14:24Z` | `P-021`–`P-024` | Probes on `/oauth/introspect`, `/oauth/token`, `/api/session` → `500` and `400` errors |
| `01:15:15Z` | `P-027` | `/oauth/introspect` → **200, 15,198 bytes, `response_larger_than_normal`** — exploit succeeds |
| `01:17:31Z` | `A-038` | **`SESSION_CREATE user=svc.sso src=203.0.113.226 method=none mfa=not_applicable note=no_credential_presented`** — session forgery, MFA bypassed at the session layer |
| `01:28:00Z`–`01:28:33Z` | `N-052`–`N-063` | Approved `soc-scan` sweep — **benign, excluded** |
| `01:55:45Z` | `N-067` | `10.170.10.10` → `10.170.40.20:3389` — the identity server is used as a trusted source |
| `01:55:47Z` | `A-047` | **Lateral movement:** `LOGIN_OK user=adm.lina dst=jump src=10.170.10.10 mfa=not_required path=service_trust_rule` |
| `01:59:19Z` | `P-033` | SOC alert `SA-9458 priv-login-from-server-source` → **`AUTO_CLOSED reason=matches_known_maintenance_pattern`** |
| `02:19:46Z`–`02:19:48Z` | `N-072`, `A-052` | `jump` → `files:445`, `adm.lina` login via `admin_trust_rule`, `mfa=not_required` |
| `02:24:29Z`–`02:24:31Z` | `N-073`, `A-054` | `jump` → `exam-db:5432`, `adm.lina` login via `admin_trust_rule` |
| `02:29:31Z` | `N-074` | **Exfiltration:** `10.170.30.15` → `192.0.2.190:443`, **4,688,452,260 bytes (4.69 GB / 4.37 GiB)** |
| `02:31:04Z`–`02:31:06Z` | `N-075`, `A-059` | `jump` → `backup:22`, `adm.lina` login via `admin_trust_rule` |
| `02:41:29Z` | `P-037` | `CHG-5871` opens for **`adm.rakan`** — the attacker's `adm.lina` sessions are outside it |
| `02:56:29Z` | `A-062` | `adm.rakan` logs into `jump` from `adm-ws`, `mfa=push_ok` — **legitimate, in window, excluded** |
| `03:01:24Z` | `E-043` | **`SERVICE_STOP name=backup-agent user=adm.lina`** |
| `03:01:42Z` | `E-044` | **`PROC_START cmd="snapshot-purge --all" snapshots_removed=24`** — recovery capability destroyed |
| `03:26:28Z` | `E-048` | Encryption begins on `files`, share `exam-materials` (1,585 renames) |
| `03:26:59Z`–`03:27:45Z` | `E-049`, `E-051` | 11,477 then 57,638 renames → **70,700 on `files`** |
| `03:27:30Z` | `E-050` | **EDR `CS-207` critical, `action=detected_only`** — first true detection signal, +2h14m29s |
| `03:28:01Z` | `E-052` | `README_RESTORE.txt` dropped — ransom note |
| `03:28:55Z` | `E-053` | `exam-db` encrypted, 395 renames — **71,095 files total** |
| `03:39:54Z` | `P-042` | `exam-app ERROR storage_unavailable mount=/mnt/files/exam-materials requests_failed=69` |
| `03:53:30Z` | `P-043` | **`INCIDENT_DECLARED id=IR-911 severity=critical scope=files,jump,backup`** — +2h40m29s |
| `04:05:30Z` | `P-044` | `ANALYSIS_REQUESTED` — **cutoff. No containment action is evidenced in any log.** |

**Chain in one line:** internet → F4 on `idp` → forged `svc.sso` session → `service_trust_rule` to
`jump` as `adm.lina` (EDR blind) → `admin_trust_rule` to `files`, `exam-db`, `backup` → 4.69 GB out →
snapshots purged → encrypt → ransom note → exam service degraded.

**Why this chain was possible at all.** Three independent controls failed *in series*, and each one
alone would have stopped it: (a) the idp trusted a forged session, (b) `jump` accepted privileged
logins with `mfa=not_required` from a server source, (c) the SOC automation closed that exact alert.
MFA is deployed and documented (`TEAM_INFO.txt`), yet **not one of the four `adm.lina` privileged
logins asked for it**.

---

## 6. Part C — incident response position

### 6.1 What the evidence says about the current state

- Contained: **not evidenced.** The last log line is a request for advice (`P-044`).
- Scope declared: `files`, `jump`, `backup` (`P-043`) — but `exam-db` was encrypted too (`E-053`)
  and `idp` was the entry point. **The declared scope understates the compromise.**
- Integrity of `jump` is unknown and unknowable from host telemetry: the agent was down for
  **7h13m** at the cutoff (`E-007` → `04:05:30Z`). Treat it as attacker-controlled.

### 6.2 Immediate actions, in order

| Priority | Action | Rationale |
|---|---|---|
| P0 | **Revoke all idp sessions and rotate the token-signing keys** | F4 let a session exist with no credential (`A-038`). Rotating passwords without rotating signing keys leaves forged sessions valid. |
| P0 | **Disable `adm.lina` and `svc.sso`; force re-auth for all admins** | Every privileged action in the chain used `adm.lina` (`A-047`, `A-052`, `A-054`, `A-059`). |
| P0 | **Isolate `files`, `exam-db`, `jump`, `backup` at the network layer** (VLAN ACL / firewall), not via EDR | EDR on `jump` is down; an EDR-issued quarantine would silently fail on the one host that matters. |
| P1 | **Delete `service_trust_rule`; require MFA from all sources** | Removes the pivot primitive for good, not just for this incident. |
| P1 | **Block `203.0.113.226` and `192.0.2.190` at the edge; deny Servers-zone egress** | 4.69 GB left from `10.170.30.15` (`N-074`). Egress from a server zone to the internet should not be a default-allowed path. |
| P1 | **Preserve evidence before rebuilding:** memory and disk images of `files`, `exam-db`, `jump`, `backup`; export `app_audit.log` and `auth_idp.log` | Credential rotation and rebuild both destroy forensic value. |
| P2 | **Do not communicate with the ransom note author**; retain `README_RESTORE.txt` (`E-052`) as evidence | Policy decision, recorded so it is a decision and not an omission. |
| P2 | **Check `idp` for persistence** — web shell, new admin account, modified auth config | Host EDR scans on `idp` returned `clean` three times (`E-013`, `E-024`, `E-054`). Clean host scans do **not** clear a web-layer compromise. |

### 6.3 The exam decision — the real constraint

The next session is `D morning`, `2026-12-14T07:30:00Z`, ~600 students (`exam_schedule.csv`), then
`10:00Z` with ~550. That is **3h24m30s** from the cutoff.

To run that session, the whole dependency chain must be up (`recovery_dependencies.csv`):
DNS → `idp` → {`exam-db`, `files`} → `exam-app`. The exam application already cannot read
`/mnt/files/exam-materials` (`P-042`), and `files` is the host with 70,700 encrypted files.

With **no documented passing restore test** — the only test in the report failed and the dashboard's
"1 of 3" has no recorded success behind it (Part D) — the honest planning
assumption is that `files` cannot be recovered and verified inside 3h24m. Realistic options, in order
of preference:

1. **Postpone or relocate the `07:30Z` and `10:00Z` sessions** and announce before `05:30Z` — about
   85 minutes from the cutoff, which is the latest point at which 600 students can be redirected.
2. **Restore `exam-app` + `exam-db` into an isolated clean segment** and serve exam materials from a
   verified pre-incident copy rather than the compromised share.
3. Run the exam on degraded/alternate delivery only if (1) and (2) fail — and state explicitly that
   results integrity is unproven.

Announcing at `07:25Z` is not a decision, it is a failure to decide.

---

## 7. Part D — backup and recovery (RTO/RPO)

### 7.1 What actually exists

| Fact | Value | Source |
|---|---|---|
| Last successful full backup | `2026-12-13T22:17:00Z` start, 41m, **227.6 GB**, exit 0 | `backup_report.txt` |
| Backup completion | ≈ `2026-12-13T22:58:00Z` | derived (start + duration) |
| Repository snapshots at report time | **0 (purged)** | `backup_report.txt` |
| Snapshots destroyed by attacker | **24** at `03:01:42Z` | `E-044` |
| Offline copy | `weekly-offline-copy`, **`2026-12-11T23:00:00Z`**, `tape-04` | `backup_report.txt` |
| Last restore test | `2026-10-18T09:00:00Z` — **FAILED after 11h18m**, step 2 of 6 | `backup_report.txt` |
| Cause of that failure | `backup vault key not found at \files\ops\vault\` | `backup_report.txt` |
| Restore tests, last 12 months | **1 of 3 succeeded** | `assurance_dashboard.txt` |

**These two sources disagree, and that matters.** The dashboard claims 1 of 3 restore tests succeeded;
the backup report records exactly one test, and it failed. No passing test exists in the pack. Until
the conflict is reconciled against the ticketing system, the pessimistic reading is the only defensible
one — a recovery capability that is asserted but not evidenced is indistinguishable from no capability.

### 7.2 RTO / RPO, stated honestly

| Recovery scenario | RPO | RTO | Verdict |
|---|---|---|---|
| **A. Local repository** (`nightly-exam-services`, `13 Dec 22:58Z`) | **4h28m28s** | Unknown — **not credible** | Snapshots 0, agent stopped, repository reachable with the same credential family the attacker held. Treat as untrusted. |
| **B. Offline tape `tape-04`** (`11 Dec 23:00Z`) | **52h26m28s** (2d 4h26m) | **≥ 8–12h**, and currently **blocked** | The vault key lives at `\files\ops\vault\` — the host now encrypted. The documented restore path cannot start without a key that the incident already destroyed. |
| **C. Rebuild from scratch** | Not applicable | **Days** | Only viable if B fails permanently. Requires clean media for four hosts plus re-enrolment. |

**Conclusion for Part D.** RTO cannot be quoted, because it has never been measured — the only
recorded attempt failed at step 2 of 6 and consumed 11h18m doing so. RPO degrades from 4h28m to
52h26m the moment the local repository is treated as untrusted, which it must be. The 100%
"backup job success" figure proves the backup *writer* worked; it says nothing about recovery, and
this incident is the proof that the distinction is not academic.

### 7.3 What must change (and it is not "take more backups")

1. **Immutable / air-gapped repository** with retention lock enforced **server-side** and credentials
   the admin console cannot use. "Retention lock configured" (`findings.csv` F5) did not survive an
   admin credential with snapshot-purge rights.
2. **Separate credential family for the backup console** — the report itself says the repository is
   reachable with "the same credential family as jump/files". One credential compromised all three.
3. **Move the vault key out of `\files\ops\vault\`** — off the file server, into a separate secret
   store, with a documented break-glass path.
4. **Restore test as a scheduled, gated operation** — quarterly, timed, with a recorded RTO, and
   blocked from being reported as "passed" unless the service actually serves traffic. A test that
   fails silently for 14 months is worse than no test, because it licenses a false claim.
5. **Report RPO and RTO in hours, per service**, in the same dashboard that reports job success.

---

## 8. Part E — control effectiveness (why the dashboard misleads)

The dashboard is not lying; it is measuring things that cannot fail. Each metric below is paired with
what it cannot prove and the evidence that the gap was already real.

| Dashboard claim | What it cannot prove | Evidence from this incident |
|---|---|---|
| Patch compliance **98.2%**, "all managed endpoints and servers" | That the **2 KEV findings on the exploited path** were closed, or that the Admin zone was in scope | `F4` and `F2` are KEV and both sit on the used path; `F4`, `F6`, `F5` are all reachable there; scans covered "User, Servers and DMZ" only — **Admin zone excluded** |
| Backup job success **100%** | That anything restores | 1-of-3 restore success; the last test failed at step 2 of 6 (`backup_report.txt`) |
| Alerts processed **4,376**, **74% auto-closed** | That auto-closure is *correct* | `SA-9458` auto-closed as "known maintenance" while the change belonged to a different account (`P-033`) — an unmeasured false negative |
| MTTA **8 min** | Time to **detect** or **contain** ("not reported") | Actual: first true signal at +2h14m29s, declaration at +2h40m29s, **no containment at +2h52m** (`E-050`, `P-043`, `P-044`) |
| Log sources **9 of 9 onboarded** | That each source is **live and complete** | `jump` EDR dark for 7h13m at the cutoff (`E-007`) — onboarded and useless on the one host that mattered |
| Vulnerability scans **100% completed** | Coverage outside the three named zones | Admin zone (`jump`, `backup`, `adm-ws`) unscanned — precisely where F5 and F6 live |
| Open critical findings **8** | Age, exploitability, or whether any are on a live path | F4 (5.5) was on the live path; F3 (9.5) has no route |

**Metrics that should replace them.** Detection coverage per log source (percent of expected events
received, per hour), MTTD/MTTC per severity, sampled QA of auto-closed alerts (target: reviewed
sample, measured error rate), restore success rate *with measured RTO*, percentage of KEV findings
closed within SLA on internet-reachable assets, and the share of privileged authentications that
required MFA — a number that was **0 of 4** for the privileged logins in this incident.

---

## 9. Triage hygiene — what was considered and excluded

Recording exclusions is part of the analysis, not an appendix to it.

| Event | Why it is not part of the incident |
|---|---|
| `N-052`–`N-063`, `01:28:00Z`–`01:28:33Z` | `soc-scan` `10.170.40.5` is the **approved** scanner (`TEAM_INFO.txt`); a 6-host, 33-second sweep on standard ports |
| `A-008`, `A-062` | `adm.rakan` on `jump` from `adm-ws` with `mfa=push_ok` — inside `CHG-9865` / `CHG-5871` |
| `A-003`, `A-021`, `A-030`, `A-034`, `A-035`, `A-045`, `A-051`, `A-064`, `A-065` | Nine scattered `AUTH_FAIL` (`bad_password`/`mfa_timeout`) from user workstations across ~7.5 hours, no follow-on success — user error, not brute force |
| `N-009`, `N-012`, `N-020`, `N-070`, `N-037` | `DROP … default_deny` toward `exam-db` on ports `22`, `3389`, `5432` — blocked lateral attempts, worth a rule review, not evidence of success |
| `N-010`, `N-019`, `N-028`, `N-031`, `N-036`, `N-043`, `N-086`, `N-088` | DNS for `time.pool.example`, `updates.vendor-a.example`, `mirror.vendor-b.example` — routine update/time traffic |
| `E-013`, `E-024`, `E-054` | `SCAN_COMPLETE result=clean` on `idp` — **not** exculpatory; F4 is a web-layer flaw with no host artefact |

**On the `.t01lck` extension:** it is a team-specific marker, consistent with a synthetic pack. In a
real case, the extension is an actor indicator to pivot on; here it is a data label. Either way, the
counts (70,700 + 395) are the impact number.

---

## 10. Repository status and roadmap

| Part | Status | Where it lives |
|---|---|---|
| A — exposure prioritisation | Done | §4 |
| B — attack-path reconstruction | Done | §5 |
| C — incident response | Position + decisions done; execution not evidenced | §6 |
| D — backup/recovery RTO-RPO | Done | §7 |
| E — control effectiveness | Done | §8 |
| Triage exclusions | Done | §9 |
| Tooling (timestamp normaliser, timeline builder) | **Not built** | Planned: `tools/` |
| Per-part long-form write-ups | **Not written** | Planned: `report/` |
| Figures (timeline, kill-chain, dependency graph) | **Not built** | Planned: `figures/` |

What this repository deliberately does **not** contain yet: parsers, tests, CI, or a dashboard. The
evidence pack is 10 static files; adding machinery before the analysis is stable would produce code
that encodes guesses. The reproduction steps in §11 are the honest tooling for now.

---

## 11. Reproducing the key numbers

Requires only PowerShell (tested on `pwsh` 7). Run from the repository root.

```powershell
# 1. Normalise the only non-UTC log (+03:00) and confirm the cutoff holds
Select-String endpoint_edr.log -Pattern '^(E-\d+) (\S+)' | ForEach-Object {
  $id, $ts = $_.Matches[0].Groups[1].Value, $_.Matches[0].Groups[2].Value
  '{0} {1}' -f $id, ([datetimeoffset]::Parse($ts)).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
}

# 2. Total files encrypted (expect 71095)
(Select-String endpoint_edr.log -Pattern 'FILE_RENAME_BURST count=(\d+)' |
  ForEach-Object { [int]$_.Matches[0].Groups[1].Value } | Measure-Object -Sum).Sum

# 3. Every privileged login that skipped MFA (expect 4, all adm.lina)
Select-String auth_idp.log -Pattern 'mfa=not_required'

# 4. Bytes exfiltrated (expect 4688452260)
Select-String network_fw_dns.log -Pattern 'dst=192\.0\.2\.190'

# 5. RPO if the local repository were trustworthy (expect 0.04:28:28)
(([datetimeoffset]'2026-12-14T03:26:28Z') - ([datetimeoffset]'2026-12-13T22:58:00Z')).ToString('d\.hh\:mm\:ss')
```

---

## 12. Assumptions and limitations

- **`203.0.113.226` and `192.0.2.190` are documentation ranges** (RFC 5737), as is the whole pack.
  The analysis treats them as the real external endpoint and exfiltration destination because that is
  what the logs assert; in production those addresses would be blocked and enriched, not assumed.
- **`E-007` is a status line, not a root cause.** Whether the `jump` agent died, was stopped, or was
  blocked is not in the pack. The analysis assumes the worst (compromised) because the host's
  integrity cannot be established, and says so rather than guessing.
- **How `A-038` becomes `A-047` is inferred, not proven.** The logs show a forged `svc.sso` session
  at `01:17:31Z` and a privileged `adm.lina` login at `01:55:47Z` over a trust rule, with no
  credential-based event between them. The defensible reading is that session validation on the
  identity service allowed the principal to be chosen. A host-based artefact would settle it — and
  the host with the artefact is the one with dark EDR.
- **RTO figures in §7.2 are estimates** and labelled as such. No restore has completed, so no RTO
  has been observed. Presenting a precise RTO would be fabrication.
- **`snapshots listed: 0` does not prove every backup is unrecoverable** — it proves point-in-time
  recovery is unavailable and that the repository cannot be trusted. §7.2 is written as a risk
  judgement, not a certainty.
- **The analysis cutoff is `04:05:30Z`.** Anything after it is a recommendation, not an observation.

---

## 13. Attribution and licence

Case study designed and prepared by **Dr. Mohammed Jubur**, Jazan University — CNET 463.
All data in the evidence pack is synthetic; no real institution, person, or network is represented.
Team attribution: **T01** (`t01.uni.lab`). See `TEAM_INFO.txt` for the authoritative pack description.

Licence: see [`LICENSE`](LICENSE).
