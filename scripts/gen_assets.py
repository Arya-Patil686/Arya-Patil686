import os, random, math
from pixfont import text_runs, text_width, FW, FH
from pixicons import ICONS

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
os.makedirs(OUT, exist_ok=True)
PX = 3  # svg units per pixel cell

BG      = "#05050a"
DEEP    = "#0b0b18"
GREEN   = "#7cf67c"
GREEN_D = "#2a8a3f"
PINK    = "#ff3fa4"
PINK_D  = "#9c1a5e"
CYAN    = "#5ce1e6"
YELLOW  = "#ffd93d"
ORANGE  = "#ff9843"
WHITE   = "#ffffff"
LILAC   = "#c9a7ff"
WIN_BG  = "#ffd0e8"
WIN_MID = "#ffa8d3"
WIN_TXT = "#4a0f30"
BRICK   = "#7a3ea8"
BRICK_D = "#4a2168"
GRASS   = "#4ad07a"

def px(v): return round(v * PX, 2)

class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h          # grid cells
        self.parts = []
    def raw(self, s): self.parts.append(s)
    def rect(self, x, y, w, h, fill, extra=""):
        self.parts.append(f'<rect x="{px(x)}" y="{px(y)}" width="{px(w)}" height="{px(h)}" fill="{fill}"{extra}/>')
    def rects(self, boxes, fill, extra=""):
        d = "".join(f'M{px(x)} {px(y)}h{px(w)}v{px(h)}h-{px(w)}z' for x,y,w,h in boxes)
        self.parts.append(f'<path d="{d}" fill="{fill}"{extra}/>')
    def text(self, x, y, s, fill, scale=1, tracking=1, extra=""):
        self.rects(list(text_runs(x, y, s, scale, tracking)), fill, extra)
    def ctext(self, cx, y, s, fill, scale=1, tracking=1, extra=""):
        w = text_width(s, scale, tracking)
        self.text(round(cx - w/2), y, s, fill, scale, tracking, extra)
    def shadow_text(self, x, y, s, fill, shadow, scale=1, off=1, tracking=1):
        self.text(x + off, y + off, s, shadow, scale, tracking)
        self.text(x, y, s, fill, scale, tracking)
    def cshadow_text(self, cx, y, s, fill, shadow, scale=1, off=1, tracking=1):
        w = text_width(s, scale, tracking)
        self.shadow_text(round(cx - w/2), y, s, fill, shadow, scale, off, tracking)
    def frame(self, x, y, w, h, color, t=1):
        """hollow rectangle of thickness t"""
        self.rects([(x,y,w,t),(x,y+h-t,w,t),(x,y+t,t,h-2*t),(x+w-t,y+t,t,h-2*t)], color)
    def svg(self, extra_defs=""):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{px(self.w)}" height="{px(self.h)}" '
                f'viewBox="0 0 {px(self.w)} {px(self.h)}" shape-rendering="crispEdges" '
                f'role="img">{extra_defs}' + "".join(self.parts) + '</svg>')
    def write(self, name, extra_defs=""):
        p = os.path.join(OUT, name)
        open(p, "w").write(self.svg(extra_defs))
        print(f"{name}  {os.path.getsize(p)/1024:.1f} KB  {px(self.w)}x{px(self.h)}")

# ---------- sprite helper ----------
def sprite(c, x, y, rows, palette, s=1):
    for ry, row in enumerate(rows):
        rx = 0
        while rx < len(row):
            ch = row[rx]
            if ch != '.':
                run = 1
                while rx+run < len(row) and row[rx+run] == ch: run += 1
                c.rect(x+rx*s, y+ry*s, run*s, s, palette[ch])
                rx += run
            else: rx += 1

CLOUD = [
    "...####...",
    "..######..",
    ".########.",
    "##########",
    "##########",
    ".WWWWWWWW.",
]
CLOUD_PAL = {"#": WHITE, "W": "#ffb3dd"}

COIN = [
    "..###..",
    ".#YYY#.",
    "#Y#Y#Y#",
    "#Y#Y#Y#",
    "#Y#Y#Y#",
    ".#YYY#.",
    "..###..",
]
COIN_PAL = {"#": "#c88a12", "Y": YELLOW}

CAT = [
    "#.....#",
    "##...##",
    "#######",
    "#O###O#",
    "#######",
    "#.###.#",
    ".#####.",
    "..#.#..",
]
CAT_PAL = {"#": WHITE, "O": "#222"}

