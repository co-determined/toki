"""Exploration sheet 01: a parametric puppet generator swept across 12 body
families, 4 variants each, rendered as solid silhouettes behind a playboard.

usage: python3 generator.py [--picks 7,19,30] [--out ../png/01_exploration.png]
"""
import cairo, math, random, argparse, json, os
from shapes import *

CW, CH = 270, 300
COLS, ROWS = 8, 6
MX, MT, MB = 70, 190, 120
W = MX * 2 + CW * COLS
H = MT + CH * ROWS + MB


# ---------------------------------------------------------------- families
def eyes_top(ctx, r, cx, top, size=None, sep=None):
    e = size or r.uniform(13, 22)
    s = sep or e * r.uniform(0.75, 1.25)
    for side in (-1, 1):
        ellipse(ctx, cx + side * s, top + e * 0.15, e, e * r.uniform(1.0, 1.25))
        ctx.fill()


def tuft(ctx, r, cx, top, w):
    n = r.randint(3, 7)
    pts = []
    for i in range(n * 2 + 1):
        u = i / (n * 2)
        x = cx - w / 2 + u * w
        y = top + (-(r.uniform(18, 34)) if i % 2 else 6)
        pts.append((x, y))
    ctx.move_to(cx - w / 2, top + 12)
    for p in pts:
        ctx.line_to(*p)
    ctx.line_to(cx + w / 2, top + 12)
    ctx.close_path()
    ctx.fill()


def fam_monster(ctx, r):
    rx, ry = r.uniform(72, 104), r.uniform(85, 118)
    cy = -ry + r.uniform(0, 40)
    blob(ctx, 0, cy, rx, ry, r.uniform(2.0, 3.3), squish=r.uniform(-0.05, 0.25))
    ctx.fill()
    top = cy - ry
    k = r.random()
    if k < 0.45:
        eyes_top(ctx, r, 0, top + 6)
    elif k < 0.65:
        for side in (-1, 1):
            limb(ctx, side * 18, top + 10, side * 30, top - 38, 8, 6, bend=side * 6); ctx.fill()
            ellipse(ctx, side * 30, top - 44, 15, 15); ctx.fill()
    if r.random() < 0.5:
        tuft(ctx, r, r.uniform(-15, 15), top + 4, rx * 0.9)
    arms(ctx, r, rx * 0.82, cy + ry * 0.15, r.uniform(55, 85), r.uniform(18, 26))
    return dict(family="monster")


def bubble_path(ctx, cx, cy, w, h, rad, tx, tip):
    """Speech bubble: rounded rect + curved tail from bottom edge at x=tx down to tip=(x,y)."""
    x, y = cx - w / 2, cy - h / 2
    rrect(ctx, x, y, w, h, rad)
    ctx.fill()
    bx = cx + tx
    ctx.move_to(bx - 26, cy + h / 2 - 4)
    ctx.curve_to(bx - 20, cy + h / 2 + 20, tip[0] - 6, tip[1] - 30, tip[0], tip[1])
    ctx.curve_to(tip[0] + 16, tip[1] - 34, bx + 22, cy + h / 2 + 16, bx + 26, cy + h / 2 - 4)
    ctx.close_path()
    ctx.fill()


def fam_bubble(ctx, r):
    w, h = r.uniform(150, 220), r.uniform(105, 150)
    rad = h * r.uniform(0.28, 0.5)
    cy = -h / 2 - r.uniform(55, 100)
    tx = r.uniform(-0.25, 0.25) * w
    tip = (tx + r.uniform(-40, 40), 30)
    bubble_path(ctx, 0, cy, w, h, rad, tx, tip)
    if r.random() < 0.4:
        eyes_top(ctx, r, r.uniform(-20, 20), cy - h / 2 + 6)
    if r.random() < 0.75:
        arms(ctx, r, w / 2 - 8, cy + h * 0.1, r.uniform(45, 70), r.uniform(14, 20))
    return dict(family="speech bubble")


def fam_cloud(ctx, r):
    w, h = r.uniform(150, 210), r.uniform(95, 130)
    cy = -h / 2 - r.uniform(70, 110)
    ellipse(ctx, 0, cy, w / 2 * 0.8, h / 2 * 0.8); ctx.fill()
    n = r.randint(6, 10)
    for i in range(n):
        a = 2 * math.pi * i / n + r.uniform(-0.15, 0.15)
        lr = r.uniform(0.28, 0.42) * h
        ellipse(ctx, math.cos(a) * w * 0.38, cy + math.sin(a) * h * 0.36, lr, lr); ctx.fill()
    # trailing thought-dots down to the playboard
    k = r.randint(2, 3)
    x = r.uniform(-30, 30)
    y = cy + h / 2 + 10
    for i in range(k):
        rr = 22 - i * 6
        y += rr + 10
        x += r.uniform(-12, 12)
        ellipse(ctx, x, y, rr, rr * 0.9); ctx.fill()
    ctx.rectangle(x - 9, y, 18, 40); ctx.fill()  # the rod / arm entry
    if r.random() < 0.6:
        arms(ctx, r, w * 0.42, cy + 10, r.uniform(40, 60), 15)
    return dict(family="thought cloud")


