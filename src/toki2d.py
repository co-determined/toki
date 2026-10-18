"""The speech-bubble puppet in 2D, posed by the same parameters a puppeteer uses:
wrist tilt (head angle), thumb drop (mouth), eye focus, lids, rod-arm angles.

Local frame: playboard top edge at y=0; the puppet rises into negative y.
"""
import cairo, math, random
from fleece import fleece, muppet_eye, shade, mix

CREAM = (0.955, 0.925, 0.845)
INKNAVY = (0.13, 0.17, 0.33)
MOUTH = (0.10, 0.11, 0.22)
TONGUE = (0.86, 0.45, 0.50)

DEFAULT = dict(W=290, H=190, R=0.40, lift=58, tail_x=36, ttop=68, tbot=48, fillet=14, lean=-62.0,
               tilt=0.0, mouth=0.0, look=(0.0, 0.25), lids=0.0, brow=0.0,
               arm_l=(2.3, 0.0), arm_r=(0.85, 0.0), curl=True, rods=False,
               body=CREAM, trim=INKNAVY, hands=INKNAVY, curl_rgb=None, piping=True,
               squash=0.0, blink=False, eye_r=30, eye_gap=1.08, smile=0.35)


def P(**kw):
    d = dict(DEFAULT)
    d.update(kw)
    return d


def bubble_outline(ctx, p, jaw=0.0):
    W, H = p["W"] * (1 + p["squash"] * 0.12), p["H"] * (1 - p["squash"] * 0.12) + jaw
    R = p["R"] * min(W, H)
    cy = -p["lift"] - H / 2
    x0, x1, y0, y1 = -W / 2, W / 2, cy - H / 2, cy + H / 2
    tx, lean = p["tail_x"], p["lean"]
    ttop, tbot, f = p["ttop"], p["tbot"], p["fillet"]
    a, b = tx + ttop / 2, tx - ttop / 2
    # keep the tail and its fillets on the flat part of the bottom edge
    lo, hi = x0 + R + 1, x1 - R - 1
    if b - f < lo:
        shift = lo - (b - f); a += shift; b += shift; tx += shift
    if a + f > hi:
        shift = (a + f) - hi; a -= shift; b -= shift; tx -= shift
    ctx.move_to(x0 + R, y0)
    ctx.line_to(x1 - R, y0)
    ctx.arc(x1 - R, y0 + R, R, -math.pi / 2, 0)
    ctx.line_to(x1, y1 - R)
    ctx.arc(x1 - R, y1 - R, R, 0, math.pi / 2)
    ctx.line_to(a + f, y1)
    ctx.curve_to(a + 2, y1, a - 2 + lean * 0.3, y1 + 26, tx + lean + tbot / 2, 46)
    ctx.line_to(tx + lean - tbot / 2, 46)
    ctx.curve_to(b + 2 + lean * 0.4, y1 + 30, b - 2, y1, b - f, y1)
    ctx.line_to(x0 + R, y1)
    ctx.arc(x0 + R, y1 - R, R, math.pi / 2, math.pi)
    ctx.line_to(x0, y0 + R)
    ctx.arc(x0 + R, y0 + R, R, math.pi, 3 * math.pi / 2)
    ctx.close_path()
    return dict(W=W, H=H, cy=cy, top=y0, bottom=y1, x0=x0, x1=x1)


def hand(ctx, x, y, r, ang, rgb, seed, open_=0.6):
    """Four-finger Muppet hand: palm, three finger lobes, a thumb. ang = direction the hand points."""
    def path(c):
        c.save(); c.translate(x, y); c.rotate(ang)
        c.new_sub_path(); c.save(); c.scale(r * 1.0, r * 0.86); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore()
        for i, off in enumerate((-0.55, 0.0, 0.55)):
            fx = r * 0.95
            fy = off * r * (0.80 + 0.40 * open_)
            c.new_sub_path(); c.save(); c.translate(fx, fy); c.rotate(off * 0.6 * open_); c.scale(r * 0.62, r * 0.27)
            c.arc(0, 0, 1, 0, 2 * math.pi); c.restore()
        c.new_sub_path(); c.save(); c.translate(r * 0.1, -r * 0.85); c.rotate(-1.0 - 0.4 * open_); c.scale(r * 0.5, r * 0.3)
        c.arc(0, 0, 1, 0, 2 * math.pi); c.restore()
        c.restore()
    fleece(ctx, path, rgb, seed=seed, density=0.7, fuzz=0.25, ao=0.35)


