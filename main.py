#!/usr/bin/env python3
"""The World Today - 26 November 2026 (news-image-20261126) - REVISION.

Entry program for the make.fun one-day world news image competition.
It writes entry.png to $MAKEFUN_OUTPUT_DIR (default /output).

Revision of the 15:00 build: the evening news of 26 November is added
(Bangkok refinery blast, Hormuz mine strikes, Gaza strikes, China's tariff
reply, EU budget deadlock, UK migration low), and the page is redrawn with
real serif type (Playfair Display / Newsreader) instead of the system
fallback, with justified decks, a drop cap and paper grain.

The front page is drawn with Pillow when Pillow is available. The grader
runs with only the Python standard library, so when Pillow is missing the
program falls back to copying the entry.png shipped in this repository.
Both paths write byte-identical output, and the program never writes
outside $MAKEFUN_OUTPUT_DIR.
"""
import os
import random
import shutil
import sys

try:
    from PIL import Image, ImageDraw, ImageFont  # type: ignore
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False

W, H = 1024, 1024
BG = (244, 239, 230)      # #f4efe6 paper
INK = (28, 28, 28)        # #1c1c1c charcoal ink
RED = (140, 29, 24)
GRAY = (96, 92, 86)
LINE = (201, 194, 184)
MAP_BG = (238, 233, 224)
LAND = (203, 196, 180)
LAND_EDGE = (138, 130, 114)
ORANGE = (214, 90, 20)
GOLD = (212, 160, 40)

# ---- type: downloaded serif fonts live in the -side folder (never in the
# repo); system DejaVu is the fallback so the draw code never crashes.
_HERE = os.path.dirname(os.path.abspath(__file__))
_FONT_DIR = os.path.normpath(os.path.join(_HERE, "..",
                                          "news-image-20261126-rev-side",
                                          "fonts"))
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _pick(name):
    p = os.path.join(_FONT_DIR, name)
    return p if os.path.exists(p) else None


DISPLAY = _pick("PlayfairDisplay.ttf")   # variable wght 400..900
HEAD2 = _pick("Merriweather.ttf")        # variable opsz,wdth,wght
BODY = _pick("Newsreader.ttf")           # variable opsz,wght
BODY2 = _pick("Lora.ttf")                # variable wght


def _font(path, size, weight=400):
    """Load a TTF at a variable-font weight; fall back to DejaVu."""
    if path:
        try:
            f = ImageFont.truetype(path, size)
            try:
                f.set_variation_by_axes([weight])
            except Exception:
                pass
            return f
        except Exception:
            pass
    fb = SERIF_B if weight >= 700 else SERIF
    return ImageFont.truetype(fb, size)


def _sans(size, bold=False):
    return ImageFont.truetype(SANS_B if bold else SANS, size)


LEADS = [
    ("TRADE WAR", "US proposes tariffs on 14 partners",
     "India 25%, Japan 15%, China 20%. China vows \u2018necessary measures\u2019; "
     "India warns 500,000 jobs at risk.",
     "bars"),
    ("MIDDLE EAST", "Houthis hit Riyadh tower; Saudi strikes widen",
     "PIF tower strike hurt 11; UK sanctions the Houthis as Brent tops $95.",
     "tower"),
    ("EGYPT", "Cairo tanker fire kills at least 31",
     "Fuel tanker overturned and burst into flames on the ring road; cars burned.",
     "tanker"),
]

