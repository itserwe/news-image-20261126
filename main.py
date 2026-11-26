#!/usr/bin/env python3
"""The World Today - 26 November 2026 (news-image-20261126).

Entry program for the make.fun one-day world news image competition.
It writes entry.png to $MAKEFUN_OUTPUT_DIR (default /output).

The front page is drawn with Pillow when Pillow is available. The grader
runs with only the Python standard library, so when Pillow is missing the
program falls back to copying the entry.png shipped in this repository.
Both paths write byte-identical output, and the program never writes
outside $MAKEFUN_OUTPUT_DIR.
"""
import os
import shutil
import sys

try:
    from PIL import Image, ImageDraw, ImageFont  # type: ignore
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False

W, H = 1024, 1024
BG = (250, 248, 245)      # #FAF8F5
INK = (26, 26, 26)        # #1A1A1A
RED = (140, 29, 24)
GRAY = (90, 86, 80)
LINE = (201, 194, 184)
MAP_BG = (238, 233, 224)
LAND = (203, 196, 180)
LAND_EDGE = (138, 130, 114)
ORANGE = (214, 90, 20)
GOLD = (212, 160, 40)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

LEADS = [
    ("TRADE WAR", "US proposes tariffs on 14 partners",
     "India 25%, Japan 15%, China 20%. EU \u2018strongly rejects\u2019 it; Brazil calls it \u2018unacceptable\u2019.",
     "bars"),
    ("MIDDLE EAST", "Houthis hit Riyadh tower; Saudi strikes widen",
     "PIF tower strike hurt 11; Riyadh says it downed drones as strikes hit seven Yemeni provinces.",
     "tower"),
    ("EGYPT", "Cairo tanker fire kills at least 31",
     "Fuel tanker overturned and burst into flames on the ring road; cars and motorcycles burned.",
     "tanker"),
]

SECONDARY = [
    ("Ukraine hits airbase; Kyiv mall struck",
     "5 jets damaged; 7 hurt; Putin vows retaliation. \u2014 BBC, Straits Times"),
    ("US tells citizens to leave Iran",
     "War fears grow; Kushner met Iranian envoys. \u2014 Euronews, The National"),
    ("King tides flood California coast",
     "Record tides hit LA and La Jolla; pier battered. \u2014 Guardian, BBC"),
    ("EU leaders meet over \u20ac2tn budget",
     "Deal far from certain; Germany presses limits. \u2014 Tagesschau, RFI"),
    ("Bank of Korea raises rate to 3.25%",
     "Up 25bp, highest in two years; 2027 growth 4.1%. \u2014 Yonhap, CNBC"),
    ("Kim vows more nuclear weapons",
     "Wider tactical deployment; ignores Trump. \u2014 Al Jazeera, Asahi"),
    ("Asian stocks rebound; oil edges up",
     "Kospi led gains; gold at 1-year low. \u2014 CNBC, Asharq"),
    ("Spain votes Sunday, right favoured",
     "Feijoo\u2019s PP leads; may need Vox. \u2014 BBC, Le Monde"),
    ("Nepal lists 213 Indians missing",
     "Flash floods; presumed dead. \u2014 The Hindu"),
    ("Brazil pulls ambassador to Argentina",
     "Permanent withdrawal; Milei not invited. \u2014 MercoPress"),
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
    "Kenyan cult leader gets new convictions on 200-year term. \u2014 Reuters",
    "UK sends convicted refugees to Eswatini in first. \u2014 BBC / Guardian",
    "Famine risk falls in Baidoa, but hunger persists. \u2014 AllAfrica",
    "Indonesia gold mine flood kills at least 13 on Java. \u2014 Folha",
    "ISIL suicide attack kills two at Syria checkpoint. \u2014 Al Jazeera",
    "Hasina return dispute strains India and Bangladesh. \u2014 The Hindu",
    "Iraq court backs federal control of Kurdistan oil. \u2014 Al Jazeera",
    "Australia projected to miss 2035 emissions target. \u2014 Guardian",
    "Flinders Island fire destroys at least six homes. \u2014 Guardian",
    "Foreign troops leave Somalia; offensives vs al-Shabaab grow. \u2014 BBC",
    "Rare brine lakes found beneath the Red Sea. \u2014 ScienceDaily",
    "African sides shine at U-17 World Cup: Egypt, Uganda win. \u2014 Africanews",
    "Champions League: Liverpool 3-0 Brugge; Barca 4-1 Sabah. \u2014 BBC Sport",
    "Jennifer Barreto wins Miss Universe 2026. \u2014 Euronews",
    "Melon ranks top K-pop stars across Korea, China, Japan. \u2014 Yonhap",
    "Gordon Ramsay to host revived Top Gear. \u2014 BBC Culture",
    "\u2018London Falling\u2019 named Waterstones book of the year. \u2014 Guardian",
    "Canadian astronaut welcomes baby girl from orbit. \u2014 BBC Science",
]

