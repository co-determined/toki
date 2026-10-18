"""Exploration sheet 02: color roughs on the three picks, and where the open seat
on the color wheel is."""
import cairo, math, json, sys, os
from shapes import paper, text, BOARD, INK, PENCIL, wobble_ring, rrect, ellipse
from fleece import fleece, muppet_eye, shade
import toki2d as T

W, H = 2300, 1330
CELL = 370
MX = 60

BUBBLE_WAYS = [
    ("paper & ink", (0.955, 0.925, 0.845), (0.13, 0.17, 0.33)),
    ("lavender & plum", (0.80, 0.74, 0.90), (0.36, 0.17, 0.40)),
    ("mint & teal", (0.72, 0.90, 0.80), (0.07, 0.38, 0.40)),
    ("coral & maroon", (0.96, 0.62, 0.52), (0.45, 0.10, 0.16)),
    ("sky & white", (0.62, 0.78, 0.95), (0.98, 0.98, 0.97)),
    ("marigold & brown", (0.98, 0.76, 0.30), (0.36, 0.22, 0.12)),
]


def board(ctx, x, y, w):
    ctx.set_source_rgb(*BOARD)
    ctx.rectangle(x, y, w, 24)
    ctx.fill()
    ctx.set_source_rgba(0, 0, 0, 0.18)
    ctx.rectangle(x, y, w, 3)
    ctx.fill()


def question_creature(ctx, body, trim, seed):
    T.curl(ctx, -10, -60, body, seed, size=3.0)
    # eyes on the top of the hook
    for sd in (-1, 1):
        muppet_eye(ctx, -2 + sd * 22, -232, 21, look=(0.1 - sd * 0.12, 0.3))
    # small mouth on the hook's front
    ctx.set_source_rgb(*trim); ctx.set_line_width(4); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(-20, -196); ctx.curve_to(-8, -186, 8, -186, 18, -196); ctx.stroke()
    # the dot: a ball it balances on
    def dot(c):
        ellipse(c, -16, -26, 34, 32)
    fleece(ctx, dot, trim, seed=seed + 4, fuzz=0.8)
    for sd in (-1, 1):
        T.arm(ctx, -16 + sd * 14, -110, math.pi / 2 - sd * 1.0, 56, 18,
              dict(body=body, hands=trim), seed + 9 + sd, sd)


def book_creature(ctx, cover, pages, seed):
    bw, bh = 170, 210
    x0, y0 = -bw / 2, -bh - 20
    def pg(c):
        c.rectangle(x0 + 16, y0 + 8, bw, bh + 40)
    fleece(ctx, pg, pages, seed=seed + 1, fuzz=0.3, ao=0.4)
    ctx.set_source_rgba(*shade(pages, -0.25), 0.6); ctx.set_line_width(1)
    for i in range(14):
        ctx.move_to(x0 + bw + 4, y0 + 14 + i * 4.2); ctx.line_to(x0 + bw + 15, y0 + 14 + i * 4.2)
    ctx.stroke()
    def cov(c):
        rrect(c, x0, y0, bw, bh + 40, 10)
    fleece(ctx, cov, cover, seed=seed, fuzz=0.6)
    for sd in (-1, 1):
        muppet_eye(ctx, sd * 30, y0 + 62, 26, look=(-sd * 0.12, 0.3))
    ctx.set_source_rgb(*shade(cover, -0.35)); ctx.set_line_width(5); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(-46, y0 + 128); ctx.curve_to(-20, y0 + 146, 20, y0 + 146, 46, y0 + 128); ctx.stroke()
    for sd in (-1, 1):
        T.arm(ctx, sd * bw / 2, y0 + 120, math.pi / 2 - sd * 0.9, 60, 20,
              dict(body=cover, hands=pages), seed + 9 + sd, sd)


# cast colors: approximate fleece/fur colors, for the wheel only
def load_cast():
    p = os.path.join(os.path.dirname(__file__), "..", "notes", "cast_colors.json")
    if os.path.exists(p):
        return json.load(open(p))
    return []