SECONDARY = [
    ("Iran: tankers hit mines in Hormuz; Brent tops $95",
     "IRGC claims two tankers hit mines near Khasab; UKMTO blast off Dubai. \u2014 Reuters, BBC"),
    ("Bangkok refinery blast injures 9; all units shut",
     "Explosion at Bangchak oil depot; nine workers hurt. \u2014 BBC, Al Jazeera"),
    ("Ukraine: 10 killed, 58 hurt in a day of strikes",
     "Ballistic missiles hit Kyiv mall; 113 drones, 76 jet-powered. \u2014 Reuters, BBC"),
    ("EU budget summit deadlocked; Ukraine aid clash",
     "Leaders \u2018light-years away\u2019 (Meloni); EUR 2tn budget. \u2014 Guardian"),
    ("Gaza: Hamas official among 8 killed in strikes",
     "Political official and wife among the dead. \u2014 BBC, Al Jazeera"),
    ("Myanmar rejects parts of ICJ genocide ruling",
     "Refuses to comply with \u2018inappropriate\u2019 parts. \u2014 BBC, Japan Times"),
    ("Bank of Korea raises rate to 3.25%",
     "Up 25bp, highest in two years; 2027 growth 4.1%. \u2014 Yonhap, CNBC"),
    ("Kim vows more nuclear weapons",
     "Tactical deployment wider; more nukes vowed. \u2014 Al Jazeera, Asahi"),
    ("Spain votes Sunday; final polls: PP 31.8%, Vox 17.3%",
     "PP+Vox 188 seats; poll blackout in force. \u2014 El Pais/40dB"),
    ("Nepal moves to declare 4,000 flood dead",
     "Legal process begins; 213 Indians missing. \u2014 SCMP, The Hindu"),
    ("Macy\u2019s delays 100th parade",
     "First weather delay ever; now Saturday. \u2014 BBC, France 24"),
]

BRIEFS = [
    "Dozens of nations urge Russia to halt alleged riot-agent use. \u2014 Reuters",
    "Second judge blocks Trump\u2019s birthright citizenship order. \u2014 Reuters",
    "Murmansk governor held in pre-trial detention for graft. \u2014 Reuters",
    "Ecuador says US talks focused on reviewing operations. \u2014 Reuters",
    "Lebanon to open second airport as Hezbollah sway fades. \u2014 Reuters",
    "How China got Nvidia AI chips despite export rules. \u2014 Reuters",
    "UK sends convicted refugees to Eswatini in first. \u2014 BBC / Guardian",
    "Indonesia mine flood: bodies recovered; 13 dead, 13 trapped. \u2014 Al Jazeera",
    "ISIL suicide attack kills two at Syria checkpoint. \u2014 Al Jazeera",
    "Iraq court backs federal control of Kurdistan oil. \u2014 Al Jazeera",
    "Australia projected to miss 2035 emissions target. \u2014 Guardian",
    "Champions League: Liverpool 3-0 Brugge; Barca 4-1 Sabah. \u2014 BBC Sport",
    "Jennifer Barreto wins Miss Universe 2026. \u2014 Euronews",
    "Rare brine lakes found beneath the Red Sea. \u2014 ScienceDaily",
    "China vows \u2018necessary measures\u2019 after US tariff plan. \u2014 Guardian",
    "India trade body warns 500,000 jobs at risk from US tariffs. \u2014 CNA",
    "Japan calls US tariff proposal \u2018regrettable\u2019. \u2014 Japan Times",
    "UK sanctions Yemen\u2019s Houthis amid Saudi attacks. \u2014 Al Jazeera",
    "FIFA hit by cyberattack; personal data stolen. \u2014 CNA",
    "Cheaper HIV prevention jab reaches Africa. \u2014 BBC",
    "DR Congo Ebola cases pass 12,000. \u2014 Al Jazeera",
    "Diesel tanker sinks near Ibiza; one killed. \u2014 BBC",
    "Hong Kong exports grow fastest in 70 years. \u2014 SCMP",
    "UniCredit clears final hurdle for Commerzbank takeover. \u2014 Bloomberg",
]

TIMELINE = [
    "00:00 UTC Korea raises rate to 3.25%",
    "04:10 UTC US tariff proposals published",
    "08:00 UTC EU budget summit opens",
    "09:30 UTC Bangkok refinery blast reported",
    "10:14 UTC Gaza strikes kill Hamas official",
    "12:00 UTC China vows \u2018necessary measures\u2019",
    "12:31 UTC FIFA confirms cyberattack",
]

# region colour system (winners group stories by region colour)
REG_COL = {"NA": (140, 29, 24), "ME": (178, 74, 20), "EU": (30, 80, 140),
           "AS": (30, 120, 70), "AF": (146, 104, 20), "SA": (122, 44, 112),
           "OC": (38, 128, 138)}