HERO = [
    "....HHHHHHHH....",
    "...HHHHHHHHHH...",
    "..HHHHHHHHHHHH..",
    "..HHHPPHHHHHHH..",
    "..HHSSSSSSSSHH..",
    "..HHSSSSSSSSHH..",
    "..HHSEESSEESHH..",
    "..HHSEESSEESHH..",
    "..HHSSSSSSSSHH..",
    "..HHSSSMMSSSHH..",
    "..HHHSSSSSSHHH..",
    "..HHHHSSSSHHHH..",
    "...HHTTTTTTHH...",
    "..HHTTTTTTTTHH..",
    "..HHTTTTTTTTHH..",
    "..HHTTTTTTTTHH..",
    "...HTTTTTTTTH...",
    "....TTTTTTTT....",
    "....DDDDDDDD....",
    "....DDD..DDD....",
    "....DDD..DDD....",
    "....DDD..DDD....",
    "...WWWW..WWWW...",
    "...WWWW..WWWW...",
]
HERO_PAL = {"H": "#3b2314", "S": "#f0c09a", "E": "#141414", "M": "#c2566b",
            "T": "#7cf67c", "D": "#3a4a7a", "W": "#ffffff", "P": "#ff3fa4"}

CAT = [
    ".WW........WW.",
    ".WWW......WWW.",
    ".WWPW....WPWW.",
    ".WWWWWWWWWWWW.",
    "WWWWWWWWWWWWWW",
    "WWKKWWWWKKWWWW",
    "WWKKWWWWKKWWWW",
    "WWWWWPPWWWWWWW",
    "WWWWWWWWWWWWWW",
    ".WWWWWWWWWWWW.",
    ".WWWWWWWWWWWW.",
    ".WWWWWWWWWWW..",
    "..WWWWWWWWW.WW",
    "..WW....WW..WW",
]
CAT_PAL = {"W": "#ffffff", "K": "#141414", "P": "#ff8ac4"}

def starfield(c, n, seed, x0, y0, x1, y1, avoid=None):
    rnd = random.Random(seed)
    cols = [WHITE, WHITE, CYAN, YELLOW, LILAC]
    for i in range(n):
        for _ in range(30):
            x = rnd.randint(x0, x1); y = rnd.randint(y0, y1)
            if avoid and (avoid[0] <= x <= avoid[2] and avoid[1] <= y <= avoid[3]): continue
            break
        else: continue
        col = rnd.choice(cols)
        dur = rnd.choice([2.2, 3.1, 4.3, 5.0, 2.7])
        beg = round(rnd.uniform(0, 4), 1)
        big = rnd.random() < 0.18
        anim = (f'<animate attributeName="opacity" values="1;0.15;1" dur="{dur}s" '
                f'begin="{beg}s" repeatCount="indefinite"/>')
        if big:
            c.parts.append(f'<g opacity="0.9">{anim}</g>'.replace("</g>",""))
            c.parts.pop()
            boxes = [(x,y-1,1,3),(x-1,y,3,1)]
            d = "".join(f'M{px(a)} {px(b)}h{px(w)}v{px(h)}h-{px(w)}z' for a,b,w,h in boxes)
            c.raw(f'<path d="{d}" fill="{col}">{anim}</path>')
        else:
            c.raw(f'<rect x="{px(x)}" y="{px(y)}" width="{PX}" height="{PX}" fill="{col}">{anim}</rect>')

