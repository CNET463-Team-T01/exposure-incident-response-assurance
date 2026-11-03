# exposure-incident-response-assurance

Prioritising exploitable exposure, reconstructing the attack path from multi-source logs, running
incident response and backup recovery (RTO/RPO), and proving control effectiveness — built on a
synthetic evidence pack.

The document has one job: state what the logs prove, in an order a reader can audit. §1 is the
situation as it stands; §2–§6 are the five parts of the analysis (A–E); §9 is how the work is split
across five people. Every claim carries an evidence id (`A-###`, `E-###`, `N-###`, `P-###`) or a file
row, so nothing has to be taken on trust.

| | |
|---|---|
| Case | CNET 463 — Case Study 3 (synthetic evidence pack) |
| Team / domain / network | T01 — `t01.uni.lab` — `10.170.0.0/16` |
| Snapshot time ("now") | `2026-12-14T04:05:30Z` — no line in any file is later |
| Incident | `IR-911`, declared `critical` at `03:53:30Z` (12 min before the snapshot) |
| Declared scope | `files`, `jump`, `backup` (`P-043`) |
| Next deadline | Exam session `D morning` at `07:30Z`, ~600 students — **3h24m30s from the snapshot** |

**Evidence pack (10 files, all synthetic):** `findings.csv` (`F1`–`F8`), `auth_idp.log` (`A-001`–`A-072`),
`endpoint_edr.log` (`E-001`–`E-058`, **local `+03:00`**), `network_fw_dns.log` (`N-001`–`N-089`),
`app_audit.log` (`P-001`–`P-044`), `change_calendar.csv`, `backup_report.txt`,
`recovery_dependencies.csv`, `exam_schedule.csv`, `assurance_dashboard.txt`.

---

## 1. Situation at `2026-12-14T04:05:30Z`

| Asset | State | Basis |
|---|---|---|
| `files` (10.170.30.15) | **Encrypted.** ~70,700 files renamed to `.t01lck` in share `exam-materials`; ransom note `README_RESTORE.txt` present. EDR agent still reporting normally. | `E-048`, `E-049`, `E-051`, `E-052`, `E-058` |
| `exam-db` (10.170.30.10) | **Partially encrypted.** 395 renames in volume `db-data`. Heartbeats OK; logical integrity of the database is unknown. | `E-053`, `E-057` |
| `exam-app` (10.170.10.20) | **Running but impaired.** 69 requests failed on mount `/mnt/files/exam-materials` at `03:39:54Z`. | `P-042`, `E-056` |
| `idp` (10.170.10.10) | **Running and still issuing tokens** (`04:02:09Z`). Also the confirmed entry point. Three EDR scans returned `clean`. | `A-072`, `E-055`, `E-013`, `E-024`, `E-054` |
| `jump` (10.170.40.20) | **Unknown — no telemetry.** EDR silent since `2026-12-13T20:52:00Z` (7h13m). Treat as attacker-controlled. | `E-007` |
| `backup` (10.170.30.30) | **Backup service stopped** at `03:01:24Z`; 24 snapshots purged at `03:01:42Z`. Repository lists **0 snapshots**. The EDR agent still reports — different process, not the backup service. | `E-043`, `E-044`, `E-047`, `backup_report.txt` |
| `soc-scan` (10.170.40.5) | Normal. Its `01:28Z` sweep was authorised. | `N-052`–`N-063`, `TEAM_INFO.txt` |
| User workstations | No compromise evidenced. 9 isolated `AUTH_FAIL` events over ~7.5h, no follow-on success. | `auth_idp.log` |
| `labsrv` (isolated lab) | No activity. Not part of this incident. | — |

**Bottom line.** An external party entered through the identity service, moved to the jump host without
MFA, took 4.69 GB off the file server, destroyed 24 backup snapshots, and encrypted 71,095 files across
two servers. The incident is declared but not contained. The file server is unusable, the exam
application is degraded, the jump host is unobservable, and the only recovery copy that is not on the
compromised network is 52 hours old. The next exam session starts in 3h24m.

---

## 2. Part A — exposure prioritisation

## 2.1 Ranking rule

CVSS is used last. The queue is ordered by:

1. **Confirmed attacker activity** on or through the asset (outranks every theoretical finding).
2. **Known-exploited + high EPSS** (KEV `Y`, EPSS ≥ 0.40) combined with real reachability.
3. **Business criticality and blast radius at the current date** — the exam timetable is live.
4. **Existing control quality** (a control already bypassed counts for zero).
5. CVSS 9.x on an asset with no route is demoted, not promoted.

## 2.2 The queue

| Rank | Finding | Asset | Why it sits here | Decision |
|---|---|---|---|---|
| 1 | **F4** session-validation flaw, 5.5, KEV, EPSS 0.83 | `idp` | Internet-facing, no privilege needed, **confirmed exploited** (`N-048`, `A-038`). A forgeable session defeats MFA for everything behind it. | Virtual patch + WAF rule now; **rotate token-signing keys**, not just passwords |
| 2 | **F2** auth bypass, 8.7, KEV, EPSS 0.49 | `files` | Reachable from User *and* Admin zones, no privilege needed; `files` is the confirmed exfiltration and encryption target (`N-074`, `E-048`). | Patch or virtual patch; disable anonymous/legacy auth; audit share ACLs |
| 3 | **F6** RDP gateway privesc, 8.2, Low priv, EPSS 0.29 | `jump` | "Admin zone, **plus trusted server sources**" is exactly the `service_trust_rule` path used in `A-047`. Combined with the EDR blind spot (`E-007`), this host is a trusted foothold. | **Delete `service_trust_rule`**; require MFA from every source; rebuild `jump` from clean media |
| 4 | **F5** backup console credential exposure, 7.4, EPSS 0.11 | `backup` | Low EPSS but confirmed destructive stage: `adm.lina` reached `backup` (`A-059`), then the agent was stopped and 24 snapshots purged (`E-043`, `E-044`). "Console shares admin credentials" is why one credential opened everything. | Break the shared credential family; separate backup-admin account with MFA; immutable/air-gapped repository |
| 5 | **F1** browser memory corruption, 8.6, KEV, EPSS 0.40 | 300 user workstations | KEV, needs user interaction, EDR already present. No compromise evidence — hence rank 5, not 1. | Emergency patch; verify EDR actually blocks the exploit rather than logs it |
| 6 | **F8** template injection, 7.3, EPSS 0.34 | `exam-app` | Authenticated, mitigated by PEP+WAF, no exploitation evidence. Ranked here only because it is the student-facing service during an active exam week. | Virtual patch before the service is declared restored |
| 7 | **F7** printer firmware command injection, 9.6 | 13 printers | CVSS 9.6 but an isolated VLAN, no sensitive data, EPSS 0.07. Blast radius is why it is last. | Schedule; no incident capacity that competes with the exam |
| 8 | **F3** teaching-lab RCE, 9.5 | `labsrv` | **CVSS 9.5, EPSS 0.06, "no route out".** The pack's clearest trap: critical score, no path. | Keep the zone isolation; **prevent** any new route being added for convenience |

**Net position.** F3 and F7 are demoted on reachability and blast radius; F4 is promoted on evidence.
Two of the eight "open critical findings" (`assurance_dashboard.txt`) are not actionable this week,
while the one actually used scores 5.5. **The exploited vulnerability has the lowest CVSS of the
eight.** That gap is the finding, not the footnote.

---

## 3. Part B — reconstructed attack path

All times UTC. The endpoint log is written in `+03:00` and was converted before any comparison —
comparing it raw shifts the attack two hours earlier and breaks the chain.

## 3.1 Headline findings