def wheel(ctx, cx, cy, R, cast, pick):
    import colorsys
    # hue ring
    for i in range(360):
        a0, a1 = math.radians(i - 90), math.radians(i + 1.2 - 90)
        r, g, b = colorsys.hls_to_rgb(i / 360, 0.6, 0.55)
        ctx.set_source_rgb(r, g, b)
        ctx.move_to(cx + math.cos(a0) * R * 0.78, cy + math.sin(a0) * R * 0.78)
        ctx.arc(cx, cy, R, a0, a1)
        ctx.arc_negative(cx, cy, R * 0.78, a1, a0)
        ctx.close_path(); ctx.fill()
    # neutral center: lightness axis for the near-whites, browns, greys
    g = cairo.RadialGradient(cx, cy, 0, cx, cy, R * 0.7)
    g.add_color_stop_rgb(0, 0.97, 0.95, 0.90); g.add_color_stop_rgb(1, 0.80, 0.78, 0.74)
    ctx.set_source(g); ctx.arc(cx, cy, R * 0.7, 0, 2 * math.pi); ctx.fill()
    placed = []
    for c in cast:
        rgb = tuple(c["rgb"])
        h, l, s = colorsys.rgb_to_hls(*rgb)
        if s < 0.18 or c.get("neutral"):
            rr = R * 0.12 + R * 0.5 * (1 - l)
            a = math.radians(c.get("angle", 200) - 90)
        else:
            rr = R * 0.89
            a = math.radians(h * 360 - 90)
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        ctx.new_path()
        ctx.set_source_rgb(*rgb); ctx.arc(x, y, 13, 0, 2 * math.pi); ctx.fill_preserve()
        ctx.set_source_rgba(0, 0, 0, 0.6); ctx.set_line_width(1.5); ctx.stroke()
        out_r = (R + 22) if rr > R * 0.8 else (rr + 20)
        lx, ly = cx + math.cos(a) * out_r, cy + math.sin(a) * out_r
        dy = sum(14 for (px, py) in placed if abs(px - lx) < 90 and abs(py - ly) < 14)
        placed.append((lx, ly + dy))
        ca = math.cos(a)
        text(ctx, c["name"], lx, ly + dy + 5, 14, face="Gill Sans",
             align="left" if ca > 0.25 else ("right" if ca < -0.25 else "center"), alpha=0.85)
    # the pick
    x, y = cx, cy - R * 0.05
    ctx.new_path()
    ctx.set_source_rgb(*pick); ctx.arc(x, y, 18, 0, 2 * math.pi); ctx.fill_preserve()
    ctx.set_source_rgb(0.13, 0.17, 0.33); ctx.set_line_width(5); ctx.stroke()
    wobble_ring(ctx, x, y, 34, 34, seed=4, width=2.6)