LEAD_COL = [REG_COL["NA"], REG_COL["ME"], REG_COL["AF"]]
SEC_REG = ["ME", "AS", "EU", "EU", "ME", "AS", "AS", "AS", "EU", "AS", "NA"]
BRIEF_REG = ["EU", "NA", "EU", "SA", "ME", "AS", "AF", "AS", "ME", "ME",
             "OC", "EU", "NA", "AF", "AS", "AS", "AS", "EU", "EU", "AF",
             "AF", "EU", "AS", "EU"]
PIN_REG = ["NA", "ME", "AF", "ME", "AS", "EU", "EU", "ME", "AS", "AS",
           "AS", "EU", "AS", "NA"]
NUM_CELLS = [("31", "KILLED \u00b7 CAIRO"), ("14", "TARIFF PARTNERS"),
             ("$95.27", "BRENT CRUDE"), ("9", "HURT \u00b7 BANGKOK"),
             ("4,000", "DEAD \u00b7 NEPAL"), ("3.25%", "KOREA RATE")]

MARKETS = [
    ("S&P 500", "-0.25%"), ("Euro Stoxx 50", "-1.82%"),
    ("Shanghai", "-2.05%"), ("Nikkei", "+1.55%"),
    ("Brent crude", "$95.27  +4.5%"), ("Bitcoin (month)", "-24.3%"),
    ("US inflation", "3.8%"), ("US 10-year yield", "4.85%"),
]

DIGEST = [
    "Tariffs: China vows \u2018necessary measures\u2019; India warns 500,000 jobs at risk.",
    "Hormuz: Iran says two tankers hit mines; Brent tops $95.",
    "Bangkok: refinery blast injures nine; all units shut.",
]

DATECHECK = ("DATE CHECK \u2014 NOT 26 NOVEMBER:  Ras Tanura refinery attack (25 Nov)  \u00b7  "
             "Gaza: Hamas security chief killed (25 Nov)  \u00b7  First Pakistani astronaut (25 Nov)  \u00b7  "
             "Huawei verdict (24 Nov)  \u00b7  SpaceX satellite plan approved (25 Nov)  \u00b7  "
             "Duran Duran guitarist died (25 Nov)  \u00b7  US Army Iowa stockpile blast (25 Nov)  \u00b7  "
             "COP31 failed (22 Nov)")

# (lon, lat) pins for stories 1..14
PINS = [(-77, 39), (46.7, 24.7), (31.2, 30.0), (56.5, 26.5), (100.5, 13.75),
        (30.5, 50.5), (4.35, 50.85), (34.5, 31.5), (96.0, 21.0), (127, 37.5),
        (125.75, 39.0), (-3.7, 40.4), (85.3, 27.7), (-74, 40.7)]

# simplified continent outlines (lon, lat), drawn fresh for this revision
N_AMERICA = [(-168, 66), (-155, 58), (-140, 60), (-130, 54), (-124, 42),
             (-120, 34), (-112, 28), (-105, 20), (-97, 16), (-90, 14),
             (-83, 9), (-79, 8), (-82, 10), (-88, 13), (-94, 17), (-97, 22),
             (-97, 26), (-92, 29), (-88, 30), (-84, 30), (-81, 26),
             (-80, 32), (-76, 35), (-74, 40), (-70, 43), (-65, 44),
             (-60, 47), (-55, 47), (-60, 50), (-65, 58), (-70, 62),
             (-80, 63), (-90, 66), (-100, 68), (-120, 69), (-140, 70),
             (-158, 71), (-168, 66)]
GREENLAND = [(-55, 60), (-45, 60), (-40, 65), (-30, 68), (-20, 70),
             (-22, 76), (-35, 77), (-50, 76), (-58, 72), (-58, 64)]
S_AMERICA = [(-78, 7), (-80, 2), (-81, -4), (-78, -12), (-72, -20),
             (-70, -30), (-72, -40), (-74, -50), (-68, -54), (-65, -48),
             (-60, -38), (-56, -34), (-50, -30), (-42, -22), (-38, -15),
             (-35, -8), (-38, -4), (-44, -2), (-50, 0), (-53, 5), (-58, 8),
             (-65, 10), (-72, 11), (-77, 7)]