def arm(ctx, sx, sy, ang, length, thick, p, seed, side, rods=False):
    ex = sx + math.cos(ang) * length
    ey = sy + math.sin(ang) * length
    bend = side * length * 0.12

    def path(c):
        from shapes import limb
        limb(c, sx, sy, ex, ey, thick, thick * 0.78, bend=bend)
    fleece(ctx, path, p["body"], seed=seed, density=0.9, fuzz=0.7, ao=0.6)
    # cuff
    if rods:
        ctx.save()
        ctx.set_source_rgba(0.12, 0.12, 0.12, 0.85)
        ctx.set_line_width(2.2)
        ctx.move_to(ex, ey)
        ctx.line_to(ex + side * 10, 60)
        ctx.stroke()
        ctx.restore()
    hand(ctx, ex, ey, thick * 0.92, ang, p["hands"], seed + 7)


def curl(ctx, cx, top, rgb, seed, size=1.0, tilt=0.0):
    """The forelock: a fleece curl shaped like the hook of a question mark. The head is the dot."""
    pts, ws = [], []
    s = size
    # spiral hook, then a short stem down into the head
    for i in range(60):
        u = i / 59
        a = math.pi * (1.15 + 1.45 * u)
        rr = s * (24 - 4 * u)
        pts.append((cx + 4 * s + math.cos(a) * rr, top - 34 * s + math.sin(a) * rr))
        ws.append(s * (9 + 6 * u))
    ex, ey = pts[-1]
    for i in range(1, 12):
        u = i / 11
        pts.append((ex - 6 * s * u, ey + 20 * s * u))
        ws.append(s * 15)

    def path(c):
        c.save(); c.translate(cx, top); c.rotate(tilt); c.translate(-cx, -top)
        left, right = [], []
        for i in range(len(pts)):
            j0, j1 = max(0, i - 1), min(len(pts) - 1, i + 1)
            tx, ty = pts[j1][0] - pts[j0][0], pts[j1][1] - pts[j0][1]
            L = math.hypot(tx, ty) or 1
            nx, ny = -ty / L, tx / L
            w = ws[i] / 2
            left.append((pts[i][0] + nx * w, pts[i][1] + ny * w))
            right.append((pts[i][0] - nx * w, pts[i][1] - ny * w))
        c.move_to(*left[0])
        for q in left[1:]:
            c.line_to(*q)
        for q in reversed(right):
            c.line_to(*q)
        c.close_path()
        # rounded end of the hook
        c.new_sub_path(); c.arc(pts[0][0], pts[0][1], ws[0] / 2, 0, 2 * math.pi)
        c.restore()
    fleece(ctx, path, rgb, seed=seed, density=1.1, fuzz=0.9, ao=0.4)