def fam_anything(ctx, r):
    hw, hh = r.uniform(55, 72), r.uniform(62, 84)
    cy = -hh - r.uniform(70, 95)
    # body (shirt) to playboard
    bw = r.uniform(80, 110)
    ctx.move_to(-bw * 0.55, cy + hh * 0.75); ctx.line_to(bw * 0.55, cy + hh * 0.75)
    ctx.line_to(bw, 30); ctx.line_to(-bw, 30); ctx.close_path(); ctx.fill()
    blob(ctx, 0, cy, hw, hh, 2.2); ctx.fill()
    style = r.choice(["bun", "flat", "curls", "pony", "bald-ears"])
    top = cy - hh
    if style == "bun":
        ellipse(ctx, 0, top - 8, 28, 22); ctx.fill()
    elif style == "flat":
        ctx.rectangle(-hw * 0.95, top - 22, hw * 1.9, 40); ctx.fill()
    elif style == "curls":
        for i in range(9):
            a = math.pi + math.pi * i / 8
            ellipse(ctx, math.cos(a) * hw * 1.02, cy + math.sin(a) * hh * 1.0, 20, 20); ctx.fill()
    elif style == "pony":
        limb(ctx, hw * 0.6, top + 20, hw * 1.6, cy + 10, 26, 10, bend=20); ctx.fill()
    else:
        for side in (-1, 1):
            ellipse(ctx, side * hw * 1.05, cy, 16, 24); ctx.fill()
    arms(ctx, r, bw * 0.6, cy + hh * 1.0, r.uniform(55, 80), 18)
    return dict(family="anything muppet")


def fam_question(ctx, r):
    t = r.uniform(42, 60)
    R = r.uniform(52, 66)
    cy = -R - r.uniform(130, 160)
    ctx.set_line_width(t)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.new_sub_path()
    ctx.arc(0, cy, R, math.pi * 1.05, math.pi * 2.45)
    # stem down
    ex = math.cos(math.pi * 2.45) * R
    ey = cy + math.sin(math.pi * 2.45) * R
    ctx.curve_to(ex - 10, ey + 30, 0, ey + 30, 0, ey + 60)
    ctx.stroke()
    # the dot sits on the playboard
    ellipse(ctx, 0, -t * 0.55, t * 0.62, t * 0.6); ctx.fill()
    if r.random() < 0.5:
        eyes_top(ctx, r, 0, cy - R - t * 0.4, size=13, sep=17)
    if r.random() < 0.6:
        arms(ctx, r, t * 0.45, ey + 40, r.uniform(40, 60), 14)
    return dict(family="question mark")


def fam_book(ctx, r):
    bw, bh = r.uniform(120, 160), r.uniform(110, 150)
    by = -bh - r.uniform(15, 40)
    ctx.rectangle(-bw / 2, by, bw, bh + 60); ctx.fill()  # lower cover / body
    # upper cover hinged at back, open as a jaw
    open_a = r.uniform(0.25, 0.7)
    ctx.save(); ctx.translate(-bw / 2, by); ctx.rotate(-open_a)
    ctx.rectangle(0, -18, bw * 1.02, 22); ctx.fill()
    ctx.restore()
    # pages fanning in the mouth
    for i in range(3):
        ctx.save(); ctx.translate(-bw / 2, by); ctx.rotate(-open_a * (0.25 + 0.2 * i))
        ctx.rectangle(0, -3, bw * 0.96, 3); ctx.fill(); ctx.restore()
    if r.random() < 0.6:
        ctx.save(); ctx.translate(-bw / 2, by); ctx.rotate(-open_a)
        eyes_top(ctx, r, bw * 0.55, -26, size=15, sep=18)
        ctx.restore()
    arms(ctx, r, bw / 2, by + bh * 0.45, r.uniform(45, 70), 16)
    return dict(family="book")