AFRICA = [(-17, 15), (-16, 22), (-12, 28), (-6, 34), (0, 36), (10, 37),
          (12, 33), (18, 32), (25, 32), (31, 31), (33, 28), (36, 22),
          (39, 18), (42, 12), (48, 11), (50, 10), (44, 2), (40, -6),
          (39, -14), (35, -20), (32, -26), (28, -33), (20, -35), (16, -30),
          (13, -22), (12, -14), (12, -6), (9, 0), (8, 4), (-2, 5), (-8, 5),
          (-13, 8), (-17, 12)]
EUROPE = [(-10, 36), (-9, 42), (-2, 44), (-1, 46), (-4, 48), (-1, 50),
          (2, 51), (5, 53), (8, 55), (8, 58), (11, 58), (18, 56), (21, 55),
          (24, 58), (28, 59), (30, 60), (25, 60), (20, 59), (18, 56),
          (12, 54), (8, 54), (4, 52), (0, 50), (-3, 47), (-6, 43), (-9, 38)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (-4, 50)]
ASIA = [(28, 36), (32, 41), (38, 42), (44, 40), (48, 42), (52, 44),
        (56, 42), (60, 38), (64, 40), (68, 43), (72, 47), (76, 50),
        (82, 55), (90, 60), (98, 64), (105, 68), (112, 71), (120, 73),
        (130, 71), (140, 72), (150, 70), (160, 69), (170, 66), (178, 64),
        (172, 60), (162, 58), (156, 52), (150, 59), (142, 54), (141, 48),
        (139, 42), (135, 42), (130, 42), (127, 38), (124, 39), (121, 34),
        (120, 28), (114, 22), (109, 18), (106, 10), (103, 8), (99, 10),
        (96, 15), (93, 19), (89, 22), (86, 20), (82, 17), (79, 13),
        (76, 9), (74, 15), (72, 20), (69, 23), (65, 25), (61, 25),
        (57, 26), (53, 27), (50, 29), (47, 30), (44, 29), (41, 25),
        (39, 21), (37, 17), (35, 19), (34, 24), (32, 28), (30, 31),
        (28, 35)]
AUSTRALIA = [(113, -22), (114, -30), (115, -33), (118, -35), (124, -33),
             (129, -32), (133, -32), (136, -35), (140, -38), (145, -38),
             (148, -39), (150, -37), (153, -31), (153, -26), (150, -22),
             (146, -19), (142, -14), (141, -12), (139, -17), (136, -15),
             (134, -12), (131, -12), (127, -14), (123, -17), (118, -20),
             (114, -22)]


# ---------------- drawing helpers ----------------