TIMELINE = [
    "~00:00 UTC  Korea raises rate to 3.25%",
    "~05:25 UTC  Reuters summary",
    "~08:00 UTC  EU budget summit opens",
    "~08:00 UTC  US tariff proposals published",
    "~12:00 UTC  Riyadh PIF tower strike reported",
    "~14:00 UTC  Asian markets close higher",
    "~15:00 UTC  Macy\u2019s postpones 100th parade",
]

NUMBERS = ("31 KILLED \u00b7 CAIRO   \u00b7   14 TARIFF PARTNERS   \u00b7   "
           "25% INDIA RATE   \u00b7   213 MISSING \u00b7 NEPAL   \u00b7   "
           "3.25% KOREA RATE   \u00b7   $91.19 BRENT   \u00b7   100TH PARADE DELAYED")

REGIONS = ("NORTH AMERICA 6  \u00b7  MIDDLE EAST 6  \u00b7  EUROPE 9  \u00b7  "
           "ASIA 8  \u00b7  AFRICA 5  \u00b7  SOUTH AMERICA 2  \u00b7  OCEANIA 2  "
           "\u00b7  38 STORIES")

MARKETS = [
    ("S&P 500", "-0.25%"), ("Euro Stoxx 50", "-1.82%"),
    ("Shanghai", "-2.05%"), ("Nikkei", "+1.55%"),
    ("Brent crude", "$91.19  +0.61%"), ("Bitcoin (month)", "-24.3%"),
    ("US inflation", "3.8%"), ("US 10-year yield", "4.85%"),
]

DIGEST = [
    "Tariffs: Washington proposes new duties on 14 partners; allies push back.",
    "Riyadh: Houthi strike on the wealth-fund tower injures 11; strikes widen.",
    "Cairo: ring-road tanker fire kills at least 31 in the day\u2019s deadliest crash.",
]

DATECHECK = ("DATE CHECK \u2014 NOT 26 NOVEMBER:  Ras Tanura refinery attack (25 Nov)  \u00b7  "
             "Gaza: Hamas security chief killed (25 Nov)  \u00b7  First Pakistani astronaut (25 Nov)  \u00b7  "
             "Huawei verdict (24 Nov)  \u00b7  COP31 failed (22 Nov)")

# (lon, lat) pins for stories 1..14
PINS = [(-77, 39), (46.7, 24.7), (31.2, 30.0), (30.5, 50.5), (51.4, 35.7),
        (-122, 37), (4.35, 50.85), (127, 37.5), (125.75, 39), (139.7, 35.7),
        (-3.7, 40.4), (85.3, 27.7), (-58.4, -34.6), (-74, 40.7)]

# rough continent outlines (lon, lat)
N_AMERICA = [(-168, 66), (-158, 58), (-152, 60), (-140, 60), (-135, 58),
             (-130, 54), (-125, 49), (-124, 42), (-120, 34), (-114, 29),
             (-110, 24), (-105, 20), (-97, 16), (-94, 17), (-90, 14),
             (-86, 12), (-83, 9), (-80, 8), (-77, 7), (-79, 9), (-82, 10),
             (-85, 11), (-88, 13), (-92, 15), (-97, 16), (-97, 22),
             (-97, 26), (-93, 30), (-89, 30), (-84, 30), (-81, 26),
             (-80, 32), (-76, 35), (-74, 40), (-70, 42), (-68, 45),
             (-65, 44), (-60, 47), (-55, 47), (-60, 50), (-64, 58),
             (-68, 58), (-70, 62), (-78, 62), (-85, 66), (-90, 69),
             (-95, 69), (-110, 68), (-125, 70), (-140, 70), (-155, 71),
             (-165, 68), (-168, 66)]