| # | Finding | Evidence |
|---|---|---|
| 1 | The identity service was compromised **from the internet in 4.5 minutes** — injection-style probing of `/oauth/introspect`, a 15 KB abnormal response, then a session created with **no credential presented**. | `N-048`, `P-021`–`P-027`, `A-038` |
| 2 | The attacker entered the **jump host as `adm.lina` with `mfa=not_required`** over a `service_trust_rule` that trusts the identity server as a source. | `A-047`, `N-067` |
| 3 | That jump-host login raised a SOC alert which **auto-closed as "known maintenance"** — while the only approved change that day belonged to a *different* account (`adm.rakan`). | `P-033`, `change_calendar.csv` |
| 4 | **4.69 GB left the Servers zone to `192.0.2.190:443`** from the file server before any encryption. | `N-074` |
| 5 | **24 backup snapshots were purged** (`snapshot-purge --all`) 24m46s before encryption started — recovery was targeted deliberately, not damaged incidentally. | `E-043`, `E-044` |
| 6 | **71,095 files renamed** to `.t01lck` across `files` and `exam-db`; a ransom note was dropped; the EDR alert fired as `action=detected_only`. | `E-048`–`E-053` |
| 7 | The exam application was already failing at `03:39:54Z` — 69 failed requests on `/mnt/files/exam-materials`. **The next session starts `07:30Z` with ~600 students.** | `P-042`, `exam_schedule.csv` |
| 8 | The jump host's EDR had been **not reporting since `2026-12-13T20:52:00Z`**, 4h21m before the intrusion — the pivot and privilege escalation have no host telemetry. | `E-007` |

## 3.2 Timeline

| Time (UTC) | Evidence | Event |
|---|---|---|
| `12-13T20:15:00Z` | `P-001` | `CHG-9865` opens for `adm.rakan` on `jump` — legitimate, in window |
| `12-13T20:52:00Z` | `E-007` | **`jump` EDR stops reporting** (`service_unreachable`) — blind spot established |
| `12-13T22:17:00Z` | `backup_report.txt` | Last good full backup starts (`nightly-exam-services`, 227.6 GB, SUCCESS, ends ~`22:58Z`) |
| `12-14T01:13:01Z` | `N-048` | **Initial access:** `203.0.113.226` → `idp:443` (2,050 bytes) |
| `01:13:01Z`–`01:14:24Z` | `P-021`–`P-024` | Probes on `/oauth/introspect`, `/oauth/token`, `/api/session` → `500` and `400` errors |
| `01:15:15Z` | `P-027` | `/oauth/introspect` → **200, 15,198 bytes, `response_larger_than_normal`** — exploit succeeds |
| `01:17:31Z` | `A-038` | **`SESSION_CREATE user=svc.sso src=203.0.113.226 method=none mfa=not_applicable note=no_credential_presented`** — session forgery, MFA bypassed at the session layer |
| `01:28:00Z`–`01:28:33Z` | `N-052`–`N-063` | Approved `soc-scan` sweep of 6 hosts — **benign, excluded** |
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
| `04:05:30Z` | `P-044` | `ANALYSIS_REQUESTED` — **snapshot. No containment action is evidenced in any log.** |

## 3.3 The chain, and why it held

**Chain:** internet → F4 on `idp` → forged `svc.sso` session → `service_trust_rule` to `jump` as
`adm.lina` (EDR blind) → `admin_trust_rule` to `files`, `exam-db`, `backup` → 4.69 GB out → snapshots
purged → encrypt → ransom note → exam service degraded.

**Three independent controls failed in series**, any one of which alone would have stopped it:
(a) the identity service trusted a forged session, (b) `jump` accepted privileged logins with
`mfa=not_required` from a server source, (c) the SOC automation closed that exact alert. MFA is
deployed and documented (`TEAM_INFO.txt`), yet **not one of the four `adm.lina` privileged logins
asked for it**.

---

## 4. Part C — incident response

## 4.1 Where the response stands

| Question | Answer | Basis |
|---|---|---|
| Declared? | **Yes** — `IR-911`, critical, at `03:53:30Z`, **2h40m29s** after first contact | `P-043` |
| Contained? | **Not evidenced anywhere in the pack** | `P-044` is the last line |
| Eradicated? | **Not evidenced** | — |
| Recovered? | **No.** `files` encrypted; `exam-app` cannot read its materials | `E-048`, `P-042` |
| Scope correct? | **No.** Declared `files, jump, backup` — but `exam-db` was encrypted too, and `idp` was the entry point | `P-043` vs `E-053`, `A-038` |
| Detection quality | One true positive raised then auto-closed; destructive phase caught by a rule set to `detected_only` | `P-033`, `E-050` |
| Time to first true signal | **2h14m29s** | `01:13:01Z` → `03:27:30Z` |
| Time to declaration | **2h40m29s** | `01:13:01Z` → `03:53:30Z` |
| Time to containment | **Unknown** | not in any log |

## 4.2 Immediate actions, in order