def draw(ctx, p, seed=11):
    """Draw the puppet. Returns geometry for callouts."""
    jaw = p["mouth"] * 34
    # wrist pivot: where the sleeve meets the head
    pivot = (p["tail_x"], -p["lift"])
    geo = {}

    # arms behind the body when they hang back; draw first
    def body_path(c):
        geo.update(bubble_outline(c, p, jaw))

    ctx.save()
    ctx.translate(*pivot); ctx.rotate(p["tilt"]); ctx.translate(-pivot[0], -pivot[1])
    # body
    fleece(ctx, body_path, p["body"], seed=seed, density=1.0, fuzz=1.0)
    g = geo
    # piping: the ink outline of a speech balloon, as a sewn cord
    if p["piping"]:
        ctx.save()
        ctx.new_path(); bubble_outline(ctx, p, jaw)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_source_rgb(*p["trim"])
        ctx.set_line_width(9)
        ctx.stroke_preserve()
        ctx.set_source_rgba(*shade(p["trim"], 0.12), 0.5)
        ctx.set_line_width(3)
        ctx.set_dash([2.2, 3.4])
        ctx.stroke()
        ctx.restore()
    W, H, cy, top = g["W"], g["H"], g["cy"], g["top"]
    # mouth: a wide hinge across the lower face; open = the lower jaw drops
    mw = W * 0.56
    my = cy + (H - jaw) * 0.14 - jaw * 0.05
    ctx.save()
    if p["mouth"] > 0.04:
        ctx.new_path()
        ctx.move_to(-mw / 2, my)
        ctx.curve_to(-mw / 4, my + 4 - p["smile"] * 6, mw / 4, my + 4 - p["smile"] * 6, mw / 2, my)
        drop = jaw * 1.25 + 8
        ctx.curve_to(mw / 2 - 4, my + drop * 0.9, mw * 0.2, my + drop * 1.05, 0, my + drop * 1.05)
        ctx.curve_to(-mw * 0.2, my + drop * 1.05, -mw / 2 + 4, my + drop * 0.9, -mw / 2, my)
        ctx.close_path()
        ctx.set_source_rgb(*MOUTH)
        ctx.fill_preserve()
        ctx.clip()
        ctx.set_source_rgb(*TONGUE)
        ctx.save(); ctx.translate(mw * 0.06, my + drop * 1.0); ctx.scale(mw * 0.26, drop * 0.42)
        ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore(); ctx.fill()
        ctx.reset_clip()
        ctx.set_source_rgba(*shade(p["body"], -0.3), 0.6)
        ctx.set_line_width(2.5)
        ctx.move_to(-mw / 2, my)
        ctx.curve_to(-mw / 4, my + 4 - p["smile"] * 6, mw / 4, my + 4 - p["smile"] * 6, mw / 2, my)
        ctx.stroke()
    else:
        ctx.set_source_rgb(*MOUTH)
        ctx.set_line_width(4)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        s = p["smile"]
        ctx.move_to(-mw / 2, my - s * 4)
        ctx.curve_to(-mw / 4, my + 10 * s + 2, mw / 4, my + 10 * s + 2, mw / 2, my - s * 4)
        ctx.stroke()
        # mouth corners (the hinge)
        for sd in (-1, 1):
            ctx.arc(sd * mw / 2, my - s * 4, 2.6, 0, 2 * math.pi)
            ctx.fill()
    ctx.restore()
    # eyes: set high and close, pupils set for focus
    er = p["eye_r"]
    ey = top + H * 0.30
    for sd in (-1, 1):
        ex = sd * er * p["eye_gap"] + 4
        lx = p["look"][0] - sd * 0.12  # slight convergence: the focus point sits just in front
        lid = 1.0 if p["blink"] else p["lids"]
        muppet_eye(ctx, ex, ey, er, look=(lx, p["look"][1]), lid=lid, lid_rgb=shade(p["body"], -0.04),
                   rim_rgb=None, seed=seed + sd)
        if p["brow"]:
            ctx.save()
            ctx.set_source_rgb(*p["trim"])
            ctx.set_line_width(5); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.move_to(ex - er * 0.7, ey - er * 1.25 - sd * p["brow"] * 6)
            ctx.line_to(ex + er * 0.7, ey - er * 1.25 + sd * p["brow"] * 6)
            ctx.stroke(); ctx.restore()
    geo.update(eye_y=ey, eye_r=er, mouth_y=my, mouth_w=mw)
    if p["curl"]:
        curl(ctx, 10, top + 2, p["curl_rgb"] or p["trim"], seed + 3)
    # arms (rod arms from the sides)
    sy = cy + H * 0.1
    for side, (ang, _) in ((-1, p["arm_l"]), (1, p["arm_r"])):
        sx = side * (W / 2 - 14)
        arm(ctx, sx, sy, ang, 74, 24, p, seed + 20 + side, side, rods=p["rods"])
    ctx.restore()
    return geo