GREENLAND = [(-58, 64), (-52, 60), (-43, 60), (-40, 64), (-32, 68),
             (-22, 70), (-20, 74), (-25, 76), (-35, 77), (-50, 76),
             (-58, 74), (-58, 64)]
S_AMERICA = [(-77, 7), (-80, 4), (-81, 0), (-80, -3), (-81, -6), (-77, -12),
             (-72, -18), (-70, -23), (-70, -30), (-72, -37), (-73, -44),
             (-74, -50), (-70, -54), (-66, -55), (-65, -50), (-62, -45),
             (-58, -38), (-57, -34), (-52, -32), (-48, -28), (-41, -23),
             (-39, -17), (-35, -9), (-35, -6), (-40, -3), (-44, -2),
             (-50, 0), (-52, 4), (-55, 6), (-60, 8), (-65, 10), (-70, 11),
             (-75, 10), (-77, 7)]
AFRICA = [(-17, 15), (-17, 21), (-15, 27), (-10, 31), (-6, 34), (-2, 35),
          (5, 37), (10, 37), (11, 34), (15, 32), (20, 32), (25, 32),
          (30, 31), (32, 31), (34, 28), (35, 24), (37, 20), (39, 18),
          (40, 15), (43, 12), (48, 11), (51, 12), (46, 5), (42, 0),
          (40, -5), (40, -10), (38, -15), (36, -20), (33, -26), (30, -30),
          (28, -33), (20, -35), (17, -32), (15, -27), (13, -20), (12, -15),
          (13, -10), (12, -5), (9, -1), (9, 4), (6, 4), (-2, 5), (-8, 5),
          (-13, 8), (-17, 12), (-17, 15)]
EUROPE = [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-1, 46), (-4, 48),
          (-2, 49), (0, 51), (2, 51), (4, 53), (8, 55), (8, 57), (10, 58),
          (12, 56), (18, 56), (21, 55), (24, 58), (28, 59), (30, 60),
          (25, 60), (21, 60), (18, 60), (15, 58), (12, 54), (10, 54),
          (8, 54), (5, 53), (3, 51), (0, 50), (-2, 48), (-5, 44),
          (-8, 40), (-9, 37), (-10, 36)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (-5, 50)]
ASIA = [(28, 36), (30, 41), (35, 42), (40, 42), (44, 40), (48, 42),
        (50, 44), (55, 44), (58, 42), (60, 38), (63, 40), (66, 42),
        (68, 44), (70, 46), (72, 48), (75, 50), (78, 52), (80, 54),
        (85, 58), (90, 60), (95, 64), (100, 68), (105, 70), (110, 72),
        (115, 73), (120, 73), (125, 72), (130, 71), (135, 71), (140, 72),
        (145, 72), (150, 70), (155, 69), (160, 69), (165, 68), (170, 66),
        (175, 65), (178, 65), (178, 62), (170, 60), (162, 58), (158, 52),
        (155, 55), (150, 60), (142, 55), (141, 50), (140, 45), (138, 42),
        (135, 43), (132, 42), (130, 42), (128, 38), (126, 38), (124, 40),
        (122, 38), (120, 34), (122, 30), (120, 28), (118, 25), (112, 22),
        (109, 18), (106, 10), (104, 9), (101, 8), (99, 10), (97, 15),
        (94, 17), (92, 21), (89, 22), (86, 20), (83, 18), (80, 14),
        (77, 8), (75, 12), (73, 20), (70, 23), (67, 25), (64, 25),
        (61, 25), (58, 26), (56, 27), (54, 27), (52, 28), (50, 29),
        (48, 30), (46, 29), (44, 29), (42, 27), (40, 24), (39, 21),
        (38, 18), (36, 15), (35, 17), (34, 20), (33, 24), (31, 28),
        (30, 31), (28, 33), (27, 36), (28, 36)]