def fam_robot(ctx, r):
    hw, hh = r.uniform(110, 150), r.uniform(85, 110)
    hy = -hh - r.uniform(85, 110)
    rrect(ctx, -hw / 2, hy, hw, hh, r.uniform(4, 22)); ctx.fill()
    ctx.rectangle(-hw * 0.42, hy + hh, hw * 0.84, 140); ctx.fill()
    ctx.rectangle(-4, hy - 34, 8, 36); ctx.fill()
    ellipse(ctx, 0, hy - 38, 10, 10); ctx.fill()
    for side in (-1, 1):
        ctx.rectangle(side * hw / 2 - (10 if side < 0 else 0), hy + hh * 0.35, 10, 24); ctx.fill()
    arms(ctx, r, hw * 0.4, hy + hh + 25, r.uniform(55, 75), 16)
    return dict(family="screen robot (control)")


def fam_lantern(ctx, r):
    w, h = r.uniform(120, 170), r.uniform(120, 165)
    cy = -h / 2 - r.uniform(70, 110)
    blob(ctx, 0, cy, w / 2, h / 2, r.uniform(2.0, 2.6)); ctx.fill()
    ctx.rectangle(-w * 0.28, cy - h / 2 - 10, w * 0.56, 16); ctx.fill()
    ctx.rectangle(-w * 0.22, cy + h / 2 - 6, w * 0.44, 14); ctx.fill()
    ctx.set_line_width(5)
    ctx.arc(0, cy - h / 2 - 12, 18, math.pi, 0); ctx.stroke()
    ctx.set_line_width(1.2)
    ctx.move_to(0, cy - h / 2 - 30); ctx.line_to(0, -CH + 30); ctx.stroke()  # hangs from a line
    if r.random() < 0.5:
        arms(ctx, r, w / 2 - 6, cy + 10, r.uniform(40, 60), 14)
    return dict(family="paper lantern")


def fam_jelly(ctx, r):
    w, h = r.uniform(140, 190), r.uniform(80, 115)
    cy = -r.uniform(150, 190)
    ctx.move_to(-w / 2, cy)
    ctx.curve_to(-w / 2, cy - h * 1.3, w / 2, cy - h * 1.3, w / 2, cy)
    n = r.randint(4, 7)
    for i in range(n):
        x0 = w / 2 - w * i / n
        x1 = w / 2 - w * (i + 1) / n
        ctx.curve_to(x0, cy + 16, x1, cy + 16, x1, cy)
    ctx.close_path(); ctx.fill()
    k = r.randint(4, 7)
    for i in range(k):
        x = -w * 0.38 + w * 0.76 * i / (k - 1)
        ctx.set_line_width(r.uniform(5, 10))
        ctx.move_to(x, cy)
        ctx.curve_to(x + r.uniform(-30, 30), cy + 60, x + r.uniform(-30, 30), cy + 120, x + r.uniform(-20, 20), 20)
        ctx.stroke()
    return dict(family="jellyfish")


def fam_sheet(ctx, r):
    w, h = r.uniform(130, 170), r.uniform(190, 240)
    top = -h
    ctx.move_to(-w / 2, 20)
    ctx.line_to(-w / 2, top + w / 2)
    ctx.arc(0, top + w / 2, w / 2, math.pi, 0)
    ctx.line_to(w / 2, 20)
    ctx.close_path(); ctx.fill()
    for side in (-1, 1):
        ellipse(ctx, side * (w / 2 + 6), top + h * 0.55, 22, 14, side * 0.5); ctx.fill()
    return dict(family="sheet ghost (control)")


def fam_bulb(ctx, r):
    R = r.uniform(62, 82)
    cy = -R - r.uniform(110, 135)
    ellipse(ctx, 0, cy, R, R * 1.05); ctx.fill()
    ctx.move_to(-R * 0.55, cy + R * 0.7); ctx.line_to(R * 0.55, cy + R * 0.7)
    ctx.line_to(R * 0.38, cy + R * 1.35); ctx.line_to(-R * 0.38, cy + R * 1.35); ctx.close_path(); ctx.fill()
    for i in range(3):
        rrect(ctx, -R * 0.42, cy + R * 1.35 + i * 14, R * 0.84, 12, 5); ctx.fill()
    ctx.rectangle(-R * 0.3, cy + R * 1.35 + 40, R * 0.6, 120); ctx.fill()
    if r.random() < 0.6:
        arms(ctx, r, R * 0.9, cy + R * 0.2, r.uniform(45, 65), 14)
    return dict(family="lightbulb (control)")