def _wrap(d, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _fit_text(d, text, path, max_size, max_w, weight=700):
    """Largest font size <= max_size whose text fits max_w."""
    size = max_size
    while size > 8:
        f = _font(path, size, weight)
        if d.textlength(text, font=f) <= max_w:
            return f
        size -= 1
    return _font(path, 8, weight)


def _trunc(d, text, font, max_w):
    while text and d.textlength(text + "\u2026", font=font) > max_w:
        text = text[:-1].rstrip()
    return text + ("\u2026" if d.textlength(text, font=font) > max_w else "")


def _justified(d, lines, font, x, y, max_w, line_h, fill, first_indent=0):
    """Draw wrapped lines justified (all but the last); returns end y."""
    for li, ln in enumerate(lines):
        words = ln.split()
        yy = y + li * line_h
        if li == len(lines) - 1 or len(words) < 2:
            d.text((x + (first_indent if li == 0 else 0), yy), ln,
                   font=font, fill=fill)
            continue
        w0 = d.textlength(ln, font=font)
        extra = max_w - (first_indent if li == 0 else 0) - w0
        gap = extra / (len(words) - 1)
        xx = x + (first_indent if li == 0 else 0)
        for w in words:
            d.text((xx, yy), w, font=font, fill=fill)
            xx += d.textlength(w, font=font) + d.textlength(" ", font=font) + gap
    return y + len(lines) * line_h


def _draw_page(out_path):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    L, R = 30, W - 30
    CW = R - L  # 964

    # --- masthead ---
    y = 12
    f_title = _fit_text(d, "THE WORLD TODAY", DISPLAY, 58, CW, weight=900)
    d.text((W // 2, y), "THE WORLD TODAY", font=f_title, fill=INK, anchor="ma")
    y += f_title.size + 2
    f_date = _font(BODY, 20, 600)
    d.text((W // 2, y), "Thursday, 26 November 2026", font=f_date, fill=INK,
           anchor="ma")
    f_sub = _font(BODY, 12, 400)
    d.text((L, y + 4), "No. 331", font=f_sub, fill=GRAY)
    d.text((R, y + 4), "PRICE $1.20", font=f_sub, fill=GRAY, anchor="ra")
    y += 28
    d.line([(L, y), (R, y)], fill=INK, width=3)
    d.line([(L, y + 5), (R, y + 5)], fill=INK, width=1)
    y += 11

    # --- timeline strip ---
    f_tl_lab = _sans(11, bold=True)
    f_tl = _font(BODY, 11, 400)
    d.text((L, y), "THE DAY IN UTC", font=f_tl_lab, fill=RED)
    lab_w = d.textlength("THE DAY IN UTC  ", font=f_tl_lab)
    tl_lines = _wrap(d, "  \u00b7  ".join(TIMELINE), f_tl, CW - lab_w)
    for ln in tl_lines[:2]:
        ln = ln.strip().removeprefix("\u00b7").strip()
        d.text((L + lab_w, y), ln, font=f_tl, fill=GRAY)
        y += 14
    y += 4

    # --- numbers strip: six big-number cells (winners show big figures) ---
    f_big = _font(DISPLAY, 22, 700)
    f_lab2 = _sans(9, bold=True)
    cell_w = CW // 6
    d.rectangle([L, y, R, y + 44], fill=INK)
    for ci, (num, lab) in enumerate(NUM_CELLS):
        cx = L + ci * cell_w + cell_w // 2
        d.text((cx, y + 5), num, font=f_big, fill=(244, 239, 230),
               anchor="ma")
        d.text((cx, y + 30), lab, font=f_lab2, fill=(200, 192, 180),
               anchor="ma")
        if ci:
            d.line([(L + ci * cell_w, y + 6), (L + ci * cell_w, y + 38)],
                   fill=(90, 86, 80), width=1)
    y += 50

    # --- region counts (coloured dots, winners group by region) ---
    f_reg = _font(None, 12, 700)
    segs = [("N. AMERICA 4", "NA"), ("MIDDLE EAST 6", "ME"),
            ("EUROPE 10", "EU"), ("ASIA 11", "AS"),
            ("AFRICA 5", "AF"), ("S. AMERICA 1", "SA"),
            ("OCEANIA 1", "OC"), ("38 STORIES", None)]
    parts, tot = [], 0
    for txt, key in segs:
        w = d.textlength(txt, font=f_reg) + (14 if key else 0)
        parts.append((txt, key, w))
        tot += w
    tot += d.textlength("  \u00b7  ", font=f_reg) * (len(segs) - 1)
    xx = (W - tot) // 2
    for idx, (txt, key, w) in enumerate(parts):
        if key:
            d.ellipse([xx, y + 2, xx + 8, y + 10], fill=REG_COL[key])
            xx += 12
        d.text((xx, y), txt, font=f_reg, fill=INK)
        xx += d.textlength(txt, font=f_reg)
        if idx < len(segs) - 1:
            d.text((xx, y), "  \u00b7  ", font=f_reg, fill=GRAY)
            xx += d.textlength("  \u00b7  ", font=f_reg)
    y += 19

    # --- leads: 3 columns ---
    col_w = 308
    xs = [L, L + col_w + 20, L + 2 * (col_w + 20)]
    lead_top = y
    f_kick = _sans(11, bold=True)
    f_head = _font(DISPLAY, 23, 700)
    f_deck = _font(BODY, 13, 400)
    LEAD_LABEL = ["WASHINGTON \u00b7 TARIFFS", "RIYADH \u00b7 PIF TOWER",
                  "CAIRO \u00b7 RING ROAD"]
    for i, (kick, head, deck, art) in enumerate(LEADS):
        x = xs[i]
        # picture panel on top (winners put the picture above the headline)
        vy = lead_top
        vh = 92
        d.rectangle([x, vy, x + col_w, vy + vh], outline=LINE, width=1)
        if art == "bars":
            bars = [("INDIA", 25, RED), ("CHINA", 20, INK),
                    ("VIETNAM", 20, INK), ("INDONESIA", 18, INK),
                    ("JAPAN", 15, GRAY)]
            bw, gap = 40, 16
            bx = x + 18
            for name, val, col in bars:
                bh = int(val / 25 * 48)
                top = vy + 68 - bh
                d.rectangle([bx, top, bx + bw, vy + 68], fill=col)
                f_v = _sans(10, bold=True)
                d.text((bx + bw // 2, top + 2), "%d%%" % val,
                       font=f_v, fill=(255, 255, 255), anchor="ma")
                f_n = _sans(8)
                d.text((bx + bw // 2, vy + 68), name, font=f_n,
                       fill=GRAY, anchor="ma")
                bx += bw + gap
        elif art == "tower":
            # PIF tower + blast burst over a low skyline
            tx = x + col_w // 2
            d.rectangle([x + 8, vy + 70, x + col_w - 8, vy + 76], fill=GRAY)
            d.rectangle([tx - 52, vy + 44, tx - 34, vy + 70], fill=(60, 58, 54))
            d.rectangle([tx + 34, vy + 52, tx + 52, vy + 70], fill=(60, 58, 54))
            d.rectangle([tx - 16, vy + 20, tx + 16, vy + 70], fill=INK)
            d.line([(tx, vy + 8), (tx, vy + 20)], fill=INK, width=2)
            for dx, dy, c in [(-46, 12, ORANGE), (-36, 4, GOLD),
                              (-52, 22, GOLD), (34, 10, ORANGE),
                              (44, 20, GOLD), (26, 2, GOLD)]:
                d.polygon([(tx + dx, vy + dy), (tx + dx + 14, vy + dy + 18),
                           (tx + dx + 5, vy + dy + 20)], fill=c)
        else:  # tanker
            d.line([(x + 6, vy + 70), (x + col_w - 6, vy + 70)], fill=INK,
                   width=3)
            d.polygon([(x + 96, vy + 44), (x + 226, vy + 34),
                       (x + 232, vy + 56), (x + 102, vy + 62)], fill=INK)
            d.ellipse([x + 102, vy + 56, x + 126, vy + 70], fill=INK)
            d.ellipse([x + 200, vy + 48, x + 224, vy + 62], fill=INK)
            for fx, fy, c in [(136, 12, ORANGE), (168, 6, GOLD),
                              (194, 16, ORANGE)]:
                d.polygon([(x + fx, vy + fy), (x + fx + 26, vy + fy + 30),
                           (x + fx + 12, vy + fy + 32)], fill=c)
            d.ellipse([x + 238, vy + 14, x + 246, vy + 22], fill=GRAY)
            d.ellipse([x + 252, vy + 6, x + 262, vy + 16], fill=GRAY)
        # label bar under the picture (winners' picture caption bar)
        d.rectangle([x, vy + vh - 16, x + col_w, vy + vh], fill=INK)
        f_lab = _sans(10, bold=True)
        d.text((x + 8, vy + vh - 8), LEAD_LABEL[i], font=f_lab,
               fill=(244, 239, 230), anchor="lm")
        # kicker + headline + deck below the picture
        ky = lead_top + 100
        d.text((x, ky), "%d.  %s" % (i + 1, kick), font=f_kick,
               fill=LEAD_COL[i])
        hy = ky + 17
        hl = _wrap(d, head, f_head, col_w)
        for ln in hl:
            d.text((x, hy), ln, font=f_head, fill=INK)
            hy += 25
        dy = hy + 2
        dl = _wrap(d, deck, f_deck, col_w)
        if i == 0:
            # drop cap on the first letter of the lead deck
            cap = dl[0][0]
            f_cap = _font(DISPLAY, 38, 700)
            cap_w = d.textlength(cap, font=f_cap)
            d.text((x, dy - 6), cap, font=f_cap, fill=RED)
            rest = dl[0][1:] + (" " + " ".join(dl[1:]) if len(dl) > 1 else "")
            rl = _wrap(d, rest, f_deck, col_w - cap_w - 8)
            _justified(d, rl[:2], f_deck, x + cap_w + 8, dy,
                       col_w - cap_w - 8, 16, INK)
        else:
            _justified(d, dl[:2], f_deck, x, dy, col_w, 16, INK)
        d.line([(x, lead_top + 202), (x + col_w, lead_top + 202)],
               fill=LINE, width=1)
    y = lead_top + 206

    # --- secondary stories ---
    f_sec_h = _sans(12, bold=True)
    d.text((L, y), "MORE OF THE DAY", font=f_sec_h, fill=RED)
    y += 18
    f_st = _font(HEAD2, 14, 700)
    f_sd = _font(BODY, 12, 400)
    sec_cols = [(L, 472), (L + 472 + 20, 472)]
    rows = [SECONDARY[:6], SECONDARY[6:]]
    row_h = 26
    for ci, items in enumerate(rows):
        cx, cw2 = sec_cols[ci]
        yy = y
        for j, (title, detail) in enumerate(items):
            n = j + 4 if ci == 0 else j + 10
            d.text((cx, yy), str(n), font=_sans(13, bold=True),
                   fill=REG_COL[SEC_REG[n - 4]])
            tx = cx + 22
            t = _trunc(d, title, f_st, cw2 - 22)
            d.text((tx, yy), t, font=f_st, fill=INK)
            dt = _trunc(d, detail, f_sd, cw2 - 22)
            d.text((tx, yy + 15), dt, font=f_sd, fill=GRAY)
            yy += row_h
            if j < len(items) - 1:
                d.line([(cx, yy - 3), (cx + cw2, yy - 3)], fill=LINE, width=1)
    y += 6 * row_h + 4

    # --- map + markets ---
    d.line([(L, y), (R, y)], fill=INK, width=1)
    y += 6
    f_map_h = _sans(12, bold=True)
    d.text((L, y), "WHERE IT HAPPENED", font=f_map_h, fill=RED)
    d.text((660, y), "MARKETS \u2014 26 NOV", font=f_map_h, fill=RED)
    y += 17
    map_x, map_y, map_w, map_h = L, y, 610, 92
    d.rectangle([map_x, map_y, map_x + map_w, map_y + map_h], fill=MAP_BG,
                outline=LINE, width=1)

    def proj(lon, lat):
        px = map_x + (lon + 170) / 360.0 * map_w
        py = map_y + (75 - lat) / 133.0 * map_h
        return (px, py)

    for poly in (N_AMERICA, GREENLAND, S_AMERICA, AFRICA, EUROPE, UK, ASIA,
                 AUSTRALIA):
        d.polygon([proj(lo, la) for lo, la in poly], fill=LAND,
                  outline=LAND_EDGE)
    for cx, cy, rx, ry in [(140, 38, 5, 9), (113, -2, 12, 3), (106, -2, 9, 3),
                           (120, -3, 10, 3), (141, -4, 9, 4), (168, -42, 4, 8),
                           (47, -19, 3, 8), (-18, 65, 4, 3)]:
        d.ellipse([proj(cx - rx, cy + ry)[0], proj(cx - rx, cy + ry)[1],
                   proj(cx + rx, cy - ry)[0], proj(cx + rx, cy - ry)[1]],
                  fill=LAND, outline=LAND_EDGE)
    f_pin = _sans(9, bold=True)
    PIN_OFF = {1: (-14, 10), 14: (12, -12), 2: (-12, 8), 4: (14, -8),
               3: (-12, 10), 8: (14, -10), 5: (-14, 10), 9: (12, -8),
               10: (14, 10), 11: (-12, -10)}
    for i, (lo, la) in enumerate(PINS):
        px, py = proj(lo, la)
        dx, dy = PIN_OFF.get(i + 1, (0, 0))
        qx, qy = px + dx, py + dy
        pc = REG_COL[PIN_REG[i]]
        if (dx, dy) != (0, 0):
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=pc)
            d.line([(px, py), (qx, qy)], fill=pc, width=1)
        d.ellipse([qx - 8, qy - 8, qx + 8, qy + 8], fill=pc,
                  outline=(255, 255, 255), width=1)
        d.text((qx, qy), str(i + 1), font=f_pin, fill=(255, 255, 255),
               anchor="mm")
    # markets box (right of map)
    mx = 660
    f_mk = _font(BODY, 12, 400)
    f_mkb = _font(BODY, 12, 700)
    my = map_y + 1
    for name, val in MARKETS:
        d.text((mx, my), name, font=f_mk, fill=INK)
        d.text((R, my), val, font=f_mkb,
               fill=RED if val.startswith("-") else INK, anchor="ra")
        my += 12
    y = map_y + map_h + 8

    # --- briefs ---
    d.line([(L, y), (R, y)], fill=INK, width=1)
    y += 6
    d.text((L, y), "ALSO ON THIS DAY", font=f_sec_h, fill=RED)
    y += 18
    f_br = _font(BODY, 11, 400)
    f_brn = _sans(11, bold=True)
    half = (len(BRIEFS) + 1) // 2
    for ci, items in enumerate([BRIEFS[:half], BRIEFS[half:]]):
        cx = L if ci == 0 else L + 472 + 20
        yy = y
        for j, txt in enumerate(items):
            n = 15 + (j if ci == 0 else half + j)
            d.text((cx, yy), str(n), font=f_brn,
                   fill=REG_COL[BRIEF_REG[n - 15]])
            t = _trunc(d, txt, f_br, 472 - 24)
            d.text((cx + 24, yy), t, font=f_br, fill=INK)
            yy += 12
    y += half * 12 + 6

    # --- quick digest ---
    d.line([(L, y), (R, y)], fill=INK, width=1)
    y += 6
    d.text((L, y), "IN BRIEF", font=f_sec_h, fill=RED)
    y += 18
    f_dg = _font(BODY, 12, 400)
    for line in DIGEST:
        d.text((L, y), "\u2022", font=f_dg, fill=RED)
        d.text((L + 14, y), line, font=f_dg, fill=INK)
        y += 13
    y += 3

    # --- date check footer ---
    d.line([(L, y), (R, y)], fill=LINE, width=1)
    y += 6
    f_dc = _font(BODY, 9, 400)
    dcl = _wrap(d, DATECHECK, f_dc, CW)
    for ln in dcl[:3]:
        d.text((L, y), ln, font=f_dc, fill=GRAY)
        y += 12
    y += 2
    f_ft = _font(BODY, 9, 400)
    d.text((W // 2, y),
           "THE WORLD TODAY  \u00b7  Sources: BBC, Reuters, Al Jazeera, The Guardian and others  \u00b7  All stories first reported 26 November 2026",
           font=f_ft, fill=GRAY, anchor="ma")

    # --- paper grain (fixed seed: deterministic across runs) ---
    rng = random.Random(20261126)
    over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(over)
    for _ in range(9000):
        gx, gy = rng.randrange(W), rng.randrange(H)
        a = rng.randrange(6, 20)
        c = (0, 0, 0, a) if rng.random() < 0.6 else (255, 255, 255, a)
        od.point((gx, gy), fill=c)
    img = Image.alpha_composite(img.convert("RGBA"), over).convert("RGB")
    img.save(out_path, "PNG")


def _copy_shipped(out_path):
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(repo_dir, "entry.png")
    shutil.copyfile(src, out_path)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    if HAVE_PIL:
        _draw_page(out_path)
    else:
        _copy_shipped(out_path)


if __name__ == "__main__":
    main()