| Priority | Action | Rationale |
|---|---|---|
| P0 | **Revoke all idp sessions and rotate the token-signing keys** | F4 let a session exist with no credential (`A-038`). Rotating passwords without rotating signing keys leaves forged sessions valid. |
| P0 | **Disable `adm.lina` and `svc.sso`; force re-auth for all admins** | Every privileged action in the chain used `adm.lina` (`A-047`, `A-052`, `A-054`, `A-059`). |
| P0 | **Isolate `files`, `exam-db`, `jump`, `backup` at the network layer** (VLAN ACL / firewall), not via EDR | EDR on `jump` is down; an EDR-issued quarantine would silently fail on the one host that matters. |
| P1 | **Delete `service_trust_rule`; require MFA from all sources** | Removes the pivot primitive for good, not just for this incident. |
| P1 | **Block `203.0.113.226` and `192.0.2.190` at the edge; deny Servers-zone egress** | 4.69 GB left from `10.170.30.15` (`N-074`). Server-zone egress to the internet should not be a default-allowed path. |
| P1 | **Preserve evidence before rebuilding:** memory and disk images of `files`, `exam-db`, `jump`, `backup`; export `app_audit.log`, `auth_idp.log` | Credential rotation and rebuild both destroy forensic value. |
| P2 | **Do not communicate with the ransom note author**; retain `README_RESTORE.txt` (`E-052`) as evidence | Recorded as a decision, not an omission. |
| P2 | **Check `idp` for persistence** — web shell, new admin account, modified auth config | Host scans on `idp` returned `clean` three times (`E-013`, `E-024`, `E-054`). Clean host scans do **not** clear a web-layer compromise. |

## 4.3 The exam decision

Next session `D morning` at `2026-12-14T07:30:00Z`, ~600 students, then `10:00Z` with ~550 — **3h24m30s**
away.

The full dependency chain must be up (`recovery_dependencies.csv`): DNS → `idp` → {`exam-db`, `files`} →
`exam-app`. The exam application already cannot read `/mnt/files/exam-materials` (`P-042`), and `files`
is the host with 70,700 encrypted files.

With **no documented passing restore test** — the only test in the report failed and the dashboard's
"1 of 3" has no recorded success behind it — the planning assumption is that `files` cannot be
recovered and verified inside 3h24m. Options, in order of preference:

1. **Postpone or relocate the `07:30Z` and `10:00Z` sessions** and announce before `05:30Z` — about
   85 minutes from the snapshot, the latest point at which 600 students can be redirected.
2. **Restore `exam-app` + `exam-db` into an isolated clean segment** and serve exam materials from a
   verified pre-incident copy rather than the compromised share.
3. Run on degraded/alternate delivery only if (1) and (2) fail — and state explicitly that results
   integrity is unproven.

Announcing at `07:25Z` is not a decision, it is a failure to decide.

---

## 5. Part D — backup and recovery (RTO/RPO)

## 5.1 What actually exists