def render(out, pick_idx=0):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    paper(ctx, W, H, seed=7)
    text(ctx, "THE WORKSHOP", MX, 74, 40, weight=cairo.FONT_WEIGHT_BOLD)
    text(ctx, "Exploration sheet 02 · color roughs on the three picks · and where the open seat is", MX, 114, 22, face="Gill Sans")
    text(ctx, "The bubble now has the curl from 19 (the hook of a question mark; the head is the dot) and an angled "
              "comic-strip tail, which is also the sleeve over the puppeteer's forearm.", MX, 146, 17, face="Gill Sans",
         slant=cairo.FONT_SLANT_ITALIC, alpha=0.75)
    # row 1: bubble colorways
    y_board = 520
    for i, (name, body, trim) in enumerate(BUBBLE_WAYS):
        x = MX + 10 + i * CELL + CELL / 2
        ctx.save(); ctx.rectangle(x - CELL / 2, 160, CELL, y_board + 20 - 160); ctx.clip()
        ctx.translate(x, y_board); ctx.scale(0.8, 0.8)
        T.draw(ctx, T.P(body=body, trim=trim, hands=trim), seed=30 + i)
        ctx.restore()
        board(ctx, x - CELL / 2 + 14, y_board, CELL - 28)
        text(ctx, f"B{i+1}  {name}", x - CELL / 2 + 18, y_board + 54, 17, face="Futura", weight=cairo.FONT_WEIGHT_BOLD, alpha=0.85)
        if i == pick_idx:
            wobble_ring(ctx, x, y_board - 125, CELL * 0.5, 190, seed=12)
    notes1 = {0: "paper & ink: the color words are written in", 1: "Abby's neighborhood",
              2: "reads 'fresh', not 'someone'", 3: "warm, but Zoe/Elmo-adjacent on camera",
              4: "white trim vanishes against the sky", 5: "Big Bird's yard"}
    for i, s in notes1.items():
        x = MX + 10 + i * CELL + 4
        good = i == 0
        text(ctx, s, x, y_board + 80, 14, face="Chalkboard SE", rgb=(0.16, 0.28, 0.55) if good else PENCIL)
    # row 2: question creature, book, wheel
    y2 = 1120
    q_ways = [("Q1 marigold", (0.98, 0.76, 0.30), (0.36, 0.22, 0.12)), ("Q2 periwinkle", (0.62, 0.66, 0.93), (0.20, 0.20, 0.45))]
    b_ways = [("K1 oxblood", (0.50, 0.14, 0.16), (0.96, 0.93, 0.84)), ("K2 teal", (0.10, 0.45, 0.48), (0.96, 0.93, 0.84))]
    for i, (name, body, trim) in enumerate(q_ways):
        x = MX + 10 + i * CELL + CELL / 2
        ctx.save(); ctx.translate(x, y2); ctx.scale(0.9, 0.9)
        question_creature(ctx, body, trim, 50 + i)
        ctx.restore()
        board(ctx, x - CELL / 2 + 14, y2, CELL - 28)
        text(ctx, name, x - CELL / 2 + 18, y2 + 54, 17, face="Futura", weight=cairo.FONT_WEIGHT_BOLD, alpha=0.85)
    text(ctx, "strong symbol, weak face: nowhere to put a hand", MX + 14, y2 + 80, 14, face="Chalkboard SE", rgb=PENCIL)
    text(ctx, "so: keep the hook, put it on the bubble", MX + 14, y2 + 102, 14, face="Chalkboard SE", rgb=(0.16, 0.28, 0.55))
    for i, (name, cover, pages) in enumerate(b_ways):
        x = MX + 10 + (i + 2) * CELL + CELL / 2
        ctx.save(); ctx.translate(x, y2); ctx.scale(0.9, 0.9)
        book_creature(ctx, cover, pages, 60 + i)
        ctx.restore()
        board(ctx, x - CELL / 2 + 14, y2, CELL - 28)
        text(ctx, name, x - CELL / 2 + 18, y2 + 54, 17, face="Futura", weight=cairo.FONT_WEIGHT_BOLD, alpha=0.85)
    text(ctx, "a library mascot: says 'contains facts', not 'someone'", MX + 14 + 2 * CELL, y2 + 80, 14, face="Chalkboard SE", rgb=PENCIL)
    text(ctx, "and a book can't be wrong. this one has to be able to be.", MX + 14 + 2 * CELL, y2 + 102, 14, face="Chalkboard SE", rgb=PENCIL)
    # wheel
    cast = load_cast()
    wx, wy = MX + 4 * CELL + CELL, y2 - 230
    wheel(ctx, wx, wy, 230, cast, BUBBLE_WAYS[pick_idx][1])
    text(ctx, "the cast on the wheel (approximate fleece/fur colors)", wx, wy + 300, 16, face="Gill Sans", align="center", alpha=0.8)
    text(ctx, "the saturated ring is full. the open seat is near the middle: a warm paper white, outlined in ink.",
         wx, wy + 324, 15, face="Chalkboard SE", align="center", rgb=(0.16, 0.28, 0.55))
    text(ctx, "drawn in code (pycairo) · Claude · 2026-10-17", W - MX, H - 40, 16, face="Gill Sans", align="right", alpha=0.6)
    surf.write_to_png(out)
    print("wrote", out)


if __name__ == "__main__":
    render(sys.argv[1] if len(sys.argv) > 1 else "../png/02_color.png")