def ground(c, y, w, top=GRASS, body=BRICK, dark=BRICK_D, h=None):
    h = h or (c.h - y)
    c.rect(0, y, w, 2, top)
    c.rect(0, y+2, w, 1, "#2f9d55")
    c.rect(0, y+3, w, h-3, body)
    # brick seams
    for row in range(0, (h-3)//4 + 1):
        yy = y + 3 + row*4
        if yy >= y + h: break
        c.rect(0, yy, w, 1, dark)
        off = 0 if row % 2 == 0 else 4
        for xx in range(off, w, 8):
            c.rect(xx, yy, 1, min(4, y+h-yy), dark)

# =====================================================================
# 1. BANNER  — title screen
# =====================================================================
def build_banner():
    W, H = 300, 122
    c = Canvas(W, H)
    c.rect(0, 0, W, H, BG)

    SX, SY, SW, SH = 20, 14, 260, 80
    starfield(c, 90, 7, 1, 1, W-2, 102, avoid=(SX-2, SY-2, SX+SW+2, SY+SH+2))

    # clouds in the margins
    sprite(c, 2, 24, CLOUD, CLOUD_PAL, s=1)
    sprite(c, 4, 68, CLOUD, CLOUD_PAL, s=1)
    sprite(c, 286, 40, CLOUD, CLOUD_PAL, s=1)
    sprite(c, 284, 78, CLOUD, CLOUD_PAL, s=1)

    # ---- HUD ----
    c.text(6, 3, "XP: TY // VIT PUNE", GREEN, 1)
    sprite(c, 176, 3, ["...", ".^.", "..."], {"^": PINK}, s=1)
    c.text(174, 3, "^", PINK, 1)
    c.frame(184, 3, 48, 7, WHITE, 1)
    c.raw(f'<rect x="{px(186)}" y="{px(5)}" height="{px(3)}" fill="{GREEN}">'
          f'<animate attributeName="width" values="{px(40)};{px(28)};{px(40)}" dur="6s" repeatCount="indefinite"/>'
          f'</rect>')
    c.text(240, 3, "PLAYER 01", WHITE, 1)

    # ---- CRT screen ----
    c.rect(SX, SY, SW, SH, "#03030a")
    c.raw(f'<g>{"".join(f"<rect x=0 y=0 width=0 height=0/>" for _ in [])}</g>')
    c.frame(SX-2, SY-2, SW+4, SH+4, GREEN_D, 1)
    c.raw('<g opacity="0.95"><animate attributeName="opacity" values="1;0.55;1" dur="3.6s" repeatCount="indefinite"/>')
    c.frame(SX, SY, SW, SH, GREEN, 1)
    c.raw('</g>')
    # corner ticks
    for (cx_, cy_) in [(SX+3, SY+3), (SX+SW-6, SY+3), (SX+3, SY+SH-6), (SX+SW-6, SY+SH-6)]:
        c.rects([(cx_, cy_, 3, 1), (cx_, cy_, 1, 3)], PINK)

    c.cshadow_text(W/2, 19, "SOFTWARE ENGINEER", CYAN, "#1d5f7a", 2, 1)
    c.cshadow_text(W/2, 37, "ARYA PATIL", PINK, GREEN, 4, 1)
    c.ctext(W/2, 70, "AI SYSTEMS ~ BACKEND ~ FULL-STACK", WHITE, 1)

    # press start
    lbl = "PRESS START TO VIEW WORK"
    bw = text_width(lbl, 1) + 12
    bx = round((W - bw) / 2)
    c.frame(bx, 80, bw, 11, GREEN_D, 1)
    c.raw('<g><animate attributeName="opacity" values="1;1;0.15;0.15" dur="1.5s" repeatCount="indefinite"/>')
    c.ctext(W/2, 82, lbl, GREEN, 1)
    c.raw("</g>")

    # scanlines over the screen
    lines = [(SX+1, y, SW-2, 1) for y in range(SY+1, SY+SH-1, 3)]
    c.rects(lines, "#ffffff", ' opacity="0.045"')

    # ---- characters / props ----
    c.raw('<g><animateTransform attributeName="transform" type="translate" '
          'values="0 0; 0 -5; 0 0" dur="2.4s" repeatCount="indefinite"/>')
    sprite(c, 3, 104 - len(HERO), HERO, HERO_PAL, s=1)
    c.raw('</g>')
    sprite(c, 283, 104 - len(CAT), CAT, CAT_PAL, s=1)

    for i, (cxp, cyp, d) in enumerate([(120, 96, 1.8), (152, 97, 2.4), (184, 96, 2.1)]):
        c.raw(f'<g><animateTransform attributeName="transform" type="translate" '
              f'values="0 0; 0 -9; 0 0" dur="{d}s" begin="{i*0.4}s" repeatCount="indefinite"/>')
        sprite(c, cxp, cyp, COIN, COIN_PAL, s=1)
        c.raw('</g>')

    ground(c, 104, W)
    c.write("banner.svg")

# =====================================================================
# 2. SCROLLING MARQUEE
# =====================================================================
def build_marquee(name, tokens, fg=PINK, accent=YELLOW, bg="#12021a", dur=22):
    W, H = 300, 22
    c = Canvas(W, H)
    c.rect(0, 0, W, H, bg)
    c.rect(0, 0, W, 1, PINK_D); c.rect(0, H - 1, W, 1, PINK_D)
    gap = 4
    uw = sum(text_width(t, 2) + text_width("~", 2) + gap * 2 for t in tokens)
    c.raw(f'<g><animateTransform attributeName="transform" type="translate" '
          f'values="0 0; -{px(uw)} 0" dur="{dur}s" repeatCount="indefinite"/>')
    reps = int(W / uw) + 2
    x = 0
    for _ in range(reps):
        for t in tokens:
            c.text(x, 4, t, fg, 2)
            x += text_width(t, 2) + gap
            c.text(x, 4, "~", accent, 2)
            x += text_width("~", 2) + gap
    c.raw("</g>")
    c.write(name)

# =====================================================================
# 3. SECTION HEADER BARS
# =====================================================================
def build_header(name, level, title, accent=GREEN):
    W, H = 300, 20
    c = Canvas(W, H)
    c.rect(0, 0, W, H, BG)
    c.frame(0, 0, W, H, "#242440", 1)
    # left accent block
    c.rect(0, 0, 3, H, accent)
    c.rects([(5, 6, 2, 8), (7, 7, 2, 6), (9, 8, 2, 4), (11, 9, 2, 2)], PINK)
    x = 14
    c.text(x, 4, level, PINK, 2)
    x += text_width(level, 2) + 8
    c.rect(x, 4, 1, 12, "#3a3a5c"); x += 6
    c.shadow_text(x, 4, title, accent, "#12121f", 2, 1)
    # right dotted rail + star, only where there is genuine room
    end = x + text_width(title, 2) + 8
    star_x = W - 12
    if end < star_x - 6:
        c.rects([(dx, 9, 2, 2) for dx in range(end, star_x - 4, 6)], "#2e2e4a")
        c.text(star_x, 6, "~", YELLOW)
    elif end > W - 4:
        raise ValueError(f"header {name!r}: title overflows the bar by {end - (W - 4)} cells")
    c.write(name)

# =====================================================================
# 4. PLAYER CARD  — retro windows
# =====================================================================
def window(c, x, y, w, h, title, lines, bar=WIN_MID, body=WIN_BG,
           txt=WIN_TXT, title_txt=WIN_TXT, accents=None):
    c.rect(x + 2, y + 2, w, h, "#00000055")           # drop shadow
    c.rect(x, y, w, h, "#2a0a1c")                      # outer border
    c.rect(x + 1, y + 1, w - 2, h - 2, body)
    c.rect(x + 1, y + 1, w - 2, 10, bar)
    c.rect(x + 1, y + 11, w - 2, 1, "#2a0a1c")
    c.text(x + 4, y + 3, title, title_txt, 1)
    # window buttons
    bx = x + w - 4
    for i in range(3):
        c.frame(bx - 6 - i * 8, y + 3, 6, 6, "#2a0a1c", 1)
        c.rect(bx - 5 - i * 8, y + 4, 4, 4, WHITE)
    yy = y + 16
    for ln in lines:
        if ln is None:
            c.rects([(x + 4 + d, yy + 3, 2, 1) for d in range(0, w - 10, 4)], "#e08ab8")
            yy += 6
            continue
        col = txt
        if isinstance(ln, tuple):
            ln, col = ln
        c.text(x + 4, yy, ln, col, 1)
        yy += 10

def build_player_card():
    W, H = 300, 118
    c = Canvas(W, H)
    c.rect(0, 0, W, H, BG)
    starfield(c, 30, 21, 1, 1, W - 2, H - 2)

    window(c, 2, 2, 180, 114, "PLAYER.DAT", [
        ("NAME    ARYA PATIL", "#8a0f4a"),
        "CLASS   SOFTWARE ENGINEER",
        "SCHOOL  VIT PUNE - TY, CE",
        "TERM    2024-2028 - CGPA 8.43",
        "BASE    PUNE, MAHARASHTRA, IN",
        None,
        "FOCUS   AI SYSTEMS, BACKEND",
        "        AND FULL-STACK APPS",
        ("STATUS  OPEN TO INTERNSHIPS", "#8a0f4a"),
    ])

    window(c, 186, 2, 112, 114, "QUEST.LOG", [
        ("ACTIVE MISSION", "#8a0f4a"),
        None,
        "SOFTWARE DEV",
        "INTERN",
        "LEARNGEETA",
        "LIBRARY PORTAL",
        "APR 2026 - NOW",
        None,
        "REACT NATIVE +",
        "FASTAPI + MYSQL",
    ], bar="#a7d8ff", body="#dff0ff", txt="#123048", title_txt="#123048")
    c.write("player-card.svg")

# =====================================================================
# 4b. ARSENAL  — pixel technology tiles
# =====================================================================
ARSENAL = [
    ("LANGUAGES", GREEN, [
        ("C++", ["C++"]), ("PYTHON", ["PYTHON"]), ("JAVA", ["JAVA"]),
        ("JAVASCRIPT", ["JAVA", "SCRIPT"]), ("SQL", ["SQL"])]),
    ("FRAMEWORKS & LIBRARIES", CYAN, [
        ("REACT", ["REACT"]), ("REACT NATIVE", ["REACT", "NATIVE"]),
        ("NODE.JS", ["NODE.JS"]), ("EXPRESS", ["EXPRESS"]),
        ("FASTAPI", ["FASTAPI"]), ("FLASK", ["FLASK"])]),
    ("DATA & INFRASTRUCTURE", PINK, [
        ("MONGODB", ["MONGODB"]), ("FIREBASE", ["FIREBASE"]), ("DOCKER", ["DOCKER"]),
        ("LINUX", ["LINUX"]), ("GIT", ["GIT"]), ("POSTMAN", ["POSTMAN"])]),
]

SLOT_W, SLOT_H = 48, 40


def build_arsenal():
    W = 300
    H = 4 + len(ARSENAL) * (10 + SLOT_H + 8)
    c = Canvas(W, H)
    c.rect(0, 0, W, H, BG)
    starfield(c, 34, 41, 1, 1, W - 2, H - 2)

    y = 4
    for label, accent, items in ARSENAL:
        c.rect(2, y, 2, 7, accent)
        c.text(7, y, label, accent, 1)
        end = 7 + text_width(label, 1) + 5
        c.rects([(dx, y + 3, 2, 2) for dx in range(end, W - 4, 6)], "#242440")
        y += 10

        x0 = round((W - len(items) * SLOT_W) / 2)
        for i, (key, lines) in enumerate(items):
            sx = x0 + i * SLOT_W
            c.rect(sx + 1, y, SLOT_W - 2, SLOT_H, "#0d0d1c")
            c.frame(sx + 1, y, SLOT_W - 2, SLOT_H, "#242440", 1)
            c.rects([(sx + 2, y + 1, 3, 1), (sx + 2, y + 1, 1, 3)], accent)
            rows, pal = ICONS[key]
            sprite(c, sx + (SLOT_W - 16) // 2, y + 4, rows, pal, s=1)
            ty = y + 23
            for ln in lines:
                # tighten tracking rather than overflow the tile on long names
                tr = 1 if text_width(ln, 1, 1) <= SLOT_W - 6 else 0
                c.ctext(sx + SLOT_W / 2, ty, ln, WHITE, 1, tr)
                ty += 9
        y += SLOT_H + 8

    c.write("arsenal.svg")


# =====================================================================
# 5. FOOTER
# =====================================================================
def build_footer():
    W, H = 300, 50
    c = Canvas(W, H)
    c.rect(0, 0, W, H, BG)
    starfield(c, 45, 99, 1, 1, W - 2, 30)
    sprite(c, 8, 4, CLOUD, CLOUD_PAL, 1)
    sprite(c, 274, 10, CLOUD, CLOUD_PAL, 1)
    c.cshadow_text(W / 2, 6, "THANKS FOR PLAYING", PINK, GREEN, 2, 1)
    c.raw('<g><animate attributeName="opacity" values="1;1;0.2;0.2" dur="1.6s" repeatCount="indefinite"/>')
    c.ctext(W / 2, 22, "CONTINUE? > LETS BUILD SOMETHING", GREEN, 1)
    c.raw("</g>")
    c.raw('<g><animateTransform attributeName="transform" type="translate" '
          'values="0 0; 0 -5; 0 0" dur="2.2s" repeatCount="indefinite"/>')
    sprite(c, 18, 16, HERO, HERO_PAL, 1)
    c.raw("</g>")
    sprite(c, 268, 21, CAT, CAT_PAL, 1)
    ground(c, 34, W)
    c.write("footer.svg")


if __name__ == "__main__":
    build_banner()
    build_marquee("marquee.svg", ["PYTHON", "C++", "REACT", "FASTAPI", "NODE.JS",
                                  "MYSQL", "MONGODB", "DOCKER", "PYTORCH", "LINUX"])
    build_header("hdr-profile.svg",  "LEVEL 01", "THE PLAYER")
    build_header("hdr-arsenal.svg",  "LEVEL 02", "ARSENAL",    CYAN)
    build_header("hdr-missions.svg", "LEVEL 03", "MISSIONS",   YELLOW)
    build_header("hdr-trophies.svg", "LEVEL 04", "TROPHIES",   ORANGE)
    build_header("hdr-stats.svg",    "LEVEL 05", "GAME STATS", LILAC)
    build_header("hdr-contact.svg",  "SAVE PT.", "CONTACT",    GREEN)
    build_player_card()
    build_arsenal()
    build_footer()