| Fact | Value | Source |
|---|---|---|
| Last successful full backup | `2026-12-13T22:17:00Z` start, 41m, **227.6 GB**, exit 0 | `backup_report.txt` |
| Backup completion | ≈ `2026-12-13T22:58:00Z` | derived (start + duration) |
| Repository snapshots at report time | **0 (purged)** | `backup_report.txt` |
| Snapshots destroyed by attacker | **24** at `03:01:42Z` | `E-044` |
| Offline copy | `weekly-offline-copy`, **`2026-12-11T23:00:00Z`**, `tape-04` | `backup_report.txt` |
| Last restore test | `2026-10-18T09:00:00Z` — **FAILED after 11h18m**, stopped at step 2 of 6 | `backup_report.txt` |
| Cause of that failure | `backup vault key not found at \files\ops\vault\` | `backup_report.txt` |
| Restore tests, last 12 months | **1 of 3 succeeded** | `assurance_dashboard.txt` |

**These two sources disagree, and that matters.** The dashboard claims 1 of 3 restore tests succeeded;
the backup report records exactly one test, and it failed. No passing test exists in the pack. Until
the conflict is reconciled against the ticketing system, the pessimistic reading is the only defensible
one — a recovery capability that is asserted but not evidenced is indistinguishable from no capability.

## 5.2 RTO / RPO, stated honestly

| Recovery scenario | RPO | RTO | Verdict |
|---|---|---|---|
| **A. Local repository** (`nightly-exam-services`, ends `13 Dec 22:58Z`) | **4h28m28s** | Unknown — **not credible** | Snapshots 0, agent stopped, repository reachable with the same credential family the attacker held. Treat as untrusted. |
| **B. Offline tape `tape-04`** (`11 Dec 23:00Z`) | **52h26m28s** (2d 4h26m) | **≥ 8–12h**, and currently **blocked** | The vault key lives at `\files\ops\vault\` — the host now encrypted. The documented restore path cannot start without a key the incident already destroyed. |
| **C. Rebuild from scratch** | Not applicable | **Days** | Only viable if B fails permanently. Requires clean media for four hosts plus re-enrolment. |

**Conclusion.** RTO cannot be quoted, because it has never been measured — the only recorded attempt
failed at step 2 of 6 and consumed 11h18m doing so. RPO degrades from 4h28m to 52h26m the moment the
local repository is treated as untrusted, which it must be. The 100% "backup job success" figure proves
the backup *writer* worked; it says nothing about recovery, and this incident is the proof that the
distinction is not academic.

## 5.3 What must change (and it is not "take more backups")

1. **Immutable / air-gapped repository** with retention lock enforced **server-side** and credentials
   the admin console cannot use. "Retention lock configured" (F5) did not survive an admin credential
   with snapshot-purge rights.
2. **Separate credential family for the backup console** — the report itself says the repository is
   reachable with "the same credential family as jump/files". One credential compromised all three.
3. **Move the vault key out of `\files\ops\vault\`** — off the file server, into a separate secret
   store, with a documented break-glass path.
4. **Restore test as a scheduled, gated operation** — quarterly, timed, with a recorded RTO, and blocked
   from being reported as "passed" unless the service actually serves traffic. A test that fails
   silently for 14 months is worse than no test, because it licenses a false claim.
5. **Report RPO and RTO in hours, per service**, on the same dashboard that reports job success.

---

## 6. Part E — control effectiveness

The dashboard is not lying; it is measuring things that cannot fail. Each claim is paired with what it
cannot prove and the evidence that the gap was already real.

| Dashboard claim | What it cannot prove | Evidence from this incident |
|---|---|---|
| Patch compliance **98.2%**, "all managed endpoints and servers" | That the **2 KEV findings on the exploited path** were closed, or that the Admin zone was in scope | `F4` and `F2` are KEV and both sit on the used path; `F4`, `F6`, `F5` are all reachable there; scans covered "User, Servers and DMZ" only — **Admin zone excluded** |
| Backup job success **100%** | That anything restores | 1-of-3 restore success; the last test failed at step 2 of 6 (`backup_report.txt`) |
| Alerts processed **4,376**, **74% auto-closed** | That auto-closure is *correct* | `SA-9458` auto-closed as "known maintenance" while the change belonged to a different account (`P-033`) — an unmeasured false negative |
| MTTA **8 min** | Time to **detect** or **contain** ("not reported") | Actual: first true signal at +2h14m29s, declaration at +2h40m29s, **no containment at +2h52m** (`E-050`, `P-043`, `P-044`) |
| Log sources **9 of 9 onboarded** | That each source is **live and complete** | `jump` EDR dark for 7h13m at the snapshot (`E-007`) — onboarded and useless on the one host that mattered |
| Vulnerability scans **100% completed** | Coverage outside the three named zones | Admin zone (`jump`, `backup`, `adm-ws`) unscanned — precisely where F5 and F6 live |
| Open critical findings **8** | Age, exploitability, or whether any are on a live path | F4 (5.5) was on the live path; F3 (9.5) has no route |

**Metrics that should replace them.** Detection coverage per log source (share of expected events
received, per hour), MTTD/MTTC per severity, sampled QA of auto-closed alerts with a measured error
rate, restore success rate *with measured RTO*, share of KEV findings closed within SLA on
internet-reachable assets, and the share of privileged authentications that required MFA — a number that
was **0 of 4** in this incident.

---

## 7. What is established, and what is not

**Established:** the entry point produced a session with no credential presented (`A-038`); four
privileged logins by `adm.lina` ran without MFA over trust rules (`A-047`, `A-052`, `A-054`, `A-059`);
4.69 GB left the Servers zone before encryption (`N-074`); recovery was destroyed before impact, 24m46s
ahead of it (`E-044` vs `E-048`); 71,095 files were encrypted (`E-048`–`E-053`); the declared scope
omits `exam-db` and `idp`.

| Question | Why it is still open |
|---|---|
| Were `idp`'s token-signing keys or secrets taken during the `01:15:15Z` response? | Only the abnormal response size is logged (`P-027`); the content is not. Decides whether any session is trustworthy. |
| Is `jump` still under attacker control? | EDR dark 7h13m (`E-007`), no host telemetry after `01:55:47Z`. |
| What exactly was in the 4.69 GB? | Volume known (`N-074`), content not. Exam materials and staff shares live on that host (`TEAM_INFO.txt`). |
| Was `adm.lina` a stolen credential or an insider? | The account acted outside both approved change windows, but the pack does not establish who held it. |
| Is there persistence on `idp`, `exam-db`, `backup`? | `idp` scans report `clean` (`E-013`, `E-024`, `E-054`); web-layer and database-level persistence would not appear there. |
| Is the `13 Dec 22:58Z` backup restorable? | Repository reports 0 snapshots and the same credential family reached the console (`backup_report.txt`, F5). |
| Is containment under way outside the logs? | Nothing in the pack shows it (`P-044` is the last line). Absence of evidence, not evidence of absence. |

---

## 8. Triage hygiene — what was considered and excluded

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
real case the extension is an actor indicator to pivot on; here it is a data label. Either way, the
counts (70,700 + 395) are the impact number.

---

## 9. Division of work — Parts A–E across five people

Five parts, five owners, no names yet. Fill in the `Owner` column when you assign. Each part has one
primary file, so two people never edit the same file at once. Total effort: **~19–24 person-hours**
(estimates, not commitments).

| Part | Owner | The question this person answers | Inputs | Deliverable | Depends on | Effort |
|---|---|---|---|---|---|---|
| **A** — Exposure prioritisation | `Person 1` | Which of F1–F8 gets action first, and why the CVSS order is wrong here | `findings.csv`, `TEAM_INFO.txt`, Part B evidence | Ranked queue (8 rows), the ranking rule, and the demotions stated explicitly (F3, F7) | None — can start now | 3–4 h |
| **B** — Attack-path reconstruction | `Person 2` | What happened, in what order, proven by which log line | the four logs, `change_calendar.csv` | UTC-normalised timeline (~25 rows, each with an id), one kill-chain figure, the `+03:00` note | None — **start first**, it is the critical path | 5–6 h |
| **C** — Incident response | `Person 3` | Where the response actually stands, and what to do about the `07:30Z` exam | B timeline, `backup_report.txt`, `exam_schedule.csv`, `recovery_dependencies.csv` | State table (declared / contained / eradicated / recovered), P0–P2 action list, exam decision with its deadline | B draft timeline | 4–5 h |
| **D** — Backup and recovery | `Person 4` | Can we recover, and to what point in time | `backup_report.txt`, `recovery_dependencies.csv`, `exam_schedule.csv`, F5 | RTO/RPO table for three scenarios, dependency order, the vault-key blocker | None — independent | 4–5 h |
| **E** — Control effectiveness | `Person 5` | Why the dashboard cannot prove the controls work | `assurance_dashboard.txt`, `findings.csv`, B timeline, C response log | Metric-by-metric table (claim → what it cannot prove → evidence), replacement metrics, measured MTTD/MTTC/auto-close error | B timeline (for the time numbers) | 3–4 h |

## 9.1 Shared work (assign these too, or they fall between chairs)

| Task | Suggested owner | Output | When |
|---|---|---|---|
| Evidence baseline: counts, id ranges, cutoff check, `+03:00` conversion script | Person 2 | `tools/normalise.ps1` — used by B, C, E | Hour 1–2 |
| Integration and consistency pass (same numbers everywhere, same wording for the chain) | Person 1 | Final merged document | End |
| Cross-review ring (A←E, B←C, C←D, D←A, E←B) | everyone | One review comment sheet each | After draft |
| README / status-report upkeep | Person 1 | `README.md` stays factual | Ongoing |

## 9.2 Sequence

```
Hour 0     A  exposure ranking           starts now, independent
           D  backup / RTO-RPO           starts now, independent
           B  timeline + normaliser      starts now, critical path

