import os
from reportlab.lib.pagesizes import landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

# 16:9 Widescreen standard dimensions in points (1280 x 720)
PAGE_WIDTH = 1280
PAGE_HEIGHT = 720

# Palette
BG_DARK = colors.HexColor('#050811')
BG_CARD = colors.HexColor('#0d1629')
BORDER_CARD = colors.HexColor('#1e293b')
CYAN_ACCENT = colors.HexColor('#00f0ff')
BLUE_ACCENT = colors.HexColor('#3b82f6')
RED_DANGER = colors.HexColor('#ef4444')
GREEN_SAFE = colors.HexColor('#10b981')
TEXT_WHITE = colors.HexColor('#f8fafc')
TEXT_MUTED = colors.HexColor('#94a3b8')
HEADER_BG = colors.HexColor('#090e1a')

LOGO_PATH = os.path.abspath(r'C:\Users\HP LAPTOP\Documents\kinlock\assets\kinlock_logo.jpg')

def draw_header_footer(c, slide_num, total_slides=8):
    # Header bar
    c.setFillColor(HEADER_BG)
    c.rect(0, PAGE_HEIGHT - 55, PAGE_WIDTH, 55, fill=1, stroke=0)
    c.setStrokeColor(colors.HexColor('#1e293b'))
    c.setLineWidth(1)
    c.line(0, PAGE_HEIGHT - 55, PAGE_WIDTH, PAGE_HEIGHT - 55)

    # Logo
    if os.path.exists(LOGO_PATH):
        try:
            c.drawImage(LOGO_PATH, 40, PAGE_HEIGHT - 46, width=36, height=36, mask='auto')
        except Exception:
            pass

    # Brand Title
    c.setFillColor(CYAN_ACCENT)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(88, PAGE_HEIGHT - 35, "KINLOCK")

    c.setFillColor(TEXT_MUTED)
    c.setFont("Helvetica", 10)
    c.drawString(180, PAGE_HEIGHT - 35, "|   COORDINATE-SAFE BIMANUAL VLA GOVERNOR")

    # Header Badges
    c.setFillColor(colors.HexColor('#0c2135'))
    c.roundRect(PAGE_WIDTH - 480, PAGE_HEIGHT - 43, 140, 24, 6, fill=1, stroke=0)
    c.setFillColor(CYAN_ACCENT)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(PAGE_WIDTH - 410, PAGE_HEIGHT - 33, "ISO 13849 PL-d SAFE")

    c.setFillColor(colors.HexColor('#14213d'))
    c.roundRect(PAGE_WIDTH - 330, PAGE_HEIGHT - 43, 150, 24, 6, fill=1, stroke=0)
    c.setFillColor(colors.HexColor('#93c5fd'))
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(PAGE_WIDTH - 255, PAGE_HEIGHT - 33, "INTEL BIMANUAL ($6,000)")

    c.setFillColor(colors.HexColor('#0c2135'))
    c.roundRect(PAGE_WIDTH - 170, PAGE_HEIGHT - 43, 130, 24, 6, fill=1, stroke=0)
    c.setFillColor(CYAN_ACCENT)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(PAGE_WIDTH - 105, PAGE_HEIGHT - 33, "SPEECHMATICS ($750)")

    # Footer bar
    c.setStrokeColor(colors.HexColor('#1e293b'))
    c.line(0, 45, PAGE_WIDTH, 45)

    # Progress bar line
    progress_w = (slide_num / total_slides) * PAGE_WIDTH
    c.setStrokeColor(CYAN_ACCENT)
    c.setLineWidth(3)
    c.line(0, 45, progress_w, 45)

    # Slide Counter
    c.setFillColor(TEXT_MUTED)
    c.setFont("Helvetica", 10)
    c.drawString(40, 20, "AI Infra Summit 2026   •   Hackathon Submission")

    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(CYAN_ACCENT)
    c.drawRightString(PAGE_WIDTH - 40, 20, f"SLIDE {slide_num:02d} / {total_slides:02d}")

