"""Build deck.pptx — Topic 4: AmbieGen (course presentation, 2 presenters x 10 min).

Method follows the pptx skill: BACKGROUND->PRIMARY->ACCENT palette (asphalt/slate/amber,
topic = autonomous-systems testing), sandwich structure (dark cover/dividers/close,
light content), one motif (rounded cards + numbered chips + oversized divider numerals),
Segoe UI + Consolas pairing, native charts, source line for every key figure.
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import (XL_CHART_TYPE, XL_LEGEND_POSITION,
                             XL_LABEL_POSITION, XL_MARKER_STYLE)
try:
    from pptx.enum.dml import MSO_LINE_DASH_STYLE
except ImportError:  # older enum alias
    from pptx.enum.dml import MSO_LINE as MSO_LINE_DASH_STYLE

HERE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join(HERE, "evidence")
OUT = os.path.join(HERE, "deck.pptx")

# ---------------- palette / fonts ----------------
BG_DARK   = RGBColor.from_string("141821")   # asphalt near-black
CARD_DARK = RGBColor.from_string("1E2530")
LINE_DARK = RGBColor.from_string("2A3342")
BG_LIGHT  = RGBColor.from_string("FFFFFF")
PRIMARY   = RGBColor.from_string("2C4A63")   # engineering slate blue
PRIM_MID  = RGBColor.from_string("5C7A93")
PRIM_LT   = RGBColor.from_string("9CB4C4")
CARD      = RGBColor.from_string("F2F5F8")   # light slate tint
ACCENT    = RGBColor.from_string("F2A61D")   # road-marking amber
ACC_TINT  = RGBColor.from_string("FCEFD3")
ACC_DEEP  = RGBColor.from_string("9A6A00")
TEXT      = RGBColor.from_string("1D2430")
MUTED     = RGBColor.from_string("66727F")
GRID      = RGBColor.from_string("DDE4EA")
ON_DARK   = RGBColor.from_string("F2F4F7")
MUT_DARK  = RGBColor.from_string("9AA6B4")
SANS = "Segoe UI"
MONO = "Consolas"

W, H, M = 13.333, 7.5, 0.55
CW = W - 2 * M  # 12.233

prs = Presentation()
prs.slide_width = Emu(12192000)
prs.slide_height = Emu(6858000)
BLANK = prs.slide_layouts[6]
prs.core_properties.title = "AmbieGen - Search-Based Test Case Generation for Autonomous Systems"
prs.core_properties.author = "Topic 4 team"

# ---------------- helpers ----------------
def slide(bg=BG_LIGHT):
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = bg
    return s

def para(t=None, runs=None, size=14, bold=False, color=TEXT, font=SANS,
         align=PP_ALIGN.LEFT, ls=1.0, sa=0, sb=0, italic=False):
    return dict(t=t, runs=runs, size=size, bold=bold, color=color, font=font,
                align=align, ls=ls, sa=sa, sb=sb, italic=italic)

def add_text(s, x, y, w, h, paras, anchor=MSO_ANCHOR.TOP, wrap=True):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    if isinstance(paras, dict):
        paras = [paras]
    first = True
    for pa in paras:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = pa["align"]
        p.line_spacing = pa["ls"]
        if pa["sa"]:
            p.space_after = Pt(pa["sa"])
        if pa["sb"]:
            p.space_before = Pt(pa["sb"])
        runs = pa["runs"] if pa["runs"] else [(pa.get("t") or "", {})]
        for rt, ro in runs:
            r = p.add_run()
            r.text = rt
            f = r.font
            f.size = Pt(ro.get("size", pa["size"]))
            f.bold = ro.get("bold", pa["bold"])
            f.italic = ro.get("italic", pa["italic"])
            f.name = ro.get("font", pa["font"])
            f.color.rgb = ro.get("color", pa["color"])
    return tb

def rect(s, x, y, w, h, fill, line=None, radius=None, shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    sp = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None:
        sp.fill.background()
    else:
        sp.fill.solid()
        sp.fill.fore_color.rgb = fill
    if line is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = line
        sp.line.width = Pt(0.75)
    sp.shadow.inherit = False
    if radius is not None and shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        try:
            sp.adjustments[0] = radius
        except Exception:
            pass
    return sp

def chip(s, x, y, size, label, fill=ACCENT, tcolor=BG_DARK, fsize=15,
         font=SANS, radius=0.28):
    sp = rect(s, x, y, size, size, fill, radius=radius)
    tf = sp.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.word_wrap = False
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = label
    r.font.size = Pt(fsize)
    r.font.bold = True
    r.font.name = font
    r.font.color.rgb = tcolor
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    return sp

def hairline(s, x, y, w, color=GRID):
    rect(s, x, y, w, 0.013, color, shape=MSO_SHAPE.RECTANGLE)

def arrow(s, x, y, w=0.34, h=0.26, color=PRIM_LT):
    return rect(s, x, y, w, h, color, shape=MSO_SHAPE.RIGHT_ARROW)

def header(s, kicker, title, page=None, source=None, kcolor=PRIMARY, tsize=29):
    add_text(s, M, 0.44, CW, 0.28,
             para(kicker, size=11.5, bold=True, color=kcolor))
    add_text(s, M, 0.76, CW, 0.8, para(title, size=tsize, bold=True, color=TEXT))
    if source:
        add_text(s, M, 7.08, 9.6, 0.26, para(source, size=10, color=MUTED))
    if page is not None:
        add_text(s, W - M - 0.8, 7.08, 0.8, 0.26,
                 para(str(page), size=10, color=MUTED, align=PP_ALIGN.RIGHT))

def kv_rows(s, x, y, w, rows, lead_size=15, desc_size=12.5, gap=0.14, lead_color=PRIMARY):
    """Row list: bold lead-in + muted description, hairline-separated."""
    cy = y
    for i, (lead, desc) in enumerate(rows):
        add_text(s, x, cy, w, 0.3, para(lead, size=lead_size, bold=True, color=lead_color))
        cpl = max(int(w / (desc_size * 0.5 / 72)), 1)
        lines = max(1, -(-len(desc) // cpl))
        dh = lines * desc_size * 1.26 / 72
        add_text(s, x, cy + 0.31, w, dh + 0.04,
                 para(desc, size=desc_size, color=MUTED, ls=1.12))
        cy += 0.31 + dh + gap
        if i < len(rows) - 1:
            hairline(s, x, cy - gap / 2, w)
    return cy

def set_cell(c, text, size=12.5, bold=False, color=TEXT, fill=None, font=SANS,
             align=PP_ALIGN.LEFT):
    if fill is not None:
        c.fill.solid()
        c.fill.fore_color.rgb = fill
    c.margin_left = Inches(0.12)
    c.margin_right = Inches(0.08)
    c.margin_top = Inches(0.03)
    c.margin_bottom = Inches(0.03)
    c.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf = c.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.name = font
    r.font.color.rgb = color

def col_chart(s, x, y, w, h, cats, vals, colors, vmax, dl_size=15):
    cd = CategoryChartData()
    cd.categories = cats
    cd.add_series("failures", vals)
    gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(x), Inches(y),
                            Inches(w), Inches(h), cd)
    ch = gf.chart
    ch.has_legend = False
    ch.font.name = SANS
    ch.font.size = Pt(12)
    pl = ch.plots[0]
    pl.gap_width = 80
    pl.vary_by_categories = False
    pl.has_data_labels = True
    dls = pl.data_labels
    dls.font.size = Pt(dl_size)
    dls.font.bold = True
    dls.font.name = SANS
    dls.font.color.rgb = TEXT
    dls.position = XL_LABEL_POSITION.OUTSIDE_END
    ser = pl.series[0]
    for i, c in enumerate(colors):
        pt = ser.points[i]
        pt.format.fill.solid()
        pt.format.fill.fore_color.rgb = c
    ca = ch.category_axis
    ca.has_major_gridlines = False
    ca.tick_labels.font.size = Pt(12)
    ca.tick_labels.font.name = SANS
    ca.tick_labels.font.color.rgb = TEXT
    ca.format.line.color.rgb = GRID
    va = ch.value_axis
    va.minimum_scale = 0
    va.maximum_scale = vmax
    va.has_major_gridlines = True
    va.major_gridlines.format.line.color.rgb = GRID
    va.major_gridlines.format.line.width = Pt(0.5)
    va.tick_labels.font.size = Pt(10.5)
    va.tick_labels.font.name = SANS
    va.tick_labels.font.color.rgb = MUTED
    va.format.line.fill.background()
    return ch

def line_chart(s, x, y, w, h, cats, name1, v1, name2, v2, ymin, ymax):
    cd = CategoryChartData()
    cd.categories = cats
    cd.add_series(name1, v1)
    cd.add_series(name2, v2)
    gf = s.shapes.add_chart(XL_CHART_TYPE.LINE, Inches(x), Inches(y),
                            Inches(w), Inches(h), cd)
    ch = gf.chart
    ch.font.name = SANS
    ch.font.size = Pt(11)
    ch.has_legend = True
    ch.legend.position = XL_LEGEND_POSITION.BOTTOM
    ch.legend.include_in_layout = False
    ch.legend.font.size = Pt(11)
    ch.legend.font.name = SANS
    ch.legend.font.color.rgb = TEXT
    s1 = ch.series[0]
    s1.smooth = False
    s1.format.line.color.rgb = PRIMARY
    s1.format.line.width = Pt(2.75)
    s1.marker.style = XL_MARKER_STYLE.NONE
    s2 = ch.series[1]
    s2.smooth = False
    s2.format.line.color.rgb = ACCENT
    s2.format.line.width = Pt(2)
    s2.marker.style = XL_MARKER_STYLE.NONE
    try:
        s2.format.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    except Exception:
        pass
    ca = ch.category_axis
    ca.has_major_gridlines = False
    ca.tick_labels.font.size = Pt(10.5)
    ca.tick_labels.font.name = SANS
    ca.tick_labels.font.color.rgb = MUTED
    ca.format.line.color.rgb = GRID
    va = ch.value_axis
    va.minimum_scale = ymin
    va.maximum_scale = ymax
    va.has_major_gridlines = True
    va.major_gridlines.format.line.color.rgb = GRID
    va.major_gridlines.format.line.width = Pt(0.5)
    va.tick_labels.font.size = Pt(10.5)
    va.tick_labels.font.name = SANS
    va.tick_labels.font.color.rgb = MUTED
    va.format.line.fill.background()
    return ch

EVALS = [str(20 * i) for i in range(1, 16)]
ROBOT_FIT = [97.0, 97.0, 105.3, 105.3, 105.3, 105.3, 126.9, 126.9, 126.9,
             126.9, 126.9, 132.1, 132.1, 132.1, 132.1]
TEAM_FIT = [3.64, 3.71, 4.14, 4.14, 4.15, 4.15, 4.38, 4.38, 4.38,
            4.38, 4.38, 4.65, 4.65, 4.65, 4.65]

# ================= SLIDE 1 — title (dark) =================
s = slide(BG_DARK)
add_text(s, M, 1.0, CW, 0.3,
         para("COURSE TOPIC 4 · AUTOMATIC SEARCH-BASED TESTING OF AUTONOMOUS SYSTEMS",
              size=13, bold=True, color=ACCENT))
add_text(s, M, 1.42, CW, 1.1, para("AmbieGen", size=60, bold=True, color=ON_DARK))
add_text(s, M, 2.62, CW, 0.55,
         para("Search-Based Test Case Generation for Autonomous Systems",
              size=25, color=PRIM_LT))
add_text(s, M, 3.32, CW, 0.32,
         para("test case = [[type, attr, attr], …] -> simplified model -> "
              "fitness + novelty -> NSGA-II",
              size=12.5, color=MUT_DARK, font=MONO))
cards = [
    ("The paper",
     "Humeniuk, Khomh, Antoniol - \u201cAmbieGen: A Search-based Framework for "
     "Autonomous Systems Testing\u201d, Science of Computer Programming 230 (2023), "
     "art. 102990 · arXiv:2301.01234"),
    ("The tool",
     "github.com/swat-lab-optimization/AmbieGen-tool - MIT license, v0.1.0, built "
     "on Pymoo; winner of the SBST 2022 tool competition"),
    ("Our runs",
     "Built-in robot study + our team case study \u201cMountain Pass\u201d, executed "
     "and logged 2026-10-16 - artifacts in tss/course-ambiegen/evidence/"),
]
cx = M
for t, d in cards:
    rect(s, cx, 4.55, 3.94, 1.7, CARD_DARK, line=LINE_DARK, radius=0.06)
    add_text(s, cx + 0.26, 4.78, 3.42, 0.3, para(t, size=14.5, bold=True, color=ACCENT))
    add_text(s, cx + 0.26, 5.14, 3.42, 1.0, para(d, size=11.5, color=MUT_DARK, ls=1.15))
    cx += 4.145
add_text(s, M, 6.62, CW, 0.3,
         para(runs=[
             ("Presenter 1 - problem · framework · method", dict(bold=True, color=ON_DARK)),
             ("      |      ", dict(color=LINE_DARK)),
             ("Presenter 2 - case studies · results · live demo", dict(bold=True, color=ON_DARK)),
         ], size=13))
add_text(s, M, 6.98, CW, 0.28,
         para("2 students × 10 minutes - the deck is split into two labeled parts",
              size=11.5, color=MUT_DARK))

# ================= SLIDE 2 — agenda =================
s = slide()
header(s, "20-MINUTE TALK · TWO PRESENTERS", "Today: from the testing problem to a live demo", page=2)
agenda = [
    ("01", "Part 1 - Problem · Framework · Method", "Presenter 1 · ~10 minutes",
     ["Why testing autonomous systems is hard",
      "AmbieGen: model-in-the-loop idea + framework",
      "Test representation, algorithms, fitness, novelty",
      "Operators, defaults and run outputs"]),
    ("02", "Part 2 - Case Studies · Results · Demo", "Presenter 2 · ~10 minutes",
     ["Paper results: failures found vs random search",
      "Built-in case study run: robot mazes (live)",
      "Team case study: \u201cMountain Pass\u201d roads (live)",
      "Strengths, limits and conclusions"]),
]
cx = M
for num, title, who, items in agenda:
    rect(s, cx, 1.72, 5.98, 4.1, CARD, radius=0.045)
    chip(s, cx + 0.32, 2.02, 0.62, num, fsize=17)
    add_text(s, cx + 1.12, 2.02, 4.6, 0.62,
             para(title, size=17.5, bold=True, color=TEXT), anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, cx + 0.34, 2.82, 5.3, 0.28, para(who, size=12.5, bold=True, color=PRIM_MID))
    iy = 3.28
    for it in items:
        rect(s, cx + 0.36, iy + 0.09, 0.09, 0.09, ACCENT, radius=0.3)
        add_text(s, cx + 0.62, iy, 5.1, 0.3, para(it, size=13.5, color=TEXT))
        iy += 0.42
    cx += 6.25
rect(s, M, 6.12, CW, 0.62, ACC_TINT, radius=0.12)
add_text(s, M + 0.3, 6.12, CW - 0.6, 0.62,
         para(runs=[
             ("Every claim in this deck is backed by an artifact: ", dict()),
             ("the paper (arXiv:2301.01234), the AmbieGen-tool repo, or our own logged runs in evidence/.",
              dict(bold=True)),
         ], size=13), anchor=MSO_ANCHOR.MIDDLE)

# ================= SLIDE 3 — divider Part 1 =================
def divider(num, kicker, title, who, items, page=None):
    s = slide(BG_DARK)
    add_text(s, 0.7, 1.95, 3.4, 2.9, para(num, size=150, bold=True, color=ACCENT))
    add_text(s, 4.45, 2.12, 8.3, 0.3, para(kicker, size=13, bold=True, color=ACCENT))
    add_text(s, 4.45, 2.5, 8.3, 0.7, para(title, size=35, bold=True, color=ON_DARK))
    add_text(s, 4.45, 3.32, 8.3, 0.55, para(who, size=15, color=MUT_DARK, ls=1.1))
    hairline(s, 4.45, 3.95, 7.6, LINE_DARK)
    iy = 4.2
    for it in items:
        rect(s, 4.45, iy + 0.1, 0.09, 0.09, ACCENT, radius=0.3)
        add_text(s, 4.72, iy, 7.9, 0.32, para(it, size=14.5, color=ON_DARK))
        iy += 0.46
    if page is not None:
        add_text(s, W - M - 0.8, 7.08, 0.8, 0.26,
                 para(str(page), size=10, color=MUT_DARK, align=PP_ALIGN.RIGHT))
    return s

divider("01", "PART 1 · PRESENTER 1 · ~10 MINUTES",
        "Problem · Framework · Method",
        "What makes testing autonomous systems hard, and how AmbieGen searches for the critical scenarios",
        ["The problem: huge parameter space, rare failures",
         "The framework: model-in-the-loop + Pymoo core",
         "The method: representation, algorithms, fitness, novelty"],
        page=3)

# ================= SLIDE 4 — the problem =================
s = slide()
header(s, "PART 1 · THE PROBLEM",
       "Testing autonomous systems does not scale by hand", page=4,
       source="Source: Humeniuk et al., SCP 2023 (arXiv:2301.01234), §Introduction")
kv_rows(s, M, 1.8, 7.15, [
    ("The parameter space is too large",
     "Road geometry, obstacle layouts, sensor ranges - simulating every scenario is impossible; "
     "the paper's premise is a space too large for exhaustive simulation."),
    ("Critical failures are rare",
     "A random scenario almost never pushes the system to its limits - the dangerous "
     "configurations cluster in small pockets of the space."),
    ("Hand-designed tests do not scale",
     "Engineers write typical cases; the failures live in atypical ones. AmbieGen "
     "searches for them automatically instead of guessing."),
], lead_size=17, desc_size=13, gap=0.24)
rect(s, M, 5.28, 7.15, 1.07, ACC_TINT, radius=0.1)
add_text(s, M + 0.28, 5.28, 6.6, 1.07,
         para(runs=[
             ("AmbieGen's answer: ", dict(bold=True, color=ACC_DEEP)),
             ("let an evolutionary algorithm search the scenario space, scoring each "
              "candidate on a fast simplified model of the system.", dict()),
         ], size=13), anchor=MSO_ANCHOR.MIDDLE)
rect(s, 7.95, 1.8, 4.83, 4.55, CARD, radius=0.045)
add_text(s, 8.25, 2.05, 4.25, 0.3,
         para("Two systems under test in the paper", size=14.5, bold=True, color=PRIMARY))
add_text(s, 8.25, 2.55, 4.25, 0.3, para("Robot - Pioneer 3-AT", size=14, bold=True, color=TEXT))
add_text(s, 8.25, 2.9, 4.25, 0.95,
         para("SICK LMS200 laser (10 m range), nearness-diagram obstacle-avoidance "
              "navigation, simulated in Player/Stage.", size=12.5, color=MUTED, ls=1.15))
hairline(s, 8.25, 3.98, 4.25)
add_text(s, 8.25, 4.16, 4.25, 0.3, para("Vehicle - Lane Keeping Assist", size=14, bold=True, color=TEXT))
add_text(s, 8.25, 4.51, 4.25, 1.3,
         para("Tested in BeamNG.tech. Failure criterion: more than 85% of the car's "
              "area leaving the lane; speed capped at 70 km/h.", size=12.5, color=MUTED, ls=1.15))
chip(s, 8.25, 5.6, 0.34, "!", fsize=15)
add_text(s, 8.72, 5.6, 3.8, 0.6,
         para("A test is \u201cfault-revealing\u201d when it breaks the system like this.",
              size=11.5, color=MUTED, ls=1.1), anchor=MSO_ANCHOR.MIDDLE)

# ================= SLIDE 5 — the idea (pipeline) =================
s = slide()
header(s, "PART 1 · THE IDEA",
       "Evolve scenarios against a cheap model of the system", page=5,
       source="Source: Humeniuk et al., SCP 2023 - model-in-the-loop testing")
boxes = [
    ("Test case", "genotype: a list of environment elements"),
    ("Simplified model", "kinematic car / A* planner - cheap to evaluate"),
    ("Fitness + novelty", "how fault-revealing and how different"),
    ("Evolutionary search", "NSGA-II: select · crossover · mutate"),
    ("Test suite", "validate on the full simulator"),
]
bx, by, bw, bh, gap = M, 2.0, 2.18, 1.8, 0.36
for i, (t, d) in enumerate(boxes):
    last = i == len(boxes) - 1
    rect(s, bx, by, bw, bh, ACCENT if last else CARD, radius=0.09)
    add_text(s, bx + 0.16, by + 0.22, bw - 0.32, 0.62,
             para(t, size=14.5, bold=True, color=BG_DARK if last else PRIMARY, ls=1.0))
    add_text(s, bx + 0.16, by + 0.85, bw - 0.32, 0.85,
             para(d, size=11, color=RGBColor.from_string("3A2E10") if last else MUTED, ls=1.12))
    if not last:
        arrow(s, bx + bw + 0.015, by + bh / 2 - 0.13, gap - 0.03, 0.26)
    bx += bw + gap
add_text(s, M, 4.02, CW, 0.3,
         para("one search loop - defaults: population 100 × 100 generations, "
              "crossover 0.9, mutation 0.4 (config.py)", size=12.5, color=MUTED,
              align=PP_ALIGN.CENTER))
rect(s, M, 4.62, CW, 1.95, CARD, radius=0.06)
add_text(s, M + 0.32, 4.88, CW - 0.64, 0.32,
         para("Why a simplified model inside the loop?", size=15.5, bold=True, color=PRIMARY))
add_text(s, M + 0.32, 5.32, CW - 0.64, 1.1,
         para("The full simulator (BeamNG.tech, Player/Stage) is far too slow to evaluate "
              "thousands of candidate scenarios. AmbieGen evolves against a cheap model of the "
              "system under test, so every evaluation is fast, and only the final test suite goes "
              "to the real simulator - the paper completes a 2-hour budget per run.",
              size=13.5, color=TEXT, ls=1.2))

# ================= SLIDE 6 — the framework =================
s = slide()
header(s, "PART 1 · THE FRAMEWORK",
       "AmbieGen: a modular tool built on the Pymoo core", page=6,
       source="Sources: repo README (Installation, Adding a new problem) · paper §framework · ambiegen/__init__.py:1-9")
rect(s, M, 1.8, 6.55, 4.55, CARD, radius=0.045)
add_text(s, M + 0.3, 2.02, 5.95, 0.3,
         para("AmbieGen-tool - MIT license · v0.1.0", size=13.5, bold=True, color=PRIMARY))
rect(s, M + 0.3, 2.44, 5.95, 0.72, BG_LIGHT, radius=0.1)
add_text(s, M + 0.5, 2.44, 5.6, 0.72,
         para("Pymoo evolutionary core - GA · NSGA-II · Random search",
              size=13.5, bold=True, color=TEXT), anchor=MSO_ANCHOR.MIDDLE)
add_text(s, M + 0.3, 3.34, 5.95, 0.28,
         para("extension points - implement 4 classes to add a system under test",
              size=11.5, color=MUTED))
ext = ["Problem", "Sampling", "Crossover / Mutation", "Solution"]
ex, ey, ew = M + 0.3, 3.72, 1.38
for i, e in enumerate(ext):
    rect(s, ex + i * (ew + 0.14), ey, ew, 0.6, BG_LIGHT, radius=0.12)
    add_text(s, ex + i * (ew + 0.14) + 0.06, ey, ew - 0.12, 0.6,
             para(e, size=11.5, bold=True, color=PRIMARY, align=PP_ALIGN.CENTER, ls=1.0),
             anchor=MSO_ANCHOR.MIDDLE)
add_text(s, M + 0.3, 4.62, 5.95, 0.28,
         para("shipped systems under test", size=11.5, color=MUTED))
for i, sut in enumerate(["robot - Player/Stage", "vehicle LKAS - BeamNG.tech"]):
    rect(s, M + 0.3 + i * 3.05, 4.98, 2.9, 0.62, BG_LIGHT, radius=0.12)
    add_text(s, M + 0.42 + i * 3.05, 4.98, 2.66, 0.62,
             para(sut, size=12.5, bold=True, color=TEXT, align=PP_ALIGN.CENTER),
             anchor=MSO_ANCHOR.MIDDLE)
add_text(s, M + 0.3, 5.8, 5.95, 0.3,
         para("search operators + samplers are pluggable the same way",
              size=11.5, color=MUTED))
kv_rows(s, 7.55, 1.8, 5.23, [
    ("Open source",
     "github.com/swat-lab-optimization/AmbieGen-tool - MIT license; the exact tool "
     "behind the paper's experiments (cloned and executed by us)."),
    ("Modular by design",
     "A new system under test plugs in as Problem + Sampling + Operators + Solution "
     "classes - no changes to the core."),
    ("Competition-proven",
     "Winner of the SBST 2022 tool competition: the most diverse fault-revealing "
     "scenarios under a limited time budget."),
    ("Reproducible runs",
     "random seeds, duplicate elimination, stats + convergence logs, and compare.py "
     "boxplots for algorithm face-offs."),
], lead_size=15, desc_size=12)

# ================= SLIDE 7 — representation =================
s = slide()
header(s, "PART 1 · TEST REPRESENTATION",
       "A test case is just an array of environment elements", page=7,
       source="Source: repo README - \u201cRepresentation of the test cases\u201d")
rep = [
    ("Robot - maze elements", "element = [type, size, x]",
     "type: 0 = horizontal wall · 1 = vertical wall",
     "[1, 15, 40]  ->  vertical wall, size 15, at x = 40"),
    ("Vehicle - road segments", "element = [type, length, angle]",
     "type: 0 = straight · 1 = turn right · 2 = turn left",
     "[1, 0, 75]  ->  turn right by 75°"),
]
cx = M
for title, sig, legend, ex in rep:
    rect(s, cx, 1.78, 5.98, 3.15, CARD, radius=0.045)
    add_text(s, cx + 0.3, 2.02, 5.4, 0.3, para(title, size=16, bold=True, color=PRIMARY))
    add_text(s, cx + 0.3, 2.42, 5.4, 0.32, para(sig, size=15, bold=True, color=TEXT, font=MONO))
    add_text(s, cx + 0.3, 2.86, 5.4, 0.3, para(legend, size=12.5, color=MUTED))
    rect(s, cx + 0.3, 3.32, 5.38, 1.28, BG_LIGHT, radius=0.1)
    add_text(s, cx + 0.55, 3.32, 4.9, 1.28, para(ex, size=14, color=TEXT, font=MONO),
             anchor=MSO_ANCHOR.MIDDLE)
    cx += 6.25
rect(s, M, 5.18, CW, 1.62, ACC_TINT, radius=0.06)
add_text(s, M + 0.32, 5.4, CW - 0.64, 0.3,
         para("Genomes are variable-length - crossover works across different lengths",
              size=14.5, bold=True, color=ACC_DEEP))
add_text(s, M + 0.32, 5.78, CW - 0.64, 0.3,
         para("A real genome from our team run - tc0, all 7 segments verbatim "
              "(opens with 75\u00b0 and 76\u00b0 turns):",
              size=12.5, color=TEXT))
add_text(s, M + 0.32, 6.12, CW - 0.64, 0.32,
         para("[[1,0,75],[2,0,76],[0,10,0],[0,7,76],[2,0,63],[0,9,0],[0,6,0]]",
              size=14.5, bold=True, color=TEXT, font=MONO))
add_text(s, M + 0.32, 6.48, CW - 0.64, 0.26,
         para("evidence/team/16-10-2026_team_tcs_nsga2/16-10-2026-tcs.json", size=10.5, color=MUTED))

# ================= SLIDE 8 — algorithms =================
s = slide()
header(s, "PART 1 · THE SEARCH",
       "Three algorithms, one Pymoo core", page=8,
       source="Sources: ambiegen/__init__.py:1-9 (registry) · optimize.py:86-120 · CLI verified via --help")
rows = [
    ("Key", "Algorithm (Pymoo class)", "Objectives", "Role"),
    ("nsga2", "NSGA-II - multi-objective GA (default)", "2: fitness + novelty",
     "best suites: critical AND diverse"),
    ("ga", "Genetic algorithm - single objective", "1: fault-revealing fitness",
     "fast single-objective baseline"),
    ("random", "Random search (RandomSearch)", "-", "control baseline for comparison"),
]
tw, th = CW, 2.1
gt = s.shapes.add_table(4, 4, Inches(M), Inches(1.78), Inches(tw), Inches(th)).table
gt.first_row = True
gt.horz_banding = False
for w, i in zip([1.15, 4.55, 3.05, 3.48], range(4)):
    gt.columns[i].width = Inches(w)
for ri, row in enumerate(rows):
    gt.rows[ri].height = Inches(0.52)
    for ci, val in enumerate(row):
        c = gt.cell(ri, ci)
        if ri == 0:
            set_cell(c, val, size=12.5, bold=True, color=BG_LIGHT, fill=PRIMARY)
        else:
            fill = BG_LIGHT if ri % 2 == 1 else CARD
            set_cell(c, val, size=13, bold=(ci == 0),
                     color=PRIMARY if ci == 0 else TEXT, fill=fill,
                     font=MONO if ci == 0 else SANS)
add_text(s, M, 4.12, CW, 0.55,
         para(runs=[
             ("Fitness values are negative and minimized by Pymoo ", dict(bold=True)),
             ("- so \u201cminimizing\u201d fitness means maximizing how fault-revealing "
              "(or how novel) a scenario is. The algorithm is wired with problem-specific "
              "sampling, crossover and mutation, plus duplicate elimination.", dict()),
         ], size=13, ls=1.15))
rect(s, M, 4.95, CW, 1.55, CARD, radius=0.06)
add_text(s, M + 0.32, 5.18, CW - 0.64, 0.3,
         para("The command line (what we will run in the demo)", size=14, bold=True, color=PRIMARY))
add_text(s, M + 0.32, 5.56, CW - 0.64, 0.35,
         para("python optimize.py --problem {robot | vehicle} --algorithm {nsga2 | ga | random} "
              "--runs 1 --seed 42", size=14.5, color=TEXT, font=MONO))
add_text(s, M + 0.32, 5.98, CW - 0.64, 0.3,
         para("verified flags; the README's example uses --algo, which does not exist "
              "(the real flag is --algorithm, optimize.py:58)",
              size=11.5, color=MUTED))

# ================= SLIDE 9 — fitness =================
s = slide()
header(s, "PART 1 · FITNESS FUNCTION",
       "Fitness: make the system misbehave on the cheap model", page=9,
       source="Sources: robot_solution.py:34-58 · vehicle_evaluate.py:99-163 · kinematic_model.py · a_star.py")
fit = [
    ("Robot - maximize the A* path",
     ["Obstacle map is built from the genotype's walls",
      "A* plans a route from (1,1) to (map_size - 2, map_size - 2)",
      "fitness = -(path length): a longer forced detour = a harder maze"],
     "Failure constraint:  G = 150 - path   ->   fault-revealing when path > 150"),
    ("Vehicle - maximize lane deviation",
     ["Road points are spline-interpolated from the segments",
      "A kinematic bicycle model + waypoint-following controller drive the road",
      "fitness = -(max distance between car and road centreline)"],
     "Failure constraint:  G = 5 - deviation   ->   failure when deviation > 5"),
]
cx = M
for title, lines, con in fit:
    rect(s, cx, 1.78, 5.98, 4.3, CARD, radius=0.045)
    add_text(s, cx + 0.3, 2.02, 5.4, 0.3, para(title, size=16, bold=True, color=PRIMARY))
    ly = 2.48
    for ln in lines:
        rect(s, cx + 0.32, ly + 0.08, 0.09, 0.09, PRIM_MID, radius=0.3)
        add_text(s, cx + 0.58, ly - 0.02, 5.1, 0.62, para(ln, size=12.5, color=TEXT, ls=1.12))
        ly += 0.68
    rect(s, cx + 0.3, 4.78, 5.38, 1.0, ACC_TINT, radius=0.1)
    add_text(s, cx + 0.52, 4.78, 4.95, 1.0,
             para(con, size=12.5, bold=True, color=ACC_DEEP, ls=1.12),
             anchor=MSO_ANCHOR.MIDDLE)
    cx += 6.25
add_text(s, M, 6.35, CW, 0.55,
         para("Edge cases handled in code: invalid scenarios get fitness 0; self-intersecting "
              "roads cap the per-step distance at 3. Our team run raises the vehicle bar to 6.",
              size=12, color=MUTED, ls=1.15))

# ================= SLIDE 10 — novelty =================
s = slide()
header(s, "PART 1 · SECOND OBJECTIVE",
       "Novelty: keep the test suite diverse", page=10,
       source="Sources: vehicle_solution.py:64-101 · vehicle_problem.py:49-61 · robot_problem.py:24-39")
rect(s, M, 1.78, 7.35, 3.05, CARD, radius=0.045)
add_text(s, M + 0.32, 2.02, 6.7, 0.3,
         para("Pairwise novelty - a Jaccard-style distance between genotypes",
              size=15, bold=True, color=PRIMARY))
add_text(s, M + 0.32, 2.48, 6.7, 0.42,
         para("novelty(a, b) = 1 - |a \u2229 b| / ( |a| + |b| - |a \u2229 b| )",
              size=16.5, bold=True, color=TEXT))
add_text(s, M + 0.32, 3.06, 6.7, 0.62,
         para("Two elements \u201cintersect\u201d when they have the same type and near-equal "
              "attributes (tolerance: 5 for vehicle, 2 for robot).",
              size=12.5, color=MUTED, ls=1.15))
add_text(s, M + 0.32, 3.78, 6.7, 0.62,
         para("A scenario's novelty = its average distance to the 5 most fault-revealing "
              "solutions in the current population.", size=12.5, color=MUTED, ls=1.15))
rect(s, 8.2, 1.78, 4.58, 3.05, ACC_TINT, radius=0.045)
add_text(s, 8.5, 2.02, 3.98, 0.3, para("Why a second objective?", size=15, bold=True, color=ACC_DEEP))
add_text(s, 8.5, 2.42, 3.98, 2.2,
         para("NSGA-II balances fault-revealing against novel, so the suite contains "
              "different failures - not 10 near-copies of one. Diversity of failing "
              "scenarios is exactly the criterion AmbieGen won at SBST 2022.",
              size=13, color=TEXT, ls=1.2))
rect(s, M, 5.12, CW, 1.5, CARD, radius=0.06)
add_text(s, M + 0.32, 5.34, CW - 0.64, 0.3,
         para("Two objectives, one search", size=14.5, bold=True, color=PRIMARY))
add_text(s, M + 0.32, 5.72, CW - 0.64, 0.62,
         para("objective 1 = fault-revealing fitness (per system under test) · "
              "objective 2 = novelty vs the elite of the population - NSGA-II evolves a "
              "Pareto front of scenarios that are critical AND diverse.",
              size=13, color=TEXT, ls=1.18))

# ================= SLIDE 11 — operators & outputs =================
s = slide()
header(s, "PART 1 · OPERATORS & OUTPUTS",
       "Operators, defaults, and what a run produces", page=11,
       source="Sources: robot_crossover.py:31-50 · vehicle_mutation.py:23-77 · vehicle_sampling.py:22-56 · config.py:2")
rect(s, M, 1.78, 6.3, 4.55, CARD, radius=0.045)
add_text(s, M + 0.3, 2.02, 5.7, 0.3, para("Search operators", size=16, bold=True, color=PRIMARY))
ops = [
    ("Crossover - one-point, p = 0.9",
     "a random cut in the element list; the tails are swapped (works across different lengths)"),
    ("Mutation - p = 0.4, 1-3 repeats",
     "exchange two random elements, or re-roll one element's type + attributes"),
    ("Sampling - random valid scenarios",
     "e.g. roads grown from random straight/right/left actions until the map border, then validity-checked"),
]
oy = 2.52
for lead, desc in ops:
    add_text(s, M + 0.3, oy, 5.7, 0.3, para(lead, size=14, bold=True, color=TEXT))
    add_text(s, M + 0.3, oy + 0.34, 5.7, 0.62, para(desc, size=12.5, color=MUTED, ls=1.15))
    oy += 1.12
add_text(s, M + 0.3, 5.88, 5.7, 0.3,
         para("duplicate elimination is built into every algorithm", size=11.5, color=MUTED))
rect(s, 7.1, 1.78, 5.68, 2.0, CARD, radius=0.045)
add_text(s, 7.4, 1.98, 5.1, 0.3, para("Shipped defaults (config.py)", size=14.5, bold=True, color=PRIMARY))
add_text(s, 7.4, 2.36, 5.1, 0.62,
         para("pop_size 100 · n_gen 100 · mut_rate 0.4\ncross_rate 0.9 · test_suite_size 10",
              size=13.5, bold=True, color=TEXT, font=MONO, ls=1.25))
add_text(s, 7.4, 3.16, 5.1, 0.5,
         para("paper experiments used 150 × 200 - our demo runs use a bounded 20 × 15 budget",
              size=11.5, color=MUTED, ls=1.1))
rect(s, 7.1, 3.98, 5.68, 2.35, CARD, radius=0.045)
add_text(s, 7.4, 4.18, 5.1, 0.3, para("Every run writes", size=14.5, bold=True, color=PRIMARY))
outs = [
    "stats JSON - suite fitness list + novelty · convergence JSON",
    "test cases JSON - the genomes of the suite",
    "scenario PNGs - one rendered image per test case",
]
oy = 4.56
for o in outs:
    rect(s, 7.42, oy + 0.08, 0.09, 0.09, ACCENT, radius=0.3)
    add_text(s, 7.66, oy - 0.02, 4.9, 0.32, para(o, size=12, color=TEXT))
    oy += 0.4
add_text(s, 7.4, 5.82, 5.1, 0.35,
         para("16-10-2026_stats_nsga2/ · _tcs_nsga2/ · _tc_images_nsga2/",
              size=11, color=MUTED, font=MONO))

# ================= SLIDE 12 — divider Part 2 =================
divider("02", "PART 2 · PRESENTER 2 · ~10 MINUTES",
        "Case Studies · Results · Demo",
        "What we ran on this machine - the paper's numbers, our built-in run, and our own team scenario",
        ["Paper results: failures found vs random search",
         "Live demo A - built-in robot case study (~86 s)",
         "Live demo B - team case study \u201cMountain Pass\u201d (~6 s)",
         "Strengths, limits, conclusions"],
        page=12)

# ================= SLIDE 13 — paper results =================
s = slide()
header(s, "PART 2 · PAPER RESULTS",
       "More failures found than random search", page=13,
       source="Source: Humeniuk et al., SCP 2023 - results sections (30 runs × 2-hour budget; NSGA-II 150 pop × 200 gens)")
rect(s, M, 1.75, 5.98, 4.45, CARD, radius=0.045)
add_text(s, M + 0.3, 1.95, 5.4, 0.55,
         para("Robot (Player/Stage) - avg failures in 2 h", size=13.5, bold=True, color=PRIMARY))
col_chart(s, M + 0.25, 2.5, 5.5, 3.5, ["AmbieGen", "Random search"], (9, 2),
          [ACCENT, PRIM_LT], vmax=10)
rect(s, 6.8, 1.75, 5.98, 4.45, CARD, radius=0.045)
add_text(s, 7.1, 1.95, 5.4, 0.55,
         para("LKAS (BeamNG.tech) - avg failures, SBST'22 pipeline", size=13.5, bold=True, color=PRIMARY))
col_chart(s, 7.05, 2.5, 5.5, 3.5, ["AmbieGen", "Frenetic", "Random"], (14, 14, 9),
          [ACCENT, PRIM_MID, PRIM_LT], vmax=16)
rect(s, M, 6.32, CW, 0.58, ACC_TINT, radius=0.12)
add_text(s, M + 0.3, 6.32, CW - 0.6, 0.58,
         para(runs=[
             ("9 vs 2", dict(bold=True, color=ACC_DEEP)),
             (" failures on the robot, and ", dict()),
             ("14 vs 9", dict(bold=True, color=ACC_DEEP)),
             (" on the LKAS vehicle - AmbieGen matches Frenetic on failures while also "
              "winning the diversity criterion (SBST 2022).", dict()),
         ], size=13), anchor=MSO_ANCHOR.MIDDLE)

# ================= SLIDE 14 — builtin run =================
s = slide()
header(s, "PART 2 · BUILT-IN CASE STUDY · OUR RUN",
       "Robot mazes: the search at work in 86 seconds", page=14,
       source="Artifacts: evidence/builtin/run_log.txt · 16-10-2026_stats_nsga2/ · images 16-10-2026_tc_images_nsga2/run0/")
add_text(s, M, 1.72, 3.3, 0.62, para("85.5 s", size=34, bold=True, color=PRIMARY))
add_text(s, M, 2.34, 3.3, 0.3, para("wall clock · 300 evaluations · seed 42", size=11.5, color=MUTED))
add_text(s, M, 2.86, 3.3, 0.72, para("132.1", size=44, bold=True, color=ACCENT))
add_text(s, M, 3.6, 3.3, 0.55,
         para("best A* path length - a maze is fault-revealing above 150",
              size=11.5, color=MUTED, ls=1.12))
add_text(s, M, 4.3, 3.3, 0.62, para("0.437", size=34, bold=True, color=PRIMARY))
add_text(s, M, 4.92, 3.3, 0.3, para("suite novelty (average pairwise)", size=11.5, color=MUTED))
add_text(s, M, 5.42, 3.35, 1.4,
         para("NSGA-II · pop 20 × 15 generations (bounded demo budget; "
              "shipped defaults are 100 × 100)", size=11.5, color=MUTED, ls=1.15))
add_text(s, 4.1, 1.72, 4.55, 0.3,
         para("Best-so-far fitness vs evaluations", size=13, bold=True, color=PRIMARY))
line_chart(s, 4.05, 2.05, 4.65, 4.0, EVALS, "best A* path length", ROBOT_FIT,
           "failure threshold (150)", [150] * 15, 80, 160)
img1 = os.path.join(EV, "builtin", "16-10-2026_tc_images_nsga2", "run0", "0.png")
img2 = os.path.join(EV, "builtin", "16-10-2026_tc_images_nsga2", "run0", "4.png")
s.shapes.add_picture(img1, Inches(8.9), Inches(1.95), width=Inches(1.85))
s.shapes.add_picture(img2, Inches(10.9), Inches(1.95), width=Inches(1.85))
add_text(s, 8.9, 3.86, 1.85, 0.26, para("tc0 - fitness 132.1", size=10, color=MUTED, align=PP_ALIGN.CENTER))
add_text(s, 10.9, 3.86, 1.85, 0.26, para("tc4 - fitness 120.7", size=10, color=MUTED, align=PP_ALIGN.CENTER))
rect(s, 8.9, 4.35, 3.85, 1.7, CARD, radius=0.09)
add_text(s, 9.12, 4.55, 3.45, 1.35,
         para("Each image is one generated maze: the walls plus the A* path the robot is "
              "forced to take. A longer path means a harder maze (bar = 150).",
              size=11.5, color=TEXT, ls=1.18))
rect(s, 4.05, 6.32, 8.7, 0.55, ACC_TINT, radius=0.12)
add_text(s, 4.3, 6.32, 8.2, 0.55,
         para(runs=[
             ("Live in the terminal: ", dict(bold=True, color=ACC_DEEP)),
             ("the pymoo table's cv_min column dropped 52.99 -> 17.92 - the search "
              "pushing path length toward the 150 bar.", dict()),
         ], size=12.5), anchor=MSO_ANCHOR.MIDDLE)

# ================= SLIDE 15 — team case study =================
s = slide()
header(s, "PART 2 · TEAM CASE STUDY",
       "\u201cMountain Pass\u201d: our scenario for the LKAS vehicle", page=15,
       source="Artifacts: runners/run_team_vehicle.py · evidence/team/team_scenario_config.json · evidence/team/README.md")
cfg = [
    ("Setting", "Shipped", "Mountain Pass"),
    ("map_size", "200", "200"),
    ("min_len", "5", "5"),
    ("max_len (straight cap)", "30", "12  *"),
    ("min_angle (turn)", "10°", "25°  *"),
    ("max_angle", "80°", "80°"),
    ("failure threshold", "5", "6  *"),
]
gt = s.shapes.add_table(7, 3, Inches(M), Inches(1.78), Inches(6.45), Inches(3.64)).table
gt.first_row = True
gt.horz_banding = False
for w, i in zip([3.05, 1.6, 1.8], range(3)):
    gt.columns[i].width = Inches(w)
for ri, row in enumerate(cfg):
    gt.rows[ri].height = Inches(0.52)
    changed = "*" in row[2]
    for ci, val in enumerate(row):
        c = gt.cell(ri, ci)
        if ri == 0:
            set_cell(c, val, size=12.5, bold=True, color=BG_LIGHT, fill=PRIMARY)
        else:
            fill = ACC_TINT if (changed and ci == 2) else (BG_LIGHT if ri % 2 == 1 else CARD)
            bold = changed and ci == 2
            col = ACC_DEEP if (changed and ci == 2) else (PRIMARY if ci == 0 else TEXT)
            set_cell(c, val, size=12.5, bold=bold, color=col, fill=fill,
                     font=MONO if ci > 0 else SANS,
                     align=PP_ALIGN.CENTER if ci > 0 else PP_ALIGN.LEFT)
add_text(s, M, 5.56, 6.45, 0.3,
         para("* the three changes that define our scenario (config.py:5-11 defaults)",
              size=11, color=MUTED))
add_text(s, M, 5.92, 6.45, 0.52,
         para("Scope, stated plainly: a team-designed scenario for the shipped LKAS SUT "
              "(runtime reconfiguration + one subclass) - not a brand-new SUT. The 4-class "
              "new-SUT recipe is mapped in research.md \u00a76 and listed under \u201cif we had "
              "more time\u201d (slide 18).",
              size=11, color=MUTED, ls=1.12))
rect(s, 7.25, 1.78, 5.53, 2.3, CARD, radius=0.045)
add_text(s, 7.55, 1.98, 4.95, 0.3, para("Why these changes", size=15, bold=True, color=PRIMARY))
whys = [
    "straights capped at 12 - the lane-keeper never gets a stable stretch to settle",
    "every turn ≥ 25° - sustained, hairpin-like curvature",
    "failure bar raised 5 -> 6 - harder to reveal a failure",
]
wy = 2.38
for wtxt in whys:
    rect(s, 7.57, wy + 0.07, 0.09, 0.09, ACCENT, radius=0.3)
    add_text(s, 7.82, wy - 0.03, 4.75, 0.5, para(wtxt, size=12, color=TEXT, ls=1.1))
    wy += 0.52
rect(s, 7.25, 4.24, 5.53, 2.1, CARD, radius=0.045)
add_text(s, 7.55, 4.44, 4.95, 0.3,
         para("How - zero repo files modified", size=15, bold=True, color=PRIMARY))
hows = [
    "scenario set through the native vehicle_env config, patched at runtime",
    "stricter constraint via subclass MountainVehicleProblem2Obj, registered as \u201cvehicle_nsga2\u201d",
]
hy = 4.84
for htxt in hows:
    add_text(s, 7.55, hy, 4.95, 0.55, para(htxt, size=12, color=TEXT, ls=1.12))
    hy += 0.62
add_text(s, 7.55, 5.98, 4.95, 0.28,
         para("runners/run_team_vehicle.py", size=11, color=MUTED, font=MONO))
rect(s, M, 6.5, CW, 0.5, ACC_TINT, radius=0.14)
add_text(s, M + 0.3, 6.5, CW - 0.6, 0.5,
         para(runs=[
             ("Research question: ", dict(bold=True, color=ACC_DEEP)),
             ("can the search still push the simplified LKAS out of its lane on aggressive "
              "geometry and a higher failure bar?", dict()),
         ], size=12.5), anchor=MSO_ANCHOR.MIDDLE)

# ================= SLIDE 16 — team results =================
s = slide()
header(s, "PART 2 · TEAM CASE STUDY · RESULTS",
       "Mountain Pass: deviation pushed to 4.65 against a bar of 6", page=16,
       source="Artifacts: evidence/team/run_log.txt · 16-10-2026_team_stats_nsga2/ · images 16-10-2026_team_tc_images_nsga2/run0/")
add_text(s, M, 1.72, 3.3, 0.62, para("5.9 s", size=34, bold=True, color=PRIMARY))
add_text(s, M, 2.34, 3.3, 0.3, para("wall clock · 300 evaluations · seed 42", size=11.5, color=MUTED))
add_text(s, M, 2.86, 3.3, 0.72, para("4.649", size=44, bold=True, color=ACCENT))
add_text(s, M, 3.6, 3.3, 0.55,
         para("best max lane deviation - failure needs more than 6 (team bar)",
              size=11.5, color=MUTED, ls=1.12))
add_text(s, M, 4.3, 3.3, 0.55, para("2.36 -> 1.35", size=30, bold=True, color=PRIMARY))
add_text(s, M, 4.88, 3.3, 0.3, para("constraint violation (cv_min) over 15 generations",
                                    size=11.5, color=MUTED))
add_text(s, M, 5.36, 3.3, 0.62, para("0.583", size=34, bold=True, color=PRIMARY))
add_text(s, M, 5.98, 3.3, 0.3, para("suite novelty (average pairwise)", size=11.5, color=MUTED))
add_text(s, 4.1, 1.72, 4.55, 0.3,
         para("Best-so-far lane deviation vs evaluations", size=13, bold=True, color=PRIMARY))
line_chart(s, 4.05, 2.05, 4.65, 4.0, EVALS, "best max deviation", TEAM_FIT,
           "failure threshold (6)", [6] * 15, 3, 6.6)
img1 = os.path.join(EV, "team", "16-10-2026_team_tc_images_nsga2", "run0", "0.png")
img2 = os.path.join(EV, "team", "16-10-2026_team_tc_images_nsga2", "run0", "1.png")
s.shapes.add_picture(img1, Inches(8.9), Inches(1.95), width=Inches(1.85))
s.shapes.add_picture(img2, Inches(10.9), Inches(1.95), width=Inches(1.85))
add_text(s, 8.9, 3.86, 1.85, 0.26, para("tc0 - deviation 4.65", size=10, color=MUTED, align=PP_ALIGN.CENTER))
add_text(s, 10.9, 3.86, 1.85, 0.26, para("tc1 - deviation 4.38", size=10, color=MUTED, align=PP_ALIGN.CENTER))
rect(s, 8.9, 4.35, 3.85, 1.7, CARD, radius=0.09)
add_text(s, 9.12, 4.55, 3.45, 1.35,
         para("Gray band = the road polygon; blue dots = the car's path drifting away "
              "from the centreline through the hairpins.", size=11.5, color=TEXT, ls=1.18))
rect(s, 4.05, 6.32, 8.7, 0.55, ACC_TINT, radius=0.12)
add_text(s, 4.3, 6.32, 8.2, 0.55,
         para(runs=[
             ("Read of the result: ", dict(bold=True, color=ACC_DEEP)),
             ("the best deviation rose 3.64 -> 4.65 and never regressed, but did not cross "
              "the stricter bar of 6 within this small budget - the expected effect of a "
              "higher threshold.", dict()),
         ], size=12.5), anchor=MSO_ANCHOR.MIDDLE)

# ================= SLIDE 17 — strengths & limits =================
s = slide()
header(s, "PART 2 · DISCUSSION",
       "What we learned: strengths and limits", page=17,
       source="Limits verified in our session, 2026-10-16 (see research.md §5, §7)")
rect(s, M, 1.78, 5.98, 4.6, CARD, radius=0.045)
add_text(s, M + 0.3, 2.0, 5.4, 0.3, para("Strengths", size=16, bold=True, color=PRIMARY))
kv_rows(s, M + 0.3, 2.44, 5.35, [
    ("Modularity is real",
     "a new scenario needed only a runtime config patch + one subclass; the 4-class "
     "extension path is how the tool is actually built."),
    ("Cheap fitness, big budget",
     "simplified models keep evaluations fast - a 2-hour budget yields a 30-case suite "
     "in the paper."),
    ("Diversity as an objective",
     "novelty inside NSGA-II produced varied failing scenarios - the SBST 2022 winning "
     "criterion."),
    ("Reproducible tooling",
     "seeds, per-run stats, convergence logs, compare.py boxplots."),
], lead_size=13.5, desc_size=11.5, gap=0.12)
rect(s, 6.8, 1.78, 5.98, 4.6, CARD, radius=0.045)
add_text(s, 7.1, 2.0, 5.4, 0.3, para("Limits", size=16, bold=True, color=ACC_DEEP))
kv_rows(s, 7.1, 2.44, 5.35, [
    ("Surrogate, not reality",
     "fitness uses simplified 2D models - no pedestrians, traffic or other cars in the "
     "representation (paper's future work)."),
    ("Small problem zoo",
     "two systems under test (robot, vehicle), three algorithms."),
    ("Dependency rough edges",
     "requirements.txt omits scipy/matplotlib/descartes; pymoo must stay pinned to "
     "0.6.0 (0.6.1+ breaks _evaluate); descartes crashes with shapely >= 2."),
    ("Docs vs code",
     "README example uses --algo; the real flag is --algorithm (optimize.py:58)."),
], lead_size=13.5, desc_size=11.5, gap=0.12)

# ================= SLIDE 18 — conclusions =================
s = slide()
header(s, "PART 2 · CONCLUSIONS", "Four takeaways", page=18)
concl = [
    ("Search finds failures that random misses",
     "9 vs 2 failures on the robot and 14 vs 9 on the LKAS vehicle, on the paper's "
     "30-run × 2-hour budget."),
    ("The recipe: cheap model + novelty objective",
     "surrogate fitness makes the loop fast; the second objective keeps the suite "
     "diverse - together they won SBST 2022."),
    ("Extensible in practice",
     "we built the \u201cMountain Pass\u201d scenario without modifying a single repo "
     "file - runtime config + one subclass."),
    ("Read the code, not just the README",
     "pin pymoo==0.6.0, install the missing deps - and remember the fitness is a "
     "simplified model, not the real simulator."),
]
cy = 1.82
for i, (lead, desc) in enumerate(concl, 1):
    chip(s, M, cy, 0.52, str(i), fsize=16)
    add_text(s, M + 0.78, cy - 0.04, 11.4, 0.32, para(lead, size=16.5, bold=True, color=PRIMARY))
    add_text(s, M + 0.78, cy + 0.34, 11.4, 0.35, para(desc, size=13, color=TEXT))
    cy += 0.98
rect(s, M, 5.85, CW, 1.0, CARD, radius=0.06)
add_text(s, M + 0.32, 6.02, 2.4, 0.66,
         para("If we had more time", size=14, bold=True, color=PRIMARY), anchor=MSO_ANCHOR.MIDDLE)
add_text(s, M + 2.75, 6.02, 9.3, 0.66,
         para("full 100 × 100 run (~45-50 min, est. from our measured 85.5 s) · a brand-new "
              "SUT via the 4-class recipe · compare.py boxplots: NSGA-II vs random · "
              "quality-diversity search (paper's future work)",
              size=12, color=TEXT, ls=1.18), anchor=MSO_ANCHOR.MIDDLE)

# ================= SLIDE 19 — references =================
s = slide()
header(s, "BOTH PARTS · BIBLIOGRAPHY", "References", page=19,
       source="All sources below were fetched, cloned or executed in our session, 2026-10-16")
rect(s, M, 1.72, CW, 1.42, CARD, radius=0.055)
add_text(s, M + 0.3, 1.92, 2.2, 0.3, para("[1]  The paper", size=14, bold=True, color=PRIMARY))
add_text(s, M + 0.3, 2.28, CW - 0.6, 0.78,
         para(runs=[
             ("Humeniuk, D., Khomh, F., Antoniol, G. \u201cAmbieGen: A Search-based Framework "
              "for Autonomous Systems Testing.\u201d ", dict()),
             ("Science of Computer Programming 230 (2023), art. 102990", dict(bold=True)),
             (" \u00b7 doi 10.1016/j.scico.2023.102990 \u00b7 arXiv:2301.01234 "
              "(abstract + full HTML, fetched 2026-10-16).", dict()),
         ], size=12.5, color=TEXT, ls=1.2))
rect(s, M, 3.3, 5.98, 1.62, CARD, radius=0.055)
add_text(s, M + 0.3, 3.5, 5.4, 0.3, para("[2]  The tool", size=14, bold=True, color=PRIMARY))
add_text(s, M + 0.3, 3.86, 5.4, 0.95,
         para("AmbieGen-tool - github.com/swat-lab-optimization/AmbieGen-tool, MIT license, "
              "v0.1.0, winner of the SBST 2022 tool competition; built on the Pymoo "
              "framework (pymoo.org). Cloned and executed by us, 2026-10-16.",
              size=12.5, color=TEXT, ls=1.2))
rect(s, 6.8, 3.3, 5.98, 1.62, CARD, radius=0.055)
add_text(s, 7.1, 3.5, 5.4, 0.3, para("[3]  Our artifacts", size=14, bold=True, color=PRIMARY))
add_text(s, 7.1, 3.86, 5.4, 0.95,
         para("research.md (verified knowledge base) \u00b7 runners/run_builtin_robot.py, "
              "run_team_vehicle.py \u00b7 evidence/builtin/, evidence/team/ (logs, stats, "
              "test cases, images) \u00b7 demo-run.md, demo-script.md.",
              size=12.5, color=TEXT, ls=1.2))
rect(s, M, 5.08, CW, 0.72, ACC_TINT, radius=0.1)
add_text(s, M + 0.3, 5.08, CW - 0.6, 0.72,
         para(runs=[
             ("AI usage for this deliverable ", dict(bold=True, color=ACC_DEEP)),
             ("(tool, purpose, prompts, results, edits, validation) is documented in "
              "AI_USAGE.md.", dict()),
         ], size=12.5), anchor=MSO_ANCHOR.MIDDLE)
add_text(s, M, 6.06, CW, 0.55,
         para("Every slide also carries its own source line (paper section, repo file:line, "
              "or evidence/ artifact) - the full index is in research.md \u00a78.",
              size=11.5, color=MUTED, ls=1.15))

# ================= SLIDE 20 — demo pointers / close (dark) =================
s = slide(BG_DARK)
add_text(s, M, 0.62, CW, 0.3, para("PART 2 · LIVE DEMO", size=12, bold=True, color=ACCENT))
add_text(s, M, 0.98, CW, 0.65, para("See it run - the exact commands", size=32, bold=True, color=ON_DARK))
demo = [
    ("A", "Built-in robot case study - ~86 s",
     "cd tss\\course-ambiegen\n.venv\\Scripts\\python.exe runners\\run_builtin_robot.py",
     "watch the pymoo table: cv_min 52.99 -> 17.92 · then the mazes in "
     "evidence\\builtin\\16-10-2026_tc_images_nsga2\\run0\\*.png"),
    ("B", "Team \u201cMountain Pass\u201d - ~6 s",
     ".venv\\Scripts\\python.exe runners\\run_team_vehicle.py",
     "watch cv_min 2.36 -> 1.35 · then the roads in "
     "evidence\\team\\16-10-2026_team_tc_images_nsga2\\run0\\*.png"),
]
cx = M
for tag, title, cmd, watch in demo:
    rect(s, cx, 2.05, 5.98, 2.6, CARD_DARK, line=LINE_DARK, radius=0.055)
    chip(s, cx + 0.28, 2.32, 0.5, tag, fsize=15)
    add_text(s, cx + 0.96, 2.32, 4.8, 0.5, para(title, size=15, bold=True, color=ON_DARK),
             anchor=MSO_ANCHOR.MIDDLE)
    rect(s, cx + 0.28, 3.0, 5.42, 0.86, BG_DARK, radius=0.1)
    add_text(s, cx + 0.46, 3.0, 5.1, 0.86,
             para(cmd, size=12, color=RGBColor.from_string("D8DFE8"), font=MONO, ls=1.25),
             anchor=MSO_ANCHOR.MIDDLE)
    add_text(s, cx + 0.28, 3.98, 5.42, 0.6, para(watch, size=11, color=MUT_DARK, ls=1.15))
    cx += 6.25
rect(s, M, 5.05, CW, 0.9, CARD_DARK, line=LINE_DARK, radius=0.07)
add_text(s, M + 0.32, 5.05, CW - 0.64, 0.9,
         para(runs=[
             ("Where the numbers come from: ", dict(bold=True, color=ACCENT)),
             ("every command, time and figure on these slides is reproduced in "
              "demo-run.md and demo-script.md, with logs under evidence/.",
              dict(color=MUT_DARK)),
         ], size=12.5), anchor=MSO_ANCHOR.MIDDLE)
add_text(s, M, 6.15, CW, 0.6, para("Thank you - questions?", size=30, bold=True, color=ON_DARK))
add_text(s, M, 6.95, CW, 0.3,
         para("Presenter 1 - problem · framework · method   |   Presenter 2 - case "
              "studies · results · demo   |   timings measured 2026-10-16",
              size=11.5, color=MUT_DARK))

prs.save(OUT)
print("saved", OUT, "slides:", len(prs.slides._sldIdLst))