def fam_chorus(ctx, r):
    n = r.choice([2, 3, 3, 4])
    bw = r.uniform(130, 180)
    body_top = -r.uniform(100, 130)
    blob(ctx, 0, body_top + 70, bw / 2, 90, 2.4); ctx.fill()
    for i in range(n):
        x = -bw * 0.36 + bw * 0.72 * (i / (n - 1) if n > 1 else 0.5)
        hr = r.uniform(30, 44)
        neck = r.uniform(30, 70)
        limb(ctx, x * 0.6, body_top + 20, x, body_top - neck, 22, 18, bend=r.uniform(-15, 15)); ctx.fill()
        ellipse(ctx, x, body_top - neck - hr * 0.6, hr, hr * 1.05); ctx.fill()
    arms(ctx, r, bw * 0.45, body_top + 50, r.uniform(45, 65), 16)
    return dict(family="chorus (many at once)")


FAMILIES = [fam_monster, fam_bubble, fam_cloud, fam_anything, fam_question, fam_book,
            fam_lantern, fam_jelly, fam_chorus, fam_robot, fam_sheet, fam_bulb]


NOTES = {
    8: "made of words; the tail is the arm sleeve",
    19: "the one who asks, not answers",
    22: "the mouth IS the book opening",
    11: "no: reads as a mushroom cloud",
    12: "no: mushroom cloud again",
    14: "no: a person in disguise",
    30: "lovely, but jellyfish sting",
    34: "reads 'antennae', not 'many'",
    37: "no: the robot it isn't",
    43: "no: scary at 4",
    47: "no: 'idea!' — a cliché",
}

# ---------------------------------------------------------------- sheet
def render(picks, out):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    paper(ctx, W, H, seed=3)
    text(ctx, "THE WORKSHOP", MX, 78, 40, weight=cairo.FONT_WEIGHT_BOLD)
    text(ctx, "Exploration sheet 01 · the first AI puppet on the Street · 48 silhouettes behind a playboard",
         MX, 118, 22, face="Gill Sans")
    text(ctx, "12 body families × 4 seeds from one parametric generator. Fill solid black: if it doesn't read as a silhouette, "
              "it won't read at a four-year-old's distance. Red rings are the picks.",
         MX, 150, 17, face="Gill Sans", slant=cairo.FONT_SLANT_ITALIC, alpha=0.75)
    meta = []
    idx = 0
    for fi, fam in enumerate(FAMILIES):
        for v in range(4):
            idx += 1
            col, row = (idx - 1) % COLS, (idx - 1) // COLS
            x0, y0 = MX + col * CW, MT + row * CH
            board_y = y0 + CH - 58
            r = random.Random(1000 * fi + v * 17 + 5)
            ctx.save()
            ctx.rectangle(x0, y0 + 4, CW, board_y - y0 + 18); ctx.clip()
            ctx.translate(x0 + CW / 2, board_y)
            ctx.scale(0.8, 0.8)
            ctx.set_source_rgb(*INK)
            info = fam(ctx, r)
            ctx.restore()
            # playboard over the puppet's waist
            ctx.set_source_rgb(*BOARD)
            ctx.rectangle(x0 + 8, board_y, CW - 16, 22); ctx.fill()
            ctx.set_source_rgba(0, 0, 0, 0.18)
            ctx.rectangle(x0 + 8, board_y, CW - 16, 3); ctx.fill()
            text(ctx, f"{idx:02d}", x0 + 14, y0 + CH - 14, 16, face="Futura", weight=cairo.FONT_WEIGHT_BOLD, alpha=0.8)
            text(ctx, info["family"], x0 + 44, y0 + CH - 14, 14, face="Gill Sans", alpha=0.7)
            info.update(n=idx, seed=1000 * fi + v * 17 + 5)
            meta.append(info)
            if idx in NOTES:
                good = not NOTES[idx].startswith("no:")
                ctx.save(); ctx.translate(x0 + 12, y0 + 30); ctx.rotate(-0.025)
                text(ctx, NOTES[idx], 0, 0, 15, face="Chalkboard SE", rgb=PENCIL if not good else (0.16, 0.28, 0.55))
                ctx.restore()
            if idx in picks:
                wobble_ring(ctx, x0 + CW / 2, y0 + CH / 2 - 22, CW * 0.47, CH * 0.47, seed=idx)
    # footer
    text(ctx, "controls (things to avoid, drawn so we can see why): screen robot · sheet ghost · lightbulb",
         MX, H - 60, 16, face="Gill Sans", alpha=0.7)
    text(ctx, "drawn in code (pycairo) · Claude · 2026-10-17", W - MX, H - 60, 16, face="Gill Sans", align="right", alpha=0.6)
    surf.write_to_png(out)
    with open(os.path.splitext(out)[0] + ".json", "w") as f:
        json.dump(meta, f, indent=1)
    print("wrote", out, W, H)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--picks", default="")
    ap.add_argument("--out", default="../png/01_exploration.png")
    a = ap.parse_args()
    picks = {int(x) for x in a.picks.split(",") if x}
    render(picks, a.out)
