"""Build blog1_v20.pdf from blog1_v20.md with styling matched to v19."""
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Image,
    Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from reportlab.platypus.flowables import Flowable, KeepInFrame
from reportlab.lib.colors import HexColor

# ---- Theme ----
BLUE = HexColor("#1F4E79")          # section headers and table header fill
BLUE_LIGHT = HexColor("#DEEBF7")    # hero box + alt row shade
BLUE_BORDER = HexColor("#9DC3E6")   # hero box border
TEXT = HexColor("#222222")
MUTED = HexColor("#666666")
RULE = HexColor("#BFBFBF")
HEADER_TEXT = colors.white

# ---- Doc template with footer ----
FOOTER_TEXT = "Chennan Li, PhD, PE  |  EnergyFlux  |  April 2026  |  Page"

class NumberedDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kw):
        super().__init__(filename, **kw)
        frame = Frame(
            self.leftMargin, self.bottomMargin,
            self.width, self.height,
            id="body", showBoundary=0,
        )
        self.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=self._footer)])

    def _footer(self, canv, doc):
        canv.saveState()
        canv.setFont("Helvetica", 9)
        canv.setFillColor(MUTED)
        w = LETTER[0]
        canv.drawCentredString(w / 2.0, 0.55 * inch, f"{FOOTER_TEXT} {doc.page}")
        canv.restoreState()

# ---- Styles ----
styles = getSampleStyleSheet()

STYLE_TITLE = ParagraphStyle(
    "Title", parent=styles["Heading1"],
    fontName="Helvetica-Bold", fontSize=20, textColor=BLUE,
    leading=24, spaceAfter=4, spaceBefore=0, alignment=TA_LEFT,
)
STYLE_SUBTITLE = ParagraphStyle(
    "Subtitle", parent=styles["Normal"],
    fontName="Helvetica", fontSize=12, textColor=TEXT,
    leading=16, spaceAfter=2,
)
STYLE_BYLINE = ParagraphStyle(
    "Byline", parent=styles["Italic"],
    fontName="Helvetica-Oblique", fontSize=10, textColor=MUTED,
    leading=14, spaceAfter=0,
)
STYLE_H2 = ParagraphStyle(
    "H2", parent=styles["Heading2"],
    fontName="Helvetica-Bold", fontSize=14, textColor=BLUE,
    leading=18, spaceBefore=18, spaceAfter=8, keepWithNext=1,
)
STYLE_H3 = ParagraphStyle(
    "H3", parent=styles["Heading3"],
    fontName="Helvetica-Bold", fontSize=11, textColor=BLUE,
    leading=15, spaceBefore=10, spaceAfter=4, keepWithNext=1,
)
STYLE_BODY = ParagraphStyle(
    "Body", parent=styles["Normal"],
    fontName="Helvetica", fontSize=10.5, textColor=TEXT,
    leading=14.5, spaceAfter=8, alignment=TA_JUSTIFY,
)
STYLE_BULLET = ParagraphStyle(
    "Bullet", parent=STYLE_BODY,
    leftIndent=18, bulletIndent=6, spaceAfter=4, alignment=TA_LEFT,
)
STYLE_CAPTION = ParagraphStyle(
    "Caption", parent=styles["Italic"],
    fontName="Helvetica-Oblique", fontSize=9, textColor=MUTED,
    leading=12, spaceAfter=10, alignment=TA_JUSTIFY,
)
STYLE_TABLE_TITLE = ParagraphStyle(
    "TableTitle", parent=styles["Normal"],
    fontName="Helvetica-Bold", fontSize=10.5, textColor=TEXT,
    leading=14, spaceBefore=8, spaceAfter=4, keepWithNext=1,
)
STYLE_FIGTITLE = ParagraphStyle(
    "FigTitle", parent=STYLE_TABLE_TITLE, spaceBefore=12,
)
STYLE_SRC = ParagraphStyle(
    "Source", parent=styles["Normal"],
    fontName="Helvetica", fontSize=8.5, textColor=TEXT,
    leading=11.5, spaceAfter=6, alignment=TA_LEFT, leftIndent=14, firstLineIndent=-14,
)
STYLE_HERO_BIG = ParagraphStyle(
    "HeroBig", parent=styles["Normal"],
    fontName="Helvetica-Bold", fontSize=24, textColor=BLUE,
    leading=30, alignment=TA_CENTER, spaceAfter=0,
)
STYLE_HERO_SUB = ParagraphStyle(
    "HeroSub", parent=styles["Normal"],
    fontName="Helvetica", fontSize=10, textColor=TEXT,
    leading=13, alignment=TA_CENTER, spaceAfter=4,
)
STYLE_HERO_ITALIC = ParagraphStyle(
    "HeroItalic", parent=styles["Italic"],
    fontName="Helvetica-Oblique", fontSize=10, textColor=TEXT,
    leading=13, alignment=TA_CENTER,
)