Hour 4     B  timeline skeleton delivered (commentary may lag)
           C  response + exam call       starts, needs B
           E  dashboard critique         starts; needs B only for MTTD/MTTC

Hour 8     cross-review ring: A<-E, B<-C, C<-D, D<-A, E<-B
Hour 10    merge + consistency pass
```

- **A and D are independent** and can run from minute one.
- **B gates C and E.** B must deliver its timeline skeleton by hour 4, even if commentary is unfinished.
- **E can start early** on the dashboard critique (needs no timeline) and only waits for B for the
  MTTD/MTTC numbers.

## 9.3 Definition of done, per part

| Part | Done means |
|---|---|
| A | Every one of the 8 findings has a rank and a stated reason; the two demotions are argued, not implied; no rank rests on CVSS alone |
| B | Every row carries an evidence id; all times UTC; the four `adm.lina` logins and the two `adm.rakan` logins are distinguished; the approved scan is excluded |
| C | The four states are filled with evidence or marked "not evidenced"; the exam decision names a time and a consequence |
| D | RPO is a number for both the repository and the tape; the report says plainly that RTO has never been measured |
| E | Each dashboard claim is paired with a concrete counter-example from the logs; replacement metrics are measurable |

## 9.4 Rules that keep the merge from breaking

1. **One evidence id per claim.** A sentence without an id is an opinion, and it gets cut at merge.
2. **One owner per file.** Do not edit another person's draft; send a comment instead.
3. **Numbers live in one place.** Totals (71,095 files, 4.69 GB, 24 snapshots) are copied from the
   baseline script, not retyped from memory.
4. **Conflicts are settled by the log, not by seniority.** If two parts disagree, the id wins.
5. **Exclusions are part of the deliverable.** The authorised `soc-scan` sweep and the two approved
   change windows must appear somewhere, or a reader will assume they were missed.

## 9.5 Open allocation questions

- Who is the **final editor**? Recommend Person 1, who already owns A and the merge.
- Does anyone own the **opening/summary section**? Unassigned, and usually written last.
- Is there a **sixth body** for figures? If not, Person 2 produces the only figure (kill chain).

---

## 10. Verifying this document

Only PowerShell needed; run from the repository root.

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

# 5. Data-loss window from last good backup to encryption (expect 0.04:28:28)
(([datetimeoffset]'2026-12-14T03:26:28Z') - ([datetimeoffset]'2026-12-13T22:58:00Z')).ToString('d\.hh\:mm\:ss')
```