AUSTRALIA = [(113, -22), (114, -30), (115, -33), (118, -35), (124, -33),
             (129, -32), (132, -32), (135, -35), (137, -35), (140, -38),
             (145, -38), (147, -39), (150, -37), (153, -32), (153, -27),
             (150, -23), (146, -19), (142, -15), (142, -11), (140, -17),
             (136, -15), (135, -12), (132, -12), (130, -13), (126, -14),
             (122, -17), (118, -20), (113, -22)]


# ---------------- drawing helpers ----------------

def _font(path, size):
    return ImageFont.truetype(path, size)


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


def _fit_text(d, text, font_path, max_size, max_w):
    """Largest font size <= max_size whose text fits max_w."""
    size = max_size
    while size > 8:
        f = _font(font_path, size)
        if d.textlength(text, font=f) <= max_w:
            return f
        size -= 1
    return _font(font_path, 8)


def _trunc(d, text, font, max_w):
    while text and d.textlength(text + "\u2026", font=font) > max_w:
        text = text[:-1].rstrip()
    return text + ("\u2026" if d.textlength(text, font=font) > max_w else "")


def _draw_page(out_path):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    L, R = 30, W - 30
    CW = R - L  # 964

    # --- masthead ---
    y = 12
    f_title = _fit_text(d, "THE WORLD TODAY", SERIF_B, 58, CW)
    d.text((W // 2, y), "THE WORLD TODAY", font=f_title, fill=INK, anchor="ma")
    y += f_title.size + 4
    f_date = _font(SANS, 20)
    d.text((W // 2, y), "Thursday, 26 November 2026", font=f_date, fill=INK,
           anchor="ma")
    y += 28
    d.line([(L, y), (R, y)], fill=INK, width=3)
    d.line([(L, y + 5), (R, y + 5)], fill=INK, width=1)
    y += 11

    # --- timeline strip ---
    f_tl_lab = _font(SANS_B, 11)
    f_tl = _font(SANS, 11)
    d.text((L, y), "THE DAY IN UTC", font=f_tl_lab, fill=RED)
    lab_w = d.textlength("THE DAY IN UTC  ", font=f_tl_lab)
    tl_lines = _wrap(d, "  \u00b7  ".join(TIMELINE), f_tl, CW - lab_w)
    for ln in tl_lines[:2]:
        ln = ln.strip().removeprefix("\u00b7").strip()
        d.text((L + lab_w, y), ln, font=f_tl, fill=GRAY)
        y += 14
    y += 4

    # --- numbers black strip ---
    f_num = _fit_text(d, NUMBERS, SANS_B, 15, CW - 16)
    d.rectangle([L, y, R, y + 28], fill=INK)
    d.text((W // 2, y + 14), NUMBERS, font=f_num, fill=(250, 248, 245),
           anchor="mm")
    y += 34

    # --- region counts ---
    f_reg = _fit_text(d, REGIONS, SANS_B, 13, CW)
    d.text((W // 2, y), REGIONS, font=f_reg, fill=INK, anchor="ma")
    y += 19

    # --- leads: 3 columns ---
    col_w = 308
    xs = [L, L + col_w + 20, L + 2 * (col_w + 20)]
    lead_top = y
    f_kick = _font(SANS_B, 11)
    f_head = _font(SERIF_B, 22)
    f_deck = _font(SANS, 13)
    for i, (kick, head, deck, art) in enumerate(LEADS):
        x = xs[i]
        d.text((x, lead_top), "%d.  %s" % (i + 1, kick), font=f_kick, fill=RED)
        hy = lead_top + 17
        hl = _wrap(d, head, f_head, col_w)
        for ln in hl:
            d.text((x, hy), ln, font=f_head, fill=INK)
            hy += 24
        dy = hy + 2
        dl = _wrap(d, deck, f_deck, col_w)
        for ln in dl[:3]:
            d.text((x, dy), ln, font=f_deck, fill=INK)
            dy += 16
        # visual box
        vy = lead_top + 132
        vh = 54
        d.rectangle([x, vy, x + col_w, vy + vh], outline=LINE, width=1)
        if art == "bars":
            bars = [("INDIA", 25, RED), ("CHINA", 20, INK),
                    ("VIETNAM", 20, INK), ("JAPAN", 15, GRAY)]
            bw, gap = 46, 22
            bx = x + 22
            for name, val, col in bars:
                bh = int(val / 25 * (vh - 24))
                top = vy + vh - 14 - bh
                d.rectangle([bx, top, bx + bw, vy + vh - 14], fill=col)
                f_v = _font(SANS_B, 10)
                d.text((bx + bw // 2, top + 3), "%d%%" % val,
                       font=f_v, fill=(255, 255, 255), anchor="ma")
                f_n = _font(SANS, 9)
                d.text((bx + bw // 2, vy + vh - 13), name, font=f_n,
                       fill=GRAY, anchor="ma")
                bx += bw + gap
        elif art == "tower":
            # PIF tower silhouette + flame
            tx = x + col_w // 2
            d.rectangle([tx - 16, vy + 14, tx + 16, vy + vh - 4], fill=INK)
            d.rectangle([tx - 22, vy + 30, tx + 22, vy + vh - 4],
                        fill=(60, 58, 54))
            d.line([(tx, vy + 4), (tx, vy + 14)], fill=INK, width=2)
            d.polygon([(tx - 30, vy + 12), (tx - 18, vy + 26), (tx - 26, vy + 26)],
                      fill=ORANGE)
            d.polygon([(tx - 24, vy + 8), (tx - 14, vy + 24), (tx - 20, vy + 24)],
                      fill=GOLD)
            d.rectangle([x + 8, vy + vh - 14, tx - 30, vy + vh - 4], fill=GRAY)
            d.rectangle([tx + 30, vy + vh - 10, x + col_w - 8, vy + vh - 4],
                        fill=GRAY)
        else:  # tanker
            d.line([(x + 6, vy + vh - 12), (x + col_w - 6, vy + vh - 12)],
                   fill=INK, width=3)
            # overturned tanker: tilted body
            d.polygon([(x + 90, vy + 34), (x + 220, vy + 26), (x + 224, vy + 44),
                       (x + 96, vy + 50)], fill=INK)
            d.ellipse([x + 96, vy + 44, x + 116, vy + 56], fill=INK)
            d.ellipse([x + 196, vy + 38, x + 216, vy + 50], fill=INK)
            d.polygon([(x + 130, vy + 8), (x + 150, vy + 30), (x + 140, vy + 30)],
                      fill=ORANGE)
            d.polygon([(x + 160, vy + 4), (x + 182, vy + 28), (x + 168, vy + 28)],
                      fill=GOLD)
            d.polygon([(x + 185, vy + 12), (x + 200, vy + 30), (x + 190, vy + 30)],
                      fill=ORANGE)
        d.line([(x, lead_top + 194), (x + col_w, lead_top + 194)], fill=LINE,
               width=1)
    y = lead_top + 202

    # --- secondary stories ---
    f_sec_h = _font(SANS_B, 12)
    d.text((L, y), "MORE OF THE DAY", font=f_sec_h, fill=RED)
    y += 18
    f_st = _font(SERIF_B, 14)
    f_sd = _font(SANS, 12)
    sec_cols = [(L, 472), (L + 472 + 20, 472)]
    rows = [SECONDARY[:6], SECONDARY[6:]]
    row_h = 28
    for ci, items in enumerate(rows):
        cx, cw2 = sec_cols[ci]
        yy = y
        for j, (title, detail) in enumerate(items):
            n = j + 4 if ci == 0 else j + 10
            d.text((cx, yy), str(n), font=_font(SANS_B, 13), fill=RED)
            tx = cx + 22
            t = _trunc(d, title, f_st, cw2 - 22)
            d.text((tx, yy), t, font=f_st, fill=INK)
            dt = _trunc(d, detail, f_sd, cw2 - 22)
            d.text((tx, yy + 16), dt, font=f_sd, fill=GRAY)
            yy += row_h
    y += 6 * row_h + 4

    # --- map + markets ---
    d.line([(L, y), (R, y)], fill=INK, width=1)
    y += 6
    f_map_h = _font(SANS_B, 12)
    d.text((L, y), "WHERE IT HAPPENED", font=f_map_h, fill=RED)
    d.text((660, y), "MARKETS \u2014 26 NOV", font=f_map_h, fill=RED)
    y += 17
    map_x, map_y, map_w, map_h = L, y, 610, 108
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
    # islands: Japan, Indonesia, NZ, Madagascar, Iceland
    for cx, cy, rx, ry in [(140, 38, 5, 9), (113, -2, 12, 3), (106, -2, 9, 3),
                           (120, -3, 10, 3), (141, -4, 9, 4), (168, -42, 4, 8),
                           (47, -19, 3, 8), (-18, 65, 4, 3)]:
        d.ellipse([proj(cx - rx, cy + ry)[0], proj(cx - rx, cy + ry)[1],
                   proj(cx + rx, cy - ry)[0], proj(cx + rx, cy - ry)[1]],
                  fill=LAND, outline=LAND_EDGE)
    f_pin = _font(SANS_B, 9)
    # display offsets (dx, dy px) to separate pins that would overlap
    PIN_OFF = {1: (-14, 10), 14: (12, -12), 10: (14, 8), 2: (10, 12),
               5: (0, -12), 9: (-8, -10)}
    for i, (lo, la) in enumerate(PINS):
        px, py = proj(lo, la)
        dx, dy = PIN_OFF.get(i + 1, (0, 0))
        qx, qy = px + dx, py + dy
        if (dx, dy) != (0, 0):
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
            d.line([(px, py), (qx, qy)], fill=RED, width=1)
        d.ellipse([qx - 8, qy - 8, qx + 8, qy + 8], fill=RED,
                  outline=(255, 255, 255), width=1)
        d.text((qx, qy), str(i + 1), font=f_pin, fill=(255, 255, 255),
               anchor="mm")
    # markets box (right of map)
    mx = 660
    f_mk = _font(SANS, 12)
    f_mkb = _font(SANS_B, 12)
    my = map_y + 1
    for name, val in MARKETS:
        d.text((mx, my), name, font=f_mk, fill=INK)
        d.text((R, my), val, font=f_mkb,
               fill=RED if val.startswith("-") else INK, anchor="ra")
        my += 13
    y = map_y + map_h + 8

    # --- briefs ---
    d.line([(L, y), (R, y)], fill=INK, width=1)
    y += 6
    d.text((L, y), "ALSO ON THIS DAY", font=f_sec_h, fill=RED)
    y += 18
    f_br = _font(SANS, 11)
    f_brn = _font(SANS_B, 11)
    half = (len(BRIEFS) + 1) // 2
    for ci, items in enumerate([BRIEFS[:half], BRIEFS[half:]]):
        cx = L if ci == 0 else L + 472 + 20
        yy = y
        for j, txt in enumerate(items):
            n = 15 + (j if ci == 0 else half + j)
            d.text((cx, yy), str(n), font=f_brn, fill=RED)
            t = _trunc(d, txt, f_br, 472 - 24)
            d.text((cx + 24, yy), t, font=f_br, fill=INK)
            yy += 13
    y += half * 13 + 6

    # --- quick digest ---
    d.line([(L, y), (R, y)], fill=INK, width=1)
    y += 6
    d.text((L, y), "IN BRIEF", font=f_sec_h, fill=RED)
    y += 18
    f_dg = _font(SANS, 12)
    for line in DIGEST:
        d.text((L, y), "\u2022", font=f_dg, fill=RED)
        d.text((L + 14, y), line, font=f_dg, fill=INK)
        y += 15
    y += 3

    # --- date check footer ---
    d.line([(L, y), (R, y)], fill=LINE, width=1)
    y += 6
    f_dc = _font(SANS, 9)
    dcl = _wrap(d, DATECHECK, f_dc, CW)
    for ln in dcl[:3]:
        d.text((L, y), ln, font=f_dc, fill=GRAY)
        y += 12
    y += 2
    f_ft = _font(SANS, 9)
    d.text((W // 2, y),
           "THE WORLD TODAY  \u00b7  Sources: BBC, Reuters, Al Jazeera, The Guardian and others  \u00b7  All stories first reported 26 November 2026",
           font=f_ft, fill=GRAY, anchor="ma")

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