def hero_box():
    """Return a flowable for the 5–8 years → 4–7 months hero box."""
    inner = [
        Spacer(1, 8),
        Paragraph("5–8 years &nbsp;&nbsp;&rarr;&nbsp;&nbsp; 4–7 months", STYLE_HERO_BIG),
        Spacer(1, 6),
        Paragraph("Traditional hyperscale path vs behind-the-meter on existing industrial land", STYLE_HERO_SUB),
        Spacer(1, 4),
        Paragraph("<i>Here's my thinking.</i>", STYLE_HERO_ITALIC),
        Spacer(1, 8),
    ]
    t = Table([[inner]], colWidths=[6.5*inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BLUE_LIGHT),
        ("BOX", (0,0), (-1,-1), 1, BLUE_BORDER),
        ("LEFTPADDING", (0,0), (-1,-1), 14),
        ("RIGHTPADDING", (0,0), (-1,-1), 14),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    return t


def styled_table(data, col_widths, header_rows=1):
    """Create a table with blue header, alternating light row fills."""
    t = Table(data, colWidths=col_widths, repeatRows=header_rows, hAlign="LEFT")
    style = [
        ("BACKGROUND", (0,0), (-1,header_rows-1), BLUE),
        ("TEXTCOLOR", (0,0), (-1,header_rows-1), HEADER_TEXT),
        ("FONTNAME", (0,0), (-1,header_rows-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8.5),
        ("LEADING", (0,0), (-1,-1), 10.5),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 5),
        ("RIGHTPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("GRID", (0,0), (-1,-1), 0.25, RULE),
        ("FONTNAME", (0,header_rows), (-1,-1), "Helvetica"),
    ]
    # alt rows
    for r in range(header_rows, len(data)):
        if (r - header_rows) % 2 == 1:
            style.append(("BACKGROUND", (0,r), (-1,r), HexColor("#F4F7FB")))
    t.setStyle(TableStyle(style))
    return t


def P(text, style=STYLE_BODY):
    return Paragraph(text, style)


# ---- Build content ----
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
FIG1 = os.path.join(_HERE, "blog1_fig1_architecture.jpg")
FIG2 = os.path.join(_HERE, "blog1_fig2_sitecount.png")

story = []

# Title
story.append(Paragraph("Turning industrial safety buffers into AI inference sites", STYLE_TITLE))
story.append(Paragraph("Part 1: Can industrial mandatory vacancy ease the AI infrastructure bottleneck?", STYLE_SUBTITLE))
story.append(Paragraph("Chennan Li, PhD, PE &nbsp;&mdash;&nbsp; April 2026", STYLE_BYLINE))
story.append(HRFlowable(width="100%", thickness=0.5, color=RULE, spaceBefore=4, spaceAfter=14))

# Hero box
story.append(hero_box())
story.append(Spacer(1, 18))

# --- 1.1 ---
story.append(Paragraph("1.1 &nbsp; Data center buildout challenges", STYLE_H2))
story.append(P(
    "Building AI data centers (or AI factories) seems to be getting harder. We are hearing long "
    "environmental reviews, limited water resources, multi-year waits for gas turbines and transformers, "
    "local noise complaints. And even after all of that is bypassed, the capital cost is heavy, and "
    "recent events &mdash; the first confirmed military attack on hyperscale data centers in the UAE "
    "and Bahrain in March 2026 [16] &mdash; have made it clear that the centralized hyperscaler model "
    "carries a real network-concentration risk. Table 1 summarizes these."
))
story.append(Paragraph("Table 1. The bottlenecks shaping AI infrastructure today", STYLE_TABLE_TITLE))

t1 = [
    ["Constraint", "Current reality", "Timeline impact"],
    ["Grid interconnection", "12,000+ projects queued across US ISOs and utilities", "3–7 year wait"],
    ["Environmental review (CEQA/NEPA)", "Multi-year EIS process", "2–5 year delay"],
    ["Water permit", "Contested in drought regions", "1–3 year delay"],
    ["Gas turbine (backup power)", "Global procurement backlog", "18–36 month lead time"],
    ["Large transformer (100 MVA+)", "Manufacturer capacity limits", "24–36 month lead time"],
    ["Community opposition", "Noise, visual, cooling footprint", "Unpredictable"],
    ["Capital concentration / attack surface", "March 2026: military strike on hyperscale sites in UAE/Bahrain", "Structural vulnerability"],
]
story.append(styled_table(t1, col_widths=[2.1*inch, 2.8*inch, 1.6*inch]))
story.append(Spacer(1, 10))

# --- 1.2 ---
story.append(Paragraph("1.2 &nbsp; Inference is different from training", STYLE_H2))
story.append(P(
    "One thing worth questioning: most of the talk about AI data centers treats them as a single "
    "category regardless of workload. Both Jensen Huang (NVIDIA) and Andrew Feldman (Cerebras) have "
    "pointed out that inference, not training, will dominate AI compute over the long run. Huang has "
    "stated explicitly that inference will be roughly <b>80% of long-term AI compute</b> versus about "
    "20% for training, that inference already makes up more than 40% of NVIDIA's data center revenue "
    "today, and that overall inference demand is &ldquo;about to go up by a billion times&rdquo; as AI "
    "gets embedded into everyday work and consumer applications [17]. Feldman has made the "
    "directionally same point from the Cerebras side, calling inference &ldquo;the dominant cost and "
    "performance bottleneck in AI&rdquo; [18]."
))
story.append(P(
    "The implication for infrastructure is important. A single NVIDIA Vera Rubin NVL72 rack holds "
    "20.7 TB of HBM4 [2] &mdash; enough to host a GPT-4-class model in memory on one rack. Cerebras "
    "CS-3 reaches a similar outcome through a wafer-scale architecture with 21 PB/s on-chip memory "
    "bandwidth [12]. If those numbers hold, inference does not need the same scale of infrastructure "
    "as training: a four-rack modular AI factory could run frontier models with redundancy in a "
    "footprint smaller than a single-family home, drawing 500 kW to 20 MW. More importantly, such "
    "factories could be distributed to every city, close to the users."
))

story.append(Paragraph("Table 2. Rack sizing reference — what each deployment can run", STYLE_TABLE_TITLE))

t2 = [
    ["Size tier", "Racks", "HBM4 total", "IT power", "What this can run"],
    ["Small", "1–2", "20–40 TB", "0.2–0.4 MW",
     "Single frontier model such as GPT-4 or Claude 3 Opus-class (~1–2T params); serves ~10K–100K users (small city, industrial park). 2 racks give N+1 redundancy."],
    ["Medium", "4–6", "80–125 TB", "0.8–1.1 MW",
     "Current frontier models (GPT-5, Claude 4, Llama 4 405B) with multiple concurrent instances; serves ~100K–500K users (a mid-sized city)."],
    ["Large", "9–25", "185–515 TB", "1.7–4.8 MW",
     "Multiple models running in parallel (GPT-5 + Claude 4 + DeepSeek R1), including reasoning models with long context; serves ~500K–2M users (a large metro)."],
    ["XL", "33–74", "680 TB – 1.5 PB", "6–14 MW",
     "Next-generation models (10T+ parameters) at hyperscaler-class throughput; serves 2M+ users (a major metro area such as Chicago, Houston, or a multi-city region)."],
]
# wrap long cell contents in Paragraphs so they wrap
cell_style = ParagraphStyle("cell", parent=STYLE_BODY, fontSize=8.5, leading=10.5, spaceAfter=0, alignment=TA_LEFT)
for i in range(1, len(t2)):
    t2[i][4] = Paragraph(t2[i][4], cell_style)
story.append(styled_table(t2, col_widths=[0.7*inch, 0.55*inch, 1.0*inch, 0.85*inch, 3.4*inch]))
story.append(Paragraph(
    "All based on NVIDIA Vera Rubin NVL72 at 190 kW / 20.7 TB HBM4 per rack [2, 3]. Cerebras CS-3 offers "
    "an alternative architecture at ~23–30 kW per system with 44 GB on-chip SRAM plus optional MemoryX for "
    "larger models [12]. Cerebras has demonstrated Llama 3.1 405B and DeepSeek R1 in production.",
    STYLE_CAPTION,
))

# --- 1.3 ---
story.append(Paragraph("1.3 &nbsp; An idea: industrial plants as hosts", STYLE_H2))
story.append(P(
    "That raises a question: why not co-locate these smaller AI factories inside existing industrial "
    "plants, operating <b>behind the meter</b>?"
))
story.append(P(
    "Most industrial plants already have what a modular AI factory needs &mdash; water for cooling, an "
    "established electrical service sized for peak operations, on-site fiber for process control, 24/7 "
    "staff, and physical security. The size of the AI factory at any given site is not a product "
    "specification to be sold off the shelf. It is sized to whatever the host site can actually "
    "support: how much electrical capacity is left in the existing service, how much water is available "
    "for cooling, how much regulated buffer land can host solar PV and battery storage, and how much "
    "local inference demand the site is well-positioned to serve. Different host plants will end up "
    "with very different factory sizes for legitimate physical reasons, not because some universal "
    "rack count happens to fit."
))
story.append(P(
    "To make the electrical question concrete, take the municipal wastewater treatment plant (WWTP) "
    "case that Part 2 will examine in detail. A typical 30 MGD WWTP has a mean process load near 2.5 MW "
    "and a daily peak around 3.0 MW. Its existing utility service is usually a 5 MW or larger feed at "
    "12 to 34.5 kV, sized to cover storm-flow peaks and motor inrush with a comfortable margin. Adding "
    "a 1 to 2 MW AI factory often fits inside that existing margin during normal operations. When it "
    "does not &mdash; a hot afternoon when blower demand spikes while the AI factory is running at "
    "full inference load &mdash; the buffer-zone PV and a 4-hour BESS can close the gap. If even that "
    "is insufficient, the next step is a distribution-level service upgrade: a transformer swap or a "
    "feeder reconductor that takes the service from, say, 5 MW up to 7 or 8 MW. That kind of upgrade "
    "is treated as a routine commercial service modification by the utility, on a 4- to 7-month "
    "timeline [13], rather than a brand-new transmission interconnection, which typically takes 3 to "
    "7 years."
))
story.append(P(
    "The site also does not need to handle every possible demand spike on its own. Inference traffic "
    "is bursty by nature, and there are conditions under which the on-site envelope will tighten "
    "&mdash; a heat wave that pushes both the plant and the AI factory toward peak power at the same "
    "time, an extended overcast week that suppresses PV output, or a feeder maintenance event. In "
    "those windows, the inference router simply shifts the overflow portion of incoming requests to a "
    "hyperscaler API in a major region. The local racks continue serving the steady-state portion of "
    "demand at sub-5 ms latency; the overflow portion accepts the higher latency of a remote "
    "hyperscaler in exchange for guaranteed capacity. Crucially, the host plant's own operations are "
    "never put at risk by the AI factory. Because the AI factory is classified as load-side equipment "
    "behind the plant's existing meter, the plant operator can curtail or disconnect it at any time "
    "without affecting the regulated process &mdash; exactly the same way a plant would shed a "
    "non-critical load during a utility demand event."
))
story.append(P(
    "Put together, this pattern flips several items in Table 1 &mdash; no new grid interconnection, "
    "no new land acquisition, no new water permit, no standalone transformer procurement, fewer "
    "residential neighbors to object to, and a distributed footprint in place of a single concentrated "
    "attack surface. <b>The approval pathway collapses from 5–8 years to 4–7 months</b> because no new "
    "utility infrastructure is being added beyond what a routine commercial service upgrade can "
    "handle. The AI factory is load-side equipment on an existing commercial service, which is "
    "regulatorily routine."
))

story.append(Paragraph("Figure 1. Distributed AI inference architecture on an industrial buffer zone", STYLE_FIGTITLE))
img1 = Image(FIG1, width=6.4*inch, height=3.78*inch)
story.append(img1)
story.append(Paragraph(
    "Industrial plant sits in the center of the site (grey, existing); the AI factory occupies a small "
    "corner adjacent to the plant. The regulated safety buffer zone surrounds the plant and hosts the "
    "PV array (most of the buffer) plus a small 4-hour BESS. Local residents live outside the buffer. "
    "The AI factory serves metropolitan-area users &mdash; hundreds of thousands to millions of people "
    "within ~20 km &mdash; at sub-5 ms latency. Peak traffic and failover route to a hyperscaler API.",
    STYLE_CAPTION,
))

# --- 1.4 ---
story.append(Paragraph("1.4 &nbsp; Checking the numbers", STYLE_H2))
story.append(P(
    "An idea needs numbers to back it up. The following is a set of first-principles estimates across "
    "eight typical industrial site categories. Each type carries its own mandatory land requirements "
    "for fire access, firewater monitor coverage, operational exclusion zones, and RMP/PSM/NFPA safety "
    "setbacks &mdash; for example, a typical WWTP reserves roughly 10–20% of its regulated area for "
    "fire access and operational clearance, a large petrochemical complex closer to 40–50% (process "
    "units, tank farm berms, loading racks). That mandatory portion is set aside, and only the "
    "remaining usable area is counted for PV. Rack counts assume Vera Rubin NVL72 at 190 kW per rack "
    "[3]. Results are in Table 3 and Figure 2."
))

story.append(Paragraph("Table 3. Industrial site types: US counts and infrastructure readiness", STYLE_TABLE_TITLE))
story.append(Paragraph(
    "All estimates assume single-axis tracking PV and Vera Rubin NVL72 at 190 kW per rack [3]. "
    "AI factory sized to match annual PV generation for PV-matched sites; small chemical plant relies "
    "primarily on grid headroom with PV as supplement. Workload tiers refer to Table 2. Bracketed "
    "numbers [N] reference the Sources list at the end.",
    STYLE_CAPTION,
))

t3 = [
    ["Site type", "US count", "Total regulated area", "Usable buffer", "PV capacity", "Racks", "Grid voltage", "Fiber availability", "Suitable workload tier"],
    ["Small–medium specialty chemical", "~1,200 [1,4]", "3–18 ha", "1.5–9 ha", "1.2–6 MW", "4–6", "34.5–69 kV", "Usually good (industrial parks)", "Medium: ~100K–500K users"],
    ["Large petrochemical complex", "~80 [5]", "~500 ha", "~150 ha", "~101 MW", "~74", "110–220 kV", "Excellent", "XL: 2M+ users"],
    ["Pharmaceutical API plant", "~200 [6]", "~20 ha", "~10 ha", "~6.7 MW", "6", "34.5–69 kV", "Excellent (biotech clusters)", "Medium: ~100K–500K users"],
    ["Ammonia / fertilizer plant", "~30 [7]", "~30 ha", "~15 ha", "~10 MW", "9", "69 kV", "Limited (rural)", "Large: ~500K–2M users"],
    ["Food processing (NH3 refrig.)", "~1,500 [8]", "~6 ha", "~3 ha", "~2 MW", "2", "34.5 kV", "Mixed (rural poor / suburban OK)", "Small: ~10K–100K users"],
    ["Large refrigerated cold storage", "~1,000 [9]", "~4 ha", "~2 ha", "~1.5 MW", "1–2", "12–34.5 kV", "Good (logistics hubs)", "Small: ~10K–100K users"],
    ["WWTP — mid-to-large (10–1,000 MGD)", "~1,500 [10]", "10–150 ha", "5–67 ha", "3–45 MW", "2–25", "34.5–138 kV", "Excellent (always urban)", "Small to Large; up to a major metro"],
    ["LNG terminal", "~170 [11]", "~150 ha", "~60 ha", "~40 MW", "33", "69–138 kV", "Variable (coastal)", "XL: 2M+ users"],
]

# Wrap cells (small font so it fits landscape-ish)
cell_s = ParagraphStyle("cellS", parent=STYLE_BODY, fontSize=7.3, leading=9, spaceAfter=0, alignment=TA_LEFT)
header_s = ParagraphStyle("hdrS", parent=STYLE_BODY, fontSize=7.6, leading=9.3, spaceAfter=0, alignment=TA_LEFT, textColor=HEADER_TEXT, fontName="Helvetica-Bold")
t3_wrapped = [[Paragraph(c, header_s) for c in t3[0]]]
for row in t3[1:]:
    t3_wrapped.append([Paragraph(c, cell_s) for c in row])

col_w3 = [1.15*inch, 0.6*inch, 0.7*inch, 0.6*inch, 0.6*inch, 0.4*inch, 0.65*inch, 0.85*inch, 1.1*inch]
t3_table = Table(t3_wrapped, colWidths=col_w3, repeatRows=1, hAlign="LEFT")
t3_style = [
    ("BACKGROUND", (0,0), (-1,0), BLUE),
    ("VALIGN", (0,0), (-1,-1), "TOP"),
    ("LEFTPADDING", (0,0), (-1,-1), 3),
    ("RIGHTPADDING", (0,0), (-1,-1), 3),
    ("TOPPADDING", (0,0), (-1,-1), 3),
    ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ("GRID", (0,0), (-1,-1), 0.25, RULE),
]
for r in range(1, len(t3_wrapped)):
    if (r - 1) % 2 == 1:
        t3_style.append(("BACKGROUND", (0,r), (-1,r), HexColor("#F4F7FB")))
t3_table.setStyle(TableStyle(t3_style))
story.append(t3_table)

story.append(Paragraph("Figure 2. US site count vs. theoretical aggregate AI factory opportunity", STYLE_FIGTITLE))
img2 = Image(FIG2, width=6.4*inch, height=3.13*inch)
story.append(img2)
story.append(Paragraph(
    "At 10–30% adoption across these categories, aggregate capacity is roughly 3,850–11,550 Vera Rubin "
    "NVL72-equivalent racks &mdash; about 7–21% of US AI data center capacity currently under "
    "construction for 2026–2027 (Sightline Climate 2026 Data Center Outlook [14]). Midpoint ~15% "
    "contribution to near-term in-construction capacity.",
    STYLE_CAPTION,
))

story.append(P(
    "<b>What this looks like across sites.</b> Municipal wastewater treatment plants stand out for "
    "sheer distribution &mdash; essentially every US city has one, they are always urban or suburban "
    "with mature grid and fiber, and 1,500 mid-to-large sites are spread across the country. Large "
    "petrochemical complexes are technically strongest (110–220 kV substations, extensive internal "
    "fiber) but carry organizational friction and concentrate on the Gulf Coast. Pharmaceutical API "
    "plants cluster in four biotech corridors (Princeton–New Brunswick, Boston–Cambridge, Research "
    "Triangle, Indianapolis). Ammonia/fertilizer plants have the most buffer land per site but often "
    "lack rural fiber. Food processing and cold storage are numerous but small per-site &mdash; best "
    "for 1–2 rack deployments close to users. The opportunity concentrates where fiber, buffer land, "
    "and grid voltage align &mdash; it is not uniform."
))
story.append(P(
    "This model is also consistent with Cerebras's own deployment pattern &mdash; their facilities "
    "range from 2.5 MW (Stockton, CA) to a planned 100 MW in Guyana co-located with a gas-to-energy "
    "plant, rather than gigawatt campuses [12]. The distributed, modular, co-located approach is "
    "already being validated at scale by inference-focused AI hardware vendors."
))

story.append(Paragraph("Notes on each site type", STYLE_H3))
for label, body in [
    ("Pharmaceutical API manufacturing.",
     "Sites cluster in biotech corridors (Princeton–New Brunswick, Boston–Cambridge, Research Triangle, "
     "Indianapolis) where fiber and grid are solid. Pfizer Kalamazoo, Merck Rahway, Novartis East "
     "Hanover, Eli Lilly Indianapolis are examples. Formulation-only plants have much smaller solvent "
     "inventories and correspondingly smaller buffers, so they are not the interesting subset."),
    ("WWTPs.",
     "Every US city has one. Always urban or suburban, so fiber is available and grid service is "
     "mature. The trade-off is municipal ownership &mdash; ground leases require city council approval "
     "and potentially competitive RFP processes, which is slow."),
    ("Food processing.",
     "Two populations. Large meatpacking plants (Tyson, JBS, Cargill, Smithfield) are rural &mdash; "
     "near livestock, far from metro fiber. A Tyson beef plant in Lexington, Nebraska has solid grid "
     "capacity (megawatts of refrigeration load) but limited high-bandwidth fiber. New fiber runs can "
     "be 12–18 months and meaningful capex. Dairy and cold storage facilities, by contrast, are often "
     "suburban near population centers and regional logistics hubs; fiber is usually fine."),
    ("Ammonia / fertilizer plants.",
     "Largest per-site buffers among manufacturing but located near cheap natural gas, which means "
     "rural (Louisiana, Iowa, Oklahoma). Fiber is a real gap at most of these sites."),
    ("LNG terminals.",
     "Coastal, some remote. Gulf Coast terminals generally have good fiber via the petrochemical "
     "corridor backbone. East Coast import terminals are better connected. Alaska and outlier "
     "locations are questionable."),
    ("Large petrochemical complexes.",
     "Best on every technical dimension: 110–220 kV dedicated substations, extensive internal fiber "
     "for process control, excellent external fiber. The constraint is political &mdash; these are "
     "high-value operating assets and any buffer-zone change goes through extensive HAZOP review."),
]:
    story.append(P(f"<b>{label}</b> {body}"))

# --- 1.5 ---
story.append(Paragraph("1.5 &nbsp; Economics: different value, not necessarily more expensive", STYLE_H2))
story.append(P(
    "Cost is the obvious follow-up question. The honest answer: it depends on the site, and a precise "
    "per-token comparison requires a full site-level model. Rough first-principles bounds can at least "
    "frame what's plausible."
))
story.append(P(
    "<b>Electricity cost range.</b> A Vera Rubin NVL72 rack draws ~190 kW at ~1.3 PUE, so roughly "
    "2,160 MWh per rack per year."
))

bullets_15 = [
    "<i>Lower-bound (hyperscale PPA):</i> $0.04–$0.06/kWh via long-term renewable PPAs. Microsoft, "
    "Amazon, and Meta routinely lock rates in this range at large scale.",
    "<i>Upper-bound (US average industrial rate):</i> $0.08–$0.12/kWh, paid by smaller operators "
    "without PPA scale.",
    "<i>Distributed BTM PV+BESS (site-specific):</i> published utility-scale LCOE is $0.045–$0.065/kWh "
    "for solar+4hr storage [15]. Smaller deployments (1–20 MW) typically run 20–40% higher. Night "
    "hours still require grid draw, so the effective blended rate lands somewhere around "
    "$0.06–$0.09/kWh depending on site solar resource and utility backup cost.",
]
for b in bullets_15:
    story.append(Paragraph(f"&bull;&nbsp;&nbsp;{b}", STYLE_BULLET))

story.append(P(
    "The conclusion: on electricity cost alone, the distributed model is plausibly competitive with a "
    "non-PPA hyperscale operator, and somewhat more expensive than a top-tier hyperscale with a 20-year "
    "renewable PPA. Call it within &plusmn;20–30% of hyperscale electricity cost."
))
story.append(P(
    "<b>Capex and lifecycle.</b> What tilts in favor of the distributed model is <b>infrastructure "
    "lifecycle mismatch</b>. PV arrays last 25–30 years. BESS lasts 10–15 years. AI hardware lasts 3–5 "
    "years before a GPU refresh. A behind-the-meter PV+BESS installation built once can support 4–6 "
    "generations of GPU hardware refresh on the same site &mdash; rack replacement only, no new grid "
    "interconnection, no new transformer procurement, no new substation, no new land. By contrast, "
    "each major hyperscale expansion typically requires new utility infrastructure with multi-year "
    "lead times."
))
story.append(P(
    "<b>20-year TCO bounds (rough).</b> Putting electricity and infrastructure together, a 20-year "
    "per-rack TCO comparison lands in a wide band &mdash; distributed could be anywhere from 10–20% "
    "cheaper (if the site has good solar resource + cheap colocation lease + multiple GPU refresh "
    "cycles) to 10–20% more expensive (if the site has poor solar + small scale + expensive lease + "
    "single-generation deployment). Taking the midpoint, the distributed model is <b>roughly "
    "cost-competitive with hyperscale on a 20-year TCO basis</b>, with the exact number being "
    "site-dependent. Part 2 will work through one specific WWTP in detail to narrow this down."
))
story.append(P(
    "<b>Market size.</b> What makes the 15% contribution figure interesting from a vendor perspective "
    "is the market it implies. At ~$3M per Vera Rubin NVL72-equivalent rack (NVIDIA) or ~$2–3M per "
    "Cerebras CS-3 system, the hardware market for a 15% adoption scenario (5,800 racks) is roughly "
    "<b>$17 billion in GPU/accelerator spend</b>, with another ~$7 billion in PV, BESS, cooling, and "
    "site integration. Over a 20-year site life with 4–6 GPU refresh cycles, cumulative hardware "
    "spend approaches $70–90 billion."
))
story.append(P(
    "The structural implication matters more than the raw number. Hyperscale AI purchases are single "
    "GW-scale contracts, stable 5-year PPAs, and unified hardware stacks &mdash; this favors NVIDIA "
    "and effectively locks out modular inference accelerators. A distributed market of thousands of "
    "2–20 rack deployments, each with independent procurement and 3–5 year refresh windows, has a "
    "completely different structure: single-site decision-making, multi-vendor feasibility, and "
    "workloads that are almost entirely inference &mdash; which happens to match the sweet spot of "
    "wafer-scale and modular inference hardware. For Cerebras, Groq, and similar vendors optimized for "
    "dense inference, a distributed market that captures 15% of near-term in-construction capacity "
    "could be the difference between a niche position and a major platform &mdash; potentially a "
    "multi-billion-dollar order flow if even a meaningful share of those sites pick non-NVIDIA "
    "accelerators."
))
story.append(P(
    "The practical takeaway: for an AI infrastructure buildout widely called &ldquo;the largest in "
    "history,&rdquo; a model that can contribute <b>~15% of near-term in-construction capacity</b> on "
    "a renewable-primary, geographically distributed basis, at cost levels broadly comparable to "
    "hyperscale, seems worth investigating. A 15% contribution to a generational infrastructure push "
    "is not trivial, especially given the faster deployment timeline &mdash; and the market structure "
    "favors modular, inference-optimized hardware vendors in a way that hyperscale does not."
))

# --- 1.6 ---
story.append(Paragraph("1.6 &nbsp; What this is not", STYLE_H2))
story.append(P(
    "This model targets distributed 1–20 MW inference nodes on land adjacent to industrial users. It "
    "is not a hyperscale alternative. Retired power plants with existing 115–345 kV transmission "
    "connections and transferable ISO interconnection agreements are a different opportunity class, "
    "and Applied Digital, Crusoe, and Data4 are already pursuing that for 50–200 MW deployments. Those "
    "assets have their own constraints (coal combustion residue liabilities, rural fiber, water rights "
    "re-permitting) but that is a different conversation."
))
story.append(P(
    "The numbers in Table 3 are first-principles estimates. Site counts come from public federal "
    "datasets (see Sources). The match between those counts and actual buffer-zone viability at the "
    "specific site level is not audited here. What the analysis shows is that the physics and "
    "regulatory pathway hold up across the site types examined &mdash; enough to justify deeper "
    "site-level work."
))
story.append(P("A few honest limits:"))
limits = [
    "Not every site in these categories has usable land. SFO has RPZs, but its runways extend into the "
    "Bay. Lots of refineries have had residential development creep in over the decades, compressing "
    "the effective buffer. Site geometry matters, and many sites that look promising on paper do not "
    "work in practice.",
    "Organizational friction is real. A chemical company's EHS committee has never approved anything "
    "in the buffer zone. A municipal water district has never signed a ground lease for a modular AI "
    "factory. These are first-of-their-kind transactions.",
    "Single-rack resilience is a real question. Four racks gives you N-1 redundancy; one rack does "
    "not. For production, at least two racks is reasonable.",
    "High-density AI racks (190 kW per rack and up) require liquid cooling &mdash; either cold plate "
    "or immersion &mdash; which adds water circulation requirements beyond standard HVAC. WWTPs have "
    "abundant water on-site (a natural fit). Petrochemical and pharmaceutical sites have water but it "
    "is typically process water, not suitable for direct cooling loops. Part 2 will address the "
    "cooling system design for the WWTP case.",
]
for b in limits:
    story.append(Paragraph(f"&bull;&nbsp;&nbsp;{b}", STYLE_BULLET))

# --- 1.7 ---
story.append(Paragraph("1.7 &nbsp; What comes next", STYLE_H2))
story.append(P(
    "Part 2 will take one typical-size municipal wastewater treatment plant (30 MGD &mdash; the rough "
    "average for a US city serving ~300,000 residents) and work through the full engineering "
    "simulation: PV layout sizing on the actual site geometry, BESS dispatch with Pyomo, power flow "
    "and load interaction with pandapower, a 20-year capex and opex rollup with multiple GPU refresh "
    "cycles, and an end-to-end estimate of tokens served per dollar. The code will be published "
    "alongside."
))
story.append(P(
    "Part 3 will demonstrate the inference layer on the same site: a working multi-agent system on a "
    "local GPU cluster, integrated with plant process data and serving both the plant's own operations "
    "and local metro inference demand."
))
story.append(Paragraph(
    "This is an idea, sketched at the first-principles level. Real deployments will run into site-specific "
    "constraints not captured here &mdash; grid studies, cooling details, HAZOP reviews, local "
    "permitting, ground lease structures. The goal of this series is to explore whether the overall "
    "direction holds up; the detailed engineering is in Part 2. Feedback from operators, utility "
    "engineers, AI infrastructure architects, regulators, and anyone with hands-on experience in "
    "similar deployments is welcome.",
    ParagraphStyle("final_italic", parent=STYLE_BODY, fontName="Helvetica-Oblique", textColor=MUTED),
))

# --- Sources ---
story.append(Paragraph("Sources", STYLE_H2))

sources = [
    ("[1]", "<b>US EPA Risk Management Program rule (40 CFR Part 68), 2024 update.</b> Regulates ~11,740 facilities "
           "across petroleum refineries, chemical manufacturers, water/wastewater treatment systems, chemical and "
           "petroleum wholesalers, food and beverage manufacturers with ammonia refrigeration, agricultural chemical "
           "distributors, and other RMP-regulated facilities. EPA, <i>Safer Communities by Chemical Accident Prevention Rule</i> "
           "(March 2024)."),
    ("[2]", "<b>NVIDIA Vera Rubin NVL72 platform specifications.</b> 72 Rubin GPUs &times; 288 GB HBM4 per GPU = 20.7 TB "
           "HBM4 per rack; 3.6 EFLOPS NVFP4 inference per rack; NVLink 6 switch. NVIDIA press release and CES 2026 keynote."),
    ("[3]", "<b>Vera Rubin NVL72 rack power specifications.</b> Max Q: ~190 kW rack TDP; Max P: ~230 kW rack TDP. Source: "
           "Ming-Chi Kuo supply chain checks (Jan 2026); SemiAnalysis <i>Vera Rubin BoM and Power Budget Model</i> (Feb 2026)."),
    ("[4]", "<b>US chemical manufacturing establishments (NAICS 325).</b> US Census Bureau County Business Patterns. "
           "RMP-triggering subset per EPA 2024."),
    ("[5]", "<b>US petroleum refineries and large petrochemical complexes.</b> 132 operable refineries as of January "
           "2025. US EIA <i>Refinery Capacity Report</i> (June 2025). Large petrochemical complexes estimated at ~80 "
           "global-scale sites."),
    ("[6]", "<b>US pharmaceutical API manufacturing sites.</b> The US accounts for 8% of total global active API DMFs "
           "as of 2024, with ~150–250 US API manufacturing sites. US Pharmacopeia, <i>Medicine Supply Map</i> (Jan 2026)."),
    ("[7]", "<b>US ammonia/fertilizer production plants.</b> 30 operating ammonia plants in the US as of 2023, with "
           "9 new plants proposed and 3 expansions. Environmental Integrity Project, <i>The Fertilizer Boom</i> (2023)."),
    ("[8]", "<b>US food processing plants with anhydrous ammonia refrigeration.</b> USDA FSIS inspects ~6,800 meat, "
           "poultry, and egg product plants; large HACCP-size subset combined with dairy, beverage, and cold storage "
           "with &gt;10,000 lb NH3 inventory gives ~1,500 RMP-triggering sites. USDA FSIS MPI Directory (2024); EPA RMP "
           "Appendix E."),
    ("[9]", "<b>US large refrigerated cold storage warehouses.</b> &ldquo;More than a thousand large cold storage warehouses "
           "spread across the country.&rdquo; Center for Land Use Interpretation, <i>Refrigerated Nation</i> (updated 2024)."),
    ("[10]", "<b>US publicly-owned wastewater treatment plants (POTWs).</b> 17,544 POTWs total as of 2022. EPA <i>2022 "
            "Clean Watersheds Needs Survey</i> (2024 report to Congress); CRS Report R48565 (June 2025)."),
    ("[11]", "<b>US LNG facilities.</b> 170+ LNG facilities operating in the US, including 8 operating export terminals. "
            "FERC LNG facility maps (accessed 2026)."),
    ("[12]", "<b>Cerebras WSE-3 / CS-3 system specifications.</b> 4 trillion transistors, 900,000 AI cores, 44 GB on-chip "
            "SRAM, 21 PB/s on-chip memory bandwidth, 125 PFLOPS peak. Cerebras press release, <i>Cerebras Systems Unveils "
            "World's Fastest AI Chip</i> (March 2024); IEEE Spectrum, <i>Cerebras WSE-3: Third Generation Superchip for AI</i> "
            "(March 2024)."),
    ("[13]", "<b>Utility distribution-level service upgrade timelines for commercial customers.</b> California Rule 21 "
            "Fast Track interconnection process sets a standard 120 business day timeline (60 days design + 60 days "
            "construction) for distribution-level interconnection upgrades. California Public Utilities Commission, "
            "Rule 21 (updated 2023–2024). Other utilities publish similar fast-track procedures for existing commercial "
            "services."),
    ("[14]", "<b>US AI data center capacity under construction.</b> Sightline Climate, <i>2026 Data Center Outlook</i> "
            "(April 2026). Reports US AI data center capacity actually under active construction as ~5 GW for 2026 and "
            "~6.3 GW for 2027, with an additional ~26 GW announced but not broken ground. Cited by Bloomberg and Tom's "
            "Hardware. BloombergNEF Global Data Center Tracker corroborates ~17 GW of the ~23 GW global in-construction "
            "total as US-based (Sept 2025)."),
    ("[15]", "<b>Levelized cost of energy (LCOE) for utility-scale PV+BESS.</b> Lazard, <i>Levelized Cost of Energy+</i> "
            "(2024): utility-scale solar PV LCOE $24–36/MWh; solar + 4-hour battery storage combined LCOE $45–65/MWh. "
            "NREL Annual Technology Baseline 2025. Behind-the-meter deployment typically saves additional $10–15/MWh "
            "by avoiding transmission and distribution charges, though smaller-scale (1–20 MW) installations can offset "
            "this with higher per-MW capex."),
    ("[16]", "<b>Military drone strikes on AWS data centers, March 1, 2026.</b> First confirmed military attack on a "
            "hyperscale cloud provider. Two AWS sites were struck in the UAE and one in Bahrain, taking down two of "
            "three availability zones in AWS ME-CENTRAL-1 (UAE) and one in ME-SOUTH-1 (Bahrain). Outages affected "
            "Emirates NBD, First Abu Dhabi Bank, Snowflake, Careem, and others. Sources: Fortune (March 9, 2026); CNBC "
            "(March 3, 2026); Rest of World (March 2026); TechPolicy.Press (March 12, 2026)."),
    ("[17]", "<b>Jensen Huang on the inference share of AI compute.</b> NVIDIA CEO, public statements at GTC 2025–2026 "
            "and subsequent investor interviews. Huang has said that inference already makes up more than 40% of "
            "NVIDIA's data center revenue and will account for roughly 80% of long-term AI compute versus 20% for "
            "training, and that overall inference demand is &ldquo;about to go up by a billion times&rdquo; as AI is embedded into "
            "work and consumer applications. Cited in Bg2 Pod (Sep 2025); Yahoo Finance (Oct 2025); Dwarkesh Podcast "
            "(2025); BizTech Magazine coverage of GTC 2026 (March 2026)."),
    ("[18]", "<b>Andrew Feldman on AI inference as the dominant workload.</b> Cerebras co-founder and CEO, public "
            "statements describing inference as &ldquo;the dominant cost and performance bottleneck in AI.&rdquo; TechArena fireside "
            "chat (2025); Bloomberg <i>Tech Disruptors</i> podcast (May 2025); CNBC interview (October 2025)."),
]
for num, body in sources:
    story.append(Paragraph(f"<b>{num}</b> {body}", STYLE_SRC))

story.append(Spacer(1, 12))
story.append(HRFlowable(width="100%", thickness=0.4, color=RULE, spaceBefore=8, spaceAfter=8))
story.append(Paragraph(
    "All calculations and the simulation platform: EnergyFlux &mdash; github.com/chennanli/EnergyFlux",
    ParagraphStyle("final1", parent=STYLE_BODY, fontSize=9, textColor=MUTED, spaceAfter=2),
))
story.append(Paragraph(
    "Chennan Li, PhD, PE &bull; chennanli@gmail.com &bull; linkedin.com/in/chennanli",
    ParagraphStyle("final2", parent=STYLE_BODY, fontSize=9, textColor=MUTED),
))

# ---- Build ----
OUT = os.path.join(os.path.dirname(_HERE), "blog1_v20.pdf")
doc = NumberedDocTemplate(
    OUT, pagesize=LETTER,
    leftMargin=1.0*inch, rightMargin=1.0*inch,
    topMargin=0.85*inch, bottomMargin=0.85*inch,
    title="Turning industrial safety buffers into AI inference sites",
    author="Chennan Li, PhD, PE",
)
doc.build(story)
print(f"wrote {OUT}")