---

## 11. Assumptions and limitations

- **`203.0.113.226` and `192.0.2.190` are documentation ranges** (RFC 5737), as is the whole pack. They
  are treated as the real external endpoint and exfiltration destination because that is what the logs
  assert; in production they would be blocked and enriched, not assumed.
- **`E-007` is a status line, not a root cause.** Whether the `jump` agent died, was stopped, or was
  blocked is not in the pack. The analysis assumes the worst because the host's integrity cannot be
  established, and says so rather than guessing.
- **How `A-038` becomes `A-047` is inferred, not proven.** A forged `svc.sso` session at `01:17:31Z` is
  followed by a privileged `adm.lina` login at `01:55:47Z` with no credential event between them. The
  defensible reading is that session validation let the principal be chosen. A host artefact would
  settle it — and that host has dark EDR.
- **RTO figures in §5.2 are estimates** and labelled as such. No restore has completed, so no RTO has
  been observed. A precise RTO would be fabrication.
- **`snapshots listed: 0` does not prove every backup is unrecoverable** — it proves point-in-time
  recovery is unavailable and the repository cannot be trusted. §5.2 is a risk judgement, not a certainty.
- **The snapshot time is `04:05:30Z`.** Anything after it is a recommendation, not an observation.

---

## 12. Provenance

Case study designed and prepared by **Dr. Mohammed Jubur**, Jazan University — CNET 463.
All data in the evidence pack is synthetic; no real institution, person, or network is represented.
Team attribution: **T01** (`t01.uni.lab`). `TEAM_INFO.txt` is the authoritative pack description.
Licence: [`LICENSE`](LICENSE).