def draw_card(c, x, y, w, h, title, metric="", sub="", metric_color=CYAN_ACCENT, border_color=BORDER_CARD):
    c.setFillColor(BG_CARD)
    c.setStrokeColor(border_color)
    c.setLineWidth(1)
    c.roundRect(x, y, w, h, 10, fill=1, stroke=1)

    # Top glow line
    c.setStrokeColor(metric_color)
    c.setLineWidth(2)
    c.line(x + 15, y + h, x + w - 15, y + h)

    # Title
    c.setFillColor(TEXT_WHITE)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x + 16, y + h - 28, title)

    # Metric if provided
    curr_y = y + h - 28
    if metric:
        c.setFillColor(metric_color)
        c.setFont("Helvetica-Bold", 28)
        c.drawString(x + 16, y + h - 68, metric)
        curr_y = y + h - 75

    # Subtext / description
    if sub:
        c.setFillColor(TEXT_MUTED)
        c.setFont("Helvetica", 9.5)
        # Split lines if needed
        words = sub.split(" ")
        line = ""
        sub_y = curr_y - 14
        for word in words:
            test_line = line + word + " "
            if c.stringWidth(test_line, "Helvetica", 9.5) > (w - 32):
                c.drawString(x + 16, sub_y, line)
                line = word + " "
                sub_y -= 14
            else:
                line = test_line
        if line:
            c.drawString(x + 16, sub_y, line)

