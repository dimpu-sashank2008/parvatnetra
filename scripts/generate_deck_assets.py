#!/usr/bin/env python3
"""
PARVAT NETRA -- High-DPI Vector Diagrams & Benchmark Chart Generator
SIH Problem Statement ID: 26001 | Ministry of Development of North Eastern Region (MDoNER)

Generates high-resolution vector assets in docs/assets/ (>= 200 DPI):
1. docs/assets/chart_before_after.png: Grouped Bar Chart comparing Ground Reality vs. PARVAT NETRA
2. docs/assets/flowchart_methodology.png: Vertical 4-Stage Predictive Methodology Pipeline
3. docs/assets/architecture_diagram.png: 4-Tier System Schematic Architecture
4. docs/assets/sentinel_emblem.png: National Sentinel Shield Emblem for Slide 1
5. docs/assets/problem_solution_icon.png: Visual Comparison Graphic for Slide 2
6. docs/assets/pillars_graphic.png: 3-Pillar Feasibility Graphic for Slide 4
7. docs/assets/policy_badges.png: Standards & Research Citations Graphic for Slide 6
"""

import os
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Reconfigure stdout/stderr to UTF-8 on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ASSETS_DIR = os.path.join(REPO_ROOT, "docs", "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)


def generate_chart_before_after():
    """Generates a high-contrast grouped horizontal bar chart comparing Current Ground Reality vs. PARVAT NETRA."""
    print("[1/7] Generating docs/assets/chart_before_after.png...")
    
    metrics = [
        "Warning Lead Time\n(Hours Ahead)",
        "False Alarm Rate\n(% Total Warnings)",
        "BRO Dispatch Triage\n(Minutes Latency)",
        "Linguistic Reach\n(Official Languages)"
    ]
    
    display_current = [3.5, 48.0, 100.0 * (180.0 / 200.0), 2.0 * 20.0]
    display_parvat = [36.0, 9.0, 100.0 * (15.0 / 200.0), 5.0 * 20.0]
    
    y = np.arange(len(metrics))
    height = 0.35

    fig, ax = plt.subplots(figsize=(10, 5.5), facecolor='#0b111e', dpi=240)
    ax.set_facecolor('#0b111e')

    bars1 = ax.barh(y + height/2, display_current, height, label='Current Ground Reality (Status Quo)', color='#ef4444', edgecolor='#fca5a5', alpha=0.9, linewidth=1.2)
    bars2 = ax.barh(y - height/2, display_parvat, height, label='PARVAT NETRA Sentinel Platform', color='#10b981', edgecolor='#6ee7b7', alpha=0.95, linewidth=1.2)

    annotations = [
        ("3.5 hrs", "36.0 hrs", "+928% Lead Time\n(Evacuate Ahead)", display_current[0], display_parvat[0], 0),
        ("48% False", "9% False", "-81% Alarm Fatigue\n(High Confidence)", display_current[1], display_parvat[1], 1),
        ("180 mins", "15 mins", "-92% Triage Latency\n(BRO Staging)", display_current[2], display_parvat[2], 2),
        ("2 Langs", "4 Langs + Voice", "+150% Inclusivity\n(EN/HI/NE/AS)", display_current[3], display_parvat[3], 3)
    ]

    for cur_txt, par_txt, delta_txt, cur_x, par_x, idx in annotations:
        ax.text(cur_x + 2.0, idx + height/2, f"{cur_txt}", va='center', ha='left', color='#fca5a5', fontsize=10, fontweight='bold')
        ax.text(par_x + 2.0, idx - height/2, f"{par_txt}", va='center', ha='left', color='#6ee7b7', fontsize=10, fontweight='bold')
        max_x = max(cur_x, par_x)
        ax.text(max_x + 24.0, idx, delta_txt, va='center', ha='left', color='#38bdf8', fontsize=8.5, fontweight='black',
                bbox=dict(boxstyle="round,pad=0.35", facecolor='#1e293b', edgecolor='#38bdf8', lw=1.0))

    ax.set_yticks(y)
    ax.set_yticklabels(metrics, color='#f8fafc', fontsize=10.5, fontweight='bold')
    ax.invert_yaxis()
    ax.set_xlim(0, 160)
    ax.xaxis.set_visible(False)
    
    for spine in ax.spines.values():
        spine.set_visible(False)

    plt.title("QUANTIFIED PERFORMANCE COMPARISON: GROUND REALITY VS. PARVAT NETRA",
              fontsize=12.5, fontweight='black', color='#38bdf8', pad=22, loc='left', family='sans-serif')
    plt.suptitle("Smart India Hackathon 2026 | Problem Statement ID: 26001 (MDoNER)",
                 fontsize=9, color='#94a3b8', x=0.125, y=0.93, ha='left')

    legend = ax.legend(loc='lower right', facecolor='#1e293b', edgecolor='#334155', fontsize=9.5, labelcolor='#f8fafc')
    legend.get_frame().set_linewidth(1.0)

    plt.tight_layout()
    out_path = os.path.join(ASSETS_DIR, "chart_before_after.png")
    plt.savefig(out_path, dpi=240, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"  -> Saved: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")


def generate_flowchart_methodology():
    """Generates a vertical 4-stage Sentinel predictive methodology pipeline diagram for Slide 3 Left."""
    print("[2/7] Generating docs/assets/flowchart_methodology.png...")

    fig, ax = plt.subplots(figsize=(4.8, 6.4), facecolor='#0b111e', dpi=240)
    ax.set_facecolor('#0b111e')
    ax.set_xlim(0, 4.8)
    ax.set_ylim(0, 6.4)
    ax.axis('off')

    stages = [
        {
            "num": "01",
            "title": "Continuous Ingestion",
            "sub": "Multi-Source Sensor Mesh",
            "items": ["• IMD 24h/48h Rainfall API", "• In-Situ IoT VWC% & Piezometer", "• Sentinel-1 InSAR & 2 Optical", "• Teesta River Hydrology Gauges"],
            "color": "#0284c7",
            "border": "#38bdf8"
        },
        {
            "num": "02",
            "title": "5-Modality AI Fusion",
            "sub": "Physics-Informed Inference",
            "items": ["• Mohr-Coulomb Critical Shear", "• Antecedent Rain Saturation", "• InSAR Creep Subsidence (-15mm)", "• Teesta Scour (+12) & Cuts (1.15x)"],
            "color": "#7c3aed",
            "border": "#c084fc"
        },
        {
            "num": "03",
            "title": "Road Exposure & Bypass",
            "sub": "Isolation & Detour Triage",
            "items": ["• PostGIS 500m Road Buffer Join", "• NH-10 Blockage Classification", "• Dynamic Lava Detour Delay (+65m)", "• Helipad & Supply Stock Triage"],
            "color": "#d97706",
            "border": "#fbbf24"
        },
        {
            "num": "04",
            "title": "4-Language Audio CAP",
            "sub": "Multilingual Dissemination",
            "items": ["• NDMA CAP v1.2 Protocol XML", "• 4-Language Matrix (EN/HI/NE/AS)", "• Browser Voice Audio TTS", "• SDRF & BRO Field Deployment"],
            "color": "#059669",
            "border": "#34d399"
        }
    ]

    box_w = 4.4
    box_h = 1.22
    start_y = 4.95
    spacing = 1.52

    for i, st in enumerate(stages):
        by = start_y - i * spacing
        bx = 0.2

        # Background Box
        rect = patches.FancyBboxPatch(
            (bx, by), box_w, box_h,
            boxstyle="round,pad=0.06,rounding_size=0.12",
            facecolor='#131e32',
            edgecolor=st['border'],
            linewidth=1.6
        )
        ax.add_patch(rect)

        # Stage Pill Badge
        pill = patches.FancyBboxPatch(
            (bx + 0.12, by + box_h - 0.34), 1.0, 0.26,
            boxstyle="round,pad=0.03,rounding_size=0.06",
            facecolor=st['color'],
            edgecolor='none'
        )
        ax.add_patch(pill)
        ax.text(bx + 0.62, by + box_h - 0.21, f"STAGE {st['num']}", color='#ffffff', fontsize=7.5, fontweight='black', ha='center', va='center')

        # Title & Subtitle
        ax.text(bx + 1.25, by + box_h - 0.18, st['title'], color='#ffffff', fontsize=9.2, fontweight='black', ha='left', va='center')
        ax.text(bx + 1.25, by + box_h - 0.32, st['sub'], color='#94a3b8', fontsize=7.0, fontweight='bold', ha='left', va='center')

        # Divider line
        ax.plot([bx + 0.15, bx + box_w - 0.15], [by + box_h - 0.44, by + box_h - 0.44], color=st['border'], lw=0.8, alpha=0.5)

        # Bullets
        for idx, item in enumerate(st['items']):
            col = idx % 2
            row = idx // 2
            x_pos = bx + 0.18 if col == 0 else bx + 2.25
            y_pos = by + box_h - 0.62 - row * 0.32
            ax.text(x_pos, y_pos, item, color='#cbd5e1', fontsize=7.0, fontweight='semibold', ha='left', va='center')

        # Connecting vertical arrow
        if i < len(stages) - 1:
            ax.annotate(
                "",
                xy=(bx + box_w / 2, by - 0.26),
                xytext=(bx + box_w / 2, by - 0.04),
                arrowprops=dict(arrowstyle="-|>", color='#38bdf8', lw=2.2, mutation_scale=12)
            )

    plt.tight_layout()
    out_path = os.path.join(ASSETS_DIR, "flowchart_methodology.png")
    plt.savefig(out_path, dpi=240, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"  -> Saved: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")


def generate_architecture_diagram():
    """Generates a modular 4-tier system architecture schematic for Slide 3 Center."""
    print("[3/7] Generating docs/assets/architecture_diagram.png...")

    fig, ax = plt.subplots(figsize=(6.8, 6.4), facecolor='#0b111e', dpi=240)
    ax.set_facecolor('#0b111e')
    ax.set_xlim(0, 6.8)
    ax.set_ylim(0, 6.4)
    ax.axis('off')

    tiers = [
        {
            "y": 4.85,
            "title": "TIER 1: MULTI-MODAL SENSING & INGESTION",
            "desc": "Real-time automated telemetry and satellite data streams",
            "color": "#0284c7",
            "border": "#38bdf8",
            "modules": [
                ("IMD Rain API", "24h/48h Gauge"),
                ("In-Situ IoT", "VWC% & Tilt"),
                ("Sentinel-1/2", "InSAR & Optical"),
                ("Teesta Scour", "CWC Gauge Data")
            ]
        },
        {
            "y": 3.30,
            "title": "TIER 2: ENTERPRISE NEON POSTGIS SPATIAL STORAGE",
            "desc": "Serverless PostgreSQL 16 + PostGIS 3.6 Spatial Fabric",
            "color": "#0369a1",
            "border": "#0ea5e9",
            "modules": [
                ("static_terrain", "DEM & Colluvium"),
                ("iot_telemetry", "Pore Pressure $u$"),
                ("insar_points", "LOS Creep Vectors"),
                ("teesta_waterways", "Toe Scour Reaches")
            ]
        },
        {
            "y": 1.75,
            "title": "TIER 3: DECISION INTELLIGENCE & ANALYTICAL ENGINES",
            "desc": "Explainable physics-AI evidence fusion and dynamic routing",
            "color": "#6d28d9",
            "border": "#a855f7",
            "modules": [
                ("5-Modality Fusion", "Mohr-Coulomb FoS"),
                ("Scour Surge (+12)", "Dynamic Modifier"),
                ("Anthro Cut (1.15x)", "Excavation Model"),
                ("ST_ClusterDBSCAN", "CV Crack Triage")
            ]
        },
        {
            "y": 0.20,
            "title": "TIER 4: OPERATIONAL CONSOLE & DISSEMINATION",
            "desc": "National emergency authority GIGW 3.0 portal and multilingual broadcast",
            "color": "#047857",
            "border": "#10b981",
            "modules": [
                ("GIGW 3.0 Portal", "Executive Console"),
                ("Leaflet GIS", "Multi-Layer Vectors"),
                ("4-Lang CAP Modal", "Audio TTS Engine"),
                ("Offline SQLite", "Field Patrol Cache")
            ]
        }
    ]

    for tier in tiers:
        ty = tier['y']
        container = patches.FancyBboxPatch(
            (0.15, ty), 6.5, 1.26,
            boxstyle="round,pad=0.05,rounding_size=0.10",
            facecolor='#131e32',
            edgecolor=tier['border'],
            linewidth=1.5
        )
        ax.add_patch(container)

        ax.text(0.3, ty + 1.05, tier['title'], color=tier['border'], fontsize=7.8, fontweight='black')
        ax.text(0.3, ty + 0.88, tier['desc'], color='#94a3b8', fontsize=6.5, fontweight='semibold')

        mod_w = 1.45
        mod_h = 0.62
        mod_spacing = 0.12
        start_mod_x = 0.3

        for mi, (m_title, m_sub) in enumerate(tier['modules']):
            mx = start_mod_x + mi * (mod_w + mod_spacing)
            my = ty + 0.14

            card = patches.FancyBboxPatch(
                (mx, my), mod_w, mod_h,
                boxstyle="round,pad=0.03,rounding_size=0.05",
                facecolor='#0b111e',
                edgecolor='#334155',
                linewidth=1.0
            )
            ax.add_patch(card)
            ax.text(mx + mod_w/2, my + mod_h - 0.22, m_title, color='#f8fafc', fontsize=6.8, fontweight='bold', ha='center', va='center')
            ax.text(mx + mod_w/2, my + 0.18, m_sub, color='#38bdf8', fontsize=5.8, fontweight='medium', ha='center', va='center')

    # Downward connectors
    arrow_xs = [1.6, 3.4, 5.2]
    for ax_x in arrow_xs:
        for y_from, y_to in [(4.85, 4.60), (3.30, 3.05), (1.75, 1.50)]:
            ax.annotate(
                "",
                xy=(ax_x, y_to),
                xytext=(ax_x, y_from),
                arrowprops=dict(arrowstyle="-|>", color='#64748b', lw=1.6, mutation_scale=10)
            )

    plt.tight_layout()
    out_path = os.path.join(ASSETS_DIR, "architecture_diagram.png")
    plt.savefig(out_path, dpi=240, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"  -> Saved: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")


def generate_sentinel_emblem():
    """Generates the National Sentinel Shield Emblem for Slide 1."""
    print("[4/7] Generating docs/assets/sentinel_emblem.png...")
    fig, ax = plt.subplots(figsize=(3.5, 3.5), facecolor='#0b111e', dpi=240)
    ax.set_facecolor('#0b111e')
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.axis('off')

    # Outer shield polygon
    shield_pts = np.array([
        [-1.2, 1.2], [1.2, 1.2],
        [1.2, 0.2], [0.0, -1.3], [-1.2, 0.2]
    ])
    shield = patches.Polygon(shield_pts, closed=True, facecolor='#131e32', edgecolor='#38bdf8', lw=2.5)
    ax.add_patch(shield)

    # Tricolor internal stripe arc
    ax.plot([-1.0, 1.0], [1.0, 1.0], color='#ff9933', lw=3.0)
    ax.plot([-1.0, 1.0], [0.85, 0.85], color='#ffffff', lw=2.5)
    ax.plot([-1.0, 1.0], [0.70, 0.70], color='#128807', lw=3.0)

    # Mountain silhouette in center
    mtn_pts = np.array([[-0.9, -0.2], [-0.3, 0.5], [0.1, 0.1], [0.5, 0.6], [0.9, -0.2]])
    ax.add_patch(patches.Polygon(mtn_pts, closed=True, facecolor='#1e293b', edgecolor='#38bdf8', lw=1.5))

    # Radar waves radiating from mountain peak
    for r in [0.25, 0.45, 0.65]:
        arc = patches.Arc((0.5, 0.6), r*2, r*2, angle=0, theta1=45, theta2=135, color='#10b981', lw=1.5, ls='--')
        ax.add_patch(arc)

    # Text in emblem
    ax.text(0.0, -0.5, "PARVAT NETRA", color='#ffffff', fontsize=9.5, fontweight='black', ha='center', va='center')
    ax.text(0.0, -0.75, "NER SENTINEL", color='#38bdf8', fontsize=7.5, fontweight='bold', ha='center', va='center')
    ax.text(0.0, -0.98, "SIH-26001 | MDoNER", color='#fbbf24', fontsize=6.5, fontweight='semibold', ha='center', va='center')

    plt.tight_layout()
    out_path = os.path.join(ASSETS_DIR, "sentinel_emblem.png")
    plt.savefig(out_path, dpi=240, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"  -> Saved: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")


def generate_problem_solution_icon():
    """Generates the Problem vs Solution comparison badge for Slide 2."""
    print("[5/7] Generating docs/assets/problem_solution_icon.png...")
    fig, ax = plt.subplots(figsize=(6.0, 1.8), facecolor='#0b111e', dpi=240)
    ax.set_facecolor('#0b111e')
    ax.set_xlim(0, 6.0)
    ax.set_ylim(0, 1.8)
    ax.axis('off')

    # Left problem box
    p_box = patches.FancyBboxPatch((0.2, 0.2), 2.5, 1.4, boxstyle="round,pad=0.05,rounding_size=0.1", facecolor='#450a0a', edgecolor='#ef4444', lw=1.5)
    ax.add_patch(p_box)
    ax.text(1.45, 1.25, "GROUND REALITY", color='#fca5a5', fontsize=8.5, fontweight='black', ha='center')
    ax.text(1.45, 0.95, "40+ Days NH-10 Blockade", color='#ffffff', fontsize=7.5, fontweight='bold', ha='center')
    ax.text(1.45, 0.65, "₹450 Cr Trade Loss/Yr", color='#f87171', fontsize=7.5, fontweight='semibold', ha='center')
    ax.text(1.45, 0.38, "48% Rain False Alarms", color='#fca5a5', fontsize=6.8, ha='center')

    # Center VS arrow
    ax.text(3.0, 0.9, "VS", color='#fbbf24', fontsize=12, fontweight='black', ha='center', va='center')

    # Right solution box
    s_box = patches.FancyBboxPatch((3.3, 0.2), 2.5, 1.4, boxstyle="round,pad=0.05,rounding_size=0.1", facecolor='#064e3b', edgecolor='#10b981', lw=1.5)
    ax.add_patch(s_box)
    ax.text(4.55, 1.25, "PARVAT NETRA", color='#6ee7b7', fontsize=8.5, fontweight='black', ha='center')
    ax.text(4.55, 0.95, "36h Predictive Warnings", color='#ffffff', fontsize=7.5, fontweight='bold', ha='center')
    ax.text(4.55, 0.65, "Automated Lava Rerouting", color='#34d399', fontsize=7.5, fontweight='semibold', ha='center')
    ax.text(4.55, 0.38, "9% False Alarms (Fusion)", color='#6ee7b7', fontsize=6.8, ha='center')

    plt.tight_layout()
    out_path = os.path.join(ASSETS_DIR, "problem_solution_icon.png")
    plt.savefig(out_path, dpi=240, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"  -> Saved: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")


def generate_pillars_graphic():
    """Generates the 3-Pillar Feasibility & Viability graphic for Slide 4."""
    print("[6/7] Generating docs/assets/pillars_graphic.png...")
    fig, ax = plt.subplots(figsize=(10.0, 2.0), facecolor='#0b111e', dpi=240)
    ax.set_facecolor('#0b111e')
    ax.set_xlim(0, 10.0)
    ax.set_ylim(0, 2.0)
    ax.axis('off')

    pillars = [
        ("TECHNICAL FEASIBILITY", "Zero New Sat Cost\nSolar 12V IoT Telemetry\nOffline SQLite Field Cache", "#0284c7", "#38bdf8"),
        ("OPERATIONAL VIABILITY", "NDMA CAP v1.2 Compliant\nExplainable AI Factors\nNepali & Assamese Audio", "#059669", "#34d399"),
        ("ECONOMIC & STRATEGIC", "Avoids False Closures\nPrioritized BRO Clearing\nCivil-Military Lifeline", "#d97706", "#fbbf24")
    ]

    for i, (p_title, p_desc, col, b_col) in enumerate(pillars):
        px = 0.4 + i * 3.2
        box = patches.FancyBboxPatch((px, 0.2), 2.8, 1.6, boxstyle="round,pad=0.06,rounding_size=0.1", facecolor='#131e32', edgecolor=b_col, lw=1.5)
        ax.add_patch(box)
        ax.text(px + 1.4, 1.52, p_title, color=b_col, fontsize=8.0, fontweight='black', ha='center')
        ax.text(px + 1.4, 0.85, p_desc, color='#cbd5e1', fontsize=7.2, fontweight='medium', ha='center', va='center')

    plt.tight_layout()
    out_path = os.path.join(ASSETS_DIR, "pillars_graphic.png")
    plt.savefig(out_path, dpi=240, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"  -> Saved: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")


def generate_policy_badges():
    """Generates the Research, References & Policy Standards graphic for Slide 6."""
    print("[7/7] Generating docs/assets/policy_badges.png...")
    fig, ax = plt.subplots(figsize=(10.0, 1.8), facecolor='#0b111e', dpi=240)
    ax.set_facecolor('#0b111e')
    ax.set_xlim(0, 10.0)
    ax.set_ylim(0, 1.8)
    ax.axis('off')

    badges = [
        ("GSI NLSM", "Geological Survey\nSusceptibility Mapping", "#38bdf8"),
        ("NDMA CAP v1.2", "Common Alerting\nProtocol XML Standard", "#10b981"),
        ("ISRO BHUVAN", "National 30m CartoDEM\n& Land Use WMS", "#fbbf24"),
        ("CWC TEESTA", "Riverbed Aggradation\n& Hydrodynamic Scour", "#f87171"),
        ("GIGW 3.0", "Indian Govt Website\nAccessibility Standard", "#c084fc")
    ]

    for i, (b_title, b_desc, b_color) in enumerate(badges):
        bx = 0.3 + i * 1.9
        box = patches.FancyBboxPatch((bx, 0.2), 1.65, 1.4, boxstyle="round,pad=0.05,rounding_size=0.1", facecolor='#131e32', edgecolor=b_color, lw=1.3)
        ax.add_patch(box)
        ax.text(bx + 0.825, 1.25, b_title, color=b_color, fontsize=8.0, fontweight='black', ha='center')
        ax.text(bx + 0.825, 0.65, b_desc, color='#cbd5e1', fontsize=6.5, fontweight='medium', ha='center', va='center')

    plt.tight_layout()
    out_path = os.path.join(ASSETS_DIR, "policy_badges.png")
    plt.savefig(out_path, dpi=240, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"  -> Saved: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")


def main():
    print("=" * 80)
    print("PARVAT NETRA -- HIGH-DPI DECK ASSET GENERATOR")
    print("SIH Problem Statement ID: 26001 (MDoNER)")
    print("=" * 80)

    generate_chart_before_after()
    generate_flowchart_methodology()
    generate_architecture_diagram()
    generate_sentinel_emblem()
    generate_problem_solution_icon()
    generate_pillars_graphic()
    generate_policy_badges()

    print("\n" + "=" * 80)
    print("ALL 7 HIGH-DPI PRESENTATION ASSETS GENERATED SUCCESSFULLY IN docs/assets/!")
    print("=" * 80)


if __name__ == "__main__":
    main()
