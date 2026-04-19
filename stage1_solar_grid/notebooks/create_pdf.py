"""
EnergyFlux Presentation for NVIDIA — 5 pages, AI-centric.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch, Rectangle
import matplotlib.image as mpimg
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "processed"
OUT_DIR = Path(__file__).parent

DARK = "#042C53"
BLUE = "#185FA5"
RED = "#E24B4A"
GREEN = "#1D9E75"
TEAL = "#0A8F8F"
GRAY = "#888780"
LGRAY = "#C8C7C2"
LIGHT = "#F5F5F0"
WHITE = "#FFFFFF"
ACCENT = "#F0A030"
NVIDIA = "#76B900"  # NVIDIA green

pdf_path = OUT_DIR / "EnergyFlux_Stage1_Overview.pdf"


def rbox(ax, x, y, w, h, color, alpha=1.0, r=0.1):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad={r}",
                                facecolor=color, edgecolor="none", alpha=alpha))

def header(ax, text):
    ax.add_patch(Rectangle((0, 8.3), 16, 0.7, facecolor=DARK, edgecolor="none"))
    ax.text(0.5, 8.55, text, fontsize=20, fontweight="bold",
            color=WHITE, va="center", fontfamily="sans-serif")


with PdfPages(str(pdf_path)) as pdf:

    # ══════════════════════════════════════════════════════════
    # PAGE 1: Title — AI-first framing
    # ══════════════════════════════════════════════════════════
    fig = plt.figure(figsize=(16, 9))
    fig.patch.set_facecolor(DARK)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 16); ax.set_ylim(0, 9); ax.axis("off")
    ax.set_facecolor(DARK)

    ax.text(8, 7.6, "EnergyFlux", fontsize=52, fontweight="bold",
            color=WHITE, ha="center", fontfamily="sans-serif")
    ax.text(8, 6.7, "AI-Powered Energy Intelligence Platform",
            fontsize=22, color=NVIDIA, ha="center", fontfamily="sans-serif",
            fontweight="bold")
    ax.plot([3.5, 12.5], [6.3, 6.3], color=TEAL, linewidth=2, alpha=0.4)

    ax.text(8, 5.7, "Physics simulation generates real-time energy data.\n"
            "AI agents understand, diagnose, and optimize the system.",
            fontsize=16, color="#99AABB", ha="center", fontfamily="sans-serif",
            linespacing=1.6)

    # 4 metric cards with AI emphasis
    cards = [
        ("185 kWp", "Bifacial Solar PV", "pvlib physics model", BLUE),
        ("400 kWh", "Battery Storage", "TOU rate optimization", GREEN),
        ("17,518", "Grid Simulations", "pandapower NR solver", TEAL),
        ("NVIDIA NIM", "AI Diagnosis Agent", "Nemotron-Ultra + RAG", NVIDIA),
    ]
    for i, (val, label, tech, color) in enumerate(cards):
        x = 0.8 + i * 3.8
        rbox(ax, x, 3.3, 3.2, 1.8, color, alpha=0.15, r=0.15)
        ax.add_patch(Rectangle((x, 4.7), 3.2, 0.4, facecolor=color,
                               edgecolor="none", alpha=0.6))
        ax.text(x + 1.6, 4.9, label, fontsize=11, fontweight="bold",
                color=WHITE, ha="center", va="center")
        ax.text(x + 1.6, 4.15, val, fontsize=24, fontweight="bold",
                color=WHITE, ha="center", va="center")
        ax.text(x + 1.6, 3.6, tech, fontsize=10, color="#88AACC",
                ha="center", va="center")

    ax.text(8, 2.2, "Solar Forecasting  →  PV Modeling  →  BESS Dispatch  →  Power Flow  →  AI Diagnosis",
            fontsize=13, color="#667788", ha="center", fontfamily="sans-serif")

    ax.plot([3.5, 12.5], [1.7, 1.7], color=TEAL, linewidth=1, alpha=0.3)
    ax.text(8, 1.1, "Chennan Li, PhD, PE",
            fontsize=14, color="#556677", ha="center", fontfamily="sans-serif")

    pdf.savefig(fig, facecolor=DARK)
    plt.close()

    # ══════════════════════════════════════════════════════════
    # PAGE 2: Architecture — AI at every layer
    # ══════════════════════════════════════════════════════════
    fig = plt.figure(figsize=(16, 9))
    fig.patch.set_facecolor(WHITE)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 16); ax.set_ylim(0, 9); ax.axis("off")
    header(ax, "System Architecture  —  AI Integrated at Every Layer")

    # Three columns: Physics | Data | AI
    cols = [
        ("PHYSICS ENGINE", "Simulation & Modeling", BLUE, [
            ("pvlib", "PV cell-level modeling\n4 configurations compared"),
            ("pandapower", "Newton-Raphson power flow\n17,518 hourly grid solutions"),
            ("BESS Model", "SOC dynamics, efficiency\nTOU rate-aware dispatch"),
        ]),
        ("DATA PIPELINE", "Collection & Processing", TEAL, [
            ("Open-Meteo API", "2-year weather history\nGHI, DNI, temperature, wind"),
            ("Time-Series DB", "Hourly PV output, load\nbus voltages, line loading"),
            ("Knowledge Base", "Engineering docs, specs\nFault patterns, O&M guides"),
        ]),
        ("AI / ML LAYER", "Intelligence & Decision", NVIDIA, [
            ("NHITS Neural Net", "Solar irradiance forecast\n24-hour ahead prediction"),
            ("NVIDIA Nemotron", "ReAct reasoning agent\nAutonomous tool calling"),
            ("FAISS RAG", "Vector similarity search\nGrounded diagnosis output"),
        ]),
    ]

    for ci, (title, subtitle, color, items) in enumerate(cols):
        x = 0.5 + ci * 5.2
        # Column header
        rbox(ax, x, 7.2, 4.6, 0.8, color, alpha=0.9)
        ax.text(x + 2.3, 7.7, title, fontsize=14, fontweight="bold",
                color=WHITE, ha="center", va="center")
        ax.text(x + 2.3, 7.35, subtitle, fontsize=10,
                color="#DDEEEE", ha="center", va="center")

        # Items
        for ii, (name, desc) in enumerate(items):
            y = 6.3 - ii * 1.6
            rbox(ax, x, y - 0.4, 4.6, 1.3, color, alpha=0.07)
            ax.add_patch(Rectangle((x, y - 0.4), 0.08, 1.3,
                                   facecolor=color, edgecolor="none"))
            ax.text(x + 0.3, y + 0.5, name, fontsize=13, fontweight="bold",
                    color=DARK, va="center")
            ax.text(x + 0.3, y, desc, fontsize=10, color=GRAY,
                    va="center", linespacing=1.4)

    # Arrows between columns
    for ci in range(2):
        x = 5.1 + ci * 5.2
        for yi in range(3):
            y = 6.1 - yi * 1.6
            ax.text(x, y, "→", fontsize=20, color=LGRAY, ha="center", va="center")

    # Bottom: data flow
    ax.add_patch(Rectangle((0, 0), 16, 0.9, facecolor=LIGHT, edgecolor="none"))
    ax.text(8, 0.45, "Data Flow:   Weather → Forecast (AI) → PV Generation (Physics) → "
            "BESS Dispatch → Power Flow (Physics) → Anomaly Detection → AI Diagnosis (NVIDIA NIM)",
            fontsize=11, color=DARK, ha="center", va="center", fontfamily="sans-serif")

    pdf.savefig(fig)
    plt.close()

    # ══════════════════════════════════════════════════════════
    # PAGE 3: Power Flow Results
    # ══════════════════════════════════════════════════════════
    fig = plt.figure(figsize=(16, 9))
    fig.patch.set_facecolor(WHITE)

    ax_h = fig.add_axes([0, 0.93, 1, 0.07])
    ax_h.set_xlim(0, 1); ax_h.set_ylim(0, 1); ax_h.axis("off")
    ax_h.add_patch(Rectangle((0, 0), 1, 1, facecolor=DARK, edgecolor="none"))
    ax_h.text(0.03, 0.5, "Simulation Results  —  Power Flow + BESS + Voltage Analysis",
              fontsize=16, fontweight="bold", color=WHITE, va="center")

    ax_m = fig.add_axes([0, 0.87, 1, 0.06])
    ax_m.set_xlim(0, 16); ax_m.set_ylim(0, 1); ax_m.axis("off")
    ax_m.add_patch(Rectangle((0, 0), 16, 1, facecolor=LIGHT, edgecolor="none"))

    metrics = [
        ("5,363 hrs overvoltage (31%)", RED),
        ("Peak: 1.074 pu (limit 1.05)", ACCENT),
        ("BESS: 239 cycles, TOU arbitrage", GREEN),
        ("Lines: max 75% loading (safe)", BLUE),
    ]
    for i, (text, color) in enumerate(metrics):
        x = 0.4 + i * 4
        ax_m.add_patch(Rectangle((x - 0.05, 0.2), 0.06, 0.6,
                                  facecolor=color, edgecolor="none"))
        ax_m.text(x + 0.15, 0.5, text, fontsize=11, fontweight="bold",
                  color=DARK, va="center")

    plot_path = DATA_DIR / "powerflow_plot.png"
    if plot_path.exists():
        ax_img = fig.add_axes([0.01, 0.01, 0.98, 0.85])
        img = mpimg.imread(str(plot_path))
        ax_img.imshow(img)
        ax_img.axis("off")

    pdf.savefig(fig)
    plt.close()

    # ══════════════════════════════════════════════════════════
    # PAGE 4: AI Agent Deep Dive (FULL PAGE FOR NVIDIA)
    # ══════════════════════════════════════════════════════════
    fig = plt.figure(figsize=(16, 9))
    fig.patch.set_facecolor(WHITE)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 16); ax.set_ylim(0, 9); ax.axis("off")

    # NVIDIA green header
    ax.add_patch(Rectangle((0, 8.3), 16, 0.7, facecolor=NVIDIA, edgecolor="none"))
    ax.text(0.5, 8.55, "AI Agent in Action  —  Powered by NVIDIA NIM  (Nemotron-Ultra-253B)",
            fontsize=20, fontweight="bold", color=WHITE, va="center")

    # Left: Complete agent workflow
    ax.text(0.5, 7.8, "Autonomous Root Cause Analysis", fontsize=17, fontweight="bold",
            color=DARK)
    ax.text(0.5, 7.4, "The agent receives an alert, decides what to investigate, calls tools,\n"
            "and produces a structured diagnosis — no human in the loop.",
            fontsize=11, color=GRAY, linespacing=1.4)

    # Alert
    rbox(ax, 0.4, 6.2, 9.2, 0.7, RED, alpha=0.12)
    ax.add_patch(Rectangle((0.4, 6.2), 0.08, 0.7, facecolor=RED, edgecolor="none"))
    ax.text(0.7, 6.55, "TRIGGER:  Overvoltage detected — PV bus 1.068 pu > 1.05 limit  |  BESS SOC 90%",
            fontsize=11, fontweight="bold", color=RED, va="center")

    # 4 tool calls with results
    steps = [
        ("1", "query_weather()", "Clear sky, GHI 930 W/m²",
         "Max solar irradiance → PV at full capacity", BLUE),
        ("2", "query_pv_status()", "PV = 135 kW, Load = 57 kW",
         "78 kW surplus with nowhere to go", BLUE),
        ("3", "query_powerflow()", "PV bus 1.068 pu, reverse flow",
         "Surplus pushes through 300m cable → voltage rise", RED),
        ("4", "query_knowledge_base()", "RAG: overvoltage pattern match",
         "Historical: midday + clear + full BESS = classic scenario", TEAL),
    ]
    for i, (num, tool, data, insight, color) in enumerate(steps):
        y = 5.5 - i * 1.05
        rbox(ax, 0.5, y - 0.25, 0.4, 0.5, color, alpha=0.9, r=0.15)
        ax.text(0.7, y, num, fontsize=14, fontweight="bold",
                color=WHITE, ha="center", va="center")
        ax.text(1.1, y + 0.1, tool, fontsize=11, fontweight="bold",
                color=DARK, fontfamily="monospace")
        ax.text(3.8, y + 0.1, data, fontsize=11, color=DARK)
        ax.text(1.1, y - 0.2, insight, fontsize=10, color=GRAY, style="italic")

    # Diagnosis output
    rbox(ax, 0.4, 0.6, 9.2, 1.1, GREEN, alpha=0.12)
    ax.add_patch(Rectangle((0.4, 0.6), 0.08, 1.1, facecolor=GREEN, edgecolor="none"))
    ax.text(0.7, 1.45, "AI OUTPUT  (structured JSON)", fontsize=12, fontweight="bold", color=GREEN)
    ax.text(0.7, 1.05, "Root Cause:  PV surplus (78kW) + saturated BESS → uncontrolled reverse power flow → voltage rise",
            fontsize=10.5, color=DARK)
    ax.text(0.7, 0.75, "Actions:  ① Increase BESS to 200kW/800kWh   ② Enable inverter VAR support   ③ Shift EV charging to midday",
            fontsize=10.5, color=DARK)

    # Right: Tech stack + what NVIDIA enables
    ax.text(10.2, 7.8, "NVIDIA Technology Stack", fontsize=17, fontweight="bold",
            color=DARK)

    nvidia_stack = [
        ("NVIDIA NIM", "API endpoint for\nNemotron-Ultra inference", "Cloud or on-prem\ndeployment ready", NVIDIA),
        ("Nemotron-Ultra\n253B", "Tool-calling LLM\nReAct reasoning loop", "Decides WHAT to\ninvestigate and WHY", DARK),
        ("LangChain\nReAct Agent", "Orchestrates multi-step\ntool calls autonomously", "No predefined\nrules — LLM decides", BLUE),
        ("FAISS RAG", "Vector search over\nengineering knowledge base", "Grounds answers\nin real documents", TEAL),
    ]
    for i, (name, desc, benefit, color) in enumerate(nvidia_stack):
        y = 6.8 - i * 1.35
        rbox(ax, 10.2, y - 0.3, 5.3, 1.1, color, alpha=0.08)
        ax.add_patch(Rectangle((10.2, y - 0.3), 0.08, 1.1,
                               facecolor=color, edgecolor="none"))
        ax.text(10.5, y + 0.4, name, fontsize=12, fontweight="bold",
                color=DARK, linespacing=1.2)
        ax.text(12.2, y + 0.4, desc, fontsize=10, color=GRAY, linespacing=1.3)
        ax.text(14.0, y + 0.4, benefit, fontsize=10, color=color,
                fontweight="bold", linespacing=1.3)

    # Bottom: key differentiator
    ax.add_patch(Rectangle((10.2, 0.6), 5.3, 0.9, facecolor=NVIDIA, edgecolor="none",
                            alpha=0.1))
    ax.text(12.85, 1.05, "Why NVIDIA NIM?", fontsize=12, fontweight="bold",
            color=NVIDIA, ha="center")
    ax.text(12.85, 0.75, "Enterprise-ready  ·  On-prem deployable  ·  No OpenAI dependency  ·  GPU-optimized inference",
            fontsize=10, color=DARK, ha="center")

    pdf.savefig(fig)
    plt.close()

    # ══════════════════════════════════════════════════════════
    # PAGE 5: AI Roadmap — What's Next
    # ══════════════════════════════════════════════════════════
    fig = plt.figure(figsize=(16, 9))
    fig.patch.set_facecolor(WHITE)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 16); ax.set_ylim(0, 9); ax.axis("off")

    ax.add_patch(Rectangle((0, 8.3), 16, 0.7, facecolor=DARK, edgecolor="none"))
    ax.text(0.5, 8.55, "AI Expansion Roadmap  —  From Diagnosis to Autonomous Optimization",
            fontsize=20, fontweight="bold", color=WHITE, va="center")

    # Current: single agent
    ax.text(0.5, 7.7, "TODAY: Single Agent — Reactive Diagnosis", fontsize=16,
            fontweight="bold", color=GREEN)
    rbox(ax, 0.5, 6.5, 15, 1.0, GREEN, alpha=0.08)
    ax.add_patch(Rectangle((0.5, 6.5), 0.08, 1.0, facecolor=GREEN, edgecolor="none"))
    ax.text(0.8, 7.15, "Alert triggers agent  →  Agent investigates autonomously  →  "
            "Structured diagnosis + recommended actions",
            fontsize=12, color=DARK)
    ax.text(0.8, 6.75, "NVIDIA NIM  ·  Nemotron-Ultra  ·  4 tools  ·  RAG knowledge base  ·  "
            "JSON output for downstream automation",
            fontsize=11, color=GRAY)

    # Next: multi-agent + optimization
    ax.text(0.5, 6.0, "NEXT: Multi-Agent System — Proactive Optimization", fontsize=16,
            fontweight="bold", color=BLUE)

    agents = [
        ("Forecast Agent", "Predicts tomorrow's PV output\n+ load demand using weather forecast",
         "Pre-positions BESS SOC for\nexpected surplus/deficit", BLUE),
        ("Dispatch Agent", "Optimizes BESS charge/discharge\nschedule against TOU electricity rates",
         "Pyomo LP solver + LLM\nfor constraint interpretation", TEAL),
        ("Grid Agent", "Monitors voltage and loading\nin real-time across all buses",
         "Triggers corrective action\nbefore limits are reached", RED),
        ("Coordinator", "Orchestrates all agents, resolves\nconflicts between objectives",
         "Multi-agent consensus via\nNVIDIA NIM inference", NVIDIA),
    ]
    for i, (name, desc, capability, color) in enumerate(agents):
        x = 0.5 + i * 3.85
        rbox(ax, x, 3.5, 3.5, 2.2, color, alpha=0.08)
        ax.add_patch(Rectangle((x, 5.3), 3.5, 0.4, facecolor=color,
                               edgecolor="none", alpha=0.7))
        ax.text(x + 1.75, 5.5, name, fontsize=12, fontweight="bold",
                color=WHITE, ha="center", va="center")
        ax.text(x + 0.2, 4.9, desc, fontsize=10, color=DARK, linespacing=1.4)
        ax.text(x + 0.2, 3.9, capability, fontsize=10, color=color,
                fontweight="bold", linespacing=1.4)

    # Arrows between agents
    for i in range(3):
        x = 4.0 + i * 3.85
        ax.text(x, 4.5, "↔", fontsize=18, color=LGRAY, ha="center", va="center")

    # Vision
    ax.text(0.5, 2.9, "VISION: Autonomous Energy Management", fontsize=16,
            fontweight="bold", color=DARK)

    rbox(ax, 0.5, 1.2, 15, 1.4, DARK, alpha=0.05)
    vision_text = (
        "Physics simulation provides the ground truth.  AI agents provide the intelligence.\n"
        "The platform evolves from reactive (diagnose after alert) to predictive (forecast + pre-position)\n"
        "to autonomous (optimize in real-time without human intervention).\n"
        "All inference powered by NVIDIA NIM — deployable on-premise for industrial data privacy."
    )
    ax.text(8, 1.9, vision_text, fontsize=12, color=DARK, ha="center",
            va="center", linespacing=1.6, fontfamily="sans-serif")

    # Tech footer
    ax.add_patch(Rectangle((0, 0), 16, 0.7, facecolor=NVIDIA, edgecolor="none", alpha=0.1))
    ax.text(8, 0.35, "Powered by:  NVIDIA NIM  ·  Nemotron-Ultra  ·  LangChain  ·  FAISS  ·  "
            "pvlib  ·  pandapower  ·  Pyomo  ·  FastAPI",
            fontsize=11, color=DARK, ha="center", va="center")

    pdf.savefig(fig)
    plt.close()

print(f"PDF saved: {pdf_path}")