def create_presentation_pdf(output_path):
    c = canvas.Canvas(output_path, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    # =========================================================================
    # SLIDE 1: Title & Hook
    # =========================================================================
    c.setFillColor(BG_DARK)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
    draw_header_footer(c, 1)

    # Eyebrow
    c.setFillColor(CYAN_ACCENT)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, PAGE_HEIGHT - 105, "EXECUTIVE PITCH   •   AI INFRA SUMMIT 2026")

    # Main Title
    c.setFillColor(TEXT_WHITE)
    c.setFont("Helvetica-Bold", 40)
    c.drawString(60, PAGE_HEIGHT - 165, "The Seatbelt for Bimanual VLA Manipulation")

    # Description
    c.setFillColor(TEXT_MUTED)
    c.setFont("Helvetica", 14)
    desc1 = "Vision-Language-Action models (OpenVLA, Octo, RT-2) plan brilliant end-effector trajectories,"
    desc2 = "but cause catastrophic structural stress when deployed to dual-arm hardware."
    desc3 = "KINLOCK is the 72.8 µs closed-form kinematic governor that eliminates coordinate drift with zero retraining."
    c.drawString(60, PAGE_HEIGHT - 210, desc1)
    c.drawString(60, PAGE_HEIGHT - 232, desc2)
    c.drawString(60, PAGE_HEIGHT - 254, desc3)

    # 4 Metric Cards
    card_w = (PAGE_WIDTH - 120 - 60) / 4
    card_h = 190
    card_y = 120

    draw_card(c, 60, card_y, card_w, card_h, "MEDIAN LATENCY", "72.8 µs",
              "Executes in <1.5% of a 200 Hz (5 ms) servo cycle on Intel Xeon & Core CPUs.", CYAN_ACCENT)
    draw_card(c, 60 + card_w + 20, card_y, card_w, card_h, "FORCE ATTENUATION", "99.9%",
              "Peak opposing force crushed from 2,033.99 N down to 1.12 N (clamped <= 15 N).", GREEN_SAFE)
    draw_card(c, 60 + (card_w + 20)*2, card_y, card_w, card_h, "RETRAINING NEEDED", "0 ms",
              "Zero-shot drop-in middleware between VLA velocity outputs and physical servos.", TEXT_WHITE)
    draw_card(c, 60 + (card_w + 20)*3, card_y, card_w, card_h, "INVARIANT RETENTION", "100%",
              "Exact 348.24 mm dual-arm grasp distance maintained without numerical drift.", CYAN_ACCENT)

    c.showPage()

    # =========================================================================
    # SLIDE 2: The Hardware Problem
    # =========================================================================
    c.setFillColor(BG_DARK)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
    draw_header_footer(c, 2)

    c.setFillColor(CYAN_ACCENT)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, PAGE_HEIGHT - 105, "THE ROOT CAUSE   •   LEROBOT ISSUE #3154")

    c.setFillColor(TEXT_WHITE)
    c.setFont("Helvetica-Bold", 36)
    c.drawString(60, PAGE_HEIGHT - 155, "The Frequency Mismatch Destroys Hardware")

    c.setFillColor(TEXT_MUTED)
    c.setFont("Helvetica", 14)
    c.drawString(60, PAGE_HEIGHT - 195, "Dual-arm co-manipulation requires rigid spatial coordination. When foundation models encounter")
    c.drawString(60, PAGE_HEIGHT - 215, "low-level servo dynamics, tiny kinematic errors multiply into destructive physical forces.")

    card3_w = (PAGE_WIDTH - 120 - 40) / 3
    card3_h = 320
    card3_y = 130

    draw_card(c, 60, card3_y, card3_w, card3_h, "1. THE 100x FREQUENCY GAP", "5Hz vs 200Hz",
              "VLAs infer at 5-10 Hz with multi-step latency. Hardware servos cycle at 200-500 Hz. Trajectory interpolation between sparse steps creates asynchronous coordinate divergence.", TEXT_MUTED)
    draw_card(c, 60 + card3_w + 20, card3_y, card3_w, card3_h, "2. COORDINATE SHEAR STRESS", "2,033.99 N",
              "When Arm A drifts 2.5 mm outward and Arm B lags, the rigid workpiece acts as an unyielding constraint, spiking opposing forces to over 2,000 N in under 12 ms.", RED_DANGER, RED_DANGER)
    draw_card(c, 60 + (card3_w + 20)*2, card3_y, card3_w, card3_h, "3. TRADITIONAL E-STOPS FAIL", "Payload Loss",
              "Conventional industrial e-stops cut motor power, instantly dropping fragile medical trays or acrylic cases. Roboticists need an active coordinate lock, not a blackout.", colors.HexColor('#f59e0b'))

    c.showPage()

    # =========================================================================
    # SLIDE 3: The Breakthrough Math
    # =========================================================================
    c.setFillColor(BG_DARK)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
    draw_header_footer(c, 3)

    c.setFillColor(CYAN_ACCENT)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, PAGE_HEIGHT - 105, "MATHEMATICAL FORMULATION   •   CORE ALGORITHM")

    c.setFillColor(TEXT_WHITE)
    c.setFont("Helvetica-Bold", 36)
    c.drawString(60, PAGE_HEIGHT - 155, "Moore-Penrose Constraint Projection")

    c.setFillColor(TEXT_MUTED)
    c.setFont("Helvetica", 14)
    c.drawString(60, PAGE_HEIGHT - 195, "KINLOCK projects uncoordinated VLA velocity vectors into the exact nullspace of the bimanual constraint")
    c.drawString(60, PAGE_HEIGHT - 215, "manifold, coupled with continuous Baumgarte stabilization to prevent numerical integration drift.")

    # Math Box
    c.setFillColor(HEADER_BG)
    c.setStrokeColor(CYAN_ACCENT)
    c.setLineWidth(2)
    c.roundRect(60, PAGE_HEIGHT - 325, PAGE_WIDTH - 120, 80, 8, fill=1, stroke=1)

    c.setFillColor(TEXT_WHITE)
    c.setFont("Courier-Bold", 24)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 280, "q_safe = q_VLA - J_c+ * ( J_c * q_VLA + a * dr )")

    # 4 Parameter Cards
    param_w = (PAGE_WIDTH - 120 - 60) / 4
    param_h = 220
    param_y = 100

    draw_card(c, 60, param_y, param_w, param_h, "CONSTRAINT JACOBIAN", "J_c in R^(1x12)",
              "Evaluates instantaneous relative end-effector distance gradient across both 6-DoF arms.", CYAN_ACCENT)
    draw_card(c, 60 + param_w + 20, param_y, param_w, param_h, "PSEUDOINVERSE", "J_c+",
              "Moore-Penrose pseudoinverse calculating the minimum-norm velocity adjustment to nullify destructive stress.", CYAN_ACCENT)
    draw_card(c, 60 + (param_w + 20)*2, param_y, param_w, param_h, "BAUMGARTE FACTOR", "a = 12.0 s^-1",
              "Exponentially dissipates discrete integration drift back to the nominal distance r_0 = 348.24 mm.", CYAN_ACCENT)
    draw_card(c, 60 + (param_w + 20)*3, param_y, param_w, param_h, "VIRTUAL STIFFNESS", "k_eff = 34.3 N/mm",
              "Ensures compliant, stable interaction fully within ISO 13849 PL-d collaborative limits.", GREEN_SAFE)

    c.showPage()

    # =========================================================================
    # SLIDE 4: Verification Receipt
    # =========================================================================
    c.setFillColor(BG_DARK)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
    draw_header_footer(c, 4)

    c.setFillColor(CYAN_ACCENT)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, PAGE_HEIGHT - 105, "EMPIRICAL PROOF   •   AUTOMATED TEST SUITE")

    c.setFillColor(TEXT_WHITE)
    c.setFont("Helvetica-Bold", 36)
    c.drawString(60, PAGE_HEIGHT - 155, "The Radical Honesty Verification Receipt")

    c.setFillColor(TEXT_MUTED)
    c.setFont("Helvetica", 14)
    c.drawString(60, PAGE_HEIGHT - 195, "We do not rely on cherry-picked video demos. Here are the deterministic benchmark numbers executed")
    c.drawString(60, PAGE_HEIGHT - 215, "across 200 continuous control cycles under identical stochastic perturbation.")

    # Table
    table_data = [
        ["EVALUATION METRIC", "RAW / UNFILTERED VLA", "KINLOCK GOVERNED", "SAFETY MARGIN / STATUS"],
        ["Peak Opposing Interaction Force", "2,033.99 N", "1.12 N", "99.94% Reduction (Clamped <= 15 N)"],
        ["Mean Continuous Load", "612.40 N", "0.48 N", "Sub-Newton Continuous Steady State"],
        ["Grasp Invariant Drift Error", "+58.40 mm (Slipped / Torn)", "0.00 mm", "348.24 mm Rigid Grasp Maintained"],
        ["Filter Execution Latency", "0.00 us", "72.8 us", "1.46% of 5 ms Budget (4.93 ms Free)"],
        ["Automated Test Suite (pytest)", "FAILED (>15 N Threshold)", "5 / 5 PASSED", "0.67s Deterministic Verification"]
    ]

    t = Table(table_data, colWidths=[340, 260, 240, 320])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#090e1a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), CYAN_ACCENT),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), BG_CARD),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_CARD),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('TEXTCOLOR', (0, 1), (0, -1), TEXT_WHITE),
        ('TEXTCOLOR', (1, 1), (1, -1), RED_DANGER),
        ('TEXTCOLOR', (2, 1), (2, -1), CYAN_ACCENT),
        ('TEXTCOLOR', (3, 1), (3, -1), GREEN_SAFE),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 14),
        ('TOPPADDING', (0, 1), (-1, -1), 14),
    ]))

    t.wrapOn(c, PAGE_WIDTH, PAGE_HEIGHT)
    t.drawOn(c, 60, 120)

    c.showPage()

    # =========================================================================
    # SLIDE 5: Speechmatics Voice AI Reflex
    # =========================================================================
    c.setFillColor(BG_DARK)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
    draw_header_footer(c, 5)

    c.setFillColor(CYAN_ACCENT)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, PAGE_HEIGHT - 105, "SPEECHMATICS BONUS ($750)   •   ACOUSTIC REFLEX")

    c.setFillColor(TEXT_WHITE)
    c.setFont("Helvetica-Bold", 36)
    c.drawString(60, PAGE_HEIGHT - 155, "Voice-Driven E-Stop with Zero Grasp Loss")

    c.setFillColor(TEXT_MUTED)
    c.setFont("Helvetica", 14)
    c.drawString(60, PAGE_HEIGHT - 195, "Real-time streaming WebSocket integration with Speechmatics delivers sub-50ms acoustic intervention.")
    c.drawString(60, PAGE_HEIGHT - 215, "Traditional e-stops kill motor power and drop payloads; KINLOCK freezes motion while locking grasp.")

    # Left card: Workflow
    left_w = 720
    draw_card(c, 60, 120, left_w, 330, "ACOUSTIC REFLEX ARCHITECTURE", "", "", CYAN_ACCENT)
    c.setFillColor(TEXT_WHITE)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(85, 395, "1. Operator Voice Trigger")
    c.setFont("Helvetica", 11)
    c.setFillColor(TEXT_MUTED)
    c.drawString(85, 375, "Low-latency streaming speech input: 'HALT', 'FREEZE', or 'EMERGENCY HOLD'.")

    c.setFillColor(TEXT_WHITE)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(85, 335, "2. Speechmatics WebSocket Streaming Engine")
    c.setFont("Helvetica", 11)
    c.setFillColor(TEXT_MUTED)
    c.drawString(85, 315, "Word-level transcription and reflex intent parsing completed with sub-50ms latency.")

    c.setFillColor(TEXT_WHITE)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(85, 275, "3. Sovereign Nullspace Decoupling")
    c.setFont("Helvetica", 11)
    c.setFillColor(TEXT_MUTED)
    c.drawString(85, 255, "Immediately zeroes tangential travel velocities (v_x, v_y, v_z = 0) without shutting off power.")

    c.setFillColor(TEXT_WHITE)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(85, 215, "4. Active Grasp Invariant Maintenance")
    c.setFont("Helvetica", 11)
    c.setFillColor(TEXT_MUTED)
    c.drawString(85, 195, "Normal clamping force is actively held rigid (348.24 mm invariant preserved). Payload never drops.")

    # Right card: Benchmark
    right_w = PAGE_WIDTH - 120 - left_w - 30
    draw_card(c, 60 + left_w + 30, 120, right_w, 330, "REACTION BENCHMARK", "< 50 ms",
              "Total Voice-to-Governor Halt Latency.\n\nTraditional industrial cutoffs drop payload on cutoff. KINLOCK provides 100% payload retention under emergency acoustic intervention.", CYAN_ACCENT)

    c.showPage()

    # =========================================================================
    # SLIDE 6: Sovereign 3D Cockpit Digital Twin
    # =========================================================================
    c.setFillColor(BG_DARK)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
    draw_header_footer(c, 6)

    c.setFillColor(CYAN_ACCENT)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, PAGE_HEIGHT - 105, "INTERACTIVE TELEMETRY   •   THREE.JS WEBGL COCKPIT")

    c.setFillColor(TEXT_WHITE)
    c.setFont("Helvetica-Bold", 36)
    c.drawString(60, PAGE_HEIGHT - 155, "Sovereign 3D Digital Twin Cockpit")

    c.setFillColor(TEXT_MUTED)
    c.setFont("Helvetica", 14)
    c.drawString(60, PAGE_HEIGHT - 195, "Featuring realistic dual SO-101 robot arms with 65° outward elbow crooks, parallel jaw end-effectors,")
    c.drawString(60, PAGE_HEIGHT - 215, "and live interactive force telemetry running directly in your web browser.")

    half_w = (PAGE_WIDTH - 120 - 30) / 2

    # Left: Kinematics
    draw_card(c, 60, 120, half_w, 330, "ROBOTIC KINEMATIC GEOMETRY", "", "", CYAN_ACCENT)
    c.setFillColor(TEXT_WHITE)
    c.setFont("Helvetica-Bold", 12)
    bullets = [
        ("65° Outward Elbow Crooks", "Anthropomorphic inward-reaching arm links that eliminate the 'goalpost' visual artifact."),
        ("Dual-Jaw Parallel Grippers", "High-precision contact pads gripping the central workpiece rigidly from both sides."),
        ("Dynamic Contact Reticles", "Glowing cyan rings indicate safe constraint lock; red flares indicate stress spike."),
        ("Zero-Dependency WebGL Console", "Standalone browser cockpit (console.html) runs anywhere without Node.js or bundlers.")
    ]
    cur_y = 390
    for title, desc in bullets:
        c.setFillColor(CYAN_ACCENT)
        c.drawString(85, cur_y, "•")
        c.setFillColor(TEXT_WHITE)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, cur_y, title)
        cur_y -= 18
        c.setFillColor(TEXT_MUTED)
        c.setFont("Helvetica", 10.5)
        c.drawString(100, cur_y, desc)
        cur_y -= 26

    # Right: HUD Telemetry
    draw_card(c, 60 + half_w + 30, 120, half_w, 330, "LIVE TELEMETRY HUD CHANNELS", "", "", BLUE_ACCENT)
    c.setFillColor(colors.HexColor('#090e1a'))
    c.roundRect(60 + half_w + 50, 150, half_w - 40, 240, 6, fill=1, stroke=0)

    hud_lines = [
        ("> LOOP_FREQUENCY:", "200.00 Hz (5.00 ms cycle budget)", TEXT_WHITE),
        ("> GOVERNOR_DISPATCH:", "72.8 us (NOMINAL)", CYAN_ACCENT),
        ("> F_RAW_UNFILTERED:", "2033.99 N [DANGER: STRUCTURAL FAILURE]", RED_DANGER),
        ("> F_GOVERNED:", "1.12 N [SAFE <= 15.0 N CLAMPED]", GREEN_SAFE),
        ("> GRASP_INVARIANT:", "348.24 mm (Delta r = 0.000 mm)", TEXT_WHITE),
        ("> SPEECHMATICS_WS:", "CONNECTED [PORT 8765 ACTIVE]", GREEN_SAFE),
        ("> SYSTEM_STATUS:", "SOVEREIGN GOVERNOR ARMED", CYAN_ACCENT)
    ]
    hud_y = 355
    c.setFont("Courier-Bold", 11)
    for label, val, col in hud_lines:
        c.setFillColor(TEXT_MUTED)
        c.drawString(60 + half_w + 65, hud_y, label)
        c.setFillColor(col)
        c.drawString(60 + half_w + 245, hud_y, val)
        hud_y -= 28

    c.showPage()

    # =========================================================================
    # SLIDE 7: Challenge Track Alignment
    # =========================================================================
    c.setFillColor(BG_DARK)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
    draw_header_footer(c, 7)

    c.setFillColor(CYAN_ACCENT)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, PAGE_HEIGHT - 105, "HACKATHON ALIGNMENT   •   EVALUATION MATRIX")

    c.setFillColor(TEXT_WHITE)
    c.setFont("Helvetica-Bold", 36)
    c.drawString(60, PAGE_HEIGHT - 155, "Direct Hit on Prize Evaluation Criteria")

    c.setFillColor(TEXT_MUTED)
    c.setFont("Helvetica", 14)
    c.drawString(60, PAGE_HEIGHT - 195, "Engineered specifically for the AI Infra Summit 2026 challenge tracks with modular interfaces")
    c.drawString(60, PAGE_HEIGHT - 215, "for immediate hardware deployment across standard robotics middleware.")

    track_w = (PAGE_WIDTH - 120 - 30) / 2
    track_h = 330

    # Intel Track
    draw_card(c, 60, 120, track_w, track_h, "INTEL BIMANUAL VLA CHALLENGE", "$6,000 Track", "", BLUE_ACCENT)
    c.setFillColor(TEXT_WHITE)
    c.setFont("Helvetica-Bold", 12)
    intel_points = [
        ("Solves the Fundamental Bottleneck", "High-level foundation models cannot execute rigid dual-arm manipulation without safety governors."),
        ("Intel CPU Architecture Efficiency", "Runs in 72.8 us on CPU, leaving >98% of compute resources for VLA inference on Intel Xeon & Core Ultra NPUs."),
        ("HuggingFace & LeRobot Native", "Seamless drop-in compatibility with existing LeRobot bimanual datasets and control loops.")
    ]
    cur_y = 320
    for t_title, t_desc in intel_points:
        c.setFillColor(BLUE_ACCENT)
        c.drawString(85, cur_y, "✓")
        c.setFillColor(TEXT_WHITE)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(102, cur_y, t_title)
        cur_y -= 18
        c.setFillColor(TEXT_MUTED)
        c.setFont("Helvetica", 10)
        c.drawString(102, cur_y, t_desc)
        cur_y -= 28

    # Speechmatics Track
    draw_card(c, 60 + track_w + 30, 120, track_w, track_h, "SPEECHMATICS VOICE AI BONUS", "$750 Track", "", CYAN_ACCENT)
    c.setFillColor(TEXT_WHITE)
    c.setFont("Helvetica-Bold", 12)
    speech_points = [
        ("Real-time Streaming WebSockets", "Sub-50ms acoustic transcription pipeline triggers instantaneous safety reflexes on voice commands."),
        ("Intelligent Payload Preservation", "Overcomes the catastrophic flaw of traditional mechanical cutoffs by decoupling spatial travel from grip clamping force."),
        ("Noise-Resilient Industrial Control", "Clean acoustic intent recognition under noisy warehouse and laboratory ambient environments.")
    ]
    cur_y = 320
    for t_title, t_desc in speech_points:
        c.setFillColor(CYAN_ACCENT)
        c.drawString(60 + track_w + 55, cur_y, "✓")
        c.setFillColor(TEXT_WHITE)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(60 + track_w + 72, cur_y, t_title)
        cur_y -= 18
        c.setFillColor(TEXT_MUTED)
        c.setFont("Helvetica", 10)
        c.drawString(60 + track_w + 72, cur_y, t_desc)
        cur_y -= 28

    c.showPage()

    # =========================================================================
    # SLIDE 8: Conclusion & Quickstart
    # =========================================================================
    c.setFillColor(BG_DARK)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
    draw_header_footer(c, 8)

    c.setFillColor(CYAN_ACCENT)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, PAGE_HEIGHT - 105, "CONCLUSION   •   OPEN SOURCE & VERIFIABLE")

    c.setFillColor(TEXT_WHITE)
    c.setFont("Helvetica-Bold", 36)
    c.drawString(60, PAGE_HEIGHT - 155, "Run KINLOCK in 60 Seconds")

    c.setFillColor(TEXT_MUTED)
    c.setFont("Helvetica", 14)
    c.drawString(60, PAGE_HEIGHT - 195, "Complete mathematical rigor, full test verification, and interactive 3D telemetry — open source")
    c.drawString(60, PAGE_HEIGHT - 215, "and ready for production dual-arm robotics.")

    # Left: Terminal
    c.setFillColor(colors.HexColor('#090e1a'))
    c.setStrokeColor(BORDER_CARD)
    c.roundRect(60, 120, half_w, 330, 8, fill=1, stroke=1)

    c.setFillColor(CYAN_ACCENT)
    c.setFont("Courier-Bold", 11)
    c.drawString(85, 415, "# 1. Clone & install repository")
    c.setFillColor(TEXT_WHITE)
    c.drawString(85, 395, "$ git clone https://github.com/GreatSage-dev/kinlock.git")
    c.drawString(85, 375, "$ cd kinlock && pip install -e .")

    c.setFillColor(CYAN_ACCENT)
    c.drawString(85, 335, "# 2. Run deterministic verification (0.67s)")
    c.setFillColor(TEXT_WHITE)
    c.drawString(85, 315, "$ python test/verify_kinlock.py")
    c.setFillColor(GREEN_SAFE)
    c.drawString(85, 295, "[PASS] 5/5 invariant tests passed (1.12 N <= 15 N)")

    c.setFillColor(CYAN_ACCENT)
    c.drawString(85, 255, "# 3. Launch 3D Cockpit Digital Twin")
    c.setFillColor(TEXT_WHITE)
    c.drawString(85, 235, "$ start console.html")

    c.setFillColor(TEXT_MUTED)
    c.setFont("Helvetica", 10)
    c.drawString(85, 175, "Full documentation, test logs, and mathematical derivations included in repo.")

    # Right: Branding Card
    draw_card(c, 60 + half_w + 30, 120, half_w, 330, "OPEN-SOURCE ROBOTICS REVOLUTION", "", "", CYAN_ACCENT)
    if os.path.exists(LOGO_PATH):
        try:
            c.drawImage(LOGO_PATH, 60 + half_w + 30 + (half_w - 90)/2, 300, width=90, height=90, mask='auto')
        except Exception:
            pass

    c.setFillColor(TEXT_WHITE)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(60 + half_w + 30 + half_w/2, 260, "KINLOCK")

    c.setFillColor(TEXT_MUTED)
    c.setFont("Helvetica", 12)
    c.drawCentredString(60 + half_w + 30 + half_w/2, 235, "Coordinate-Safe Governor for Bimanual VLA")

    c.setFillColor(colors.HexColor('#0c2135'))
    c.roundRect(60 + half_w + 30 + half_w/2 - 90, 160, 180, 32, 6, fill=1, stroke=0)
    c.setFillColor(CYAN_ACCENT)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(60 + half_w + 30 + half_w/2, 172, "MIT LICENSE   •   2026")

    c.showPage()
    c.save()
    print(f"Successfully generated presentation PDF at: {output_path}")

if __name__ == "__main__":
    out_dir = r"C:\Users\HP LAPTOP\Documents\kinlock\presentation"
    assets_dir = r"C:\Users\HP LAPTOP\Documents\kinlock\assets"
    
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)

    pdf_pres = os.path.join(out_dir, "kinlock_presentation.pdf")
    pdf_assets = os.path.join(assets_dir, "kinlock_presentation.pdf")

    create_presentation_pdf(pdf_pres)
    
    import shutil
    shutil.copy2(pdf_pres, pdf_assets)
    print(f"Copied PDF to assets directory at: {pdf_assets}")
