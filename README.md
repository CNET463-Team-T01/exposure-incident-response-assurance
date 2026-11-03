# exposure-incident-response-assurance

Prioritising exploitable exposure, reconstructing the attack path from multi-source logs, running
incident response and backup recovery (RTO/RPO), and proving control effectiveness with security
metrics — built on a synthetic evidence pack.

**Fill in the names below, then work only inside your own part.**

---

## Allocation

| Part | Title | Evidence | Owner | Reviewer |
|---|---|---|---|---|
| A | Exposure prioritisation | `findings.csv` |  | Abdulaziz Mashnawi |
| B | Attack-path reconstruction | `auth_idp.log`, `endpoint_edr.log`, `network_fw_dns.log`, `app_audit.log` |  | Abdulaziz Mashnawi |
| C | Incident response | `change_calendar.csv`, Part B output |  | Abdulaziz Mashnawi |
| D | Backup, recovery and exam continuity (RTO/RPO) | `backup_report.txt`, `recovery_dependencies.csv`, `exam_schedule.csv` |  | Abdulaziz Mashnawi |
| E | Assurance and control effectiveness | `assurance_dashboard.txt`, `findings.csv` |  | Abdulaziz Mashnawi |

### Shared tasks

| Task | Output | Owner |
|---|---|---|
| Evidence baseline (counts, id ranges, time-base check) | `tools/normalise.ps1` |  |
| Cross-review of one other part | comment sheet |  |
| Final merge and consistency pass | this document |  |

---

## Evidence pack

`findings.csv` · `auth_idp.log` · `endpoint_edr.log` · `network_fw_dns.log` · `app_audit.log` ·
`change_calendar.csv` · `backup_report.txt` · `recovery_dependencies.csv` · `exam_schedule.csv` ·
`assurance_dashboard.txt`

---

## Part A — Exposure prioritisation

**Owner:** ____________________ **Reviewer:** Abdulaziz Mashnawi

**Deliverable.** A ranked table of the findings, the rule used to rank them, and the justification
for every position.

| Rank | Finding | Asset | Decision | Rationale (evidence id) |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |
| 6 |  |  |  |  |
| 7 |  |  |  |  |
| 8 |  |  |  |  |

**Ranking rule.**

>

**Findings deliberately not acted on this week.**

>

---

## Part B — Attack-path reconstruction

**Owner:** ____________________ **Reviewer:** Abdulaziz Mashnawi

**Deliverable.** A time-ordered table of events, each tied to an evidence id, plus a short narrative
of the path from first contact to business impact.

**Time base used:** ____________________

| # | Time (UTC) | Asset | Event | Evidence id |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |
| 6 |  |  |  |  |
| 7 |  |  |  |  |
| 8 |  |  |  |  |
| 9 |  |  |  |  |
| 10 |  |  |  |  |

**Narrative.**

>

**Activity considered and excluded as legitimate.**

>

---

## Part C — Incident response

**Owner:** ____________________ **Reviewer:** Abdulaziz Mashnawi

**Deliverable.** The response position at the analysis cutoff, the actions with their priorities, and
the decision that affects the next examination session.

| Question | Answer | Evidence |
|---|---|---|
| Detected? |  |  |
| Declared? |  |  |
| Contained? |  |  |
| Eradicated? |  |  |
| Recovered? |  |  |
| Scope of the declaration |  |  |
| Time to detect |  |  |
| Time to contain |  |  |

**Actions.**

| Priority | Action | Owner | Rationale | Status |
|---|---|---|---|---|
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |

**Examination decision and deadline.**

>

---

## Part D — Backup, recovery and exam continuity

**Owner:** ____________________ **Reviewer:** Abdulaziz Mashnawi

**Deliverable.** Measured RTO/RPO per service, the restore order dictated by dependencies, and the
constraints that block recovery.

| Service | Recovery order | RTO | RPO | Restore source | Blocker |
|---|---|---|---|---|---|
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |

**Evidence used for the RTO/RPO figures.**

>

**Effect on the examination schedule.**

>

---

## Part E — Assurance and control effectiveness

**Owner:** ____________________ **Reviewer:** Abdulaziz Mashnawi

**Deliverable.** For each management metric: what it reports, what it can and cannot prove, and the
evidence from the pack.

| Metric | Reported value | What it proves | What it cannot prove | Evidence |
|---|---|---|---|---|
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |

**Metrics proposed instead.**

>

---

## Conventions

1. Every claim carries an evidence id (`A-###`, `E-###`, `N-###`, `P-###`, `F#`, `CHG-####`).
2. One owner per section; do not edit another person's part — leave a comment instead.
3. State the time base you used, and keep it consistent across the whole document.
4. Totals and counts are taken from the evidence, never retyped from memory.
