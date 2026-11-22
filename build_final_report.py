import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#4A5568"))
        
        # Don't draw running header/footer on cover page (page 1)
        if self._pageNumber > 1:
            # Running Header
            self.drawString(36, 756, "CNET 463: Network Security Management | Case Study 3 - Technical Advisory Report")
            self.drawRightString(letter[0] - 36, 756, "Team T01 (t01.uni.lab)")
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.75)
            self.line(36, 748, letter[0] - 36, 748)
            
            # Running Footer
            self.line(36, 42, letter[0] - 36, 42)
            self.setFont("Helvetica", 7.5)
            self.drawString(36, 30, "CONFIDENTIAL & FORENSIC ASSURANCE - FOR SENIOR UNIVERSITY LEADERSHIP & SOC TEAMS")
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(letter[0] - 36, 30, page_text)
            
        self.restoreState()

def create_report():
    pdf_filename = "Case_Study_3_Parts_C_and_E_Report_T01.pdf"
    
    # Document Setup: 0.5 in margins (36 pt) for clean printable density
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=54,
        bottomMargin=54
    )
    
    printable_width = letter[0] - 72  # 540 pt
    
    # Professional Corporate / Academic Color Palette
    PRIMARY = colors.HexColor("#1A365D")    # Deep Navy
    SECONDARY = colors.HexColor("#2B6CB0")  # Slate Blue
    ACCENT = colors.HexColor("#2C5282")     # Medium Dark Blue
    DARK_TEXT = colors.HexColor("#2D3748")  # Charcoal Text
    LIGHT_BG = colors.HexColor("#F7FAFC")   # Soft Off-white
    ALT_ROW = colors.HexColor("#EDF2F7")    # Subtle Table Row Grey
    BORDER_COL = colors.HexColor("#CBD5E0") # Border Grey
    ALERT_RED = colors.HexColor("#9B2C2C")  # Crimson
    ALERT_BG = colors.HexColor("#FFF5F5")   # Crimson Background Tint
    WARN_AMBER = colors.HexColor("#C05621") # Dark Amber
    SUCCESS_GRN = colors.HexColor("#22543D")# Dark Green
    
    styles = getSampleStyleSheet()
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=PRIMARY,
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=SECONDARY,
        spaceAfter=12
    )
    
    meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=DARK_TEXT
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=PRIMARY,
        spaceBefore=12,
        spaceAfter=5,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=SECONDARY,
        spaceBefore=9,
        spaceAfter=4,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=DARK_TEXT,
        spaceAfter=4
    )
    
    callout_style = ParagraphStyle(
        'Callout_Text',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.2,
        textColor=DARK_TEXT
    )
    
    tbl_hdr = ParagraphStyle(
        'TableHdr',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.2,
        leading=9,
        textColor=colors.white,
        alignment=0
    )
    
    tbl_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=6.8,
        leading=8.4,
        textColor=DARK_TEXT
    )
    
    tbl_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=6.8,
        leading=8.4,
        textColor=DARK_TEXT
    )

    tbl_cell_code = ParagraphStyle(
        'TableCellCode',
        parent=styles['Normal'],
        fontName='Courier-Bold',
        fontSize=6.2,
        leading=7.6,
        textColor=colors.HexColor("#1A202C")
    )
    
    story = []
    
    # ---------------------------------------------------------
    # COVER / HEADER BLOCK
    # ---------------------------------------------------------
    story.append(Paragraph("CNET 463: Network Security Management - Case Study 3", subtitle_style))
    story.append(Paragraph("Forensic SOC Incident Investigation & Security Assurance Report", title_style))
    story.append(Paragraph("Comprehensive Technical Advisory for Senior Leadership: Parts C & E", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceBefore=2, spaceAfter=8))
    
    meta_table_data = [
        [
            Paragraph("<b>Target Organisation:</b> University Network Environment (Team T01)", meta_style),
            Paragraph("<b>Evaluation Time ('Now'):</b> 2026-12-14T04:05:30Z UTC", meta_style)
        ],
        [
            Paragraph("<b>Domain & Subnet:</b> t01.uni.lab | Subnet 10.170.0.0/16", meta_style),
            Paragraph("<b>Active Incident ID:</b> IR-911 (Critical Ransomware & Exfiltration)", meta_style)
        ],
        [
            Paragraph("<b>Advisory Team:</b> Network Security Management Team (T01)", meta_style),
            Paragraph("<b>Course Instructor:</b> Dr. Mohammed Jubur, Jazan University", meta_style)
        ]
    ]
    meta_table = Table(meta_table_data, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COL),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))
    
    # Executive Alert Box
    exec_summary_text = (
        "<b>CRITICAL OPERATIONAL DECISION CONTEXT:</b><br/>"
        "At evaluation time <b>2026-12-14T04:05:30Z UTC</b>, the university is in examination week. "
        "A severe double-extortion ransomware attack has compromised the File Server (<code>files.t01.uni.lab</code>) "
        "and Exam Database (<code>exam-db.t01.uni.lab</code>), causing total storage failure for the student-facing "
        "Examination Application (<code>exam-app.t01.uni.lab</code>) at 03:39:54Z. Simultaneously, <b>4.69 GB</b> of confidential data "
        "was exfiltrated to an external server at 02:29:31Z, and all 24 volume recovery snapshots were purged at 03:01:42Z. "
        "With the next exam session scheduled for <b>07:30:00Z UTC (~600 students)</b>, senior leadership has exactly "
        "<b>3 hours, 24 minutes</b> to make critical containment, recovery, and exam cancellation decisions. "
        "This technical report delivers the complete forensic investigation (Part C) and assurance governance redesign (Part E)."
    )
    callout_table = Table([[Paragraph(exec_summary_text, callout_style)]], colWidths=[printable_width])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), ALERT_BG),
        ('BOX', (0,0), (-1,-1), 1, ALERT_RED),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
    ]))
    story.append(callout_table)
    story.append(Spacer(1, 10))
    
    # ---------------------------------------------------------
    # PART C: SOC INVESTIGATION & INCIDENT TIMELINE
    # ---------------------------------------------------------
    story.append(Paragraph("Part C - SOC Investigation and Multi-Source Incident Timeline", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=SECONDARY, spaceBefore=2, spaceAfter=5))
    
    story.append(Paragraph(
        "<b>Section C.1: Multi-Source Chronological Incident Timeline</b><br/>"
        "To establish an irrefutable reconstruction of the attack, telemetry from all four evidence pack sources has been "
        "correlated: Identity Provider (<code>auth_idp.log</code>), Endpoint Detection & Response (<code>endpoint_edr.log</code>), "
        "Network Firewall & DNS (<code>network_fw_dns.log</code>), and Application / SOC Audit (<code>app_audit.log</code>).<br/>"
        "<b>Timestamp Standardization:</b> All timestamps are normalized to <b>Coordinated Universal Time (UTC)</b>. "
        "Endpoint logs recorded in local Arabian Standard Time (UTC+03:00) have been converted to UTC by subtracting 3 hours "
        "(e.g., 06:01:24+03:00 converts to 03:01:24Z UTC). The timeline reflects all significant events up to 'Now' (2026-12-14T04:05:30Z UTC).",
        body_style
    ))
    story.append(Spacer(1, 4))
    
    timeline_data = [
        [Paragraph("Time (UTC)", tbl_hdr), Paragraph("Host / Entity", tbl_hdr), Paragraph("ID", tbl_hdr), Paragraph("Forensic Event Description & Supporting Telemetry Evidence", tbl_hdr), Paragraph("Classification", tbl_hdr)],
        
        # Authorized Baseline & Maintenance
        [Paragraph("12-13 20:15:00Z", tbl_cell_bold), Paragraph("jump<br/>10.170.40.20", tbl_cell), Paragraph("P-001", tbl_cell_code), 
         Paragraph("<b>Change Window Open (CHG-9865):</b> Pre-exam health check window opened for <code>adm.rakan</code> until 22:00:00Z (change_calendar.csv).", tbl_cell), Paragraph("Authorized Change", tbl_cell)],
         
        [Paragraph("12-13 20:52:00Z<br/><i>(23:52 +03)</i>", tbl_cell_bold), Paragraph("jump<br/>10.170.40.20", tbl_cell), Paragraph("E-007", tbl_cell_code), 
         Paragraph("<b>EDR Telemetry Blackout:</b> Jump host EDR agent enters <code>not_reporting</code> status (reason: service unreachable). Endpoint visibility lost.", tbl_cell), Paragraph("Sensor Failure", tbl_cell)],

        [Paragraph("12-13 20:58:00Z", tbl_cell_bold), Paragraph("jump<br/>10.170.40.50", tbl_cell), Paragraph("A-008", tbl_cell_code), 
         Paragraph("<b>Authorized Admin Session:</b> <code>adm.rakan</code> logs into jump host from admin workstation with push MFA during CHG-9865.", tbl_cell), Paragraph("Legitimate Admin", tbl_cell)],

        # External Weaponization & Initial Access
        [Paragraph("12-14 01:13:01Z", tbl_cell_bold), Paragraph("idp (DMZ)<br/>203.0.113.226", tbl_cell), Paragraph("N-048<br/>P-021", tbl_cell_code), 
         Paragraph("<b>External Adversary Ingress:</b> External IP <code>203.0.113.226</code> initiates HTTPS connection to IdP (2050 bytes). Probes <code>/oauth/introspect</code> returning HTTP 500 (User-Agent: <code>http-lib/4.1</code>).", tbl_cell), Paragraph("Initial Access / Recon", tbl_cell)],

        [Paragraph("12-14 01:13:34Z - 01:14:43Z", tbl_cell_bold), Paragraph("idp-web<br/>203.0.113.226", tbl_cell), Paragraph("P-022<br/>P-023<br/>P-024<br/>P-026", tbl_cell_code), 
         Paragraph("<b>Vulnerability Fuzzing (Finding F4):</b> Attacker fuzzes <code>/oauth/token</code> (500), <code>/oauth/introspect</code> (400), <code>/api/session</code> (400), and <code>/oauth/introspect</code> (500).", tbl_cell), Paragraph("Exploit Execution", tbl_cell)],

        [Paragraph("12-14 01:15:15Z", tbl_cell_bold), Paragraph("idp-web<br/>203.0.113.226", tbl_cell), Paragraph("P-027", tbl_cell_code), 
         Paragraph("<b>Successful Authentication Bypass:</b> POST to <code>/oauth/introspect</code> succeeds with HTTP 200 and an abnormal 15,198-byte payload (Finding F4, SYN-2026-7537, EPSS 0.83).", tbl_cell), Paragraph("Exploit Success", tbl_cell)],

        [Paragraph("12-14 01:17:31Z", tbl_cell_bold), Paragraph("idp.t01.uni.lab<br/>203.0.113.226", tbl_cell), Paragraph("A-038", tbl_cell_code), 
         Paragraph("<b>Rogue SSO Session Creation:</b> Attacker creates authenticated session for service account <code>svc.sso</code> without presenting credentials or MFA (<code>method=none</code>, <code>mfa=not_applicable</code>).", tbl_cell), Paragraph("Credential Access / Persistence", tbl_cell)],

        # Vulnerability Scanner Noise Deconfliction
        [Paragraph("12-14 01:28:00Z - 01:28:33Z", tbl_cell_bold), Paragraph("soc-scan<br/>10.170.40.5", tbl_cell), Paragraph("N-052<br/>to<br/>N-063", tbl_cell_code), 
         Paragraph("<b>Authorized SOC Vulnerability Scan:</b> Approved internal scanner probes ports 22, 80, 135, 443, 445, 5432 across Servers, DMZ, and Admin zones (authorized per TEAM_INFO.txt line 21).", tbl_cell), Paragraph("Benign Security Scan", tbl_cell)],

        # Lateral Movement to Jump Host & Failed Alert
        [Paragraph("12-14 01:55:45Z - 01:55:47Z", tbl_cell_bold), Paragraph("idp -> jump<br/>10.170.10.10", tbl_cell), Paragraph("N-067<br/>A-047", tbl_cell_code), 
         Paragraph("<b>Lateral Movement to Admin Zone:</b> RDP connection (port 3389) from DMZ IdP to Jump host. Logs in as <code>adm.lina</code> bypassing MFA via flawed <code>service_trust_rule</code> (Finding F6).", tbl_cell), Paragraph("Lateral Movement / Priv Escalation", tbl_cell)],

        [Paragraph("12-14 01:59:19Z", tbl_cell_bold), Paragraph("soc / jump<br/>10.170.40.20", tbl_cell), Paragraph("P-033", tbl_cell_code), 
         Paragraph("<b>FATAL SOC DETECTION FAILURE:</b> SOC alert <code>SA-9458</code> (priv-login-from-server-source) fires on Lina's login, but is <b>AUTO-CLOSED</b> by SOAR playbook citing false maintenance pattern.", tbl_cell), Paragraph("Defense Evasion / SOC Blindspot", tbl_cell)],

        # Lateral Pivots Across Server Zone
        [Paragraph("12-14 02:19:46Z - 02:19:48Z", tbl_cell_bold), Paragraph("jump -> files<br/>10.170.40.20", tbl_cell), Paragraph("N-072<br/>A-052", tbl_cell_code), 
         Paragraph("<b>Lateral Movement to File Server:</b> SMB connection (port 445) from Jump to Files. Authenticated as <code>adm.lina</code> bypassing MFA via <code>admin_trust_rule</code>.", tbl_cell), Paragraph("Lateral Movement", tbl_cell)],

        [Paragraph("12-14 02:24:29Z - 02:24:31Z", tbl_cell_bold), Paragraph("jump -> db<br/>10.170.40.20", tbl_cell), Paragraph("N-073<br/>A-054", tbl_cell_code), 
         Paragraph("<b>Lateral Movement to Exam Database:</b> PostgreSQL connection (port 5432) from Jump to <code>exam-db</code>. Authenticated as <code>adm.lina</code> via <code>admin_trust_rule</code>.", tbl_cell), Paragraph("Lateral Movement", tbl_cell)],

        # Double Extortion: Data Exfiltration
        [Paragraph("12-14 02:29:31Z", tbl_cell_bold), Paragraph("files -> ext<br/>192.0.2.190", tbl_cell), Paragraph("N-074", tbl_cell_code), 
         Paragraph("<b>MASS DATA EXFILTRATION:</b> 4,688,452,260 bytes (<b>~4.69 GB</b>) egressed over port 443 from File Server to external IP <code>192.0.2.190</code> (Double-extortion theft).", tbl_cell), Paragraph("Exfiltration", tbl_cell)],

        [Paragraph("12-14 02:31:04Z - 02:31:06Z", tbl_cell_bold), Paragraph("jump -> backup<br/>10.170.40.20", tbl_cell), Paragraph("N-075<br/>A-059", tbl_cell_code), 
         Paragraph("<b>Compromise of Backup Server:</b> SSH session from Jump to <code>backup</code> server. Authenticated as <code>adm.lina</code> via shared administrative credentials (Finding F5).", tbl_cell), Paragraph("Lateral Movement", tbl_cell)],

        # Scheduled Maintenance Overlap
        [Paragraph("12-14 02:41:29Z - 02:56:29Z", tbl_cell_bold), Paragraph("jump<br/>10.170.40.50", tbl_cell), Paragraph("P-037<br/>A-062", tbl_cell_code), 
         Paragraph("<b>Scheduled Maintenance (CHG-5871):</b> Change window opens; <code>adm.rakan</code> logs into Jump from admin workstation with push MFA for approved maintenance.", tbl_cell), Paragraph("Legitimate Admin", tbl_cell)],

        # Sabotage of Backups
        [Paragraph("12-14 03:01:24Z - 03:01:42Z<br/><i>(06:01 +03)</i>", tbl_cell_bold), Paragraph("backup<br/>10.170.30.30", tbl_cell), Paragraph("E-043<br/>E-044", tbl_cell_code), 
         Paragraph("<b>SABOTAGE OF RECOVERY ASSETS:</b> Attacker stops <code>backup-agent</code> and executes <code>snapshot-purge --all</code> as <code>adm.lina</code>, destroying <b>all 24 recovery snapshots</b>.", tbl_cell), Paragraph("Inhibit Recovery", tbl_cell)],

        # Ransomware Mass Encryption
        [Paragraph("12-14 03:26:28Z - 03:27:45Z<br/><i>(06:26 +03)</i>", tbl_cell_bold), Paragraph("files<br/>10.170.30.15", tbl_cell), Paragraph("E-048<br/>E-049<br/>E-051", tbl_cell_code), 
         Paragraph("<b>Mass File Encryption Burst:</b> Encrypts exam materials share with extension <code>.t01lck</code> (1,585 + 11,477 + 57,638 = <b>70,700 files encrypted</b>).", tbl_cell), Paragraph("Impact (Ransomware)", tbl_cell)],

        [Paragraph("12-14 03:27:30Z<br/><i>(06:27 +03)</i>", tbl_cell_bold), Paragraph("files<br/>10.170.30.15", tbl_cell), Paragraph("E-050", tbl_cell_code), 
         Paragraph("<b>Passive EDR Detection:</b> Rule CS-207 triggers critical alert for 'mass file modification', but enforcement is misconfigured to <b>detected_only</b> (no blocking).", tbl_cell), Paragraph("Failed Containment", tbl_cell)],

        [Paragraph("12-14 03:28:01Z", tbl_cell_bold), Paragraph("files<br/>10.170.30.15", tbl_cell), Paragraph("E-052", tbl_cell_code), 
         Paragraph("<b>Ransom Note Dropped:</b> Adversary creates <code>\\\\files\\shares\\exam-materials\\README_RESTORE.txt</code>.", tbl_cell), Paragraph("Impact", tbl_cell)],

        [Paragraph("12-14 03:28:55Z<br/><i>(06:28 +03)</i>", tbl_cell_bold), Paragraph("exam-db<br/>10.170.30.10", tbl_cell), Paragraph("E-053", tbl_cell_code), 
         Paragraph("<b>Database Encryption:</b> 395 database data files encrypted with <code>.t01lck</code> on volume <code>db-data</code>.", tbl_cell), Paragraph("Impact", tbl_cell)],

        # Application Outage & Incident Declaration
        [Paragraph("12-14 03:39:54Z", tbl_cell_bold), Paragraph("exam-app<br/>10.170.10.20", tbl_cell), Paragraph("P-042", tbl_cell_code), 
         Paragraph("<b>APPLICATION CRASH & SERVICE OUTAGE:</b> Exam application fails with <code>storage_unavailable</code> on <code>/mnt/files/exam-materials</code>; 69 student requests fail.", tbl_cell), Paragraph("Operational Failure", tbl_cell)],

        [Paragraph("12-14 03:53:30Z", tbl_cell_bold), Paragraph("soc audit", tbl_cell), Paragraph("P-043", tbl_cell_code), 
         Paragraph("<b>FORMAL INCIDENT DECLARATION:</b> Incident <code>IR-911</code> declared as Critical by SOC lead. Scope: files, jump, backup.", tbl_cell), Paragraph("Incident Declaration", tbl_cell)],

        [Paragraph("12-14 04:05:30Z", tbl_cell_bold), Paragraph("management", tbl_cell), Paragraph("P-044", tbl_cell_code), 
         Paragraph("<b>'Now' Evaluation Cutoff:</b> Security Manager requests executive advisory on containment, recovery, and exam scheduling.", tbl_cell), Paragraph("Advisory Cutoff", tbl_cell)]
    ]
    
    timeline_table = Table(timeline_data, colWidths=[65, 65, 42, 308, 60], repeatRows=1)
    timeline_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 3),
        ('RIGHTPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, ALT_ROW]),
    ]))
    story.append(timeline_table)
    story.append(Spacer(1, 10))
    
    # ---------------------------------------------------------
    # SECTION C.2: EPISTEMIC CERTAINTY ANALYSIS
    # ---------------------------------------------------------
    story.append(Paragraph("Section C.2: Epistemic Analysis - Confirmed, Assumed, and Unknown Findings", h2_style))
    story.append(Paragraph(
        "To uphold scientific and legal standards of evidence, all conclusions are classified into three epistemic categories: "
        "<b>Confirmed</b> (directly supported by concrete log lines), <b>Assumed</b> (logically inferred from contextual telemetry), "
        "and <b>Unknown</b> (unobservable due to sensor blindness or pack boundaries).",
        body_style
    ))
    
    epistemic_data = [
        [Paragraph("Investigative Finding", tbl_hdr), Paragraph("Epistemic Status", tbl_hdr), Paragraph("Forensic Basis, Citations, and Analytical Deduction", tbl_hdr)],
        
        [Paragraph("<b>Initial Ingress & Vulnerability Exploitation</b>", tbl_cell_bold),
         Paragraph("<font color='#276749'><b>CONFIRMED</b></font>", tbl_cell),
         Paragraph("The adversary exploited an unpatched session-validation flaw (Finding F4, SYN-2026-7537) on the external IdP. "
                   "Citations: <code>N-048</code> shows incoming TCP connection from <code>203.0.113.226:50370</code>; <code>P-021</code> to <code>P-027</code> "
                   "show exploit fuzzing on <code>/oauth/introspect</code> resulting in an abnormal 15,198-byte payload; <code>A-038</code> confirms creation of "
                   "an authenticated session for service account <code>svc.sso</code> with <code>method=none</code> and <code>mfa=not_applicable</code>.", tbl_cell)],
                   
        [Paragraph("<b>Jump Host Compromise & Elevation</b>", tbl_cell_bold),
         Paragraph("<font color='#276749'><b>CONFIRMED</b></font><br/>&<br/><font color='#B7791F'><b>ASSUMED</b></font>", tbl_cell),
         Paragraph("<b>Confirmed:</b> Direct RDP connection occurred from IdP to Jump host at 01:55:45Z (<code>N-067</code>), logging in "
                   "as <code>adm.lina</code> bypassing MFA via <code>service_trust_rule</code> (<code>A-047</code>).<br/>"
                   "<b>Assumed:</b> Inferred that the adversary extracted cached administrative credentials for <code>adm.lina</code> from the memory "
                   "of <code>idp.t01.uni.lab</code> or forged an identity assertion utilizing the compromised <code>svc.sso</code> service token.", tbl_cell)],

        [Paragraph("<b>Internal Execution on Jump Host</b>", tbl_cell_bold),
         Paragraph("<font color='#742A2A'><b>UNKNOWN</b></font>", tbl_cell),
         Paragraph("Specific process executions, CLI arguments, and memory injection commands executed directly inside <code>jump.t01.uni.lab</code> "
                   "remain <b>Unknown</b> because the Jump host EDR agent silently failed and stopped reporting at 20:52:00Z UTC (<code>E-007</code>). "
                   "Confirmation requires uncorrupted host-level security event logs (Windows Event IDs 4688, 4104).", tbl_cell)],

        [Paragraph("<b>Lateral Movement Across Core Servers</b>", tbl_cell_bold),
         Paragraph("<font color='#276749'><b>CONFIRMED</b></font>", tbl_cell),
         Paragraph("The attacker pivoted from Jump host to File Server over SMB at 02:19:46Z (<code>N-072</code>, <code>A-052</code>), to Exam Database over "
                   "PostgreSQL at 02:24:29Z (<code>N-073</code>, <code>A-054</code>), and to Backup Server over SSH at 02:31:04Z (<code>N-075</code>, <code>A-059</code>). "
                   "All sessions utilized Lina's compromised account and bypassed MFA via <code>admin_trust_rule</code>.", tbl_cell)],

        [Paragraph("<b>Data Exfiltration Volume & Target</b>", tbl_cell_bold),
         Paragraph("<font color='#276749'><b>CONFIRMED</b></font><br/>&<br/><font color='#742A2A'><b>UNKNOWN</b></font>", tbl_cell),
         Paragraph("<b>Confirmed:</b> Exactly 4,688,452,260 bytes (~4.69 GB) were egressed from <code>files.t01.uni.lab</code> to external IP <code>192.0.2.190</code> "
                   "over port 443 at 02:29:31Z (<code>N-074</code>).<br/>"
                   "<b>Unknown:</b> The precise contents of the exfiltrated archive (e.g., upcoming exam questions, student records, PII) cannot be determined "
                   "from layer-4 firewall bytes alone; DLP logs or full packet capture (PCAP) inspection is required.", tbl_cell)],

        [Paragraph("<b>Backup Sabotage & Snapshot Purging</b>", tbl_cell_bold),
         Paragraph("<font color='#276749'><b>CONFIRMED</b></font>", tbl_cell),
         Paragraph("The adversary systematically halted the <code>backup-agent</code> service (<code>E-043</code> at 03:01:24Z) and executed <code>snapshot-purge --all</code> "
                   "(<code>E-044</code> at 03:01:42Z) as <code>adm.lina</code>, deleting all 24 volume snapshots. Corroborated by <code>backup_report.txt</code> line 18.", tbl_cell)],

        [Paragraph("<b>Ransomware Encryption & Service Outage</b>", tbl_cell_bold),
         Paragraph("<font color='#276749'><b>CONFIRMED</b></font>", tbl_cell),
         Paragraph("Over 70,700 files on <code>files</code> (<code>E-048</code>, <code>E-049</code>, <code>E-051</code>) and 395 database files on <code>exam-db</code> "
                   "(<code>E-053</code>) were encrypted with extension <code>.t01lck</code>. Ransom note dropped (<code>E-052</code>). "
                   "Direct application crash confirmed at 03:39:54Z when <code>exam-app</code> logged <code>storage_unavailable</code> (<code>P-042</code>).", tbl_cell)],

        [Paragraph("<b>Adversary Attribution & Real Identity</b>", tbl_cell_bold),
         Paragraph("<font color='#742A2A'><b>UNKNOWN</b></font>", tbl_cell),
         Paragraph("The physical identity, geographic location, and organizational affiliation of the threat actor operating <code>203.0.113.226</code> and "
                   "<code>192.0.2.190</code> is completely <b>Unknown</b>. Synthetic evidence packs contain no threat intelligence attribution data.", tbl_cell)]
    ]
    
    epistemic_table = Table(epistemic_data, colWidths=[90, 75, 375], repeatRows=1)
    epistemic_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, ALT_ROW]),
    ]))
    story.append(epistemic_table)
    story.append(Spacer(1, 10))
    
    # ---------------------------------------------------------
    # SECTION C.3: DECONFLICTION & DETECTION FAILURE ANALYSIS
    # ---------------------------------------------------------
    story.append(Paragraph("Section C.3: Suspicious Activity Deconfliction & Defensive Control Failures", h2_style))
    story.append(Paragraph(
        "A rigorous SOC investigation requires separating genuine adversary actions from benign operational anomalies, "
        "and evaluating why deployed defensive controls failed to halt the attack.",
        body_style
    ))
    
    deconflict_text = (
        "<b>1. Deconfliction of Benign Operational Anomalies (False Positives Explained):</b><br/>"
        "&bull; <b>Authorized SOC Vulnerability Scanning:</b> Firewall logs <code>N-052</code> through <code>N-063</code> (01:28:00Z - 01:28:33Z) reveal rapid connection bursts "
        "probing ports 22, 80, 135, 443, 445, 5432 across IDP, exam-app, exam-db, files, and backup servers. While mimicking network reconnaissance, "
        "this traffic originated strictly from <code>10.170.40.5</code>. <code>TEAM_INFO.txt</code> line 21 confirms: <i>'Approved vulnerability scanner: soc-scan (10.170.40.5). "
        "Scanning from it is authorised.'</i> This was confirmed as authorized scheduled scanning, not adversary reconnaissance.<br/>"
        "&bull; <b>Authorized Administrative Maintenance:</b> Privileged logins by administrator <code>adm.rakan</code> to <code>jump.t01.uni.lab</code> at 20:58:00Z "
        "(<code>A-008</code>) and 02:56:29Z (<code>A-062</code>) originated from the official admin workstation (<code>10.170.40.50</code>) and were validated with push MFA. "
        "Cross-referencing <code>change_calendar.csv</code> and audit logs (<code>P-001</code>, <code>P-037</code>) confirms these sessions corresponded to approved "
        "change windows CHG-9865 (Pre-exam health check) and CHG-5871 (Scheduled jump-host maintenance).<br/>"
        "&bull; <b>Campus Network Noise:</b> Student authentication failures (<code>A-003</code>, <code>A-021</code>, <code>A-030</code>, <code>A-034</code>, <code>A-035</code>) "
        "and firewall drops (<code>N-009</code>, <code>N-012</code>, <code>N-020</code>, <code>N-037</code>) reflect routine authentication typos and misconfigured routing "
        "successfully dropped by default-deny rules.<br/><br/>"
        "<b>2. SOC Detection Failures & Alert Suppression Root Cause Analysis:</b><br/>"
        "&bull; <b>Fatal SOAR Playbook Auto-Closure Failure (Alert SA-9458):</b> At 01:59:19Z, audit log <code>P-033</code> records SOC alert <code>SA-9458</code> triggered by rule "
        "<code>priv-login-from-server-source</code> when <code>adm.lina</code> logged into the Jump host directly from the DMZ IdP (<code>10.170.10.10</code>). "
        "Tragically, the automated SOAR playbook closed the alert (<code>status=AUTO_CLOSED</code>) citing <code>reason=matches_known_maintenance_pattern</code>. "
        "<b>Flaw Analysis:</b> The playbook made a fatal logic error. The active change window at that time (CHG-9865) had ended at 22:00:00Z and was authorized "
        "only for <code>adm.rakan</code> from <code>10.170.40.50</code>. An administrative login from an Internet-facing DMZ server by <code>adm.lina</code> was completely "
        "unauthorized. Blind playbook auto-closure suppressed the single high-fidelity detection that could have isolated the jump host before data exfiltration or ransomware deployment.<br/>"
        "&bull; <b>Passive EDR Configuration Failure (Alert CS-207):</b> At 03:27:30Z UTC (06:27:30+03:00), the file server EDR triggered critical alert <code>CS-207</code> "
        "for <i>'mass file modification'</i> (<code>E-050</code>). However, the agent's enforcement policy was set to <code>action=detected_only</code> rather than automated "
        "process killing or host isolation. Consequently, encryption continued uninterrupted, destroying 70,700 files and knocking the exam service offline."
    )
    story.append(Paragraph(deconflict_text, body_style))
    story.append(Spacer(1, 8))
    
    # ---------------------------------------------------------
    # SECTION C.4: ATTACK MILESTONES & EXPOSURE DURATION
    # ---------------------------------------------------------
    story.append(Paragraph("Section C.4: Attack Milestones and Exposure Duration Quantification", h2_style))
    story.append(Paragraph(
        "To evaluate operational latency and dwell time, the attack lifecycle has been measured across precise operational milestones:",
        body_style
    ))
    
    milestone_data = [
        [Paragraph("Operational Milestone", tbl_hdr), Paragraph("Exact Timestamp (UTC)", tbl_hdr), Paragraph("Evidence Citation & Forensic Basis", tbl_hdr), Paragraph("Operational Latency / Exposure Window", tbl_hdr)],
        
        [Paragraph("<b>1. Attack Initiation & Compromise</b>", tbl_cell_bold),
         Paragraph("<b>2026-12-14 01:13:01Z</b><br/><i>(Session: 01:17:31Z)</i>", tbl_cell),
         Paragraph("First malicious probe on IdP from <code>203.0.113.226</code> (<code>N-048</code>, <code>P-021</code>). Rogue <code>svc.sso</code> session established at 01:17:31Z (<code>A-038</code>).", tbl_cell),
         Paragraph("<b>T + 0 min</b><br/>(Baseline Intrusion Start)", tbl_cell)],

        [Paragraph("<b>2. First SOC Visibility</b>", tbl_cell_bold),
         Paragraph("<b>2026-12-14 01:59:19Z</b>", tbl_cell),
         Paragraph("SOC alert <code>SA-9458</code> fires on jump login from IdP (<code>P-033</code>). Auto-closed by SOAR playbook.", tbl_cell),
         Paragraph("<b>46 min 18 sec</b> after first probe<br/><i>(Suppressed & Ignored)</i>", tbl_cell)],

        [Paragraph("<b>3. First Endpoint Visibility</b>", tbl_cell_bold),
         Paragraph("<b>2026-12-14 03:27:30Z</b>", tbl_cell),
         Paragraph("EDR alert <code>CS-207</code> fires on mass file encryption on <code>files</code> (<code>E-050</code>). Action: detected only.", tbl_cell),
         Paragraph("<b>2 hr 14 min 29 sec</b> after first probe<br/><i>(Passive detection)</i>", tbl_cell)],

        [Paragraph("<b>4. First Service Impact</b>", tbl_cell_bold),
         Paragraph("<b>2026-12-14 03:01:42Z</b> (Backup)<br/><b>2026-12-14 03:39:54Z</b> (Service)", tbl_cell),
         Paragraph("Backup snapshots purged at 03:01:42Z (<code>E-044</code>). Exam app storage failure on <code>exam-materials</code> at 03:39:54Z (<code>P-042</code>).", tbl_cell),
         Paragraph("<b>1 hr 48 min 41 sec</b> (Backup)<br/><b>2 hr 26 min 53 sec</b> (Exam App)", tbl_cell)],

        [Paragraph("<b>5. Incident Declaration</b>", tbl_cell_bold),
         Paragraph("<b>2026-12-14 03:53:30Z</b>", tbl_cell),
         Paragraph("Incident <code>IR-911</code> formally declared as Critical by SOC lead (<code>P-043</code>). Scope: files, jump, backup.", tbl_cell),
         Paragraph("<b>2 hr 40 min 29 sec</b> total exposure<br/>(<b>160.5 minutes</b>)", tbl_cell)],

        [Paragraph("<b>6. Leadership Cutoff ('Now')</b>", tbl_cell_bold),
         Paragraph("<b>2026-12-14 04:05:30Z</b>", tbl_cell),
         Paragraph("Security Manager requests senior leadership advisory (<code>P-044</code>). Cutoff time for all decisions.", tbl_cell),
         Paragraph("<b>2 hr 52 min 29 sec</b> since ingress<br/>(Next exam in <b>3 hr 24 min</b>)", tbl_cell)]
    ]
    
    milestone_table = Table(milestone_data, colWidths=[95, 80, 245, 120], repeatRows=1)
    milestone_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, ALT_ROW]),
    ]))
    story.append(milestone_table)
    story.append(Spacer(1, 14))
    
    # ---------------------------------------------------------
    # PART E: ASSURANCE & SECURITY METRICS
    # ---------------------------------------------------------
    story.append(PageBreak()) # Clean break into Part E
    story.append(Paragraph("Part E - Assurance, Security Metrics, and Executive Guidance", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=SECONDARY, spaceBefore=2, spaceAfter=5))
    
    story.append(Paragraph(
        "<b>Section E.1: Critical Evaluation of Weekly Management Dashboard (<code>assurance_dashboard.txt</code>)</b><br/>"
        "Following the incident, senior leadership received the weekly executive dashboard for the week ending 2026-12-13. "
        "A rigorous audit comparing dashboard assertions against empirical log telemetry reveals catastrophic assurance failures. "
        "The dashboard presents a superficial facade of operational control while obscuring critical systemic vulnerabilities.",
        body_style
    ))
    story.append(Spacer(1, 4))
    
    dashboard_audit_data = [
        [Paragraph("Dashboard Reported Metric", tbl_hdr), Paragraph("Reported Value", tbl_hdr), Paragraph("Empirical Reality from Evidence Pack & Technical Root Cause", tbl_hdr), Paragraph("Assurance Weakness & Risk", tbl_hdr)],
        
        [Paragraph("<b>Alerts processed & Playbook Auto-Closure</b>", tbl_cell_bold),
         Paragraph("4376 processed<br/><b>74% auto-closed</b>", tbl_cell),
         Paragraph("The dashboard celebrates high automation (74% closed automatically) as an efficiency triumph. In reality, "
                   "at 01:59:19Z, SOC alert <code>SA-9458</code> (priv-login-from-server-source) detected unauthorized lateral movement by "
                   "<code>adm.lina</code> from the DMZ IdP to the Jump host. The SOAR playbook blindly closed it (<code>P-033</code>) citing "
                   "<code>matches_known_maintenance_pattern</code>. The playbook failed to validate that CHG-9865 was expired and was only for "
                   "<code>adm.rakan</code>. This single false negative allowed the entire breach to proceed unimpeded.", tbl_cell),
         Paragraph("<b>Vanity Metric / Blind Automation:</b> Measures execution volume rather than decision fidelity. Aggressive auto-closure without strict reconciliation creates catastrophic blindspots.", tbl_cell)],

        [Paragraph("<b>Backup Job Success vs. Restore Capability</b>", tbl_cell_bold),
         Paragraph("<b>100%</b> Job Success<br/>Restore: 1 of 3 (12 mo)", tbl_cell),
         Paragraph("While nightly backup jobs completed with exit code 0 (<code>backup_report.txt</code> lines 5-11), recoverability was completely non-existent. "
                   "1) The only exam-service restore test in 12 months failed on 2026-10-18 (<code>duration=11h18m</code>) because the vault encryption key "
                   "was missing from <code>\\\\files\\ops\\vault\\</code>. No retest occurred. 2) The backup console shared credentials with the compromised admin accounts "
                   "(Finding F5). The attacker logged in (<code>A-059</code>), stopped the backup service (<code>E-043</code>), and purged all 24 volume snapshots (<code>E-044</code>).", tbl_cell),
         Paragraph("<b>The Backup Mirage:</b> Conflates backup job completion with business recoverability. Snapshot immutability and restore validation were completely absent.", tbl_cell)],

        [Paragraph("<b>Mean Time to Acknowledge (MTTA)</b>", tbl_cell_bold),
         Paragraph("<b>8 min</b><br/><i>(MTTD & MTTC: Not Reported)</i>", tbl_cell),
         Paragraph("The dashboard proudly reports an 8-minute MTTA, yet explicitly admits: <i>'(time to detect / time to contain: not reported)'</i>. "
                   "Acknowledging an alert in 8 minutes is completely meaningless when the alert is auto-closed without investigation (<code>P-033</code>). "
                   "Empirical evidence proves the university suffered an uncontained adversary dwell time of <b>160.5 minutes</b> (01:13:01Z to 03:53:30Z). "
                   "Furthermore, when EDR detected ransomware encryption at 03:27:30Z (<code>E-050</code>), policy was <code>detected_only</code>, resulting in an automated MTTC of infinity.", tbl_cell),
         Paragraph("<b>Misleading Operational Metric:</b> MTTA tracks ticket clicks, not threat neutralization. Omitting MTTD and MTTC masks severe detection and response delays.", tbl_cell)],

        [Paragraph("<b>Patch Compliance & Vulnerability Scanning</b>", tbl_cell_bold),
         Paragraph("<b>98.2%</b> Compliance<br/><b>100%</b> Scan Scope<br/>8 Open Criticals", tbl_cell),
         Paragraph("98.2% patch compliance creates an illusion of perimeter defense. However, the Internet-facing IdP hosted finding F4 (SYN-2026-7537), "
                   "which had an alarming EPSS of 0.83 (83% exploitation probability) and was listed on CISA KEV (exploited in wild). It had no patch or virtual patch applied. "
                   "Moreover, 100% scan coverage provided no protection because the architectural trust flaw (Finding F6: Jump host allowing RDP without MFA "
                   "from trusted servers via <code>service_trust_rule</code>) was an architectural design failure, not a missing software patch.", tbl_cell),
         Paragraph("<b>Flawed Vulnerability Governance:</b> Aggregating endpoint compliance percentages obscures exposed, high-risk edge assets and ignores architectural trust bypasses.", tbl_cell)],

        [Paragraph("<b>Log Source Onboarding vs. Telemetry Health</b>", tbl_cell_bold),
         Paragraph("<b>9 of 9</b> Onboarded<br/>(100%)", tbl_cell),
         Paragraph("While 9 of 9 hosts are marked 'onboarded', onboarding does not reflect real-time agent health or operational availability. "
                   "At 20:52:00Z UTC (<code>E-007</code>), the EDR agent on <code>jump.t01.uni.lab</code> silently failed (<code>status=not_reporting</code>) "
                   "and remained offline throughout the entire lateral movement and sabotage campaign. The dashboard was blind to this telemetry blackout.", tbl_cell),
         Paragraph("<b>Blind Telemetry Inventory:</b> Measures static configuration rather than dynamic stream liveness and sensor health.", tbl_cell)]
    ]
    
    dashboard_table = Table(dashboard_audit_data, colWidths=[85, 70, 265, 120], repeatRows=1)
    dashboard_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, ALT_ROW]),
    ]))
    story.append(dashboard_table)
    story.append(Spacer(1, 10))
    
    # ---------------------------------------------------------
    # SECTION E.2: METRICS ARCHITECTURE DESIGN
    # ---------------------------------------------------------
    story.append(Paragraph("Section E.2: Robust Assurance Metrics Architecture", h2_style))
    story.append(Paragraph(
        "To replace the defective dashboard, a comprehensive metrics framework has been designed covering exposure governance, "
        "architectural risk, SOC operational efficacy, and disaster recovery resilience.",
        body_style
    ))
    
    metrics_spec_data = [
        [Paragraph("Metric Specification", tbl_hdr), Paragraph("Metric 1: Exposure Management (KPI)", tbl_hdr), Paragraph("Metric 2: Architecture & Identity (KRI)", tbl_hdr), Paragraph("Metric 3: SOC Operations (Response)", tbl_hdr), Paragraph("Metric 4: Resilience & DR (Recovery)", tbl_hdr)],
        
        [Paragraph("<b>Name & Code</b>", tbl_cell_bold),
         Paragraph("<b>Mean Time to Mitigate Critical Edge Flaws (MTTM-Edge)</b>", tbl_cell),
         Paragraph("<b>Cross-Zone Trust & MFA Bypass Ratio (KRI-TrustBypass)</b>", tbl_cell),
         Paragraph("<b>Mean Time to Contain Lateral Movement (MTTC-Lateral)</b>", tbl_cell),
         Paragraph("<b>Tested RTO Deficit / Vault Key Validation (RTO-Deficit)</b>", tbl_cell)],

        [Paragraph("<b>Core Purpose</b>", tbl_cell_bold),
         Paragraph("Ensure Internet-facing assets with active exploitation signals (KEV=Y, EPSS > 0.5) receive immediate patching or virtual WAF patching.", tbl_cell),
         Paragraph("Quantify and eliminate network and identity bypasses (e.g., <code>service_trust_rule</code>) that allow unauthenticated/single-factor cross-zone traversal.", tbl_cell),
         Paragraph("Measure SOC speed in detecting, triaging, and isolating active lateral movement across administrative and server boundaries.", tbl_cell),
         Paragraph("Validate end-to-end recoverability of mission-critical systems and ensure recovery keys/immutability are operational.", tbl_cell)],

        [Paragraph("<b>Formula & Scope</b>", tbl_cell_bold),
         Paragraph("<code>MTTM = (Sigma(T_patch - T_publish)) / N</code><br/>Scope: All external/DMZ assets (IDP, Exam-App, Firewalls).", tbl_cell),
         Paragraph("<code>Ratio = N_bypass_logins / N_total_priv_logins * 100</code><br/>Scope: All logins into Admin (10.170.40.0/24) and Server (10.170.30.0/24) zones.", tbl_cell),
         Paragraph("<code>MTTC = T_isolation - T_first_lateral_pivot</code><br/>Scope: All high-severity internal alerts (priv-login, mass-edr).", tbl_cell),
         Paragraph("<code>Deficit = Tested_Restore_Time - Defined_RTO</code><br/>Scope: Tier-1 academic assets (Exam Database, Files, SSO).", tbl_cell)],

        [Paragraph("<b>Data Source</b>", tbl_cell_bold),
         Paragraph("Vulnerability scanner, WAF virtual patch logs, Asset Management CMDB.", tbl_cell),
         Paragraph("IdP authentication logs (<code>auth_idp.log</code>) and Jump host event logs.", tbl_cell),
         Paragraph("SOAR audit logs, EDR console, Network firewall session tables.", tbl_cell),
         Paragraph("Disaster recovery orchestrator, Backup agent logs, restore test reports.", tbl_cell)],

        [Paragraph("<b>Target Threshold</b>", tbl_cell_bold),
         Paragraph("<b>< 24 Hours</b> for KEV/EPSS > 0.5;<br/><b>< 72 Hours</b> for CVSS >= 8.0.", tbl_cell),
         Paragraph("<b>0.0%</b> (Zero tolerance for non-MFA cross-zone administrative sessions).", tbl_cell),
         Paragraph("<b>< 15 Minutes</b> from initial unauthorized pivot to host network isolation.", tbl_cell),
         Paragraph("<b><= 0 Hours</b> (Tested restore must complete inside agreed RTO window).", tbl_cell)],

        [Paragraph("<b>Owner & Accountability</b>", tbl_cell_bold),
         Paragraph("Lead Infrastructure Security Engineer & Vulnerability Management Lead.", tbl_cell),
         Paragraph("Identity & Access Management (IAM) Architect & Network Security Lead.", tbl_cell),
         Paragraph("SOC Operations Manager & Incident Response Lead.", tbl_cell),
         Paragraph("Disaster Recovery Coordinator & Head of Enterprise Infrastructure.", tbl_cell)],

        [Paragraph("<b>Action Trigger</b>", tbl_cell_bold),
         Paragraph("If unpatched > 24h, trigger automated emergency WAF virtual patch / IP restriction.", tbl_cell),
         Paragraph("Any single login with <code>mfa=not_required</code> immediately severs session and locks account.", tbl_cell),
         Paragraph("If MTTC > 15m or alert auto-closed without ticket ID, escalate to CISO on-call.", tbl_cell),
         Paragraph("If restore fails or test > RTO, freeze production changes until successful retest.", tbl_cell)],

        [Paragraph("<b>Inherent Limitation</b>", tbl_cell_bold),
         Paragraph("Vendor zero-days without published signatures or WAF rules cannot be patched immediately.", tbl_cell),
         Paragraph("May flag legitimate automated service account batch jobs if service accounts lack MFA integration.", tbl_cell),
         Paragraph("Does not measure stealthy living-off-the-land techniques that evade initial heuristic detection.", tbl_cell),
         Paragraph("Full restore testing cannot run concurrently on production database without isolated staging sandbox.", tbl_cell)]
    ]
    
    metrics_table = Table(metrics_spec_data, colWidths=[75, 115, 115, 115, 120], repeatRows=1)
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, ALT_ROW]),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 10))
    
    # ---------------------------------------------------------
    # SECTION E.3: CONTROL ASSURANCE PROGRAM
    # ---------------------------------------------------------
    story.append(Paragraph("Section E.3: In-Depth Control Assurance Plan - Administrative Access & Trust Rules", h2_style))
    story.append(Paragraph(
        "<b>Selected High-Impact Control:</b> <i>Enforcement of Phishing-Resistant Multi-Factor Authentication (MFA) and "
        "Strict Network Boundary Segmentation for Administrative Jump Host Access (NIST SP 800-207 Zero Trust Architecture).</i><br/>"
        "In this incident, two fatal control design and operational failures enabled total network compromise: 1) The presence of "
        "<code>service_trust_rule</code> allowing an unauthenticated session on the DMZ IdP to RDP directly into the Admin Jump Host (<code>A-047</code>), "
        "and 2) The SOAR auto-closure rule that blindly dismissed the resulting alert (<code>P-033</code>).",
        body_style
    ))
    
    control_test_text = (
        "<b>1. Design Effectiveness Evaluation (Is the control designed to prevent the threat?):</b><br/>"
        "&bull; <b>Control Objective:</b> Ensure that zero administrative sessions can be initiated from untrusted zones (DMZ, Users) or "
        "bypass hardware-backed MFA, regardless of source account or service context.<br/>"
        "&bull; <b>Design Review & Testing Procedures:</b><br/>"
        "  1) <i>Firewall Rulebase Audit:</i> Inspect edge and inter-zone firewall configurations between DMZ (10.170.10.0/24) and Admin (10.170.40.0/24). "
        "Verify that port 3389 (RDP) and port 22 (SSH) are blocked by default and cannot be overridden by service object groups.<br/>"
        "  2) <i>Authentication Policy Review:</i> Audit the Identity Provider and Jump Host PAM/RDP configurations. Verify that 'trust rules' "
        "(e.g., <code>service_trust_rule</code>, <code>admin_trust_rule</code>) that set <code>mfa=not_required</code> are completely deprecated.<br/>"
        "  3) <i>SOAR Playbook Logic Verification:</i> Review the decision logic of playbook rule <code>priv-login-from-server-source</code>. "
        "Verify that auto-closure is cryptographically impossible unless the source IP, destination IP, user account, AND active Change Window Ticket ID "
        "match an approved API token from the ITSM change calendar.<br/>"
        "&bull; <b>Evidence to Retain:</b> Exported firewall rulebase JSON, IdP conditional access JSON policies, SOAR playbook XML/Python definitions, "
        "and formal architecture approval sign-offs.<br/><br/>"
        "<b>2. Operating Effectiveness Evaluation (Is the control functioning reliably over time?):</b><br/>"
        "&bull; <b>Sampling Strategy & Population:</b> 100% census of all privileged sessions initiated into the Admin Zone (10.170.40.0/24) and Server Zone "
        "(10.170.30.0/24) over the preceding 90 days. For automated alerts, sample 100% of auto-closed privileged alerts.<br/>"
        "&bull; <b>Operating Testing Procedures:</b><br/>"
        "  1) <i>Log Reconciliation (Triangulation):</i> Correlate every connection event on firewall port 3389/22 (<code>network_fw_dns.log</code>) against "
        "IdP authentication logs (<code>auth_idp.log</code>) and ITSM change tickets. Identify any instance where MFA was marked <code>not_required</code> or "
        "where source IP was not an approved admin workstation (10.170.40.50).<br/>"
        "  2) <i>Breach Simulation & Penetration Testing:</i> Execute automated synthetic attack simulations from a compromised DMZ container attempting "
        "RDP connection to the Jump host. Confirm that: a) the firewall drops the packet, b) the Jump host denies authentication without FIDO2 push, "
        "and c) an alert is routed to SOC tier-2 analysts with automated host network isolation triggered.<br/>"
        "  3) <i>EDR Enforcement Audit:</i> Query all EDR agent policies across all servers. Confirm zero agents are set to <code>action=detected_only</code>.<br/>"
        "&bull; <b>Evidence to Retain:</b> SQL reconciliation query outputs, penetration test execution PCAPs, SIEM alert audit logs, signed ITSM change tickets, "
        "and quarterly auditor-attested operating compliance reports."
    )
    story.append(Paragraph(control_test_text, body_style))
    story.append(Spacer(1, 10))
    
    # ---------------------------------------------------------
    # SECTION E.4: EXECUTIVE RECOMMENDATION
    # ---------------------------------------------------------
    story.append(Paragraph("Section E.4: Strategic Executive Memorandum (Advice at 'Now' 2026-12-14T04:05:30Z UTC)", h2_style))
    
    exec_memo_text = (
        "<b>MEMORANDUM FOR:</b> Senior Executive Leadership & University Examination Board<br/>"
        "<b>FROM:</b> University Network Security Management Advisory Team<br/>"
        "<b>DATE & TIME:</b> 2026-12-14T04:05:30Z UTC ('Now' Cutoff)<br/>"
        "<b>SUBJECT:</b> URGENT ADVISORY: INCIDENT IR-911 CONTAINMENT & MORNING EXAM SESSION DECISION<br/>"
        "<hr/>"
        "<b>1. Immediate Priority Actions (What to do FIRST and WHY):</b><br/>"
        "&bull; <b>Action 1: Immediate Network Isolation of Impacted Infrastructure (Within 10 Minutes):</b><br/>"
        "  <i>Execution:</i> Sever all network connectivity to <code>files.t01.uni.lab</code> (10.170.30.15), <code>jump.t01.uni.lab</code> (10.170.40.20), "
        "and <code>backup.t01.uni.lab</code> (10.170.30.30). Sever all outbound internet traffic from the DMZ and Server zones.<br/>"
        "  <i>Justification:</i> File server and database encryption is actively spreading (<code>E-048</code>, <code>E-053</code>). 4.69 GB was already exfiltrated "
        "to <code>192.0.2.190</code> (<code>N-074</code>). Outbound isolation halts secondary data theft, while internal isolation prevents ransomware propagation "
        "to student workstations or remaining administrative assets.<br/>"
        "&bull; <b>Action 2: Enterprise Identity Revocation & Credential Reset (Within 15 Minutes):</b><br/>"
        "  <i>Execution:</i> Invalidate all active OAuth/SSO session tokens on IdP (<code>P-027</code>, <code>A-038</code>). Globally disable service account "
        "<code>svc.sso</code> and administrative accounts <code>adm.lina</code> and <code>adm.rakan</code>. Enforce out-of-band administrative password resets with mandatory FIDO2 hardware tokens.<br/>"
        "  <i>Justification:</i> The attacker established persistence using <code>svc.sso</code> and hijacked Lina's credentials across all core servers.<br/>"
        "&bull; <b>Action 3: Physical Preservation of Offline Backup Media (Immediate):</b><br/>"
        "  <i>Execution:</i> Dispatch an on-site data center engineer to physically lock and airgap offline tape media <code>tape-04</code> "
        "(created 2026-12-11T23:00:00Z per <code>backup_report.txt</code> line 14). Do NOT mount or connect this media until clean infrastructure is stood up.<br/>"
        "  <i>Justification:</i> The adversary purged all 24 online disk snapshots (<code>E-044</code>). <code>tape-04</code> is the university's sole surviving recovery asset.<br/><br/>"
        "<b>2. Critical Examination Continuity Decision (D Morning Session: 07:30:00Z UTC, ~600 Students):</b><br/>"
        "&bull; <b>HONEST OPERATIONAL VERDICT: POSTPONE OR ACTIVATE PAPER CONTINGENCY IMMEDIATELY.</b><br/>"
        "&bull; <b>Technical Feasibility Justification:</b> The next exam session begins in exactly <b>3 hours, 24 minutes</b>. "
        "The examination file share is completely encrypted (<code>E-051</code>), the database has encrypted data files (<code>E-053</code>), and the application is failing requests (<code>P-042</code>). "
        "Historical restore evidence proves that the only attempted exam restore took <b>11 hours, 18 minutes and FAILED</b> due to a missing vault key (<code>backup_report.txt</code> line 21). "
        "Restoring 220+ GB of database and application storage from weekly offline tape media (<code>tape-04</code>), rebuilding corrupted schemas, validating exam questions, "
        "and conducting penetration smoke testing cannot physically occur in 3.4 hours. Attempting to run the session will result in massive student panic and exam invalidation.<br/>"
        "&bull; <b>Interim Contingency:</b> Postpone Session D morning by 24 hours or invoke the University Senate Emergency Paper Exam protocol for the ~600 enrolled candidates.<br/><br/>"
        "<b>3. Key Uncertainties & Unknowns Requiring Forensic Resolution:</b><br/>"
        "&bull; <b>Scope of Exfiltrated Data:</b> It is confirmed that 4.69 GB egressed to <code>192.0.2.190</code> (<code>N-074</code>). However, whether this archive contains "
        "upcoming exam question banks, student academic records, or employee financial data remains <b>Unknown</b> pending forensic carving and DLP analysis.<br/>"
        "&bull; <b>Web Shell / Secondary Backdoors on IdP & Exam-App:</b> The attacker maintained sustained access to IdP (<code>P-027</code>). It is unknown whether persistent "
        "web shells or cron backdoors were planted in DMZ web server directories.<br/>"
        "&bull; <b>Compromise of Vault Encryption Key:</b> The historical restore test failed because the backup encryption key was missing at <code>\\\\files\\ops\\vault\\</code>. "
        "It is currently unknown whether the vault key on <code>files</code> was encrypted by ransomware, exfiltrated, or permanently lost, which dictates whether offline tape media can be successfully decrypted."
    )
    story.append(Paragraph(exec_memo_text, body_style))
    story.append(Spacer(1, 10))
    
    # ---------------------------------------------------------
    # REFERENCES & FRAMEWORKS
    # ---------------------------------------------------------
    story.append(Paragraph("References, Standards, and Forensic Methodologies", h2_style))
    ref_text = (
        "1. <b>NIST SP 800-61 Rev. 2:</b> <i>Computer Security Incident Handling Guide</i>, National Institute of Standards and Technology.<br/>"
        "2. <b>NIST SP 800-207:</b> <i>Zero Trust Architecture</i> (Enforcing dynamic context-based policy and eliminating static trust rules).<br/>"
        "3. <b>MITRE ATT&CK Framework (Enterprise v14):</b> T1190 (Exploit Public-Facing Application), T1078 (Valid Accounts), T1021.001 (Remote Desktop Protocol), T1048 (Exfiltration Over Alternative Protocol), T1486 (Data Encrypted for Impact), T1490 (Inhibit System Recovery).<br/>"
        "4. <b>CIS Critical Security Controls v8:</b> Control 4 (Secure Configuration), Control 5 (Account Management), Control 6 (Access Control Management), Control 11 (Data Recovery).<br/>"
        "5. <b>ISO/IEC 27004:2016:</b> <i>Information technology - Security techniques - Information security management - Monitoring, measurement, analysis and evaluation</i>."
    )
    story.append(Paragraph(ref_text, body_style))
    
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated {pdf_filename}")

if __name__ == "__main__":
    create_report()
